import os
import shutil
import unittest

import pygit2
from ieml.constants import IEMLDB_DEFAULT_GIT_ADDRESS
from ieml.dictionary.script import script
from ieml.ieml_database import GitInterface
from ieml.ieml_database.transactions.DBTransaction import DBTransactions

REPO_TEST_PATH = 'git-test'
REPO_TEST_PATH_CACHE = 'git-test-cache'


class TestGitInterface(unittest.TestCase):
    def setUp(self):
        # repo = pygit2.init_repository(REPO_TEST_PATH)
        self.git = GitInterface(folder=REPO_TEST_PATH)


    # def tearDown(self):
    #     shutil.rmtree(REPO_TEST_PATH)

    def test_checkout_at_commit(self):
        versions = ['148505dbea8ec25fa81162c7bdeed685986094a6', 'f8f3c2882db71e8b70c6f1b73566fc53c877ea6e']

        # for version in versions:
        #     self.assertEqual(str(self.git.get_version()[1]), version)

        for version in versions:
            self.git.checkout(None, version)
            self.assertEqual(str(self.git.get_version()[1]), version)

    def test_reset(self):
        with open(os.path.join(REPO_TEST_PATH, "test"), 'w') as fp:
            fp.write("test\n")

        self.assertIn('test', self.git.repo.status())
        self.git.reset()
        self.assertDictEqual(self.git.repo.status(), {})


    def test_transaction(self):
        trans = DBTransactions(self.git, pygit2.Signature('git', 'git'), REPO_TEST_PATH_CACHE, use_cache=True)
        trans.set_descriptors(script("E:"), "tags", {'fr': "test"})

