import unittest
from ieml.AST.propositions import Word, Clause, Sentence, SuperSentence, Morpheme, SuperClause
from ieml.AST.terms import Term
from ieml.AST.usl import Text, HyperText
from ieml.operator import usl, sc
from ieml.calculation.distance import (object_proximity_index,
                                       set_proximity_index, mutual_inclusion_index, connexity, build_graph,
                                       partition_graph, get_parents, get_grammar_class, get_paradigm, connexity_index)


class DistanceComputationTests(unittest.TestCase):

    def setUp(self):

        # These words are going to serve as building blocks to build objects of the layers above.
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

    def test_set_proximity_text(self):
        # TODO: DO IT
        pass

    def test_set_proximity_super_sentence(self):
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

        s_6 = Sentence([Clause(self.word_6, self.word_3, self.word_1), Clause(self.word_6, self.word_4, self.word_10),
                        Clause(self.word_4, self.word_7, self.word_9)])

        super_sentence_1 = SuperSentence([SuperClause(s_1, s_2, s_3), SuperClause(s_1, s_6, s_4)])
        super_sentence_2 = SuperSentence([SuperClause(s_4, s_2, s_5), SuperClause(s_4, s_1, s_6),
                                          SuperClause(s_4, s_3, s_5)])
        super_sentence_3 = SuperSentence([SuperClause(s_6, s_1, s_3), SuperClause(s_1, s_2, s_4),
                                          SuperClause(s_2, s_5, s_3)])
        super_sentence_4 = SuperSentence([SuperClause(s_4, s_2, s_6), SuperClause(s_4, s_1, s_6),
                                          SuperClause(s_2, s_3, s_6)])

        usl_a = HyperText(Text([super_sentence_1, super_sentence_2, super_sentence_3]))
        usl_b = HyperText(Text([super_sentence_1, super_sentence_2, super_sentence_4]))
        usl_a.check()
        usl_b.check()
        index = set_proximity_index(SuperSentence, usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        index = set_proximity_index(SuperSentence, usl_a, usl_a)
        print("Proximity Index for the identical USLs: " + str(index))
        self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

    def test_set_proximity_sentence(self):
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

        s_6 = Sentence([Clause(self.word_6, self.word_3, self.word_1), Clause(self.word_6, self.word_4, self.word_10),
                    Clause(self.word_4, self.word_7, self.word_9)])

        usl_a = HyperText(Text([s_1, s_2, s_6, s_5]))
        usl_b = HyperText(Text([s_2, s_3, s_6, s_4]))
        usl_a.check()
        usl_b.check()
        index = set_proximity_index(Sentence, usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        index = set_proximity_index(Sentence, usl_a, usl_a)
        print("Proximity Index for the identical USLs: " + str(index))
        self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

    def test_set_proximity_word(self):

        usl_a = HyperText(Text([self.word_1, self.word_3, self.word_2]))
        usl_b = HyperText(Text([self.word_2, self.word_5]))
        usl_a.check()
        usl_b.check()

        index = set_proximity_index(Word, usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        index = set_proximity_index(Word, usl_a, usl_a)
        print("Proximity Index for the identical USLs: " + str(index))
        self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

    def test_object_proximity_text(self):
        # TODO
        pass

    def test_object_proximity_super_sentence(self):
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

        s_6 = Sentence([Clause(self.word_6, self.word_3, self.word_1), Clause(self.word_6, self.word_4, self.word_10),
                        Clause(self.word_4, self.word_7, self.word_9)])

        super_sentence_1 = SuperSentence([SuperClause(s_1, s_2, s_3), SuperClause(s_1, s_6, s_4)])
        super_sentence_2 = SuperSentence([SuperClause(s_4, s_2, s_5), SuperClause(s_4, s_1, s_6),
                                          SuperClause(s_4, s_3, s_5)])
        super_sentence_3 = SuperSentence([SuperClause(s_6, s_1, s_3), SuperClause(s_1, s_2, s_4),
                                          SuperClause(s_2, s_5, s_3)])
        super_sentence_4 = SuperSentence([SuperClause(s_4, s_2, s_6), SuperClause(s_4, s_1, s_6),
                                          SuperClause(s_2, s_3, s_6)])

        usl_a = HyperText(Text([super_sentence_1, super_sentence_2, super_sentence_3]))
        usl_b = HyperText(Text([super_sentence_1, super_sentence_2, super_sentence_4]))
        usl_a.check()
        usl_b.check()
        index = object_proximity_index(SuperSentence, usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        # index = object_proximity_index(SuperSentence, usl_a, usl_a)
        # print("Proximity Index for the identical USLs: " + str(index))
        # self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

    def test_object_proximity_sentence(self):
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

        s_6 = Sentence([Clause(self.word_6, self.word_3, self.word_1), Clause(self.word_6, self.word_4, self.word_10),
                    Clause(self.word_4, self.word_7, self.word_9)])

        usl_a = HyperText(Text([s_1, s_2, s_6, s_5]))
        usl_b = HyperText(Text([s_2, s_3, s_6, s_4]))
        usl_a.check()
        usl_b.check()
        index = object_proximity_index(Sentence, usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        # index = object_proximity_index(Sentence, usl_a, usl_a)
        # print("Proximity Index for the identical USLs: " + str(index)))
        # self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

    def test_object_proximity_word(self):
        usl_a = HyperText(Text([self.word_1, self.word_3, self.word_2]))
        usl_b = HyperText(Text([self.word_2, self.word_5]))
        usl_a.check()
        usl_b.check()

        index = object_proximity_index(Word, usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        # index = object_proximity_index(Sentence, usl_a, usl_a)
        # print("Proximity Index for the identical USLs: " + str(index))
        # self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

    def test_mutual_inclusion_text(self):
        # TODO: implement
        pass

    def test_mutual_inclusion_super_sentence(self):
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

        s_6 = Sentence([Clause(self.word_6, self.word_3, self.word_1), Clause(self.word_6, self.word_4, self.word_10),
                        Clause(self.word_4, self.word_7, self.word_9)])

        super_sentence_1 = SuperSentence([SuperClause(s_1, s_2, s_3), SuperClause(s_1, s_6, s_4)])
        super_sentence_2 = SuperSentence([SuperClause(s_4, s_2, s_5), SuperClause(s_4, s_1, s_6),
                                          SuperClause(s_4, s_3, s_5)])
        super_sentence_3 = SuperSentence([SuperClause(s_6, s_1, s_3), SuperClause(s_1, s_2, s_4),
                                          SuperClause(s_2, s_5, s_3)])
        super_sentence_4 = SuperSentence([SuperClause(s_4, s_2, s_6), SuperClause(s_4, s_1, s_6),
                                          SuperClause(s_2, s_3, s_6)])

        usl_a = HyperText(Text([super_sentence_1, super_sentence_2, super_sentence_3]))
        usl_b = HyperText(Text([super_sentence_1, super_sentence_2, super_sentence_4]))
        usl_a.check()
        usl_b.check()
        index = mutual_inclusion_index(usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        index = mutual_inclusion_index(usl_a, usl_a)
        print("Proximity Index for the identical USLs: " + str(index))
        self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

    def test_mutual_inclusion_sentence(self):
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

        s_6 = Sentence([Clause(self.word_6, self.word_3, self.word_1), Clause(self.word_6, self.word_4, self.word_10),
                    Clause(self.word_4, self.word_7, self.word_9)])

        usl_a = HyperText(Text([s_1, s_2, s_6, s_5]))
        usl_b = HyperText(Text([s_2, s_3, s_6, s_4]))
        usl_a.check()
        usl_b.check()
        index = mutual_inclusion_index(usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        # index = mutual_inclusion_index(Sentence, usl_a, usl_a)
        # print("Proximity Index for the same USLs: " + str(index))
        # self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

    def test_mutual_inclusion_word(self):
        usl_a = HyperText(Text([self.word_1, self.word_3, self.word_2]))
        usl_b = HyperText(Text([self.word_2, self.word_5]))
        usl_a.check()
        usl_b.check()

        index = mutual_inclusion_index(usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        # index = mutual_inclusion_index(Sentence, usl_a, usl_a)
        # print("Proximity Index for the identical USLs: " + str(index))
        # self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

    def test_connexity_index_text(self):
        pass

    def test_connexity_index_super_sentence(self):
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

        s_6 = Sentence([Clause(self.word_6, self.word_3, self.word_1), Clause(self.word_6, self.word_4, self.word_10),
                    Clause(self.word_4, self.word_7, self.word_9)])

        super_sentence_1 = SuperSentence([SuperClause(s_1, s_2, s_3), SuperClause(s_1, s_6, s_4)])
        super_sentence_2 = SuperSentence([SuperClause(s_4, s_2, s_5), SuperClause(s_4, s_1, s_6),
                                         SuperClause(s_4, s_3, s_5)])
        super_sentence_3 = SuperSentence([SuperClause(s_6, s_1, s_3), SuperClause(s_1, s_2, s_4),
                                          SuperClause(s_2, s_5, s_3)])
        super_sentence_4 = SuperSentence([SuperClause(s_4, s_2, s_6), SuperClause(s_4, s_1, s_6),
                                          SuperClause(s_2, s_3, s_6)])

        usl_a = HyperText(Text([super_sentence_1, super_sentence_2, super_sentence_3]))
        usl_b = HyperText(Text([super_sentence_1, super_sentence_2, super_sentence_4]))
        usl_a.check()
        usl_b.check()
        index = connexity_index(SuperSentence, usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        index = connexity_index(SuperSentence, usl_a, usl_a)
        print("Proximity Index for the same USLs: " + str(index))
        self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

    def test_connexity_index_sentence(self):
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

        s_6 = Sentence([Clause(self.word_6, self.word_3, self.word_1), Clause(self.word_6, self.word_4, self.word_10),
                    Clause(self.word_4, self.word_7, self.word_9)])

        usl_a = HyperText(Text([s_1, s_2, s_6, s_5]))
        usl_b = HyperText(Text([s_2, s_3, s_6, s_4]))
        usl_a.check()
        usl_b.check()
        index = connexity_index(Sentence, usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        # index = connexity_index(Sentence, usl_a, usl_a)
        # print("Proximity Index for the same USLs: " + str(index))
        # self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

    def test_connexity_index_word(self):
        usl_a = HyperText(Text([self.word_1, self.word_3, self.word_2]))
        usl_b = HyperText(Text([self.word_2, self.word_5]))
        usl_a.check()
        usl_b.check()

        index = connexity_index(Word, usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        # index = connexity_index(Sentence, usl_a, usl_a)
        # print("Proximity Index for the same USLs: " + str(index))
        # self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

if __name__ == '__main__':
    unittest.main()