import simpy

from src.prob import random_variable
from src.sim import (
    message,
    node_module,
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
        return (
            "Network( \n"
            f"{super().__repr__()} \n"
            ")"
        )

    def register(node: node_module.Node):
        self.id_to_node_map[node._id] = node
        log(DEBUG, "Done", dst_id=dst_id, node=node)

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

        self.process_run = env.process(self.run())

    def __repr__(self):
        return (
            "Network_wZeroDelay( \n"
            f"{super().__repr__()} \n"
            ")"
        )

    def run(self):
        while True:
            msg = yield self.msg_store.get()
            check(msg._id in self.id_to_node_map,
                  "A msg for an unregistered node arrived"
                  msg=msg, id_to_node_map=self.id_to_node_map)

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

        self.process_run = env.process(self.run())

    def __repr__(self):
        return (
            "Network_wZeroDelay( \n"
            f"{super().__repr__()} \n"
            f"\t delay_rv= {self.delay_rv} \n"
            ")"
        )

    def run(self):
        # TODO: Complete this

        pass
