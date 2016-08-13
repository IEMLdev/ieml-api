from enum import Enum

from ieml.AST.usl import HyperText
from ieml.calculation.distance import (paradigmatic_equivalence_class_index, set_proximity_index,
                                       object_proximity_index, connexity_index, mutual_inclusion_index)
from ieml.AST.propositions import Word, Sentence, SuperSentence
from ieml.AST.terms import Term
from math import ceil


class FilteringLevel(Enum):
    UNITERM_WORD = 1
    MULTITERM_WORD = 2
    SENTENCE = 3
    SUPERSENTENCE = 4

    @classmethod
    def get_usl_filtering_level(cls, input_usl):
        """If the max level for a USL is a sentence or supersentence, then its filtering level is the same,
        else, this function figures out if it's a multiterm on uniterm word"""

        if isinstance(input_usl, HyperText):
            usl = input_usl.texts[0]
        else:
            usl = input_usl

        usl_max_level = usl.max_level
        # TODO : unittest this function
        if usl_max_level == Sentence:
            return cls.SENTENCE
        elif usl_max_level == SuperSentence:
            return cls.SUPERSENTENCE
        else: # must be a word, we have to figure out if single term or not
            # all of the USL's elements have to be words, so for each words, we check if the substance's
            # count is 1 and if the mode is empty
            for word in usl:
                if len(word.subst.children) != 1 or word.mode is not None:
                    return cls.MULTITERM_WORD
            return cls.UNITERM_WORD # reached only if all words are monoterm

    @classmethod
    def get_higher_levels(cls, level):
        return [cls(index) for index in range(level.value, cls.SUPERSENTENCE.value + 1)]



class AbstractFilter:
    def __init__(self, level=1, ratio=None):
        self.level = level
        self.ratio = ratio

    def filter(self, query_usl, usl_list, ratio):
        """Returns a list of filtered usl, using the ratio"""
        pass


class ParadigmaticProximityFilter(AbstractFilter):
    """Filter based on the P(OE^1) indicator"""

    def filter(self, query_usl, usl_list, ratio):
        """Overrides the AbstractFilter method to return a list ranked based on the
        P(OE^1) indicator """

        # TODO: check which paradigm table rank to use and how (i.e. should we take the mean of the indicator over all ranks)
        usl_score = {usl: paradigmatic_equivalence_class_index(query_usl, usl, 1, "OE") for usl in usl_list}
        sorted_by_score =  sorted(usl_score, key=lambda e: usl_score[e], reverse=True)
        return sorted_by_score[:ceil(ratio*len(usl_list))], usl_score

    def __str__(self):
        return "P(OE^1)"


class IndicatorFilter(AbstractFilter):
    """Filter based on any indicator, parametrized by the indicator function."""

    def __init__(self, indicator_function, **kwargs):
        super().__init__(**kwargs)
        self.indicator = indicator_function

    def filter(self, query_usl, usl_list, ratio):
        usl_score = {usl: self.indicator(level_mapping[self.level], query_usl, usl) for usl in usl_list}
        sorted_by_score = sorted(usl_score, key=lambda e: usl_score[e], reverse=True)
        return sorted_by_score[:ceil(ratio * len(usl_list))], usl_score

    def __str__(self):
        function_to_symbol_mappin = {
            set_proximity_index : "EO",
            object_proximity_index : "(O,O)",
            connexity_index : "(O-O)",
            mutual_inclusion_index: "(O,o)"
        }
        return function_to_symbol_mappin[self.indicator] + " lvl %i" % self.level

class BinaryFilter:

    def __init__(self, mode=FilteringLevel.MULTITERM_WORD):
        self.filtering_level = mode
        self.mode = type_mapping[mode]

    def filter(self, query_usl, usl_list):
        return [usl for usl in usl_list if any(query_obj in usl for query_obj in query_usl.tree_iter()
                                               if isinstance(query_obj, type_mapping[self.mode]))]

level_mapping = {
    1: Term,
    2: Word,
    3: Sentence,
    4: SuperSentence
}

type_mapping = {
    FilteringLevel.MULTITERM_WORD: Word,
    FilteringLevel.SENTENCE: Sentence,
    FilteringLevel.SUPERSENTENCE: SuperSentence
}
