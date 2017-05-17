import logging
import os
import pprint
import sys
from itertools import product
from random import randint, shuffle

import matplotlib.pyplot as plt

from ieml.AST.propositions import Word, Morpheme, Sentence, Clause, ClosedProposition
from ieml.AST.terms import Term
from ieml.operator import script
from ieml.script.script import Script
from models.terms.terms_queries import get_random_terms

os.chdir(os.path.dirname(sys.argv[0]))

from ieml.AST.tools.random_generation import RandomPropositionGenerator
from ieml.AST.usl import HyperText, Text
from ieml.filtering.pipeline import LinearPipeline, USLSet


def simple_word_from_terms(input_term):
    if isinstance(input_term, list):
        unchecked_terms_list = input_term
    else:
        unchecked_terms_list = [input_term]

    terms_list = [Term(term) if isinstance(term,(Script, str)) else term for term in unchecked_terms_list]
    new_usl = Word(Morpheme(terms_list))
    new_usl.check()
    return new_usl


def flexed_word_form_term(term_subs, term_mode):
    morph_subst = [Term(term_subs) if isinstance(term_subs,(Script, str)) else term_subs]
    morph_mode = [Term(term_mode) if isinstance(term_mode,(Script, str)) else term_mode]
    word = Word(morph_subst, morph_mode)
    word.check()
    return word


def uniterm_usl_from_term(input_term):
    new_usl = HyperText(Text([simple_word_from_terms(input_term)]))
    new_usl.check()
    return new_usl


def sentence_from_terms_triple(term_subst, term_attr, term_mode):
    sentence = Sentence([Clause(simple_word_from_terms(term_subst),
                                simple_word_from_terms(term_attr),
                                simple_word_from_terms(term_mode))])
    sentence.check()
    return sentence

def usl_from_prptns(propositions_list):
    if isinstance(propositions_list, list):
        new_usl =  HyperText(Text(propositions_list))
    elif isinstance(propositions_list, ClosedProposition):
        new_usl = HyperText(Text([propositions_list]))
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
        all_cell_uniterms = list(Word(Morpheme([Term(sing_seq)])) for paradigm in  paradigms
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
        filtered_set = pipeline.filter(USLSet(all_usls), query_usl, 20, kwargs.get("ratios"))
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
        logging.info("On average, the USL outputted by the pipeline contain %f singular terms from the query paradigm"
                     % (sum(filtered_usls_common_terms_count)/len(filtered_usls_common_terms_count)))
        logging.info("On average, the USL eliminated by the pipeline contain %f singular terms from the query paradigm"
                     % (sum(eliminated_usls_common_terms_count) / len(eliminated_usls_common_terms_count)))

        self.results["common_terms_percentage"] = sum(filtered_usls_common_terms_count)/len(filtered_usls_common_terms_count)


class LinearPipelineTermProportionExperiment(BasePLExperiment):
    """Comparing of the ratios of USL containing the query term (in onmb of occurence)
    in filtered and non-filtered terms"""

    def _get_singular_sequences(self, paradigm_term):
        return [Term(sing_seq) for sing_seq in paradigm_term.script.singular_sequences]

    def gen_set_and_query(self, **kwargs):
        # defined in the document
        query_term = Term("e.-u.-we.h.-")
        query_paradigm = Term("O:M:.-O:M:.-we.h.-")
        mmommo_paradigm = Term("M:M:.o.-M:M:.o.-")
        ommo_paradigm = Term("O:M:.M:O:.-")
        auxiliary = Term("E:T:.p.-")
        query_term.check(), query_paradigm.check(), mmommo_paradigm.check(), auxiliary.check()

        qry_prdgm_singular_seqs = self._get_singular_sequences(query_paradigm)
        mmommo_singular_seqs = self._get_singular_sequences(mmommo_paradigm)
        ommo_singular_seqs = self._get_singular_sequences(ommo_paradigm)

        single_clause_sentences, flexed_words, double_morphemes= [], [], []
        # building each sets of propositions
        for subst, attr in product(qry_prdgm_singular_seqs, mmommo_singular_seqs):
            single_clause_sentences.append(sentence_from_terms_triple(subst, attr, auxiliary))
        for subst, mode in product(ommo_singular_seqs, qry_prdgm_singular_seqs):
            flexed_words.append(flexed_word_form_term(subst,mode))
        for ommo_sing_seq in ommo_singular_seqs:
            double_morphemes.append(simple_word_from_terms([query_term, ommo_sing_seq]))

        #building the USL set
        usl_pool = []
        for d_morpheme, f_word, sngl_sentence in product(double_morphemes, flexed_words, single_clause_sentences):
            usl_pool += [usl_from_prptns(d_morpheme), usl_from_prptns(f_word), usl_from_prptns(sngl_sentence),
                         usl_from_prptns([sngl_sentence, f_word]), usl_from_prptns([d_morpheme, f_word]),
                         usl_from_prptns([d_morpheme, sngl_sentence]),
                         usl_from_prptns([d_morpheme, sngl_sentence, f_word])
                         ]

        return usl_pool, query_term


    def process_results(self, filtered_usl_pool, pipeline, **kwargs):
        pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    experiment= ParadigmaticInclusionUnitermExperiment()
    results = {}
    for i in range(10):
        ratios = (i / 10, (10-i)/10)
        results[ratios] = []
        for j in range(5):
            logging.info("Running experiment %i" % i)
            experiment.run_experiment(base_nb=20, derivative_count=15, ratios=list(ratios))
            results[ratios].append(experiment.results["common_terms_percentage"])
        results[ratios] = sum(results[ratios])/len(results[ratios])
    pprint.pprint(results)
    plt.bar(range(len(results)), list(results.values()), align='center')
    plt.xticks(range(len(results)), [str(key) for key in results], size='small')
    plt.show()
