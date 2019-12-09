from unittest import TestCase

from ieml.ieml_database import GitInterface, IEMLDatabase
from ieml.usl.usl import usl


class IEMLDatabaseTestCase(TestCase):
    def setUp(self):
        self.gitdb = GitInterface()
        self.gitdb.pull()
        self.db = IEMLDatabase(self.gitdb.folder)

    def test_list(self):
        allieml = self.db.list()

        self.assertEqual(len(set(allieml)), len(allieml))

        # for _ in range(10):
        #     self.assertEqual(set(allieml), set(self.db.list()))

        for r in allieml:
            self.assertEqual(r, str(usl(r)), "{} not normalized".format(r))
        allieml_parser = self.db.list(parse=True)


        # for _ in range(10):
        #     self.assertEqual(set(allieml_parser), set(self.db.list(parse=True)))

        self.assertSetEqual(set(allieml), {str(e) for e in allieml_parser})
