from itertools import chain, islice
from typing import List, Tuple, Iterable

import tqdm
from neo4j import GraphDatabase

from ieml.relations.graph_backend.basic_backend import BasicGraphBackend, RelationType
from ieml.relations.relation_type.constants import relation_types_to_id
from ieml.usl import USL, PolyMorpheme
from ieml.usl.parser import IEMLParser


constraints = ["CREATE CONSTRAINT constraint_unique_ieml ON (u:USL) ASSERT u.ieml IS UNIQUE"]
indexes = []#["CREATE INDEX index_USL FOR (u:USL) ON (u.ieml)"]

import logging
neo4j_log = logging.getLogger("neobolt")
neo4j_log.setLevel(logging.WARNING)

def neo4j_serialize_usl(u: USL, name='u'):
    assert isinstance(u, USL), u.__class__.__name__

    props = {
        'ieml': str(u),
        'cardinal': u.cardinal,
    }

    is_morpheme = isinstance(u, PolyMorpheme) and u.cardinal == 1 and len(u.constant) == 1

    return "(" + name + ":USL:" + u.__class__.__name__ + (":Morpheme" if is_morpheme else '') +\
            " { " + ", ".join('{}: "{}"'.format(key, value) for key, value in props.items()) +\
           "})"


class Neo4jGraphBackend(BasicGraphBackend, GraphDatabase):
    def __init__(self):
        self._driver = GraphDatabase.driver('bolt://localhost:7687',  auth=("neo4j", "yU4j123Db",), encrypted=False)

    def close(self):
        self._driver.close()

    def drop(self):

        with self._driver.session() as session:
            session.run("""MATCH (n)
                           DETACH DELETE n""")

            # Drop constraints / indices
            for constraint in session.run("CALL db.constraints"):
                session.run('DROP CONSTRAINT {}'.format(constraint[0]))

    @staticmethod
    def _init_indexes(tx):
        for c in constraints:
            tx.run(c)

        for i in indexes:
            tx.run(i)

    def init(self):
        self._exec_query(self._init_indexes, read=False)

    @property
    def nodes(self) -> Iterable[USL]:
        parser = IEMLParser()
        parse = lambda e: parser.parse(e.value(), auto_promote_to_USL=True)
        yield from map(parse, self._exec_query(self._list_nodes))

    @property
    def relations(self):
        yield from self._exec_query(self._list_relations)

    def add_node(self, node: USL):
        self._exec_query(self._write_nodes, [node], read=False)

    def add_nodes(self, nodes: List[USL]):
        NODES_BATCH_SIZE = 100
        it = iter(nodes)
        for batch in tqdm.tqdm(iter(lambda: list(islice(it, NODES_BATCH_SIZE)), []),
                               total=len(nodes)//NODES_BATCH_SIZE, desc="Adding nodes"):
            self._exec_query(self._write_nodes, batch, read=False)

    def add_relation(self, substance: USL, attribute: USL, mode: RelationType):
        self._exec_query(self._write_nodes, [substance, attribute], read=False)
        self._exec_query(self._write_relations, [(substance, attribute, mode)], read=False)

    def add_relations(self, relations: List[Tuple[USL, USL, RelationType]]):
        nodes = list(set(chain.from_iterable(([r[0], r[1]] for r in relations))))
        self.add_nodes(nodes)

        RELATIONS_BATCH_SIZE = 100
        it = iter(relations)
        for batch in tqdm.tqdm(iter(lambda: list(islice(it, RELATIONS_BATCH_SIZE)), []),
                               total=len(relations)//RELATIONS_BATCH_SIZE, desc="Adding relations"):
            self._exec_query(self._write_relations, batch, read=False)


    @staticmethod
    def _list_nodes(tx):
        return tx.run("""MATCH (a:USL) RETURN a.ieml""")

    @staticmethod
    def _list_relations(tx):
        return tx.run("""MATCH (a:USL)-[r]->(b:USL) RETURN a.ieml, b.ieml, type(r)""")

    @staticmethod
    def _write_nodes(tx, nodes: List[USL]):
        nodes_str = '\n'.join("MERGE " + neo4j_serialize_usl(u, name="u"+str(i)) for i, u in enumerate(nodes))
        return tx.run(nodes_str)

    @staticmethod
    def _write_relations(tx, relations: List[Tuple[USL, USL, RelationType]]):
        res = []
        for s, a, m in relations:
            res.append(tx.run("""MATCH (a:USL),(b:USL)
                WHERE a.ieml = "{}" AND b.ieml = "{}"
                MERGE (a)-[r:{}]->(b)
                """.format(str(s), str(a), relation_types_to_id[m])))

        return res

    def _exec_query(self,  query, *args, read=True):
        with self._driver.session() as session:
            if read:
                result = session.read_transaction(query, *args)
            else:
                result = session.write_transaction(query, *args)

            return result


# if __name__ =='__main__':
#     RelationsGraph('bolt://localhost:7687', "neo4j", "yU4j123Db").print_greeting("test")