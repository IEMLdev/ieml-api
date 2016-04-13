from .helpers import *

class TestParser(unittest.TestCase):

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
