import unittest
import os
import shutil

import pygit2

from ieml.constants import DESCRIPTORS_CLASS, LANGUAGES
from ieml.ieml_database import GitInterface, IEMLDatabase


def init_repo(folders):
    if all(os.path.isdir(folder) for folder in folders):
        commit_id= '7f3a0b96aba5cf299ecc4e2985ec49f9bb7559ba'

    else:
        commit_id = None
        for folder in folders:
            if os.path.isdir(folder):
                shutil.rmtree(folder)

        folder = '/tmp/iemldb_test/tmp'
        if os.path.isdir(folder):
            shutil.rmtree(folder)

        print("Cloning IEML db : ", folder)
        gitdb = GitInterface(folder=folder)

    gitdbs = []
    for f in folders:

        if not commit_id:
            print("Copying IEML db: ", f)

            shutil.copytree(folder, f)
            git = GitInterface(folder=f)
        else:
            git = GitInterface(folder=f)
            git.reset(commit_id)

        gitdbs.append(git)

    if not commit_id:
        shutil.rmtree('/tmp/iemldb_test/tmp')
    return gitdbs

def commit(git, db, ieml, name, value):
    signature = pygit2.Signature('test', 'test@ieml.io')
    print("Committing: ", name)
    with git.commit(signature, "merge conflict test A"):
        db.remove_descriptor(ieml)

        for d in DESCRIPTORS_CLASS:
            for l in LANGUAGES:
                for e in value[d][l]:
                    db.add_descriptor(ieml, l, d, e)


class MergeConflict(unittest.TestCase):
    def test_merge_conflict(self):
        # clone two id repository
        gitA, gitB = init_repo(['/tmp/iemldb_test/A', '/tmp/iemldb_test/B'])
        # gitA = gitdbs[0]
        # gitB = gitdbs[1]

        print("Building DB...")
        dbA = IEMLDatabase(folder=gitA.folder)
        dbB = IEMLDatabase(folder=gitB.folder)

        # commit two differents values
        ieml = "(a.)"
        name = 'A'
        valueA = {
            'translations': {'fr': ['test' + name], 'en': ['test' + name]},
            'comments': {'fr': ['test' + name], 'en': ['test' + name]},
            'tags': {'fr': ['test' + name], 'en': ['test' + name]}
        }
        commit(gitA, dbA, ieml, 'A', valueA)

        name = 'B'
        valueB = {
            'translations': {'fr': ['test' + name], 'en': ['test' + name]},
            'comments': {'fr': ['test' + name], 'en': ['test' + name]},
            'tags': {'fr': ['test' + name], 'en': ['test' + name]}
        }
        commit(gitB, dbB, ieml, 'B', valueB)

        # then a same value commit
        ieml2 = '(b.)'
        commit(gitA, dbA, ieml2, 'A', valueB)
        commit(gitB, dbB, ieml2, 'B', valueB)

        # then a commit only on A
        ieml3 = '(s.)'
        commit(gitA, dbA, ieml3, 'A', valueA)


        # set B as a remote for A
        gitA.add_remote('B', os.path.join(gitB.folder, '.git'))

        print("Pulling A from B")
        conflicts = gitA.pull('B')

        print(conflicts)
        dbA = IEMLDatabase(folder=gitA.folder)

        descA = dbA.get_descriptors()
        self.assertDictEqual(descA.get_descriptor(ieml), valueB)
        self.assertDictEqual(conflicts[ieml], valueA)

    def test_add_remove(self):
        # clone two id repository
        gitA, gitB = init_repo(['/tmp/iemldb_test/A', '/tmp/iemldb_test/B'])
        # gitA = gitdbs[0]
        # gitB = gitdbs[1]

        print("Building DB...")
        dbA = IEMLDatabase(folder=gitA.folder)
        dbB = IEMLDatabase(folder=gitB.folder)

        # commit two differents values
        ieml = "(a.)"
        name = 'A'
        valueA = {
            'translations': {'fr': ['test' + name], 'en': ['test' + name]},
            'comments': {'fr': ['test' + name], 'en': ['test' + name]},
            'tags': {'fr': ['test' + name], 'en': ['test' + name]}
        }
        commit(gitA, dbA, ieml, 'A', valueA)

        commit(gitB, dbB, ieml, 'B', valueA)
        valueB = {
            'translations': {'fr': [], 'en': []},
            'comments': {'fr': [], 'en': []},
            'tags': {'fr': [], 'en': []}
        }

        # set B as a remote for A
        gitA.add_remote('B', os.path.join(gitB.folder, '.git'))
        gitB.add_remote('A', os.path.join(gitA.folder, '.git'))

        print("Pulling A from B")
        conflicts = gitA.pull('B')

        print(conflicts)
        dbA = IEMLDatabase(folder=gitA.folder)

        descA = dbA.get_descriptors()
        self.assertDictEqual(descA.get_descriptor(ieml), valueA)
        self.assertDictEqual(conflicts, {})

        # modify ieml in A, and remove it in B
        valueA = {
            'translations': {'fr': ['test2' + name], 'en': ['test' + name]},
            'comments': {'fr': ['test2' + name], 'en': ['test' + name]},
            'tags': {'fr': ['test2' + name], 'en': ['test' + name]}
        }
        commit(gitA, dbA, ieml, 'A', valueA)
        commit(gitB, dbB, ieml, 'B', valueB)

        print("Pulling A from B")
        conflicts = gitA.pull('B')

        print(conflicts)
        dbA = IEMLDatabase(folder=gitA.folder)

        descA = dbA.get_descriptors()
        self.assertDictEqual(descA.get_descriptor(ieml), valueB)
        self.assertDictEqual(conflicts[ieml], valueA)

        print("Pulling B from A")
        conflicts = gitB.pull('A')

        print(conflicts)
        dbB = IEMLDatabase(folder=gitB.folder)

        descB = dbB.get_descriptors()
        self.assertDictEqual(descB.get_descriptor(ieml), valueB)
        self.assertDictEqual(conflicts, {})


if __name__ == '__main__':
    unittest.main()
