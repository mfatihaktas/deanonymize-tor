import simpy

from src.prob import random_variable
from src.sim import (
    message,
    node,
)

from src.debug_utils import *


class Client(node.Node):
    def __init__(
        self,
        env: simpy.Environment,
        _id: str,
        dst_id: str,
        inter_msg_gen_time_rv: random_variable.RandomVariable,
        next_hop = None,
    ):
        super().__init__(env=env, _id=_id)

        self.dst_id = dst_id
        self.inter_msg_gen_time_rv = inter_msg_gen_time_rv
        self.next_hop = next_hop

        self.process_run = env.process(self.run())

    def __repr__(self):
        return (
            "Client( \n"
            f"{super().__repr__()} \n"
            f"\t dst_id= {self.dst_id} \n"
            f"\t inter_msg_gen_time_rv= {self.inter_msg_gen_time_rv} \n"
            ")"
        )

    def run(self):
        check(self.next_hop is not None, "Next hop cannot be `None`")

        msg_id = 0
        while True:
            msg = message.Message(_id=msg_id, src_id=self._id, dst_id=self.dst_id)
            slog(DEBUG, self.env, self, "sending", msg=msg)
            self.next_hop.put(msg)

            msg_id += 1
