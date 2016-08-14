import logging
import os
import pprint
import sys
from random import randint, shuffle
os.chdir(os.path.dirname(sys.argv[0]))

from ieml.AST.tools.random_generation import RandomPropositionGenerator
from ieml.AST.usl import HyperText, Text
from ieml.filtering.pipeline import LinearPipeline, USLSet


class BasePLExperiment:

    def __init__(self):
        self.generator = RandomPropositionGenerator()
        self.results = {}

    def gen_set_and_query(self):
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
            for i in range(kwargs["rnd_usls"]):
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
            for i in range(kwargs["rnd_usls"]):
                new_usl = HyperText(Text([word] +
                                         [self.generator.get_random_multiterm_word()
                                          for i in range(randint(1, 5))]))
                new_usl.check()
                all_usls.append(new_usl)
        shuffle(all_usls)
        query = HyperText(Text([words[0]]))
        query.check()
        return all_usls, query

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    experiment= ConditionalPLMultitermExperiment()
    results = []
    for i in range(1):
        logging.info("Running experiment %i" % i)
        experiment.run_experiment(base_nb=20, rnd_usls=15)
        results.append(experiment.results["query_occurences"])
    logging.info("Average of %i occurrences of query in top 10" % (sum(results)/len(results)))