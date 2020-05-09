from collections import defaultdict
from typing import List

import bidict

from ieml.dictionary import Dictionary
from ieml.dictionary.script import script
from ieml.relations.graph_backend.basic_backend import BasicGraphBackend
from ieml.relations.relation_type.program.axioms import AxiomRelationProgram
from ieml.relations.relation_type.program.relation_program import RelationProgram
from ieml.relations.relation_type.relation_type import RelationType
from ieml.usl import PolyMorpheme, USL



class RelationProgramsRegistry:
    def __init__(self):
        self.name2usl = bidict.bidict()
        self.registry = {}
        self.dependencies = defaultdict(set)

        self._compute_layers = []

    def apply(self, backend: BasicGraphBackend, usls: List[USL], dictionary: Dictionary):
        for layer in self._compute_layers:
            for l in layer:
                l.build(backend, usls, dictionary)

    def register(self, program: RelationProgram):
        for reltype in program.relation_types:
            for reltype2 in self.registry:
                if reltype2.name == reltype.name:
                    raise KeyError("Duplicate relation name : {}:[{}] vs. {}:[{}]".format(reltype.name, str(reltype.usl),
                                                                                          reltype2.name, str(reltype2.usl)))
                if reltype2.usl == reltype.usl:
                    raise KeyError("Duplicate relation USL : {}:[{}] vs. {}:[{}]".format(reltype.name, str(reltype.usl),
                                                                                     reltype2.name, str(reltype2.usl)))

            self.name2usl[reltype.name] = reltype.usl
            self.registry[reltype] = program

        for dependency in program.dependencies:
            self.dependencies[self.name2usl[dependency]].add(program)

        self._build_compute_layers()

    def _build_compute_layers(self):
        # the roots are the axioms
        roots = set(reltype for reltype, program in self.registry.items() if isinstance(program, AxiomRelationProgram))

        self._compute_layers = [roots]

        computed = set(roots)
        other_nodes = set(self.registry) - roots

        while other_nodes:
            layer = set()
            for n in other_nodes:
                if self.dependencies[n].issubset(computed):
                    layer.add(n)

            if not layer:
                raise ValueError("Unable to build dependency graph, the following nodes are unreachable : " + '\n'.join("\t- {}:[{}]".format(n.name, str(n.usl)) for n in other_nodes))

            other_nodes = other_nodes - layer
            computed = computed | layer
            self._compute_layers.append(layer)