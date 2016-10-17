from handlers.library.base import texts_db
from ieml.ieml_objects import Term, Text, Hypertext, Word, Sentence, SuperSentence
from ieml.ieml_objects.parser import IEMLParser
from ieml.exceptions import CannotParse
from ieml.object.tree_metadata import HypertextMetadata, PropositionMetadata, TextMetadata
from .base import propositions_db, hypertexts_db


def update_tag(body):
    """Updates the value of the tag attached to an IEMl object"""
    proposition_type_to_db = {"HYPERTEXT": hypertexts_db,
                              "TEXT": texts_db,
                              "PROPOSITION": propositions_db}

    db_connector = proposition_type_to_db[body["type"]]
    db_connector.update_tags(body["IEML"], body["TAGS"])


def search_library(query):
    return {}
    # language_to_tag = {
    #     '0': "EN",
    #     '1': "FR"
    # }
    #
    # level_to_type_table = {
    #     '0': Term,
    #     '1': Word,
    #     '2': Sentence,
    #     '3': SuperSentence,
    #     '4': Text,
    #     '5': Hypertext
    # }
    #
    # categories = {
    #     '0': 0,  # noun,
    #     '1': 1,  # verb,
    #     '2': 2,  # auxiliary
    # }
    #
    # term_types = {
    #     '0': 0,  # table,
    #     '1': 1,  # cell,
    #     '2': 2,  # paradigm
    # }
    #
    # language = None
    # level = None
    # category = None
    # term_type = None
    #
    # if query['language']:
    #     language = [language_to_tag[query['language']]]
    #
    # if query['level']:
    #     level = [level_to_type_table[lvl] for lvl in query['level']]
    #
    # if (Term in level or Word in level) and query['category']:
    #     category = categories[query['category']]
    #
    # if Term in level and query['term_type']:
    #     term_type = term_types[query['term_type']]
    #
    # search_string = query['search_string']
    #
    # return SearchRequest.search_string(search_string, language, level, category, term_type)


def check_library_tag_exists(tag, language):
    result = propositions_db.check_tag_exist(tag, language) or \
             hypertexts_db.check_tag_exist(tag, language)
    return {'exist': result}


def decompose_ieml_element(ieml_string):
    return {}
    # """Decomposes any IEML string input into its sub elements"""
    #
    # def _gen_proposition_json(proposition):
    #     #  if the proposition is promoted, we're getting its origin before building its JSON
    #     rendered_proposition = proposition.get_promotion_origin() if proposition.is_promotion else proposition
    #     return {"IEML": str(rendered_proposition),
    #             "TYPE": rendered_proposition.level,
    #             "TAGS": rendered_proposition.metadata["TAGS"]}
    #
    # def _children_list_json(children_list):
    #     return [_gen_proposition_json(child) for child in children_list]
    #
    # def _decompose_word(word_ast):
    #     return {"substance": _children_list_json(word_ast.root),
    #             "mode": _children_list_json(word_ast.flexing)}
    #
    # def _decompose_sentence(sentence_ast):
    #     """Decomposes and builds the ieml object for a sentence/supersentence"""
    #     return [{"substance": _gen_proposition_json(clause.substance),
    #              "attribute": _gen_proposition_json(clause.attribute),
    #              "mode": _gen_proposition_json(clause.mode)}
    #             for clause in sentence_ast.children]
    #
    # def _decompose_text(text_ast):
    #     return {'text': _children_list_json(text_ast.children)}
    #
    # def _decompose_hypertext(hypertext_ast):
    #     output_list = []
    #
    #     for hyperlink in hypertext_ast:
    #         output_list.append({
    #             "substance": str(hyperlink.start),
    #             "mode": {"literal": '', "path": str(hyperlink.path)},
    #             "attribute": str(hyperlink.end),
    #         })
    #
    #     return output_list
    #
    # # setting the DB connectors for all types of IEML objects
    # PropositionMetadata.set_connector(PropositionsQueries())
    # TextMetadata.set_connector(TextQueries())
    # HypertextMetadata.set_connector(HyperTextQueries())
    #
    # try:
    #     ieml_hypertext = USLParser().parse(ieml_string)
    #     if ieml_hypertext.strate == 0:  # it's a text
    #         return _decompose_text(ieml_hypertext.children[0])  #  decomposing the first element
    #     else:  # it's an hypertext with more than one element
    #         return _decompose_hypertext(ieml_hypertext)
    #
    # except CannotParse:
    #     ieml_proposition = IEMLParser().parse(ieml_string)
    #     if isinstance(ieml_proposition, Word):
    #         return _decompose_word(ieml_proposition)
    #     elif isinstance(ieml_proposition, (Sentence, SuperSentence)):
    #         return _decompose_sentence(ieml_proposition)
    #
