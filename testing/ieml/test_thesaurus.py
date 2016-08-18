import unittest
from ieml.AST.propositions import Word, Sentence, SuperSentence, Morpheme, Clause, SuperClause
from ieml.AST.terms import Term
from ieml.operator import sc
from ieml.calculation.thesaurus import rank_paradigms, rank_usls, paradigm_usl_distribution


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

        for t in self.terms:
            t.check()

        self.term_scripts = [t.script for t in self.terms]

        self.words = [
            Word(Morpheme([self.terms[0],
                           self.terms[8],
                           self.terms[33],
                           self.terms[6],
                           self.terms[5]]),
                 Morpheme([self.terms[23],
                           self.terms[7],
                           self.terms[13]])),
            Word(Morpheme([self.terms[5],
                           self.terms[6]]),
                 Morpheme([self.terms[7],
                           self.terms[8]])),
            Word(Morpheme([self.terms[9],
                           self.terms[19],
                           self.terms[3]]),
                 Morpheme([self.terms[4]])),
            Word(Morpheme([self.terms[32]]),
                 Morpheme([self.terms[34],
                           self.terms[26],
                           self.terms[17]])),
            Word(Morpheme([self.terms[24],
                           self.terms[2],
                           self.terms[30]]),
                 Morpheme([self.terms[20],
                           self.terms[14],
                           self.terms[22]])),
            Word(Morpheme([self.terms[21]])),
            Word(Morpheme([self.terms[15],
                           self.terms[10],
                           self.terms[18]]),
                 Morpheme([self.terms[29]])),
            Word(Morpheme([self.terms[29]])),
            Word(Morpheme([self.terms[28],
                           self.terms[31],
                           self.terms[12]])),
            Word(Morpheme([self.terms[1],
                           self.terms[6]]),
                 Morpheme([self.terms[27],
                           self.terms[25],
                           self.terms[16]]))
        ]

        for w in self.words:
            w.check()

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

        for s in self.sentences:
            s.check()

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

        for ss in self.super_sentences:
            ss.check()

    def test_paradigm_ranking(self):
        # We are going to test for all terms (root paradigms, paradigms, and singular terms) at once

        pass

    def test_usl_ranking(self):
        pass

    def test_paradigm_citation_dist(self):
        pass


if __name__ == '__main__':
    unittest.main()
