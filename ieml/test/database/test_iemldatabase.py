from unittest import TestCase

from ieml.ieml_database import GitInterface, IEMLDatabase


class IEMLDatabaseTestCase(TestCase):
    def setUp(self):
        self.gitdb = GitInterface()
        self.gitdb.pull()
        self.db = IEMLDatabase(self.gitdb.folder)

    def test_list(self):
        allieml = self.db.list()

        self.assertEqual(len(set(allieml)), len(allieml))

        allieml_parser = self.db.list(parse=True)
        self.assertSetEqual(set(allieml), {str(e) for e in allieml_parser})
