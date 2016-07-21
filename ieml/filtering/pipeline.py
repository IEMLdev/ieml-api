from math import ceil


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
    pass


class SimplePipeline(AbtractPipeline):
    pass

class ComplexPipeline(AbtractPipeline):
    pass