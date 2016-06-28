import logging

from handlers.library.base import propositions_db
from ieml import PropositionsParser
from ieml.AST import Word, Morpheme, promote_to
from ieml.AST.tools import SentenceGraph, SuperSentenceGraph
from .exceptions import EmptyUslChecking

def build_ieml_word_ast(data):
    """Using the data from the JSON requests, builds an AST of the IEML object being checked. Returns a
        checked and ordered IEML object"""
    parser = PropositionsParser()

    substance_list = [parser.parse(substance) for substance in data["substance"]]
    mode_list = [parser.parse(mode) for mode in data["mode"]]

    if len(mode_list) == 0:
        mode = None
    else:
        mode = Morpheme(mode_list)

    if len(substance_list) == 0:
        raise EmptyUslChecking()

    # making the two morphemes and then the word using the two term lists
    word_ast = Word(Morpheme(substance_list), mode)

    # asking the proposition to check itself
    word_ast.check()

    return word_ast


def validate_word(body):
    """Checks that a give graph representing a word is well formed, and if it is,
    returns the corresponding IEML string"""
    word_ast = build_ieml_word_ast(body)
    return {"valid": True, "ieml": str(word_ast)}


def save_word(body):
    """Checks the graph of a word is correct (alike the word graph checker), and saves it."""
    word_ast = build_ieml_word_ast(body)
    # saving after building the AST
    propositions_db.save_closed_proposition(word_ast, body["tags"])
    return {"valid": True, "ieml": str(word_ast)}


def build_ieml_sentence_ast(data):
    """Using the data from the JSON requests, builds an AST of the IEML sentence/supersentence being checked.
    Returns a checked and ordered IEML sentence/supersentence"""
    parser = PropositionsParser()
    if "validation_type" in data:
        graph_type = SentenceGraph if data["validation_type"] == 1 else SuperSentenceGraph
    else:
        logging.warning("Couldn't find validation_type field, defaulting to sentence level")
        graph_type = SentenceGraph

    nodes_table = {}
    for node in data["nodes"]:
        nodes_table[node["id"]] = parser.parse(node["ieml_string"])
        if not isinstance(nodes_table[node["id"]], graph_type.primitive_type):
            nodes_table[node["id"]] = promote_to(nodes_table[node["id"]], graph_type.primitive_type)

    # transforming the vertices into clauses or superclauses
    multiplication_elems = []
    for vertice in data["graph"]:
        new_element = graph_type.multiplicative_type(nodes_table[vertice["substance"]],
                                                     nodes_table[vertice["attribute"]],
                                                     nodes_table[vertice["mode"]])
        multiplication_elems.append(new_element)

    # OH WAIT, we can make it into a sentence/supersentence now, and return it
    proposition_ast = graph_type.additive_type(multiplication_elems)
    # asking the proposition to check then order itself
    proposition_ast.check()

    return proposition_ast


def validate_tree(body):
    """Checks that a give graph representing a sentence/supersentence is well formed, and if it is,
    returns the corresponding IEML string"""
    proposition_ast = build_ieml_sentence_ast(body)
    return {"valid": True, "ieml": str(proposition_ast)}


def save_tree(body):
    """Checks that a give graph representing a sentence/supersentence is well formed, and if it is,
    returns the corresponding IEML string and saves it to the DB"""
    proposition_ast = build_ieml_sentence_ast(body)
    # saving after building the AST
    propositions_db.save_closed_proposition(proposition_ast, body["tags"])
    return {"valid": True, "ieml": str(proposition_ast)}
