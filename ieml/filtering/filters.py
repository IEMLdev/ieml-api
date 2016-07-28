
class AbstractFilter:
    def __init__(self, level=1, ratio=None):
        pass

    def proportional_filtering(self, query_usl, usl_list, ratio):
        """Returns a list of filtered usl, using the ratio"""
        pass

    def binary_filtering(self, query_usl, usl_list):
        pass


class ParadigmaticProximityFilter(AbstractFilter):
    """Filter based on the P(OE^k) indicator"""
    pass


class ProximityFilter(AbstractFilter):
    """Filter based on the OE^k indicator"""
    pass


class TwoByTwoProximityFilter(AbstractFilter):
    """Filter based on the (O^k,O^k) indicator"""


class ConnexityFilter(AbstractFilter):
    """Filter based on the O^k - O^k indicator"""

