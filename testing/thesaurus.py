import unittest
import pprint
from ieml.AST.propositions import Word, Clause, Sentence, SuperSentence, Morpheme, SuperClause
from ieml.AST.terms import Term
from ieml.AST.usl import Text, HyperText
from ieml.operator import usl, sc
from ieml.calculation.thesaurus import rank_paradigms, rank_usls
from models.terms import TermsConnector


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

        # The root paradigm of term_3 is E:F:.M:M:.-
        term_3 = Term(sc("E:M:.k.-"))

        usl_list1 = [term_1, term_2]
        usl_list2 = [term_3, term_1, term_3]
        usl_list3 = [term_1, term_3, term_2]
        usl_list4 = [s_1, s_2, s_3, s_4, s_5]

        tc = TermsConnector()
        full_root_paradigms = tc.root_paradigms(ieml_only = True) # list of the 53 strings of the root paradigms

        # E:F:.O:O:.- is a random paradigm to create paradigms_list
        #paradigms_list = ["E:F:.O:O:.-", "E:F:.M:M:.-", "E:E:F:."]

        (rootp_list_1, dico_1) = rank_paradigms(full_root_paradigms, usl_list1)
        self.assertTrue(len(rootp_list_1) == 1)
        self.assertTrue(rootp_list_1[0] == "E:E:F:.")
        self.assertTrue(dico_1["E:E:F:."][0] == dico_1["E:E:F:."][1] + dico_1["E:E:F:."][2] + dico_1["E:E:F:."][3])

        (rootp_list_2, dico_2) = rank_paradigms(full_root_paradigms, usl_list2)
        self.assertTrue(len(rootp_list_2) == 2)
        self.assertTrue(rootp_list_2[0] == "E:F:.M:M:.-")
        self.assertTrue(rootp_list_2[1] == "E:E:F:.")
        self.assertTrue(dico_2["E:E:F:."][0] == dico_2["E:E:F:."][1] + dico_2["E:E:F:."][2] + dico_2["E:E:F:."][3])
        self.assertTrue(dico_2["E:F:.M:M:.-"][0] == dico_2["E:F:.M:M:.-"][1] + dico_2["E:F:.M:M:.-"][2] + dico_2["E:F:.M:M:.-"][3])

        (rootp_list_3, dico_3) = rank_paradigms(full_root_paradigms, usl_list3)
        self.assertTrue(len(rootp_list_3) == 2)
        self.assertTrue(rootp_list_3[0] == "E:E:F:.")
        self.assertTrue(rootp_list_3[1] == "E:F:.M:M:.-")
        self.assertTrue(dico_3["E:E:F:."][0] == dico_3["E:E:F:."][1] + dico_3["E:E:F:."][2] + dico_3["E:E:F:."][3])
        self.assertTrue(dico_3["E:F:.M:M:.-"][0] == dico_3["E:F:.M:M:.-"][1] + dico_3["E:F:.M:M:.-"][2] + dico_3["E:F:.M:M:.-"][3])

        (rootp_list_4, dico_4) = rank_paradigms(full_root_paradigms, usl_list4)
        self.assertFalse(len(rootp_list_4) == 0)

    def test_rank_usls(self):
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

        # The root paradigm of term_3 is E:F:.M:M:.-
        term_3 = Term(sc("E:M:.k.-"))

        usl_list1 = [term_1, term_2]
        usl_list2 = [term_3, term_1, term_3]
        usl_list3 = [term_1, term_3, term_2]
        usl_list4 = [s_1, s_2, s_3, s_4, s_5]

        tc = TermsConnector()
        full_root_paradigms = tc.root_paradigms(ieml_only = True) # list of the 53 strings of the root paradigms

        paradigm_dico1 = rank_usls(full_root_paradigms, usl_list1)
        self.assertTrue(len(paradigm_dico1) == len(full_root_paradigms))
        self.assertTrue(len(paradigm_dico1["E:E:F:."]) == 2)
        self.assertTrue(paradigm_dico1["E:F:.M:M:.-"] == [])

if __name__ == '__main__':
    unittest.main()
