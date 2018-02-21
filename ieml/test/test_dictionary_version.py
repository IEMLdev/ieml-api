import unittest

from ieml.dictionary.version import get_default_dictionary_version


class TestDictionaryVersion(unittest.TestCase):
    def test_phonetic(self):
        dv = get_default_dictionary_version()
        dv.load()
        self.assertDictEqual(dv.get_phonetic_mapping(), dv.get_phonetic_mapping())