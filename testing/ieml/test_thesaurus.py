import unittest
from ieml.calculation.thesaurus import rank_paradigms, rank_usls, paradigm_usl_distribution
from ieml.ieml_objects.terms import Term
from ieml.ieml_objects.words import Morpheme, Word
from ieml.script.operator import sc
from ieml.usl.tools import usl
from models.terms import TermsConnector
import numpy as np


class ThesaurusTests(unittest.TestCase):

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

        # self.sentences = [
        #     Sentence([Clause(self.words[0], self.words[1], self.words[4]),
        #               Clause(self.words[0], self.words[3], self.words[6]),
        #               Clause(self.words[0], self.words[5], self.words[8]),
        #               Clause(self.words[1], self.words[2], self.words[6]),
        #               Clause(self.words[1], self.words[7], self.words[4]),
        #               Clause(self.words[5], self.words[9], self.words[4])]),
        #     Sentence([Clause(self.words[3], self.words[0], self.words[6]),
        #               Clause(self.words[3], self.words[5], self.words[7]),
        #               Clause(self.words[0], self.words[2], self.words[8]),
        #               Clause(self.words[0], self.words[9], self.words[1]),
        #               Clause(self.words[5], self.words[4], self.words[8])]),
        #     Sentence([Clause(self.words[8], self.words[1], self.words[0]),
        #               Clause(self.words[1], self.words[5], self.words[2]),
        #               Clause(self.words[1], self.words[3], self.words[2]),
        #               Clause(self.words[1], self.words[7], self.words[6]),
        #               Clause(self.words[3], self.words[9], self.words[6])]),
        #     Sentence([Clause(self.words[7], self.words[6], self.words[0]),
        #               Clause(self.words[6], self.words[5], self.words[1]),
        #               Clause(self.words[5], self.words[3], self.words[2]),
        #               Clause(self.words[5], self.words[4], self.words[8])]),
        #     Sentence([Clause(self.words[5], self.words[6], self.words[3]),
        #               Clause(self.words[7], self.words[9], self.words[2])]),
        #     Sentence([Clause(self.words[5], self.words[2], self.words[0]),
        #               Clause(self.words[5], self.words[3], self.words[9]),
        #               Clause(self.words[3], self.words[6], self.words[8])])
        # ]
        #
        # for s in self.sentences:
        #     s.check()
        #
        # self.super_sentences = [
        #     SuperSentence([SuperClause(self.sentences[0], self.sentences[1], self.sentences[2]),
        #                    SuperClause(self.sentences[0], self.sentences[5], self.sentences[3])]),
        #     SuperSentence([SuperClause(self.sentences[3], self.sentences[1], self.sentences[4]),
        #                    SuperClause(self.sentences[3], self.sentences[0], self.sentences[5]),
        #                    SuperClause(self.sentences[3], self.sentences[2], self.sentences[4])]),
        #     SuperSentence([SuperClause(self.sentences[5], self.sentences[0], self.sentences[2]),
        #                    SuperClause(self.sentences[0], self.sentences[1], self.sentences[3]),
        #                    SuperClause(self.sentences[1], self.sentences[4], self.sentences[2])]),
        #     SuperSentence([SuperClause(self.sentences[3], self.sentences[1], self.sentences[5]),
        #                    SuperClause(self.sentences[3], self.sentences[0], self.sentences[5]),
        #                    SuperClause(self.sentences[1], self.sentences[2], self.sentences[5])])
        # ]
        #
        # for ss in self.super_sentences:
        #     ss.check()

    def test_paradigm_ranking(self):
        # We are going to test for all terms (root paradigms, paradigms, and singular terms) at once

        usl_collection = [
            usl(Word(Morpheme([self.terms[1], self.terms[4]]), Morpheme([self.terms[3]]))),
            usl(Word(Morpheme([self.terms[1], self.terms[0]]), Morpheme([self.terms[3]]))),
            usl(Word(Morpheme([self.terms[3], self.terms[0]]),
                     Morpheme([self.terms[3], self.terms[1]])))
        ]

        term_order = [self.term_scripts[3], self.term_scripts[1], self.term_scripts[0], self.term_scripts[4],
                      self.term_scripts[2]]

        result = rank_paradigms(self.term_scripts[:5], usl_collection)

        res_order = [p.paradigm for p in result]

        self.assertEqual(term_order, res_order)

    def test_usl_ranking(self):
        usl_collection = [
            usl(Word(Morpheme([self.terms[1], self.terms[3], self.terms[2]]),
                     Morpheme([self.terms[1], self.terms[3]]))),
            usl(Word(Morpheme([self.terms[2], self.terms[3]]), Morpheme([self.terms[2]]))),
            usl(Word(Morpheme([self.terms[3], self.terms[1]])))
        ]

        result = rank_usls(self.term_scripts[1:4], usl_collection)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[self.term_scripts[1]], [usl_collection[0], usl_collection[2], usl_collection[1]])
        self.assertEqual(result[self.term_scripts[2]], [usl_collection[1], usl_collection[0], usl_collection[2]])
        self.assertEqual(result[self.term_scripts[3]], [usl_collection[0], usl_collection[1], usl_collection[2]])

    def test_paradigm_citation_dist(self):

        paradigm = sc("E:O:O:.")
        cells = [
            Term("E:U:U:."),
            Term("E:U:A:."),
            Term("E:A:U:."),
            Term("E:A:A:.")
        ]
        headers = [Term("E:O:U:."), Term("E:O:A:."), Term("E:U:O:."), Term("E:A:O:.")]

        usl_collection = [
            usl(Word(Morpheme([cells[0], cells[1]]), Morpheme([cells[3], cells[1], cells[2]]))),
            usl(Word(Morpheme([cells[0], cells[2]]), Morpheme([cells[3]]))),
            usl(Word(Morpheme([headers[0], cells[3]]), Morpheme([headers[3], headers[2]]))),
            usl(Word(Morpheme([cells[1]]), Morpheme([cells[1]])))
        ]

        result = paradigm_usl_distribution(paradigm, usl_collection)
        correct_result = np.zeros((2, 2), dtype=np.int32)

        correct_result[0][0] = 4
        correct_result[0][1] = 5
        correct_result[1][0] = 4
        correct_result[1][1] = 4

        self.assertEqual(len(result), 1, "The paradigm has one table so we should have one distribution table")
        self.assertTrue(np.array_equal(result[0], correct_result))




if __name__ == '__main__':
    unittest.main()
