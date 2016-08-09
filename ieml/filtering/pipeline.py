from math import ceil

from ieml.AST.propositions import SuperSentence
from ieml.AST.usl import HyperText, Text

#
from ieml.calculation.distance import set_proximity_index
from ieml.filtering.filters import FilteringLevel, ParadigmaticProximityFilter, IndicatorFilter, BinaryFilter

TOP_USL_TYPES = [SuperSentence, HyperText, Text]


class USLSet:
    """A Wrapper object for a USL list"""

    def __init__(self, usl_list):
        self.usl_table = {}
        # splitting the USL list by type
        self._sort_usl_from_list(usl_list)

    def __len__(self):
        return sum([len(usl_level_list) for usl_level_list in self.usl_table.values()])

    def _sort_usl_from_list(self, usl_list):
        """Sorting USL in a table, by USL filtering level"""
        for usl in usl_list:
            usl_type = FilteringLevel.get_usl_filtering_level(usl)
            if usl_type not in self.usl_table:
                self.usl_table[usl_type] = list()
            self.usl_table[usl_type].append(usl)

    def get_usls(self, usl_types=None):
        """Retrieve all USLs, or only USLs of a certain filtering type"""
        if usl_types is None:
            table_keys = self.usl_table.keys()
        else:
            table_keys = usl_types

        for usl_type in table_keys:
            for usl in self.usl_table[usl_type]:
                yield usl

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
            raise Exception("Ratios count doesn't match the filter count")

        if sum(self.ratios) != 1:
            raise Exception("Ratio sum doesn't sum to 1")


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

    def filter(self, usl_set, query, final_pool_size, ratios_list=None):
        pass

    def _check_ratios_list(self, ratios_list, filters_list):
        if len(ratios_list) == len(filters_list):
            self.chained_filters, self.filters_ratios = filters_list, ratios_list
            self.couples = zip(filters_list, ratios_list)
        else:
            raise Exception("Ratios count doesn't match the filter count")

        if sum(ratios_list) != 1:
            raise Exception("Ratio sum doesn't sum to 1")


class LinearPipeline(AbtractPipeline):
    """Pipeline for a simple linear F1 -> F2 -> ... schema for the filtering order.
    The Pipeline uses the defined ratios to reach the desired end ratio"""

    def __init__(self, filters_lists):
        self.filters_list = filters_lists
        self.filters_count = len(self.filters_list)

    def filter(self, usl_set, query_usl, final_pool_size, ratios_list=None):
        if ratios_list is not None:
            self._check_ratios_list(self.filters_list, ratios_list)
        else:
            self._check_ratios_list(self.filters_list, [1/self.filters_count] * self.filters_list)

        ratio = final_pool_size / len(usl_set)
        current_usl_pool = usl_set.get_usls()
        for filter, ratio_power in self.couples:
            # if there are already not enough elements, let's not uselessly apply the filters
            if len(current_usl_pool) > final_pool_size:
                current_usl_pool = filter.filter(query_usl, current_usl_pool, pow(ratio, ratio_power))
            else:
                break

        return usl_set.set_usls(current_usl_pool)


class ConditionalPipeline(AbtractPipeline):

    def __init__(self,filters_list, prefixed_filter):
        self.filters_list = filters_list
        self.prefixed_filter = prefixed_filter
        self.inner_pipeline = LinearPipeline(filters_list)

    def filter(self, usl_set, query, final_pool_size, ratios_list=None):
        higher_filtering_levels = FilteringLevel.get_higher_levels(self.prefixed_filter.filtering_level)

        higher_level_usls = usl_set.get_usls(higher_filtering_levels)
        pre_filtered_usl_list = self.prefixed_filter.filter(higher_level_usls)
        output_list_count = len(pre_filtered_usl_list)
        if output_list_count == final_pool_size:
            return USLSet(pre_filtered_usl_list)
        elif output_list_count > final_pool_size:
            # linear pipeline for higher level USL
            linear_pl = LinearPipeline(self.filters_list)
            return linear_pl.filter(USLSet(pre_filtered_usl_list),query, final_pool_size, ratios_list)
        else:
            # conditional pipeline on one level lower
            conditional_pl = filtering_pipelines_mappings[FilteringLevel(higher_filtering_levels.value - 1)]
            usl_set.set_usls(pre_filtered_usl_list, higher_filtering_levels)
            if ratios_list is None:
                return conditional_pl.filter(usl_set, query, final_pool_size, ratios_list)
            else:
                # dividing the first ratio among the last ratios
                new_ratio_list = [ ratio + (ratios_list[0] / len(ratios_list)) for ratio in ratios_list[1::]]
                return conditional_pl.filter(usl_set, query, final_pool_size, new_ratio_list)


filtering_pipelines_mappings = {
    FilteringLevel.UNITERM_WORD: LinearPipeline([ParadigmaticProximityFilter(),
                                                 IndicatorFilter(set_proximity_index, level=1)]),

    FilteringLevel.MULTITERM_WORD: ConditionalPipeline([IndicatorFilter(set_proximity_index, level=1),
                                                        ParadigmaticProximityFilter()],
                                                       BinaryFilter(FilteringLevel.MULTITERM_WORD)),

    FilteringLevel.SENTENCE: ConditionalPipeline([IndicatorFilter(set_proximity_index, level=2),
                                                  IndicatorFilter(set_proximity_index, level=1),
                                                  ParadigmaticProximityFilter()],
                                                 BinaryFilter(FilteringLevel.SENTENCE)),

    FilteringLevel.SUPERSENTENCE: ConditionalPipeline([IndicatorFilter(set_proximity_index, level=3),
                                                       IndicatorFilter(set_proximity_index, level=2),
                                                       IndicatorFilter(set_proximity_index, level=1),
                                                       ParadigmaticProximityFilter()],
                                                      BinaryFilter(FilteringLevel.SUPERSENTENCE))
}
