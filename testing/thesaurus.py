import unittest
import pprint
from ieml.AST.propositions import Word, Clause, Sentence, SuperSentence, Morpheme, SuperClause
from ieml.AST.terms import Term
from ieml.AST.usl import Text, HyperText
from ieml.operator import usl, sc
from ieml.calculation.thesaurus import rank_paradigms

class ThesaurusTests(unittest.TestCase):
    def test_rank_paradigms(self):

        self.word_1 = Word(Morpheme([Term(sc('wa.')), Term(sc("l.-x.-s.y.-'")), Term(sc("e.-u.-we.h.-'")),
                                     Term(sc("M:.E:A:M:.-")), Term(sc("E:A:.k.-"))]),
                           Morpheme([Term(sc('wo.')), Term(sc("T:.E:A:T:.-")),
                                     Term(sc("T:.-',S:.-',S:.-'B:.-'n.-S:.U:.-',_"))]))
        self.word_2 = Word(Morpheme([Term(sc("l.-x.-s.y.-'")), Term(sc("e.-u.-we.h.-'"))]),
                           Morpheme([Term(sc("T:.E:A:T:.-")), Term(sc("E:A:.k.-"))]))
        self.word_3 = Word(Morpheme([Term(sc("E:S:.O:B:.-")), Term(sc("E:S:.O:T:.-")), Term(sc("E:S:.U:M:.-"))]),
                           Morpheme([Term(sc("E:O:.S:M:.-"))]))
        self.word_4 = Word(Morpheme([Term(sc("S:M:.e.-t.u.-'"))]),
                           Morpheme([Term(sc("B:M:.y.-")), Term(sc("T:M:.y.-")), Term(sc("M:S:.y.-"))]))
        self.word_5 = Word(Morpheme([Term(sc("j.-'F:.-'k.o.-t.o.-',")), Term(sc("h.-'F:.-'k.o.-t.o.-',")),
                                     Term(sc("c.-'F:.-'k.o.-t.o.-',"))]),
                           Morpheme([Term(sc("E:M:.wa.-")), Term(sc("E:M:.wu.-")), Term(sc("E:M:.we.-"))]))
        self.word_6 = Word(Morpheme([Term(sc("we.y.-"))]))
        self.word_7 = Word(Morpheme([Term(sc("we.b.-")), Term(sc("p.m.-")), Term(sc("M:M:.we.-"))]),
                           Morpheme([Term(sc("a."))]))
        self.word_8 = Word(Morpheme([Term(sc("s.i.-b.i.-'"))]))
        self.word_9 = Word(Morpheme([Term(sc("we.O:B:.-")), Term(sc("we.O:T:.-")), Term(sc("wo.M:U:.-"))]))
        self.word_10 = Word(Morpheme([Term(sc("b.-S:.A:.-'B:.-'B:.-',")), Term(sc("e.-u.-we.h.-'"))]),
                            Morpheme([Term(sc("m.a.-M:M:.a.-f.o.-'")), Term(sc("n.a.-M:M:.a.-f.o.-'")),
                                      Term(sc("b.-S:.A:.-'T:.-'T:.-',"))]))

        self.word_1.check()
        self.word_2.check()
        self.word_3.check()
        self.word_4.check()
        self.word_5.check()
        self.word_6.check()
        self.word_7.check()
        self.word_8.check()
        self.word_9.check()
        self.word_10.check()

        s_1 = Sentence([Clause(self.word_1, self.word_2, self.word_5), Clause(self.word_1, self.word_4, self.word_7),
                        Clause(self.word_1, self.word_6, self.word_9), Clause(self.word_2, self.word_3, self.word_7),
                        Clause(self.word_2, self.word_8, self.word_5), Clause(self.word_6, self.word_10, self.word_5)])

        s_2 = Sentence([Clause(self.word_4, self.word_1, self.word_7), Clause(self.word_4, self.word_6, self.word_8),
                        Clause(self.word_1, self.word_3, self.word_9), Clause(self.word_1, self.word_10, self.word_2),
                        Clause(self.word_6, self.word_5, self.word_9)])

        s_3 = Sentence([Clause(self.word_9, self.word_2, self.word_1), Clause(self.word_2, self.word_6, self.word_3),
                        Clause(self.word_2, self.word_4, self.word_3), Clause(self.word_2, self.word_8, self.word_7),
                        Clause(self.word_4, self.word_10, self.word_7)])
        s_4 = Sentence([Clause(self.word_8, self.word_7, self.word_1), Clause(self.word_7, self.word_6, self.word_2),
                        Clause(self.word_6, self.word_4, self.word_3), Clause(self.word_6, self.word_5, self.word_9)])

        s_5 = Sentence([Clause(self.word_8, self.word_7, self.word_4), Clause(self.word_8, self.word_10, self.word_3)])

        # These 2 terms have the same root paradigm : E:E:F:.
        term_1 = Term(sc("E:E:F:."))
        term_2 = Term(sc("E:E:M:."))

        #
        term_3 = Term(sc("E:M:.k.-"))
        root_p3 = Term(sc("E:F:.M:M:.-"))

        # est ce qu'un paradigme est un term ?
        root_p = Term(sc("E:E:F:."))

        usl_list1 = [s_1, s_2, s_3, s_4, s_5]
        usl_list2 = [term_1, term_2]
        usl_list3 = [term_3, term_1, term_3]

        # get the list of all the root paradigms in mongodb
        # comment faire ?
        # presque cette commande : avec redondance ici : db.getCollection('relations').find({}, {'_id':0, 'ROOT':1}).sort({'ROOT':1})


        # paradigm random to create paradigms_list
        root_pr = Term(sc("E:F:.O:O:.-"))
        #paradigms_list = [root_pr, root_p3, root_p]
        paradigms_list = ["E:F:.O:O:.-", "E:F:.M:M:.-", "E:E:F:."]

        # pas sure du résultat à voir en laissant tourner
        #self.assertTrue(len(rank_paradigms(paradigms_list, usl_list1)) == 0)

        dico_2 = rank_paradigms(paradigms_list, usl_list2)
        #self.assertTrue(len(rank_paradigms(paradigms_list, usl_list2)) == 1)
        self.assertTrue(dico_2[0] == 2)
        #self.assertTrue(dico_2["E:E:F:."] == 2)

        #self.assertTrue(len(rank_paradigms(paradigms_list, usl_list3)) == 2)
        #self.assertTrue(rank_paradigms([root_p] == 1))
        #self.assertTrue(rank_paradigms([root_p3] == 2))


if __name__ == '__main__':
    unittest.main()
