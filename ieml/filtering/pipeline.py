from math import ceil

from ieml.AST.propositions import SuperSentence
from ieml.AST.usl import HyperText, Text

#
TOP_USL_TYPES = [SuperSentence, HyperText, Text]

class USLSet:
    """A Wrapper object for a USL list"""

    def __init__(self, usl_list):
        self.usl_table = {}
        # splitting the USL list by type
        self._sort_usl_from_list(usl_list)

    def _sort_usl_from_list(self, usl_list):
        for usl in usl_list:
            if type(usl) not in self.usl_table:
                self.usl_table[type(usl_list)] = list()
            self.usl_table[type(usl_list)].append(usl)

    def get_usls(self, usl_types=None):
        if usl_types is None:
            for key in self.usl_table:
                for usl in self.usl_table[key]:
                    yield usl
        else:
            pass

    def set_usls(self, usl_list, usl_t=None):
        if usl_t is None:
            self.usl_table = {}
        else:
            for usl_t in usl_t:
                del self.usl_table[usl_t]
        self._sort_usl_from_list(usl_list)


class FilteringPipeLine:

    def __init__(self, filters_list, ratios_list):
        # check if there is an equal number of ratios and filters
        self._check_ratios_list(filters_list, ratios_list)

    def _check_ratios_list(self, ratios_list, filters_list):
        if len(ratios_list) == len(filters_list):
            self.filters = filters_list
            self.ratios = ratios_list
            self.couples = zip(filters_list, ratios_list)
        else:
            raise Exception()

    def _apply_single_filter(self, filter, ouput_number, usl_set, query):
        #returns the filtered set
        usl_and_score = [(usl, filter.score(query, usl)) for usl in usl_set]

    def filter(self, usl_set, query, ratios_list=None):
        if ratios_list:
            self._check_ratios_list(self.filters, ratios_list)

        current_usl_pool = usl_set
        for filter, ratio in self.couples:
            outpout__count = ceil(len(current_usl_pool) * ratio)
            current_usl_pool = self._apply_single_filter(filter, outpout__count, current_usl_pool, query)


class AbtractPipeline:

    def filter(self, usl_set, query, ratios_list=None):
        pass

    def _check_ratios_list(self, ratios_list, filters_list):
        if len(ratios_list) == len(filters_list):
            self.chained_filters, self.filters_ratios = filters_list, ratios_list
            self.couples = zip(filters_list, ratios_list)
        else:
            raise Exception("Ratios count doesn't match filter count")


class SimplePipeline(AbtractPipeline):
    """Pipeline for a simple linear F1 -> F2 -> ... schema for the filtering order.
    The Pipeline uses the defined ratios to reach the desired end ratio"""

    def __init__(self, filters_lists):
        self.filters_list = filters_lists


class ComplexPipeline(AbtractPipeline):

    def __init__(self,filters_list, prefixed_filter):
        self.prefixed_filter = prefixed_filter
        self.inner_pipeline = SimplePipeline(filters_list)

    def filter(self, usl_set, query, ratios_list=None):
        pass


def gen_filtering_pipeline(query_usl, usl_list):
    pass
