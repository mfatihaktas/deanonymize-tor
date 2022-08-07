import pytest
import simpy

from src.prob import random_variable
from src.sim import (
    client as client_module,
    network as network_module,
    server as server_module,
)

from src.debug_utils import *


def test_network_w_one_client_server():
    env = simpy.Environment()

    # network = network_module.Network_wZeroDelay(
    #     env=env,
    #     _id="n",
    # )

    network = network_module.Network_wDelayAssignedPerMessage(
        env=env,
        _id="n",
        delay_rv=random_variable.DiscreteUniform(min_value=1, max_value=5),
    )

    server = server_module.Server(
        env=env,
        _id="s0",
        num_msgs_to_recv=10
    )

    network.register(node=server)

    client = client_module.Client(
        env=env,
        _id="c0",
        dst_id=server._id,
        inter_msg_gen_time_rv=random_variable.Exponential(mu=1),
        next_hop=network,
        num_msgs_to_send=10,
    )

    log(INFO, "env.run starting")
    # env.run(until=server.process_recv_messages)
    env.run(until=10)
    log(INFO, "env.run done")
