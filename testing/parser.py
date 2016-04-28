from .helpers import *
from ieml.parsing import USLParser

class TestPropositionParser(unittest.TestCase):

    def setUp(self):
        self.morpheme_subst = Morpheme([Term("a.i.-"), Term("i.i.-")])
        self.morpheme_mode = Morpheme([Term("E:A:T:."), Term("E:S:.wa.-"), Term("E:S:.o.-")])
        self.word_object = Word(self.morpheme_subst, self.morpheme_mode)
        self.word_object.check()
        self.parser = PropositionsParser()

    def test_parse_morpheme(self):
        with open("data/example_morpheme.txt") as ieml_file:
            morpheme_ast = self.parser.parse(ieml_file.read())
        morpheme_ast.check()
        self.assertEqual(morpheme_ast, self.morpheme_mode)

    def test_parse_word(self):
        with open("data/example_word.txt") as ieml_file:
            word_ast = self.parser.parse(ieml_file.read())
        word_ast.check()
        self.assertEqual(word_ast, self.word_object)

class TestUSLParser(unittest.TestCase):

    def setUp(self):
        self.parser = USLParser()

    def test_text(self):
        """Weak test of the USL with hyperlink parsing"""
        with open("../data/example_text.txt") as ieml_file:
            usl_obj = self.parser.parse(ieml_file.read())
        self.assertEqual(len(usl_obj.texts), 1)
        self.assertEqual(len(usl_obj.childs), 1)
        self.assertEqual(len(usl_obj.texts[0].childs), 2)
        self.assertEqual(usl_obj.strate, 0)

    def test_with_hyperlink(self):
        """Weak test of the USL with hyperlink parsing"""
        with open("../data/example_usl.txt") as ieml_file:
            usl_obj = self.parser.parse(ieml_file.read())
        self.assertEqual(len(usl_obj.texts), 2)