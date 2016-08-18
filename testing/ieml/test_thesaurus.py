import unittest
from ieml.AST.propositions import Word, Sentence, SuperSentence, Morpheme, Clause, SuperClause
from ieml.AST.terms import Term
from ieml.operator import sc


class MyTestCase(unittest.TestCase):

    def setUp(self):

        # These words are going to serve as building blocks to build objects of the layers above.
        self.terms = [
            Term(sc("wa.")),
            Term(sc("b.-S:.A:.-'B:.-'B:.-',")),
            Term(sc("h.-'F:.-'k.o.-t.o.-',")),
            Term(sc("E:S:.U:M:.-")),
            Term(sc("E:O:.S:M:.-")),
            Term(sc("l.-x.-s.y.-'")),
            Term(sc("e.-u.-we.h.-'")),
            Term(sc("T:.E:A:T:.-")),
            Term(sc("E:A:.k.-")),
            Term(sc("E:S:.O:B:.-")),
            Term(sc("p.m.-")),
            Term(sc("s.i.-b.i.-'")),
            Term(sc("wo.M:U:.-")),
            Term(sc("T:.-',S:.-',S:.-'B:.-'n.-S:.U:.-',_")),
            Term(sc("E:M:.wu.-")),
            Term(sc("we.b.-")),
            Term(sc("b.-S:.A:.-'T:.-'T:.-',")),
            Term(sc("M:S:.y.-")),
            Term(sc("M:M:.we.-")),
            Term(sc("E:S:.O:T:.-")),
            Term(sc("E:M:.wa.-")),
            Term(sc("we.y.-")),
            Term(sc("E:M:.we.-")),
            Term(sc("wo.")),
            Term(sc("j.-'F:.-'k.o.-t.o.-',")),
            Term(sc("n.a.-M:M:.a.-f.o.-'")),
            Term(sc("T:M:.y.-")),
            Term(sc("m.a.-M:M:.a.-f.o.-'")),
            Term(sc("we.O:B:.-")),
            Term(sc("a.")),
            Term(sc("c.-'F:.-'k.o.-t.o.-',")),
            Term(sc("we.O:T:.-")),
            Term(sc("S:M:.e.-t.u.-'")),
            Term(sc("M:.E:A:M:.-")),
            Term(sc("B:M:.y.-"))
        ]

        self.words = [
            Word(Morpheme([Term(sc('wa.')),
                           Term(sc("l.-x.-s.y.-'")),
                           Term(sc("e.-u.-we.h.-'")),
                           Term(sc("M:.E:A:M:.-")),
                           Term(sc("E:A:.k.-"))]),
                 Morpheme([Term(sc('wo.')),
                           Term(sc("T:.E:A:T:.-")),
                           Term(sc("T:.-',S:.-',S:.-'B:.-'n.-S:.U:.-',_"))])),
            Word(Morpheme([Term(sc("l.-x.-s.y.-'")),
                           Term(sc("e.-u.-we.h.-'"))]),
                 Morpheme([Term(sc("T:.E:A:T:.-")),
                           Term(sc("E:A:.k.-"))])),
            Word(Morpheme([Term(sc("E:S:.O:B:.-")),
                           Term(sc("E:S:.O:T:.-")),
                           Term(sc("E:S:.U:M:.-"))]),
                 Morpheme([Term(sc("E:O:.S:M:.-"))])),
            Word(Morpheme([Term(sc("S:M:.e.-t.u.-'"))]),
                 Morpheme([Term(sc("B:M:.y.-")),
                           Term(sc("T:M:.y.-")),
                           Term(sc("M:S:.y.-"))])),
            Word(Morpheme([Term(sc("j.-'F:.-'k.o.-t.o.-',")),
                           Term(sc("h.-'F:.-'k.o.-t.o.-',")),
                           Term(sc("c.-'F:.-'k.o.-t.o.-',"))]),
                 Morpheme([Term(sc("E:M:.wa.-")),
                           Term(sc("E:M:.wu.-")),
                           Term(sc("E:M:.we.-"))])),
            Word(Morpheme([Term(sc("we.y.-"))])),
            Word(Morpheme([Term(sc("we.b.-")),
                           Term(sc("p.m.-")),
                           Term(sc("M:M:.we.-"))]),
                 Morpheme([Term(sc("a."))])),
            Word(Morpheme([Term(sc("s.i.-b.i.-'"))])),
            Word(Morpheme([Term(sc("we.O:B:.-")),
                           Term(sc("we.O:T:.-")),
                           Term(sc("wo.M:U:.-"))])),
            Word(Morpheme([Term(sc("b.-S:.A:.-'B:.-'B:.-',")),
                           Term(sc("e.-u.-we.h.-'"))]),
                 Morpheme([Term(sc("m.a.-M:M:.a.-f.o.-'")),
                           Term(sc("n.a.-M:M:.a.-f.o.-'")),
                           Term(sc("b.-S:.A:.-'T:.-'T:.-',"))]))
        ]

        self.sentences = [
            Sentence([Clause(self.words[1], self.words[2], self.words[5]),
                      Clause(self.words[1], self.words[4], self.words[7]),
                      Clause(self.words[1], self.words[6], self.words[9]),
                      Clause(self.words[2], self.words[3], self.words[7]),
                      Clause(self.words[2], self.words[8], self.words[5]),
                      Clause(self.words[6], self.words[10], self.words[5])]),
            Sentence([Clause(self.words[4], self.words[1], self.words[7]),
                      Clause(self.words[4], self.words[6], self.words[8]),
                      Clause(self.words[1], self.words[3], self.words[9]),
                      Clause(self.words[1], self.words[10], self.words[2]),
                      Clause(self.words[6], self.words[5], self.words[9])]),
            Sentence([Clause(self.words[9], self.words[2], self.words[1]),
                      Clause(self.words[2], self.words[6], self.words[3]),
                      Clause(self.words[2], self.words[4], self.words[3]),
                      Clause(self.words[2], self.words[8], self.words[7]),
                      Clause(self.words[4], self.words[10], self.words[7])]),
            Sentence([Clause(self.words[8], self.words[7], self.words[1]),
                      Clause(self.words[7], self.words[6], self.words[2]),
                      Clause(self.words[6], self.words[4], self.words[3]),
                      Clause(self.words[6], self.words[5], self.words[9])]),
            Sentence([Clause(self.words[8], self.words[7], self.words[4]),
                      Clause(self.words[8], self.words[10], self.words[3])]),
            Sentence([Clause(self.words[6], self.words[3], self.words[1]),
                      Clause(self.words[6], self.words[4], self.words[10]),
                      Clause(self.words[4], self.words[7], self.words[9])])
        ]

        self.super_sentences = [
            SuperSentence([SuperClause(self.sentences[1], self.sentences[2], self.sentences[3]),
                           SuperClause(self.sentences[1], self.sentences[6], self.sentences[4])]),
            SuperSentence([SuperClause(self.sentences[4], self.sentences[2], self.sentences[5]),
                           SuperClause(self.sentences[4], self.sentences[1], self.sentences[6]),
                           SuperClause(self.sentences[4], self.sentences[3], self.sentences[5])]),
            SuperSentence([SuperClause(self.sentences[6], self.sentences[1], self.sentences[3]),
                           SuperClause(self.sentences[1], self.sentences[2], self.sentences[4]),
                           SuperClause(self.sentences[2], self.sentences[5], self.sentences[3])]),
            SuperSentence([SuperClause(self.sentences[4], self.sentences[2], self.sentences[6]),
                           SuperClause(self.sentences[4], self.sentences[1], self.sentences[6]),
                           SuperClause(self.sentences[2], self.sentences[3], self.sentences[6])])
        ]
        
    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
