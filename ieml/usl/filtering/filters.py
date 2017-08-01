from enum import Enum
from ieml.calculation.distance import (paradigmatic_equivalence_class_index, set_proximity_index,
                                       object_proximity_index, connexity_index, mutual_inclusion_index)
from math import ceil

from ieml.ieml_objects.hypertexts import Hypertext
from ieml.ieml_objects.sentences import Sentence, SuperSentence
from ieml.ieml_objects.terms import Term
from ieml.ieml_objects.texts import Text
from ieml.ieml_objects.words import Word
from ieml.usl.tools import usl
from ieml.usl.usl import Usl


class FilteringLevel(Enum):
    UNITERM_WORD = 1
    MULTITERM_WORD = 2
    SENTENCE = 3
    SUPERSENTENCE = 4

    @classmethod
    def get_usl_filtering_level(cls, input_usl):
        """If the max level for a USL is a sentence or supersentence, then its filtering level is the same,
        else, this function figures out if it's a multiterm on uniterm word"""

        input_usl = usl(input_usl)

        usl_max_level = input_usl.max_level
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
    def get_proposition_filtering_level(cls, proposition):
        if isinstance(proposition, (Sentence, SuperSentence)):
            return cls.SENTENCE if isinstance(proposition, Sentence) else cls.SUPERSENTENCE
        else:
            if len(proposition.subst.children) != 1 or proposition.mode is not None:
                return cls.MULTITERM_WORD
            else:
                return cls.UNITERM_WORD

    @classmethod
    def get_higher_levels(cls, level):
        return [cls(index) for index in range(level.value, cls.SUPERSENTENCE.value + 1)]


class AbstractFilter:
    def __init__(self, level=Term, ratio=None):
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
        sorted_by_score = sorted(usl_score, key=lambda e: usl_score[e], reverse=True)
        return sorted_by_score[:ceil(ratio*len(usl_list))], usl_score

    def __str__(self):
        return "P(OE^1)"


class IndicatorFilter(AbstractFilter):
    """Filter based on any indicator, parametrized by the indicator function."""

    def __init__(self, indicator_function, **kwargs):
        super().__init__(**kwargs)
        self.indicator = indicator_function

    def filter(self, query_usl, usl_list, ratio):
        usl_score = {usl: self.indicator(self.level, query_usl, usl) for usl in usl_list}
        sorted_by_score = sorted(usl_score, key=lambda e: usl_score[e], reverse=True)
        return sorted_by_score[:ceil(ratio * len(usl_list))], usl_score

    def __str__(self):
        function_to_symbol_mapping = {
            set_proximity_index : "EO",
            object_proximity_index : "(O,O)",
            connexity_index : "(O-O)",
            mutual_inclusion_index: "(O,o)"
        }
        return function_to_symbol_mapping[self.indicator] + " lvl %s" % self.level.__name__


class BinaryFilter:

    def __init__(self, mode=FilteringLevel.MULTITERM_WORD):
        self.filtering_level = mode
        self.mode = type_mapping[mode]

    def __str__(self):
        return "BinF(%s)" %  self.mode.__name__

    def _filter_by_lvl(self, propositions_list):
        return {proposition for proposition in propositions_list
                if FilteringLevel.get_proposition_filtering_level(proposition) == self.filtering_level}

    def filter(self, query_usl, usl_list):
        """Filters out the USL who's propositions of the filter's filteringlevel do not intersect with the queries's
        proposition of the same filteringlevel"""
        query_usl_propositions = self._filter_by_lvl(query_usl.texts[0].children)
        return [usl for usl in usl_list
                if query_usl_propositions.intersection(self._filter_by_lvl(usl.texts[0].children))]

type_mapping = {
    FilteringLevel.MULTITERM_WORD: Word,
    FilteringLevel.SENTENCE: Sentence,
    FilteringLevel.SUPERSENTENCE: SuperSentence
}
