import random
from unittest.case import TestCase

from ieml.exceptions import InvalidPathException
from ieml.ieml_objects.terms import Term
from ieml.ieml_objects.texts import Text
from ieml.ieml_objects.tools import RandomPoolIEMLObjectGenerator


class TestTreeStructure(TestCase):
    def test_path(self):
        text = RandomPoolIEMLObjectGenerator(level=Text).text()
        with self.assertRaises(InvalidPathException):
            text.path([Term('wa.')])

        path = []
        c = text
        while not isinstance(c, Term):
            c = c.children[random.randint(0, len(c.children) - 1)]
            path.append(c)

        c2 = Term(c.script)

        self.assertEqual(text.path(path), c2)