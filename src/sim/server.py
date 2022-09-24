import simpy

from src.attack import adversary as adversary_module
from src.debug_utils import *
from src.sim import message, node


class Server(node.Node):
    def __init__(
        self,
        env: simpy.Environment,
        _id: str,
        num_msgs_to_recv: int = None,
    ):
        super().__init__(env=env, _id=_id)
        self.num_msgs_to_recv = num_msgs_to_recv

        self.adversary: adversary_module.Adversary = None

        self.msg_store = simpy.Store(env)
        self.process_recv_messages = env.process(self.recv_messages())

    def __repr__(self):
        # return (
        #     "Server( \n"
        #     f"{super().__repr__()} \n"
        #     ")"
        # )

        return f"Server(id= {self._id})"

    def put(self, msg: message.Message):
        slog(DEBUG, self.env, self, "recved", msg=msg)

        if self.adversary:
            self.adversary.server_recved_msg(server_id=self._id)

        self.msg_store.put(msg)

    def recv_messages(self):
        slog(DEBUG, self.env, self, "started")

        num_msgs_recved = 0
        while True:
            msg = yield self.msg_store.get()
            num_msgs_recved += 1
            slog(
                DEBUG,
                self.env,
                self,
                "processed",
                num_msgs_recved=num_msgs_recved,
                msg=msg,
            )

            if self.num_msgs_to_recv and num_msgs_recved >= self.num_msgs_to_recv:
                break

        slog(DEBUG, self.env, self, "done")
