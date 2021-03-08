import unittest

import tqdm

from ieml.ieml_database import GitInterface, IEMLDatabase
from ieml.usl import Word, PolyMorpheme, Lexeme
from ieml.usl.table import enumerate_partitions
from ieml.usl.usl import usl


class TestVariationsTestCase(unittest.TestCase):
    def test_enumerate_variations(self):
        u = usl("[! E:B:. ()(k.a.-k.a.-' l.o.-k.o.-') > E:.f.- ()(m1(p.E:A:S:.- p.E:A:B:.- p.E:A:T:.- t.i.-l.i.-' c.-'B:.-'k.o.-t.o.-',))]")

        dim, partitions = enumerate_partitions(u)
        self.assertEqual(dim, 1)

    def test_enumerate_variations_all_db(self):
        gitdb = GitInterface(origin='https://github.com/plevyieml/ieml-language.git')
        gitdb.pull()
        db = IEMLDatabase(folder=gitdb.folder)

        usls = db.list(type=Word, parse=True) + db.list(type=PolyMorpheme, parse=True) + db.list(type=Lexeme,
                                                                                                 parse=True)
        for u in tqdm.tqdm(usls):
            dim, partitions = enumerate_partitions(u)

