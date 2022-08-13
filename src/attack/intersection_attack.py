import heapq
import simpy

from src.sim import (
    message,
    node as node_module,
)


class IntersectionAttack:
    def __init__(self, initial_candidate_set: set[str]):
        self.candidate_set = set(initial_candidate_set)

    def __repr__(self):
        return (
            "IntersectionAttack( \n"
            f"\t candidate_set= {self.candidate_set} \n"
            ")"
        )
.
    def get_number_of_candidates(self):
        return len(self.candidate_set)

    def update(self, candidate_set: set[str]):
        self.candidate_set = self.candidate_set.intersection(candidate_set)


class AttackWindow:
    def __init__(
        self,
        start_time: float,
        end_time: float,
    ):
        self.start_time = start_time
        self.end_time = end_time

        self.candidate_set = {}

    def add_candidate(candidate: str):
        self.candidate_set.add(candidate)

    def __lt__(self, other_attack_window: AttackWindow):
        return (
            self.end_time < other_attack_window.end_time or
            (
                self.end_time == other_attack_window.end_time and
                self.begin_time < other_attack_window.begin_time
            )
        )


class Adversary_wIntersectionAttack:
    def __init__(
        self,
        env: simpy.Environment,
        max_msg_delivery_time: float,
        num_target_client: int,
    ):
        self.env = env
        self.max_msg_delivery_time = max_msg_delivery_time
        self.num_target_client = num_target_client

        self.active_attack_window_heapq: list[AttackWindow] = []
        self.completed_attack_window_list: list[AttackWindow] = []

        self.intersection_attack = IntersectionAttack()

        self.attack_window_store = simpy.Store(env)
        self.interrupt_attack = None
        self.attack_process = env.process(self.run_attack())

    def __repr__(self):
        return f"Adversary_wIntersectionAttack(max_msg_delivery_time= {self.max_msg_delivery_time})"

    def inform_about_msg(self, node: node_module.Node):
        if isinstance(node, client_module.Client):
            self.target_client_sent_msg(client_id=node._id)
        elif isinstance(node, server_module.Server):
            self.candidate_server_recved_msg(server_id=node._id)
        else:
            raise RuntimeError(
                "Unexpected node type \n"
                f"\t node= {node}"
            )

    def target_client_sent_msg(self, client_id: str):
        slog(DEBUG, self.env, self, "recved; starting new attack window", client_id=client_id)

        attack_window = AttackWindow(
            start_time=self.env.now,
            end_time=self.env.now + self.max_msg_delivery_time
        )

        heapq.heappush(self.active_attack_window_heapq, attack_window)

        # Note: Attack windows are consumed in `attack()` through `active_attack_window_heapq`.
        # The only reason to put messages in `attack_window_store` is to use it as a trigger to wake up
        # the attack loop when there is an attack window to process.
        self.attack_window_store.put(attack_window)

        if self.interrupt_attack:
            self.interrupt_attack.succeed()

    def candidate_server_recved_msg(self, server_id: str):
        slog(DEBUG, self.env, self, "recved", server_id=server_id)

        for attack_window in self.active_attack_window_heapq:
            attack_window.add_candidate(candidate)

    def run_attack(self):
        slog(DEBUG, self.env, self, "started")

        while True:
            yield self.attack_window_store.get()

            attack_window = self.active_attack_window_heapq[0]
            wait_time = attack_window.end_time - self.env.now

            slog(DEBUG, self.env, self, "waiting for trigger", wait_time=wait_time)
            self.interrupt_attack = self.env.event()
            yield self.env.timeout(wait_time) | self.interrupt_attack
            self.interrupt_attack = None

            if self.env.now - attack_window.end_time >= 0:
                attack_window = heapq.heappop(self.active_attack_window_heapq)

                slog(DEBUG, self.env, self, "updating intersection attack", candidate_set=attack_window.candidate_set)
                self.intersection_attack.update(candidate_set=attack_window.candidate_set)

                if self.intersection_attack.get_number_of_candidates() == self.num_target_client:
                    slog(DEBUG, self.env, self, "found the targets!", num_target_client=self.num_target_client, target=self.intersection_attack.candidate_set)

            else:
                slog(DEBUG, self.env, self, "wait interrupted by new attack window")
                self.attack_window_store.put(attack_window)
