import logging
import pprint
from random import shuffle, randint

from ieml.AST.tools import RandomPropositionGenerator
from ieml.AST.usl import Text, HyperText
from ieml.filtering import *
from ieml.filtering.filters import BinaryFilter
from testing.ieml.helper import *


class BasePipelineTester(unittest.TestCase):

    def setUp(self):
        self.generator = RandomPropositionGenerator()
        self.random_uniterm_words = [self.generator.get_random_uniterm_word() for i in range(10)]
        self.random_multiterm_words = [self.generator.get_random_multiterm_word() for i in range(10)]
        self.random_sentences = [self.generator.get_random_proposition(Sentence) for i in range(3)]


class TestUSLFilteringLevels(BasePipelineTester):
    """Testing how the FilteringLevel Object/Enum behaves, if it assigns the right level to texts"""

    def test_uniterm_level(self):
        text = Text(self.random_uniterm_words)
        self.assertEqual(FilteringLevel.get_usl_filtering_level(text), FilteringLevel.UNITERM_WORD)

    def test_multiterm_level(self):
        text = Text(self.random_multiterm_words + self.random_uniterm_words[1:3])
        self.assertEqual(FilteringLevel.get_usl_filtering_level(text), FilteringLevel.MULTITERM_WORD)

    def test_sentence_level(self):
        text = Text(self.random_sentences + self.random_multiterm_words[1:2] + self.random_uniterm_words[1:3])
        self.assertEqual(FilteringLevel.get_usl_filtering_level(text), FilteringLevel.SENTENCE)

    def test_supersentence_level(self):
        text = Text([self.generator.get_random_proposition(SuperSentence)] + self.random_sentences +
                    self.random_multiterm_words[1:2] + self.random_uniterm_words[1:3])
        self.assertEqual(FilteringLevel.get_usl_filtering_level(text), FilteringLevel.SUPERSENTENCE)

    def test_with_hypertext(self):
        hypertext  = HyperText(Text(self.random_sentences + self.random_multiterm_words[1:2] +
                                    self.random_uniterm_words[1:3]))
        self.assertEqual(FilteringLevel.get_usl_filtering_level(hypertext), FilteringLevel.SENTENCE)


class TestUSLSets(BasePipelineTester):
    """Testing that the USLSet object stores the right objects and orders them properly"""

    def setUp(self):
        super().setUp()
        all_usl_texts = []
        for proposition in self.random_uniterm_words + self.random_multiterm_words + self.random_sentences:
            text = Text([proposition])
            all_usl_texts.append(text)
            text.check()
        self.usl_set = USLSet(all_usl_texts)

    def test_usl_set_sorting(self):
        self.assertEqual(len(self.usl_set.usl_table[FilteringLevel.UNITERM_WORD]), len(self.random_uniterm_words))
        self.assertEqual(len(self.usl_set.usl_table[FilteringLevel.MULTITERM_WORD]), len(self.random_multiterm_words))
        self.assertEqual(len(self.usl_set.usl_table[FilteringLevel.SENTENCE]), len(self.random_sentences))

    def test_usl_set_retrieving(self):
        self.assertEqual(len(list(self.usl_set.get_usls())),
                         len(self.random_uniterm_words + self.random_multiterm_words + self.random_sentences))

    def test_usl_set_store_by_type(self):
        all_words_usl = list(self.usl_set.get_usls([FilteringLevel.MULTITERM_WORD, FilteringLevel.UNITERM_WORD]))
        shuffle(all_words_usl)
        all_words_usl = all_words_usl[5::]
        self.usl_set.set_usls(all_words_usl, [FilteringLevel.MULTITERM_WORD, FilteringLevel.UNITERM_WORD])
        self.assertEqual(len(self.usl_set.usl_table[FilteringLevel.MULTITERM_WORD]) +
                         len(self.usl_set.usl_table[FilteringLevel.UNITERM_WORD]),
                         len(all_words_usl))




class TestPipeLineCreation(unittest.TestCase):

    def test_linear_pipeline_gen(self):
        query = Text([RandomPropositionGenerator().get_random_uniterm_word()])
        pipeline = LinearPipeline.gen_pipeline_from_query(query)
        self.assertEqual(type(pipeline), LinearPipeline)

    def test_conditionnal_pipeline_gen(self):
        query = Text([RandomPropositionGenerator().get_random_proposition(Sentence)])
        pipeline = ConditionalPipeline.gen_pipeline_from_query(query)
        self.assertEqual(type(pipeline), ConditionalPipeline)
        self.assertEqual(len(pipeline.filters_list), 3)
        self.assertEqual(type(pipeline.prefixed_filter), BinaryFilter)

class BasePipelineTester(unittest.TestCase):
    pass

class TestLinearPipeLine(unittest.TestCase):

    def setUp(self):
        self.generator = RandomPropositionGenerator()
        logging.basicConfig(level=logging.DEBUG)

    def test_linear_pl_two_usl(self):
        """Only inputs two USL repeatedly, and uses of them as a query"""
        word_a, word_b = tuple(self.generator.get_random_uniterm_word()for i in range(2))
        usl_a_derivates = [HyperText(Text([word_a, self.generator.get_random_uniterm_word()])) for i in range(50)]
        usl_b_derivates = [HyperText(Text([word_b, self.generator.get_random_uniterm_word()])) for i in range(50)]
        all_usls = usl_a_derivates + usl_b_derivates
        shuffle(all_usls)
        for usl in all_usls:
            usl.check()
        query = HyperText(Text([word_a]))
        query.check()
        pipeline = LinearPipeline.gen_pipeline_from_query(query)
        filtered_set = pipeline.filter(USLSet(all_usls), query, 10)
        pprint.pprint([str(usl) for usl in filtered_set.get_usls()])
        print(str(word_a))

    def test_linear_pl_ten_usl(self):
        """Only inputs two USL repeatedly, and uses of them as a query"""
        words = [self.generator.get_random_uniterm_word() for i in range(10)]
        all_usls = []
        for word  in words:
            for i in range(15):
                new_usl = HyperText(Text([word] +
                                     [self.generator.get_random_uniterm_word()
                                      for i in range(randint(1,5))]))
                new_usl.check()
                all_usls.append(new_usl)
        shuffle(all_usls)
        query = HyperText(Text([words[0]]))
        query.check()
        pipeline = LinearPipeline.gen_pipeline_from_query(query)
        filtered_set = pipeline.filter(USLSet(all_usls), query, 10, [0.1, 0.9])
        pprint.pprint([str(usl) for usl in filtered_set.get_usls()])
        print(str(words[0]))
        pprint.pprint([str(usl) for usl in filtered_set.get_usls() if words[0] in usl.texts[0].children])


class TestConditionalPipeLine(unittest.TestCase):
    pass
