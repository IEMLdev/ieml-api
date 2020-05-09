from collections import defaultdict
from typing import List, Tuple, Iterable

from ieml.relations.relation_type.relation_type import RelationType
from ieml.usl import USL


class BasicGraphBackend:
    def __init__(self):
        self.nodes = set()
        self.relations = defaultdict(set)

    def add_node(self, node: USL):
        self.nodes.add(node)

    def add_nodes(self, nodes: List[USL]):
        self.nodes.union(nodes)

    def add_relations(self, relations: Iterable[Tuple[USL, USL, RelationType]]):
        for r in relations:
            self.add_relation(*r)

    def add_relation(self, substance: USL, attribute: USL, mode: RelationType):
        self.add_nodes([substance, attribute])
        self.relations[(substance, mode)].add(attribute)

