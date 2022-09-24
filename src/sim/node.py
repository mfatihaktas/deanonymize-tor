import simpy

from src.debug_utils import *
from src.sim import message


class Node:
    def __init__(self, env: simpy.Environment, _id: str):
        self.env = env
        self._id = _id

    def __repr__(self):
        return "Node( \n" f"\t id= {self._id} \n" ")"
