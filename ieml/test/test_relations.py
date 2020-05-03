import unittest
import time

import tqdm

from ieml.ieml_database import GitInterface, IEMLDatabase
from ieml.relations.graph_backend.neo4j_backend import Neo4jGraphBackend
from ieml.relations.relation_type.constants import GENUS_PM
from ieml.relations.relations_graph import RelationGraph, Neo4jRelationsEngine
from ieml.usl.usl import usl


class TestRelations(unittest.TestCase):
    def test_all_db_relations(self):
        git = GitInterface("https://github.com/plevyieml/ieml-language.git")
        db = IEMLDatabase(git.folder)

        graph = RelationGraph()
        before = time.time()

        for u in db.list(parse=True):
            graph.addUSL(u)

        print(len(graph.backend.nodes))
        print(len(graph.backend.relations))
        print((time.time() - before) / 60)

    def test_neo4j_driver(self):
        graph = RelationGraph(backend=Neo4jGraphBackend)
        graph.backend.drop()
        res = list(graph.backend.nodes)
        self.assertEqual(len(res), 0)

        u0 = usl("B: m1(A: S:)")

        graph.backend.add_node(u0)
        res1 = list(graph.backend.nodes)
        self.assertEqual(len(res1), 1)

        u1 = usl("B: m1(A:)")
        graph.backend.add_node(u1)
        res1 = list(graph.backend.nodes)
        self.assertEqual(len(res1), 2)


        graph.backend.add_relation(u0, u1, GENUS_PM)

    def test_neo4j_driver_all_USLS(self):
        git = GitInterface("https://github.com/plevyieml/ieml-language.git")
        db = IEMLDatabase(git.folder)

        graph = RelationGraph(backend=Neo4jGraphBackend)
        graph.backend.drop()
        graph.backend.init()

        before = time.time()
        graph.addManyUSLs(db.list(parse=True, auto_promote_to_USL=True))

        print(len(list(graph.backend.nodes)))
        print(len(list(graph.backend.relations)))
        print((time.time() - before) / 60)

    def test_neo4j_relations_engine_all_USLS(self):
        git = GitInterface("https://github.com/plevyieml/ieml-language.git")
        db = IEMLDatabase(git.folder)

        graph = RelationGraph(backend=Neo4jGraphBackend)
        graph.backend.drop()
        graph.backend.init()

        before = time.time()

        engine = Neo4jRelationsEngine(graph.backend)
        engine.build(db.list(parse=True, auto_promote_to_USL=True))

        print(len(list(graph.backend.nodes)))
        print(len(list(graph.backend.relations)))
        print((time.time() - before) / 60)


    def test_neo4j_relations_engine_dictionary(self):
        git = GitInterface("https://github.com/plevyieml/ieml-language.git")
        db = IEMLDatabase(git.folder)
        dic = db.get_dictionary()

        graph = RelationGraph(backend=Neo4jGraphBackend)
        graph.backend.drop()
        graph.backend.init()

        before = time.time()

        engine = Neo4jRelationsEngine(graph.backend)
        engine.build_dictionary_relations(dic.relations)

        print(len(list(graph.backend.nodes)))
        print(len(list(graph.backend.relations)))
        print((time.time() - before) / 60)
