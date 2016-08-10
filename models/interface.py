from .base_queries import DictionaryQueries, Tag
from .propositions import PropositionsQueries
from .usl import HyperTextQueries
from ieml.AST import Term, Text, HyperText, Word, Sentence, SuperSentence
from .exceptions import InvalidTags, InvalidASTType

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


class IemlDb:
    db_terms = DictionaryQueries()
    db_propositions = PropositionsQueries()
    db_hypertexts = HyperTextQueries()

    @classmethod
    def check_tag_available(cls, tags):
        return Tag.check_tags(tags) and cls.db_propositions.check_tags_available(tags) \
               and cls.db_terms.check_tags_available(tags) and cls.db_hypertexts.check_tag_available(tags)

    @classmethod
    def store_ast(cls, ast, tags):
        if not cls.check_tag_available(tags):
            # TODO not the correct exception to raise
            raise InvalidTags(tags)

        if isinstance(ast, (Word, Sentence, SuperSentence)):
            cls.db_propositions.save_closed_proposition(ast, tags)
            return

        if isinstance(ast, Text):
            cls.db_hypertexts.save_text(ast, tags)
            return

        if isinstance(ast, HyperText):
            cls.db_hypertexts.save_hypertext(ast, tags)
            return

        raise InvalidASTType()

