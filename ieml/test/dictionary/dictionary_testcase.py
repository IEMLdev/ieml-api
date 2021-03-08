from unittest import TestCase

from ieml.ieml_database import GitInterface, IEMLDatabase


class DictionaryTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.git = GitInterface()
        cls.git.pull()
        cls.db = IEMLDatabase(folder=cls.git.folder)
        cls.dictionary = cls.db.get_dictionary()
