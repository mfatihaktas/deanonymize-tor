import abc
import simpy


class Adversary(abc.ABC):
    def __init__(
        self,
        env: simpy.Environment,
        max_msg_delivery_time: float,
        num_target_client: int,
    ):
        self.env = env
        self.max_msg_delivery_time = max_msg_delivery_time
        self.num_target_client = num_target_client

    @abc.abstractmethod
    def client_sent_msg(self, client_id: str):
        pass

    @abc.abstractmethod
    def server_recved_msg(self, server_id: str):
        pass
