import unittest
from unittest.mock import Mock

from bson import ObjectId
from ieml.AST import Term, Morpheme, Word, Clause, Sentence, SuperClause, SuperSentence
from ieml.parsing import PropositionsParser
from ieml.exceptions import IEMLTermNotFoundInDictionnary, IndistintiveTermsExist

def get_test_word_instance():
    morpheme_subst = Morpheme([Term("a.i.-"), Term("i.i.-")])
    morpheme_attr = Morpheme([Term("E:A:T:."), Term("E:S:.wa.-"),Term("E:S:.o.-")])
    return Word(morpheme_subst, morpheme_attr)

def get_test_morpheme_instance():
    return Morpheme([Term("E:A:T:."), Term("E:S:.wa.-"),Term("E:S:.o.-")])

def get_words_list():
    #this list is already sorted
    terms_list = [Term("E:A:T:."), Term("E:S:.wa.-"),Term("E:S:.o.-"), Term("u.M:M:.-"), Term("a.i.-"), Term("i.i.-")]
    return [Word(Morpheme(term)) for term in terms_list]

def get_test_sentence():
    a, b, c, d, e, f = tuple(get_words_list())
    clause_a, clause_b, clause_c, clause_d = Clause(a,b,f), Clause(a,c,f), Clause(b,d,f), Clause(b,e,f)
    sentence = Sentence([clause_b, clause_a, clause_d, clause_c])
    sentence.check()
    return sentence