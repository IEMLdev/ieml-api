import unittest
from string import ascii_lowercase

from ieml import IEMLDatabase
from ieml.constants import LANGUAGES
from ieml.dictionary.script import script
from ieml.ieml_database.descriptor import DescriptorSet

from random import sample

def rand_entry():
    return {l: sample(ascii_lowercase, 15) for l in LANGUAGES}


def valid_desc(desc):
    assert isinstance(desc, DescriptorSet)

    assert desc.descriptors.columns == ['values']
    assert desc.descriptors.index.names == ['script', 'language', 'descriptor']

    # assert not desc.descriptors.duplicated(['script', 'language', 'descriptor']).any()


class TestDescriptor(unittest.TestCase):

    def test_build_descriptors(self):
        translations = {l: {} for l in LANGUAGES}
        comments = {l: {} for l in LANGUAGES}

        desc = DescriptorSet.build_descriptors(translations=translations, comments=comments)
        valid_desc(desc)

    def test_db_descriptor(self):
        db = IEMLDatabase()
        desc = db.descriptors()
        valid_desc(desc)

        desc.write_to_file(db.folder + '/' + desc.file[0])
        desc2 = DescriptorSet.from_file(db.folder + '/' + desc.file[0])

        valid_desc(desc2)

        assert desc.descriptors.equals(desc2.descriptors)

    def test_get_set_value(self):
        db = IEMLDatabase()
        desc = db.descriptors()
        valid_desc(desc)

        old_d = desc.descriptors.copy(deep=True)

        key = ('E:', 'fr', 'translations')
        old = desc.get(*key)

        assert isinstance(old, list) and all(isinstance(s, str) for s in old)

        new_trans = ['tout vide', 'turette']
        desc.set_value(*key, new_trans)
        valid_desc(desc)

        assert desc.get(*key) == new_trans

        desc.set_value(*key, old)
        valid_desc(desc)

        assert desc.descriptors.equals(old_d)

    def test_non_existant(self):
        db = IEMLDatabase()
        desc = db.descriptors()
        valid_desc(desc)

        key = ('O:O:O:.O:.-', 'fr', 'translations')
        assert desc.get(*key) == []

        new_trans = ['tout vide', 'turette']
        desc.set_value(*key, new_trans)
        valid_desc(desc)

        assert desc.get(*key) == ['tout vide', 'turette']


    def test_partial_get(self):
        db = IEMLDatabase()
        desc = db.descriptors()
        valid_desc(desc)

        key = ('wa.', None, 'translations')
        r = desc.get(*key)
        assert isinstance(r, dict)
        for (s, l, d), v in r.items():
            assert desc.get(s, l, d) == v


if __name__ == '__main__':
    unittest.main()
