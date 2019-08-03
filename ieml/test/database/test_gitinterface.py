import unittest

import pygit2
from ieml.constants import IEMLDB_DEFAULT_GIT_ADDRESS
from ieml.ieml_database import GitInterface



class TestGitInterface(unittest.TestCase):
    def test_checkout_at_commit(self):
        versions = ['148505dbea8ec25fa81162c7bdeed685986094a6', 'f8f3c2882db71e8b70c6f1b73566fc53c877ea6e']

        for version in versions:
            gitdb = GitInterface(origin=IEMLDB_DEFAULT_GIT_ADDRESS, commit_id=version, credentials=pygit2.Username('git'))
            self.assertEqual(str(gitdb.get_version()[1]), version)

        gitdb = GitInterface(origin=IEMLDB_DEFAULT_GIT_ADDRESS, commit_id=None, credentials=pygit2.Username('git'))

        for version in versions:
            gitdb.set_version('master', version)
            self.assertEqual(str(gitdb.get_version()[1]), version)


