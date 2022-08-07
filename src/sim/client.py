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
        next_hop: node.Node,
        num_msgs_to_send: int = None,
    ):
        super().__init__(env=env, _id=_id)
        self.dst_id = dst_id
        self.num_msgs_to_send = num_msgs_to_send
        self.inter_msg_gen_time_rv = inter_msg_gen_time_rv
        self.next_hop = next_hop

        self.process_send_messages = env.process(self.send_messages())

    def __repr__(self):
        # return (
        #     "Client( \n"
        #     f"{super().__repr__()} \n"
        #     f"\t dst_id= {self.dst_id} \n"
        #     f"\t num_msgs_to_send= {self.num_msgs_to_send} \n"
        #     f"\t inter_msg_gen_time_rv= {self.inter_msg_gen_time_rv} \n"
        #     ")"
        # )

        return f"Client(id= {self._id})"

    def send_messages(self):
        slog(DEBUG, self.env, self, "started")

        msg_id = 0
        while True:
            inter_msg_gen_time = self.inter_msg_gen_time_rv.sample()
            slog(DEBUG, self.env, self, "waiting", inter_msg_gen_time=inter_msg_gen_time)
            yield self.env.timeout(inter_msg_gen_time)

            msg = message.Message(_id=msg_id, src_id=self._id, dst_id=self.dst_id)
            slog(DEBUG, self.env, self, "sending", msg=msg)
            self.next_hop.put(msg)

            msg_id += 1
            if self.num_msgs_to_send and msg_id >= self.num_msgs_to_send:
                break
