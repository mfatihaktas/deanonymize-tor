import numpy

from src.attack import intersection_attack
from src.prob import random_variable
from src.sim import tor as tor_module

from src.debug_utils import *
from src.plot_utils import *


def test_plot_avg_time_to_deanonymize_vs_num_servers():
    num_clients = 5 # 10
    inter_msg_gen_time_rv = random_variable.Exponential(mu=1)
    network_delay_rv = random_variable.DiscreteUniform(min_value=1, max_value=5)
    num_target_client = 1
    num_samples = 5

    log(INFO, "Started",
        num_clients=num_clients,
        inter_msg_gen_time_rv=inter_msg_gen_time_rv,
        network_delay_rv=network_delay_rv,
        num_target_client=num_target_client,
        num_samples=num_samples,
    )

    num_servers_list = []
    E_time_to_deanonymize_list = []
    for num_servers in range(1, 7):
        log(INFO, f">> num_servers= {num_servers}")

        time_to_deanonymize_list = tor_module.sim_time_to_deanonymize_w_intersection_attack(
            num_clients=num_clients,
            num_servers=num_servers,
            inter_msg_gen_time_rv=inter_msg_gen_time_rv,
            network_delay_rv=network_delay_rv,
            num_target_client=num_target_client,
            num_samples=num_samples,
        )

        E_time_to_deanonymize = numpy.mean(time_to_deanonymize_list)
        log(INFO, "",
            E_time_to_deanonymize=E_time_to_deanonymize,
        )

        num_servers_list.append(num_servers)
        E_time_to_deanonymize_list.append(E_time_to_deanonymize)

    plot.plot(num_servers_list, E_time_to_deanonymize_list, color=NICE_BLUE, marker="x")

    # TODO: Add stdev with error margin bars.

    fontsize = 14
    plot.xlabel(r"$N_s$", fontsize=fontsize)
    plot.ylabel(r"$E[T_d]$", fontsize=fontsize)
    title = \
        r"$N_c = {}$, ".format(num_clients) + \
        r"$X \sim {}$, ".format(inter_msg_gen_time_rv.to_latex()) + \
        r"$D \sim {}$, ".format(network_delay_rv.to_latex()) + \
        r"$N_t = {}$".format(num_target_client) + "\n" \
        r"$N_{\mathbf{samples}} = $" + "${}$".format(num_samples)
    plot.title(title, fontsize=fontsize) # , y=1.05
    plot.gcf().set_size_inches(6, 6)
    plot.savefig(f"plots/plot_avg_time_to_deanonymize_vs_num_servers.png", bbox_inches="tight")
    plot.gcf().clear()
    log(INFO, "Done.")
