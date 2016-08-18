import logging
import os
import pprint
import sys
from random import randint, shuffle

from ieml.AST.propositions import Word, Morpheme
from ieml.AST.terms import Term
from ieml.operator import script
from ieml.script.script import Script
from models.terms.terms_queries import get_random_terms

os.chdir(os.path.dirname(sys.argv[0]))

from ieml.AST.tools.random_generation import RandomPropositionGenerator
from ieml.AST.usl import HyperText, Text
from ieml.filtering.pipeline import LinearPipeline, USLSet


def uniterm_usl_from_term(input_term):
    if isinstance(input_term, (Script, str)):
        new_usl = HyperText(Text([Word(Morpheme([Term(str(input_term))]))]))
    elif isinstance(Term, input_term):
        new_usl = HyperText(Text([Word(Morpheme([input_term]))]))
    new_usl.check()
    return new_usl

class BasePLExperiment:

    def __init__(self):
        self.generator = RandomPropositionGenerator()
        self.results = {}

    def gen_set_and_query(self, **kwargs):
        pass

    def run_experiment(self, **kwargs):
        pass

    def process_results(self, filtered_usl_pool, pipeline, **kwargs):
        pass


class BasicRandomUslsExperiments(BasePLExperiment):

    def run_experiment(self, **kwargs):
        all_usls, query = self.gen_set_and_query(**kwargs)
        logging.debug("Running with query %s" % str(query))
        pipeline = LinearPipeline.gen_pipeline_from_query(query)
        filtered_set = pipeline.filter(USLSet(all_usls), query, 10, [0.1, 0.9])
        self.process_results(filtered_set.get_usls(), pipeline, query_word=query.texts[0].children[0])

    def process_results(self, filtered_usl_pool, pipeline, **kwargs):
        filtered_pool_count = len(filtered_usl_pool)
        logging.info("Filtered original USL pool down to %i USL, here are some stats:" % filtered_pool_count)
        usls_containing_query = [str(usl) for usl in filtered_usl_pool if
                                 kwargs["query_word"] in usl.texts[0].children]
        logging.info("%i/%i USL in the filtered pool contain the query word"
                     % (len(usls_containing_query), filtered_pool_count))
        logging.debug("Filtered USL pool:")
        logging.debug(pprint.pformat([str(usl) for usl in filtered_usl_pool]))
        self.results["query_occurences"] = len(usls_containing_query)

class LinearPLUnitermExperiment(BasicRandomUslsExperiments):

    def gen_set_and_query(self, **kwargs):
        words = [self.generator.get_random_uniterm_word() for i in range(kwargs["base_nb"])]
        all_usls = []
        for word in words:
            for i in range(kwargs["derivative_count"]):
                new_usl = HyperText(Text([word] +
                                         [self.generator.get_random_uniterm_word()
                                          for i in range(randint(1, 5))]))
                new_usl.check()
                all_usls.append(new_usl)
        shuffle(all_usls)
        query = HyperText(Text([words[0]]))
        query.check()
        return all_usls, query


class ConditionalPLMultitermExperiment(BasicRandomUslsExperiments):

    def gen_set_and_query(self, **kwargs):
        words = [self.generator.get_random_multiterm_word() for i in range(kwargs["base_nb"])]
        all_usls = []
        for word in words:
            for i in range(kwargs["derivative_count"]):
                new_usl = HyperText(Text([word] +
                                         [self.generator.get_random_multiterm_word()
                                          for i in range(randint(1, 5))]))
                new_usl.check()
                all_usls.append(new_usl)
        shuffle(all_usls)
        query = HyperText(Text([words[0]]))
        query.check()
        return all_usls, query


class ParadigmaticInclusionUnitermExperiment(BasePLExperiment):

    def _get_usl_terms(self, usl):
        return {word.subst.children[0].script for word in usl.texts[0]}

    def _get_common_terms_count(self, usls, query_sing_terms):
        output_counts_list = []
        for usl in usls:
            output_counts_list.append(
                len(query_sing_terms.intersection(self._get_usl_terms(usl)))
            )
        return output_counts_list

    def _get_rnd_elements(self, terms_list, count):
        return [terms_list[randint(0, len(terms_list) - 1)] for i in range(count)]

    def gen_set_and_query(self, **kwargs):
        paradigms = [script(term_str) for term_str in get_random_terms(kwargs["base_nb"])]
        all_cell_uniterms = list(Word(Morpheme([Term(str(sing_seq))])) for paradigm in  paradigms
                             for sing_seq in paradigm.singular_sequences)
        shuffle(all_cell_uniterms)
        input_usls = []
        for paradigm in paradigms:
            for i in range(kwargs["derivative_count"]):
                usl = HyperText(Text(self._get_rnd_elements(all_cell_uniterms, randint(1,3)) +
                                     [self.generator.get_random_uniterm_word()
                                      for i in range(randint(1, 3))])
                                )
                usl.check()
                input_usls.append(usl)
        return input_usls, paradigms[0]


    def run_experiment(self, **kwargs):
        all_usls, query = self.gen_set_and_query(**kwargs)
        query_usl = uniterm_usl_from_term(query)
        logging.debug("Running with query %s" % str(query))
        pipeline = LinearPipeline.gen_pipeline_from_query(query_usl)
        filtered_set = pipeline.filter(USLSet(all_usls), query_usl, 10, [0.1, 0.9])
        self.process_results(filtered_set.get_usls(), pipeline, query_paradigm=query, input_usl_pool=all_usls)

    def process_results(self, filtered_usl_pool, pipeline, **kwargs):
        # preparing all kinds of stats on the output
        qry_prdgm_sing_seqs = set(kwargs["query_paradigm"].singular_sequences)
        filtered_pool_count = len(filtered_usl_pool)
        filtered_usls_common_terms_count = self._get_common_terms_count(filtered_usl_pool, qry_prdgm_sing_seqs)
        eliminated_usls = set(kwargs["input_usl_pool"]) - set(filtered_usl_pool)
        eliminated_usls_common_terms_count = self._get_common_terms_count(eliminated_usls, qry_prdgm_sing_seqs)

        #logging it to the console
        logging.info("Filtered original USL pool down to %i USL, here are some stats:" % filtered_pool_count)
        usls_containing_query = [str(usl) for usl in filtered_usl_pool if
                                 kwargs["query_paradigm"] in usl.texts[0].children]
        logging.info("%i/%i USL in the filtered pool contain the query paradigm"
                     % (len(usls_containing_query), filtered_pool_count))
        logging.info("On average, the USL outputted by the pipeline contain %f singular terms from the query paradigm"
                     % (sum(filtered_usls_common_terms_count)/len(filtered_usls_common_terms_count)))
        logging.info("On average, the USL eliminated by the pipeline contain %f singular terms from the query paradigm"
                     % (sum(eliminated_usls_common_terms_count) / len(eliminated_usls_common_terms_count)))

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    experiment= ParadigmaticInclusionUnitermExperiment()
    results = []
    for i in range(1):
        logging.info("Running experiment %i" % i)
        experiment.run_experiment(base_nb=20, derivative_count=15)
        results.append(experiment.results["query_occurences"])
    logging.info("Average of %i occurrences of query in top 10" % (sum(results)/len(results)))