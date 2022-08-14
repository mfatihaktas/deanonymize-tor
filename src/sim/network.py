import heapq
import simpy

from src.prob import random_variable
from src.sim import (
    client as client_module,
    message,
    node as node_module,
    server as server_module,
)

from src.debug_utils import *


class Network(node_module.Node):
    def __init__(
        self,
        env: simpy.Environment,
        _id: str,
    ):
        super().__init__(env=env, _id=_id)

        self.msg_store = simpy.Store(env)

        self.client_list = []
        self.id_to_server_map = {}

    def __repr__(self):
        # return (
        #     "Network( \n"
        #     f"{super().__repr__()} \n"
        #     ")"
        # )

        return f"Network(id= {self._id})"

    def register_client(self, client: client_module.Client):
        self.client_list.append(client)
        log(DEBUG, "Done", client=client)

    def register_server(self, server: server_module.Server):
        self.id_to_server_map[server._id] = server
        log(DEBUG, "Done", server=server)

    def get_client_list(self):
        return self.client_list

    def get_server_list(self):
        return list(self.id_to_server_map.values())

    def put(self, msg: message.Message):
        slog(DEBUG, self.env, self, "recved", msg=msg)
        self.msg_store.put(msg)


class Network_wZeroDelay(Network):
    def __init__(
        self,
        env: simpy.Environment,
        _id: str,
    ):
        super().__init__(env=env, _id=_id)
        self.process_forward_messages = env.process(self.forward_messages())

    def __repr__(self):
        # return (
        #     "Network_wZeroDelay( \n"
        #     f"{super().__repr__()} \n"
        #     ")"
        # )

        return f"Network_wZeroDelay(id= {self._id})"

    def forward_messages(self):
        while True:
            msg = yield self.msg_store.get()

            dst_node = self.id_to_server_map[msg.dst_id]
            slog(DEBUG, self.env, self, "forwarding", msg=msg, dst_node=dst_node)
            dst_node.put(msg)


class Network_wDelayAssignedPerMessage(Network):
    def __init__(
        self,
        env: simpy.Environment,
        _id: str,
        delay_rv: random_variable.RandomVariable,
    ):
        super().__init__(env=env, _id=_id)
        self.delay_rv = delay_rv

        self.forward_time_and_msg_heapq = []

        # TODO: Replace interrupt with the "process interrupt"
        # https://simpy.readthedocs.io/en/latest/simpy_intro/process_interaction.html#interrupting-another-process
        self.interrupt_forward_messages = None
        self.forward_messages_process = env.process(self.forward_messages())

    def __repr__(self):
        # return (
        #     "Network_wZeroDelay( \n"
        #     f"{super().__repr__()} \n"
        #     f"\t delay_rv= {self.delay_rv} \n"
        #     ")"
        # )

        return f"Network_wZeroDelay(_id= {self._id})"

    def put(self, msg: message.Message):
        slog(DEBUG, self.env, self, "recved", msg=msg)

        delay = self.delay_rv.sample()
        forward_time = self.env.now + delay
        heapq.heappush(self.forward_time_and_msg_heapq, (forward_time, msg))

        # Note: Messages are consumed in `forward_messages()` through `forward_time_and_msg_heapq`.
        # The only reason to put messages in `msg_store` is to use it as a trigger to wake up
        # the loop when there is a message to be forwarded.
        self.msg_store.put(msg)

        if self.interrupt_forward_messages:
            self.interrupt_forward_messages.succeed()

    def forward_messages(self):
        slog(DEBUG, self.env, self, "started")

        while True:
            msg = yield self.msg_store.get()

            min_forward_time, _ = self.forward_time_and_msg_heapq[0]
            wait_time = min_forward_time - self.env.now

            slog(DEBUG, self.env, self, "waiting for trigger", wait_time=wait_time)
            self.interrupt_forward_messages = self.env.event()
            yield self.env.timeout(wait_time) | self.interrupt_forward_messages
            self.interrupt_forward_messages = None

            if self.env.now - min_forward_time >= 0:
                _, msg = heapq.heappop(self.forward_time_and_msg_heapq)

                dst_node = self.id_to_server_map[msg.dst_id]
                slog(DEBUG, self.env, self, "forwarding", msg=msg, dst_node=dst_node)
                dst_node.put(msg)

            else:
                slog(DEBUG, self.env, self, "wait interrupted by msg arrival")
                self.msg_store.put(msg)
