import simpy

from src.sim import (
    message,
    node,
)

from src.debug_utils import *


class Server(node.Node):
    def __init__(self, env: simpy.Environment, _id: str):
        super().__init__(env=env, _id=_id)

        self.msg_store = simpy.Store(env)
        self.process_run = env.process(self.run())

    def __repr__(self):
        return (
            "Server( \n"
            f"{super().__repr__()} \n"
            ")"
        )

    def put(self, msg: message.Message):
        slog(DEBUG, self.env, self, "recved", msg=msg)
        self.msg_store.put(msg)

    def run(self):
        while True:
            msg = yield self.msg_store.get()
            slog(DEBUG, self.env, self, "processed", msg=msg)
