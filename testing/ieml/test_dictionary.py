import os
from unittest.case import TestCase

from ieml.ieml_objects.dictionary import from_file


class DictionaryTest(TestCase):
    def test_load_dictionary(self):
        print(os.getcwd())
        dic = from_file("../../data/dictionary.ieml")
        print(len(dic))