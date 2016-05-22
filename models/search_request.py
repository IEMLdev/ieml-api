from .base_queries import DictionaryQueries
from .propositions import PropositionsQueries
from .usl import HyperTextQueries
from ieml.AST import Term, Text, HyperText, Word, Sentence, SuperSentence


class SearchRequest:
    db_terms = DictionaryQueries()
    db_propositions = PropositionsQueries()
    db_hypertexts = HyperTextQueries()

    def __init__(self):
        super().__init__()

    @staticmethod
    def _format_response(response):
        return {
            "IEML": response['IEML'],
            "TAGS": response['TAGS'],
            "TYPE": response['TYPE']
        }

    @classmethod
    def search_string(cls, search_string, languages=None, levels=None, category=None, term_type=None):
        result = []
        if levels is None or Term in levels:
            result.extend([cls._format_response(e)
                           for e in cls.db_terms.search_terms(search_string, languages, category, term_type)])

        if levels is None or Word in levels or Sentence in levels or SuperSentence in levels:
            result.extend([cls._format_response(e)
                           for e in cls.db_propositions.search_propositions(search_string, languages, levels)])

        if levels is None or Text in levels or HyperText in levels:
            result.extend([cls._format_response(e)
                           for e in cls.db_hypertexts.search_request(search_string, languages, levels)])

        return result
