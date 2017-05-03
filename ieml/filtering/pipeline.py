import logging

#
from ieml.calculation.distance import set_proximity_index
from ieml.filtering.filters import FilteringLevel, ParadigmaticProximityFilter, IndicatorFilter, BinaryFilter
from ieml.ieml_objects.hypertexts import Hypertext
from ieml.ieml_objects.sentences import SuperSentence, Sentence
from ieml.ieml_objects.terms import Term
from ieml.ieml_objects.texts import Text
from ieml.ieml_objects.words import Word

TOP_USL_TYPES = [SuperSentence, Hypertext, Text]


class USLSet:
    """A Wrapper object for a USL list"""

    def __init__(self, usl_list):
        self.usl_table = {}
        # splitting the USL list by type
        self._sort_usl_from_list(usl_list)

    def __len__(self):
        return sum([len(usl_level_list) for usl_level_list in self.usl_table.values()])

    @property
    def is_empty(self):
        """Returns true if there's at least one USL in the set"""
        for usl_list in self.usl_table.values():
            if usl_list:
                return False

        return True


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

        usls = []
        for usl_type in table_keys:
            if usl_type in self.usl_table:
                usls += self.usl_table[usl_type]

        return usls

    def set_usls(self, usl_list, usl_types=None):
        if usl_types is None:
            self.usl_table = {}
        else:
            for usl_t in usl_types:
                if usl_t in self.usl_table:
                    del self.usl_table[usl_t]
        self._sort_usl_from_list(usl_list)


class AbtractPipeline:

    def _filter(self, usl_set, query, final_pool_size, ratios_list=None):
        """Actual child class-dependent filtering function. Does the hard work"""
        pass

    def filter(self, usl_set, query, final_pool_size, ratios_list=None):
        """Does pre-checks on the pipeline's entry"""
        if usl_set.is_empty:
            logging.info("Empty USL set, aborting filtering")
            return usl_set
        else:
            return self._filter(usl_set, query, final_pool_size, ratios_list)

    def _check_ratios_list(self, filters_list, ratios_list):
        if len(ratios_list) == len(filters_list):
            self.chained_filters, self.filters_ratios = filters_list, ratios_list
            self.couples = list(zip(filters_list, ratios_list))
        else:
            raise Exception("Ratios count %i doesn't match the filter count %i" %
                            (len(ratios_list), len(filters_list)))

        if sum(ratios_list) != 1:
            raise Exception("Ratio sum doesn't sum to 1")

    @staticmethod
    def gen_pipeline_from_query(query_usl):
        return filtering_pipelines_mappings[FilteringLevel.get_usl_filtering_level(query_usl)]


class LinearPipeline(AbtractPipeline):
    """Pipeline for a simple linear F1 -> F2 -> ... schema for the filtering order.
    The Pipeline uses the defined ratios to reach the desired end ratio"""

    def __init__(self, filters_lists):
        self.filters_list = filters_lists
        self.filters_count = len(self.filters_list)
        self.scores_list , self.scores_dict= [],{}

    def log_appearance(self, start_pool_size, end_pool_size):
        logging.debug("Linear Pipeline:")
        filters_str_reprs = "-->".join("[%s, τ %1.3f]" % (str(filter), ratio) for filter, ratio in self.couples)
        logging.debug("[%i USL]-->%s-->[%i USL]" % (start_pool_size, filters_str_reprs, end_pool_size))

    def _store_scores(self, filter, score, filtered_usls):
        """For experimental uses: stores the scores of each USLs after filtering"""
        filtered_scores = { usl : score[usl] for usl in filtered_usls}
        self.scores_dict[filter] = filtered_scores
        self.scores_list.append((filter, filtered_scores))

    def _filter(self, usl_set, query_usl, final_pool_size, ratios_list=None):
        if ratios_list is not None:
            self._check_ratios_list(self.filters_list, ratios_list)
        else:
            self._check_ratios_list(self.filters_list, [1/self.filters_count] * self.filters_count)

        if not isinstance(usl_set, USLSet):
            # TODO : set the right exception for this case
            raise Exception("Expecting an USL set object, not an USL List")

        logging.debug("Starting filtering with the following pipeline: ")
        current_usl_pool = usl_set.get_usls()
        self.log_appearance(len(current_usl_pool), final_pool_size)
        master_ratio = final_pool_size / len(usl_set)

        for filter, ratio_power in self.couples:
            # if there are already not enough elements, let's not uselessly apply the filters
            if len(current_usl_pool) > final_pool_size:
                previous_count = len(current_usl_pool)
                current_usl_pool, scores = filter.filter(query_usl, current_usl_pool, pow(master_ratio, ratio_power))
                #self._store_scores(filter, scores, current_usl_pool)
                logging.debug("Removed %i elements at [%s] filter"
                              % (previous_count - len(current_usl_pool), str(filter)))
            else:
                break

        usl_set.set_usls(current_usl_pool)
        return usl_set


class ConditionalPipeline(AbtractPipeline):

    def __init__(self,filters_list, prefixed_filter):
        self.filters_list = filters_list
        self.prefixed_filter = prefixed_filter
        self.inner_pipeline = LinearPipeline(filters_list)

    @property
    def bf_lvl(self):
        return self.prefixed_filter.filtering_level

    def log_appearance(self, start_pool_size, end_pool_size):
        logging.debug("Conditional Pipeline:")
        prefilter_str_repr = "[%s]" % str(self.prefixed_filter)
        logging.debug("[%i USL]-->%s-->[UNKNOWN]-->[%i USL]" % (start_pool_size, prefilter_str_repr, end_pool_size))

    def _filter(self, usl_set, query, final_pool_size, ratios_list=None):
        self.log_appearance(len(usl_set.get_usls()), final_pool_size)

        higher_filtering_levels = FilteringLevel.get_higher_levels(self.bf_lvl)
        higher_level_usls = usl_set.get_usls(higher_filtering_levels)
        pre_filtered_usl_list = self.prefixed_filter.filter(query, higher_level_usls)
        output_list_count = len(pre_filtered_usl_list)
        logging.debug("Filtered %i of levels %s."
                      % (len(higher_level_usls) - output_list_count,
                         ", ".join([filt_lvl.name for filt_lvl in higher_filtering_levels])))
        if output_list_count == final_pool_size:
            logging.debug("Pretty lucky, ended up with the right number of USLs")
            return USLSet(pre_filtered_usl_list)

        elif output_list_count > final_pool_size:
            # linear pipeline for higher level USL
            logging.debug("Still %i too much. Picking a linear pipeline on the remaining USL equal or higher than %s"
                          % (output_list_count - final_pool_size,
                             str(self.prefixed_filter.filtering_level.name)))
            linear_pl = LinearPipeline(self.filters_list)
            return linear_pl.filter(USLSet(pre_filtered_usl_list),query, final_pool_size, ratios_list)

        else:

            if self.bf_lvl == FilteringLevel.MULTITERM_WORD:
                logging.debug("% i short of objective, picking a 2-filters linear pipeline for all remaining USLs"
                              % (final_pool_size - output_list_count))
                linear_pl = LinearPipeline(self.filters_list)
                usl_set.set_usls(pre_filtered_usl_list, higher_filtering_levels)
                return linear_pl.filter(usl_set, query, final_pool_size, ratios_list)
            else:
                # conditional pipeline on one level lower
                logging.debug("% i short of objective, picking a conditional pipeline for all remaining USLs"
                              % (final_pool_size - output_list_count))
                conditional_pl = filtering_pipelines_mappings[FilteringLevel(self.bf_lvl.value - 1)]
                usl_set.set_usls(pre_filtered_usl_list, higher_filtering_levels)
                if ratios_list is None:
                    return conditional_pl.filter(usl_set, query, final_pool_size, ratios_list)
                else:
                    # dividing the first ratio among the last ratios
                    new_ratio_list = [ ratio + (ratios_list[0] / len(ratios_list)) for ratio in ratios_list[1::]]
                    return conditional_pl.filter(usl_set, query, final_pool_size, new_ratio_list)


filtering_pipelines_mappings = {
    FilteringLevel.UNITERM_WORD: LinearPipeline([ParadigmaticProximityFilter(),
                                                 IndicatorFilter(set_proximity_index, level=Term)]),

    FilteringLevel.MULTITERM_WORD: ConditionalPipeline([IndicatorFilter(set_proximity_index, level=Term),
                                                        ParadigmaticProximityFilter()],
                                                       BinaryFilter(FilteringLevel.MULTITERM_WORD)),

    FilteringLevel.SENTENCE: ConditionalPipeline([IndicatorFilter(set_proximity_index, level=Word),
                                                  IndicatorFilter(set_proximity_index, level=Term),
                                                  ParadigmaticProximityFilter()],
                                                 BinaryFilter(FilteringLevel.SENTENCE)),

    FilteringLevel.SUPERSENTENCE: ConditionalPipeline([IndicatorFilter(set_proximity_index, level=Sentence),
                                                       IndicatorFilter(set_proximity_index, level=Word),
                                                       IndicatorFilter(set_proximity_index, level=Term),
                                                       ParadigmaticProximityFilter()],
                                                      BinaryFilter(FilteringLevel.SUPERSENTENCE))
}
