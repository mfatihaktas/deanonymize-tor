import pytest
import simpy

from src.attack import intersection_attack
from src.prob import random_variable
from src.sim import client as client_module
from src.sim import network as network_module
from src.sim import server as server_module

from src.debug_utils import *


@pytest.fixture(scope="module")
def env() -> simpy.Environment:
    return simpy.Environment()


@pytest.fixture(scope="module", params=[1])
def num_clients(request) -> int:
    return request.param


@pytest.fixture(scope="module", params=[1])
def num_servers(request) -> int:
    return request.param


@pytest.fixture(scope="module", params=[10])
def num_msgs(request) -> int:
    return request.param


@pytest.fixture(
    scope="module",
    params=[
        random_variable.Exponential(mu=1),
    ],
)
def inter_msg_gen_time_rv(request) -> int:
    return request.param


@pytest.fixture
def client_list(
    env: simpy.Environment,
    num_msgs: int,
    inter_msg_gen_time_rv: random_variable.RandomVariable,
    num_clients: int,
) -> list[client_module.Client]:
    return [
        client_module.Client(
            env=env,
            _id=f"c{i}",
            inter_msg_gen_time_rv=inter_msg_gen_time_rv,
            num_msgs_to_send=num_msgs,
        )
        for i in range(num_clients)
    ]


@pytest.fixture
def server_list(
    env: simpy.Environment,
    num_msgs: int,
    num_servers: int,
) -> list[server_module.Server]:
    return [
        server_module.Server(
            env=env,
            _id=f"s{i}",
            num_msgs_to_recv=num_msgs,
        )
        for i in range(num_servers)
    ]


@pytest.fixture
def network_delay_rv() -> random_variable.RandomVariable:
    return random_variable.DiscreteUniform(min_value=1, max_value=5)


@pytest.fixture
def network(
    env: simpy.Environment,
    network_delay_rv: random_variable.RandomVariable,
    client_list: list[client_module.Client],
    server_list: list[server_module.Server],
) -> network_module.Network:
    # return network_module.Network_wZeroDelay(
    #     env=env,
    #     _id="n",
    # )

    network = network_module.Network_wDelayAssignedPerMessage(
        env=env,
        _id="n",
        delay_rv=network_delay_rv,
    )

    num_servers = len(server_list)
    for i, client in enumerate(client_list):
        client.next_hop = network
        client.dst_id = server_list[i % num_servers]._id

        network.register_client(client)

    for server in server_list:
        network.register_server(server)

    return network


def test_network_w_one_client_server(
    network: network_module.Network,
):
    env = network.env

    env.run(
        until=env.all_of(
            server.process_recv_messages for server in network.get_server_list()
        )
    )
    # env.run(until=100)


def test_Adversary_wIntersectionAttack_w_one_client_server(
    network: network_module.Network,
):
    env = network.env

    adversary = intersection_attack.Adversary_wIntersectionAttack(
        env=env,
        max_msg_delivery_time=network.delay_rv.max_value,
        num_target_client=1,
    )

    client = network.get_client_list()[0]
    client.adversary = adversary

    for server in network.get_server_list():
        server.adversary = adversary

    env.run(until=adversary.attack_process)
