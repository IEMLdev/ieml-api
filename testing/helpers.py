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

