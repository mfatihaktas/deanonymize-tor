import pytest

from src.attack import intersection_attack
from src.prob import random_variable
from src.sim import tor as tor_module

from src.debug_utils import *


@pytest.mark.parametrize(
    "num_clients,num_servers,inter_msg_gen_time_rv,network_delay_rv,num_target_client",
    [
        (
            1, # num_clients
            1, # num_servers
            random_variable.Exponential(mu=1), # inter_msg_gen_time_rv
            random_variable.DiscreteUniform(min_value=1, max_value=5), # network_delay_rv
            1, # num_target_client
        ),
    ],
)
def test_time_to_deanonymize_w_intersection_attack(
    num_clients: int,
    num_servers: int,
    inter_msg_gen_time_rv: random_variable.RandomVariable,
    network_delay_rv: random_variable.RandomVariable,
    num_target_client: int
):
    env = simpy.Environment()

    tor = tor_module.TorSystem(
        env=env,
        num_clients=num_clients,
        num_servers=num_servers,
        inter_msg_gen_time_rv=inter_msg_gen_time_rv,
        network_delay_rv=network_delay_rv,
        num_target_client=num_target_client,
    )

    adversary = intersection_attack.Adversary_wIntersectionAttack(
        env=env,
        max_msg_delivery_time=network_delay_rv.max_value,
        num_target_client=1,
    )

    tor.register_adversary(adversary=adversary)
    tor.run()
