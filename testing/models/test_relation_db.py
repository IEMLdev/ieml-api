import os

from multiprocessing import Process

import time

import functools

from ieml.script.constants import OPPOSED_SIBLING_RELATION
from ieml.script.operator import script
from models.exceptions import CollectionAlreadyLocked
from models.relations.relations import RelationsConnector
from models.relations.relations_queries import RelationsQueries
from testing.models.stub_db import ModelTestCase
from testing.models.test_model import paradigms


class TestRelationCollection(ModelTestCase):
    connectors = ('terms', 'relations')

    def setUp(self):
        super().setUp()
        self._clear()
        for p in paradigms:
            self._save_paradigm(paradigms[p], recompute_relations=False)

        self.terms.recompute_relations()

    def test_no_reflexive_relations(self):
        self.assertEqual(RelationsQueries.relations('O:O:.O:O:.-', OPPOSED_SIBLING_RELATION), [])

    def test_set_lock(self):
        RelationsConnector().set_lock('testing')
        status = RelationsConnector().lock_status()
        self.assertIsNotNone(status, 'Lock not set.')

        self.assertEqual(status['pid'], os.getpid(), 'Wrong pid.')
        self.assertEqual(status['role'], 'testing', 'Wrong role.')

        RelationsConnector().free_lock()

        self.assertIsNone(RelationsConnector().lock_status(), 'Lock not removed.')

    def test_double_lock(self):
        RelationsConnector().set_lock('testing')
        try:
            RelationsConnector().set_lock('testing_again')
        except:
            self.fail()

        def lock():
            with self.assertRaises(CollectionAlreadyLocked):
                RelationsConnector().set_lock('testing_again')

            return

        p = Process(target=lock)
        p.start()
        p.join()

        # multi free
        RelationsConnector().free_lock()
        RelationsConnector().free_lock()

    def test_multi_process_lock(self):
        def lock():
            RelationsConnector().set_lock('testing')

        p = Process(target=lock)
        p.start()
        p.join()

        self.assertFalse(RelationsConnector().free_lock(), 'A process has deleted another process lock.')
        self.assertIsNotNone(RelationsConnector().lock_status())
        self.assertTrue(RelationsConnector().free_lock(force=True), 'Unable to force delete the lock.')
        self.assertIsNone(RelationsConnector().lock_status())


    def test_no_multiple_relation_computation(self):
        def mock_compute(verbose=False):
            time.sleep(1)

        RelationsQueries._compute_global_relations = mock_compute

        target = functools.partial(RelationsQueries.compute_relations, globals=True)
        p = Process(target=target)
        p.start()

        # give time to start
        time.sleep(0.5)
        with self.assertRaises(CollectionAlreadyLocked):
            target()

        p.join()

    def test_index(self):
        r0 = [t['_id'] for t in sorted(self.relations.relations.find(), key=lambda c: c['INDEX'])]
        r1 = list(map(str, sorted(map(script, r0))))

        self.assertListEqual(r0, r1)