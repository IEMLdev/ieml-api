from ieml.calculation.distance import (paradigmatic_equivalence_class_index, set_proximity_index,
                                       object_proximity_index, connexity_index, mutual_inclusion_index)
from math import ceil


class AbstractFilter:
    def __init__(self, level=1, ratio=None):
        pass

    def proportional_filtering(self, query_usl, usl_list, ratio):
        """Returns a list of filtered usl, using the ratio"""
        pass

    def binary_filtering(self, query_usl, usl_list):
        pass


class ParadigmaticProximityFilter(AbstractFilter):
    """Filter based on the P(OE^1) indicator"""

    def proportional_filtering(self, query_usl, usl_list, ratio):
        """Overrides the AbstractFilter method to return a list ranked based on the
        P(OE^1) indicator """

        # TODO: check which paradigm rank to use and how (i.e. should we take the mean of the indicator over all ranks)
        usl_score = {usl: paradigmatic_equivalence_class_index(query_usl, usl, 1, "OE") for usl in usl_list}

        return sorted(usl_score, key=lambda e: usl_score[e], reversed=True)[:ceil(ratio*len(usl_list))]




class ProximityFilter(AbstractFilter):
    """Filter based on the OE^k indicator"""
    pass


class TwoByTwoProximityFilter(AbstractFilter):
    """Filter based on the (O^k,O^k) indicator"""


class ConnexityFilter(AbstractFilter):
    """Filter based on the O^k - O^k indicator"""

