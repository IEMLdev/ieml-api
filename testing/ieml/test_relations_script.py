from ieml.script.parser import ScriptParser
from ieml.script.tools import RemarkableSibling as rq
from testing.ieml.helper import *


class TestRelationScript(unittest.TestCase):
    def setUp(self):
        self.parser = ScriptParser()

    def test_opposed_sibling_regex(self):
        script1 = self.parser.parse("S:M:.e.-M:M:.u.-wa.e.-'")
        regex = rq.opposed_sibling_regex(script1)
        self.assertIsNotNone(regex.match("M:M:.u.-S:M:.e.-wa.e.-'"))

    def test_associated_sibling_regex(self):
        script1 = self.parser.parse("S:M:.e.-M:M:.u.-wa.e.-'")
        regex = rq.associated_sibling_regex(script1)
        self.assertIsNone(regex.match("M:M:.u.-S:M:.e.-wa.h.-'"))
        self.assertIsNone(regex.match("S:M:.e.-M:M:.u.-wa.e.-'"))
        self.assertIsNotNone(regex.match("S:M:.e.-M:M:.u.-h.e.-'"))

    def test_twin_siblings(self):
        regex = rq.twin_siblings_regex(layer=3)
        self.assertIsNotNone(regex.match("M:M:.u.-M:M:.u.-wa.e.-'"))

    def test_cross_siblings(self):
        script1 = self.parser.parse("S:M:.e.-M:M:.u.-wa.e.-'")
        regex = rq.cross_sibling_regex(script1)
        self.assertIsNotNone(regex.match("e.S:M:.-u.M:M:.-wa.e.-'"))