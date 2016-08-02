from ieml.calculation.distance import (paradigmatic_equivalence_class_index, set_proximity_index,
                                       object_proximity_index, connexity_index, mutual_inclusion_index)
from ieml.AST.propositions import Word, Sentence, SuperSentence
from ieml.AST.terms import Term
from math import ceil


class AbstractFilter:
    def __init__(self, level=1, ratio=None):
        self.level = level
        self.ratio = ratio

    def proportional_filtering(self, query_usl, usl_list, ratio):
        """Returns a list of filtered usl, using the ratio"""
        pass


class ParadigmaticProximityFilter(AbstractFilter):
    """Filter based on the P(OE^1) indicator"""

    def proportional_filtering(self, query_usl, usl_list, ratio):
        """Overrides the AbstractFilter method to return a list ranked based on the
        P(OE^1) indicator """

        # TODO: check which paradigm table rank to use and how (i.e. should we take the mean of the indicator over all ranks)
        usl_score = {usl: paradigmatic_equivalence_class_index(query_usl, usl, 1, "OE") for usl in usl_list}
        return sorted(usl_score, key=lambda e: usl_score[e], reversed=True)[:ceil(ratio*len(usl_list))]


class IndicatorFilter(AbstractFilter):
    def __init__(self, indicator_function, **kwargs):
        super().__init__(**kwargs)
        self.indicator = indicator_function

    def proportional_filtering(self, query_usl, usl_list, ratio):
        usl_score = {usl: self.indicator(level_mapping[self.level], query_usl, usl) for usl in usl_list}
        return sorted(usl_score, key=lambda e: usl_score[e], reversed=True)[:ceil(ratio * len(usl_list))]


class BinaryFilter:

    def __init__(self, mode='word'):
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
    'word': Word,
    'sentence': Sentence,
    'super_sentence': SuperSentence
}
