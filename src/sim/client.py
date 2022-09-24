import simpy

from src.attack import adversary as adversary_module
from src.debug_utils import *
from src.prob import random_variable
from src.sim import message, node


class Client(node.Node):
    def __init__(
        self,
        env: simpy.Environment,
        _id: str,
        inter_msg_gen_time_rv: random_variable.RandomVariable,
        num_msgs_to_send: int = None,
    ):
        super().__init__(env=env, _id=_id)
        self.num_msgs_to_send = num_msgs_to_send
        self.inter_msg_gen_time_rv = inter_msg_gen_time_rv

        # To be set while getting connected to the network
        self.next_hop = None
        self.dst_id = None

        self.adversary: adversary_module.Adversary = None

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
            slog(
                DEBUG, self.env, self, "waiting", inter_msg_gen_time=inter_msg_gen_time
            )
            yield self.env.timeout(inter_msg_gen_time)

            msg = message.Message(_id=msg_id, src_id=self._id, dst_id=self.dst_id)
            slog(DEBUG, self.env, self, "sending", msg=msg)
            self.next_hop.put(msg)
            if self.adversary:
                self.adversary.client_sent_msg(client_id=self._id)

            msg_id += 1
            if self.num_msgs_to_send and msg_id >= self.num_msgs_to_send:
                break
