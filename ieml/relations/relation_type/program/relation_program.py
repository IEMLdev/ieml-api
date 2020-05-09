from typing import Iterable, List

from ieml import logger
from ieml.dictionary import Dictionary
from ieml.relations.graph_backend.basic_backend import BasicGraphBackend
from ieml.relations.graph_backend.neo4j_backend import Neo4jGraphBackend
from ieml.relations.relation_type.relation_type import RelationType
from ieml.usl import USL


class RelationProgram:
    def __init__(self, relation_types: Iterable[RelationType], dependencies: Iterable[str]):
        self.dependencies = set(dependencies)
        self.relation_types = set(relation_types)

    def build(self, backend: Neo4jGraphBackend, usls: List[USL], dictionary: Dictionary):
        raise NotImplementedError()


class GenerativeRelationProgram(RelationProgram):
    def __init__(self, relation_types: Iterable[RelationType], dependencies: Iterable[str], cypher_query: str):
        super().__init__(relation_types, dependencies)
        self.cypher_query = cypher_query

    def build(self, backend: Neo4jGraphBackend, usls: List[USL], dictionary: Dictionary):
        logger.info("Building relations [{}] from [{}] with {}".format(', '.join(r.name for r in self.relation_types),
                                                                       ', '.join(r for r in self.dependencies),
                                                                       self.cypher_query))
        backend._exec_query(self.cypher_query, read=False)

