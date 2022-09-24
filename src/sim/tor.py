import simpy

from src.attack import (
    adversary as adversary_module,
    intersection_attack,
)
from src.prob import random_variable
from src.sim import client as client_module
from src.sim import network as network_module
from src.sim import server as server_module

from src.debug_utils import *


class TorSystem():
    def __init__(
        self,
        env: simpy.Environment,
        num_clients: int,
        num_servers: int,
        inter_msg_gen_time_rv: random_variable.RandomVariable,
        network_delay_rv: random_variable.RandomVariable,
        num_target_client: int,
    ):
        check(num_target_client <= num_clients, "num_target_client should be less than num_clients")

        self.env = env
        self.num_clients = num_clients
        self.num_servers = num_servers
        self.inter_msg_gen_time_rv = inter_msg_gen_time_rv
        self.network_delay_rv = network_delay_rv
        self.num_target_client = num_target_client

        # Network
        self.network = network_module.Network_wDelayAssignedPerMessage(
            env=self.env,
            _id="n",
            delay_rv=network_delay_rv,
        )

        # Servers
        self.server_list = []
        for i in range(num_servers):
            server = server_module.Server(
                env=self.env,
                _id=f"s{i}",
            )
            self.server_list.append(server)

            self.network.register_server(server)

        # Clients
        self.client_list = []
        for i in range(num_clients):
            client = client_module.Client(
                env=self.env,
                _id=f"c{i}",
                inter_msg_gen_time_rv=self.inter_msg_gen_time_rv,
            )
            client.next_hop = self.network
            client.dst_id = self.server_list[i % num_servers]._id
            self.client_list.append(client)

            self.network.register_client(client)

    def register_adversary(self, adversary: adversary_module.Adversary):
        self.adversary = adversary

        for client in self.network.get_client_list()[: self.num_target_client]:
            client.adversary = self.adversary

        for server in self.network.get_server_list():
            server.adversary = self.adversary

        log(
            DEBUG,
            "Registered \n"
            f" adversary= {adversary}"
        )

    def __repr__(self):
        return (
            "TorSystem( \n"
            f"\t num_clients= {self.num_clients} \n"
            f"\t num_servers= {self.num_servers} \n"
            f"\t inter_msg_gen_time_rv= {self.inter_msg_gen_time_rv} \n"
            f"\t network_delay_rv= {self.network_delay_rv} \n"
            f"\t num_target_client= {self.num_target_client} \n"
            f"\t network= {self.network} \n"
            ")"
        )

    def run(self):
        log(DEBUG, "Started")

        self.env.run(until=self.adversary.attack_process)

        log(DEBUG, "Done")
