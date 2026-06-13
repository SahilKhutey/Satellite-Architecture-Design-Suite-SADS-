# SADS - Thermal Network
from typing import List
from .ThermalNode import ThermalNode
from .ConductionModel import ConductiveLink

class ThermalNetwork:
    def __init__(self, nodes: List[ThermalNode], links: List[ConductiveLink] = None):
        self.nodes = nodes
        self.links = links if links else []

    def get_node(self, name: str) -> ThermalNode:
        for n in self.nodes:
            if n.name == name:
                return n
        raise ValueError(f"Node {name} not found.")
