
class AbstractFilter:
    def __init__(self, level=1, ratio=None):
        pass

    def score(self, query_usl, other_usl):
        """Returns a score for a given filter"""
        pass


class ParadigmaticProximityFilter(AbstractFilter):
    """Filter based on the P(OE^k) indicator"""
    pass


class ProximityFilter(AbstractFilter):
    """Filter based on the P(OE^k) indicator"""


class TwoByTwoProximityFilter(AbstractFilter):
    """Filter based on the (O^k,O^k) indicator"""


class ConnexityFilter(AbstractFilter):
    """Filter based on the O^k - O^k indicator"""

