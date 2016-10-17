from unittest.case import TestCase

from ieml.ieml_objects.terms import Term
from ieml.ieml_objects.words import Word, Morpheme
from ieml.usl import usl
from models.commons import generate_tags


class TestModelCommons(TestCase):
    def test_generate_tag(self):
        t = generate_tags(usl(Word(Morpheme([Term('U:')]), Morpheme([Term('A:')]))))
        self.assertEqual(t['FR'], 'virtuel actuel')
        self.assertEqual(t['EN'], 'virtual actual')