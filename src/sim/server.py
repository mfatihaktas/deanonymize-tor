import simpy

from src.sim import (
    message,
    node,
)

from src.debug_utils import *


class Server(node.Node):
    def __init__(
        self,
        env: simpy.Environment,
        _id: str,
        num_msgs_to_recv: int = None,
    ):
        super().__init__(env=env, _id=_id)
        self.num_msgs_to_recv = num_msgs_to_recv

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
        self.msg_store.put(msg)

    def recv_messages(self):
        num_msgs_recved = 0

        while True:
            msg = yield self.msg_store.get()
            num_msgs_recved += 1
            slog(DEBUG, self.env, self, "processed", num_msgs_recved=num_msgs_recved, msg=msg)

            if self.num_msgs_to_recv and num_msgs_recved >= self.num_msgs_to_recv:
                break
