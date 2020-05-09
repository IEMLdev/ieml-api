from typing import List

from tqdm import tqdm

from ieml.dictionary import Dictionary
from ieml.dictionary.relation import RelationsGraph
from ieml.ieml_database import IEMLDatabase
from ieml.relations.graph_backend.basic_backend import BasicGraphBackend
from ieml.relations.graph_backend.neo4j_backend import Neo4jGraphBackend
from ieml.relations.relation_type.program.axioms import ComposedAxiomProgram, ContainsAxiomProgram
from ieml.relations.relation_type.relations_registry import RelationProgramsRegistry
from ieml.usl import USL, PolyMorpheme


class RelationGraph:
    def __init__(self,
                 database: IEMLDatabase,
                 programs_registry: RelationProgramsRegistry=None,
                 backend: Neo4jGraphBackend=None):

        self.database = database

        if backend is None:
            self.backend = Neo4jGraphBackend()
        else:
            self.backend = backend

        if programs_registry is None:
            self.programs_registry = RelationProgramsRegistry()
            self.programs_registry.register(ContainsAxiomProgram())
            self.programs_registry.register(ComposedAxiomProgram())
        else:
            self.programs_registry = programs_registry


    def drop(self):
        self.backend.drop()

    def build(self):
        usls = self.database.list(parse=True, auto_promote_to_USL=True)
        dictionary = self.database.get_dictionary()
        self.programs_registry.apply(self.backend, usls, dictionary)