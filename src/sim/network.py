import heapq
import simpy

from src.prob import random_variable
from src.sim import (
    message,
    node as node_module,
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

        self.id_to_node_map = {}

    def __repr__(self):
        # return (
        #     "Network( \n"
        #     f"{super().__repr__()} \n"
        #     ")"
        # )

        return f"Network(id= {self._id})"

    def register(self, node: node_module.Node):
        self.id_to_node_map[node._id] = node
        log(DEBUG, "Done", node=node)

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

            dst_node = self.id_to_node_map[msg.dst_id]
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

        self.interrupt_forward_messages = self.env.event()
        self.process_forward_messages = env.process(self.forward_messages())

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

        self.interrupt_forward_messages.succeed()
        self.interrupt_forward_messages = self.env.event()

        # Note: Messages are consumed in `forward_messages()` through `forward_time_and_msg_heapq`.
        # The only reason to put messages in `msg_store` is to use it as a trigger to wake up
        # the loop when there is a message to be forwarded.
        self.msg_store.put(msg)

    def forward_messages(self):
        slog(DEBUG, self.env, self, "started")

        while True:
            msg = yield self.msg_store.get()

            min_forward_time, _ = self.forward_time_and_msg_heapq[0]
            wait_time = min_forward_time - self.env.now

            triggered_event = yield self.env.timeout(wait_time) | self.interrupt_forward_messages

            # if triggered_event == {self.interrupt_forward_messages: None}:
            if self.env.now - min_forward_time > 0.0001:
                _, msg = heapq.heappop(self.forward_time_and_msg_heapq)

                dst_node = self.id_to_node_map[msg.dst_id]
                slog(DEBUG, self.env, self, "forwarding", msg=msg, dst_node=dst_node)
                dst_node.put(msg)

            else:
                slog(DEBUG, self.env, self, "wait interrupted by msg arrival")
                self.msg_store.put(msg)

            break
