from uuid import uuid4

from handlers.library.base import propositions_db, hypertexts_db, texts_db
from ieml import USLParser, PropositionsParser
from ieml.AST import ClosedPropositionMetadata
from ieml.AST import Term, Text, Word, Sentence, SuperSentence, PropositionPath
from ieml.object.tools import demote_once, promote_to
from .exceptions import InvalidIEMLReference


def validate_text(body):
    """Validates an IEML text, stores it in the text database collection, and returns its IEML form"""

    # create the list of propositions
    parser = PropositionsParser()
    proposition_list = [parser.parse(proposition) for proposition in body["text"]]

    # check all propositions are stored in database
    if not all(map(propositions_db.check_proposition_stored, proposition_list)):
        raise InvalidIEMLReference()

    # promoting term to word
    proposition_list = [promote_to(e, Word) if isinstance(e, Term) else e for e in proposition_list]

    # create the text's ast and check it
    text_ast = Text(proposition_list)
    text_ast.check()

    # save the text to the db
    texts_db.save_text(text_ast, body["tags"])

    return {"valid": True, "ieml": str(text_ast)}


def validate_hypertext(body):
    parser = USLParser()
    hypertexts = {}
    for text in body["nodes"]:
        hypertexts[text["id"]] = parser.parse(text["ieml_string"])

    # parse the graph and add hyperlink, check the cycle
    for hyperlink in body["graph"]:
        path = hypertexts[hyperlink['substance']].get_path_from_ieml(hyperlink['mode']['selection'])
        hypertexts[hyperlink['substance']].add_hyperlink(path,
                                                         hyperlink['mode']['literal'],
                                                         hypertexts[hyperlink['attribute']])

    # get the root hypertext, the one with the highest strata
    root = hypertexts[max(hypertexts, key=lambda key: hypertexts[key].strate)]

    # verification of the usl
    root.check()

    # save to db
    hypertexts_db.save_hypertext(root, self.json_data["tags"])

    return {'valid': True, "ieml": str(root)}


def decompose_text(ieml_string):
    
    def _build_data_field(proposition_path, tags):
        """Returns the representation of the ieml *closed* proposition JSON, loading it from the database"""
        return {"PATH": proposition_path.to_ieml_list(),
                "TAGS": tags,
                "TYPE": proposition_path.path[-1].level}  # last node is the current node

    def _promoted_proposition_walker(path_to_node, end_node, tags):
        """Recursive function. Handles the JSON creation for promoted propositions"""
        current_node = path_to_node.path[-1]
        proposition_data = _build_data_field(path_to_node, tags)

        if current_node == end_node:
            if isinstance(end_node, Word):  # if endnode it's a word, let's stop, else, we go back to the regular walker
                children_data = []
            else:
                children_data = [_ast_walker(subpath) for subpath in path_to_node.get_children_subpaths(depth=2)]
        else:
            demoted_current_node = demote_once(current_node)
            new_path = PropositionPath(path_to_node.path + [demoted_current_node, demote_once(demoted_current_node)])
            children_data = [_promoted_proposition_walker(new_path, end_node, tags)]

        return {'id': str(uuid4()),  # unique ID for this node, needed by the client's graph library
                'name': tags['EN'],
                'data': proposition_data,
                'children': children_data}

    def _promoted_proposition_chain(path_to_node):
        """Prepares the call for the recursive _promoted_proposition_walker, which is itself recursive"""
        current_node = path_to_node.path[-1]
        original_proposition_ast = current_node.get_promotion_origin()
        original_proposition_ast.check()

        if isinstance(original_proposition_ast, Term):
            # if the original proposition is a term, then we can't go down that far, let's raise end_node to word
            end_node_ast = promote_to(original_proposition_ast, Word)
        else:  #  else it's probably a word or a sentence
            end_node_ast = original_proposition_ast

        return _promoted_proposition_walker(path_to_node,
                                            end_node_ast, original_proposition_ast.metadata["TAGS"])

    def _ast_walker(path_to_node):
        """Recursive function. Returns a JSON "tree" of the closed propositions for and IEML node,
        each node of that tree containing data for that proposition and its closed children"""
        current_node = path_to_node.path[-1]  #  current node is the last one in the path

        if current_node.is_promotion:  # cannot use the "in" operator on metadata
            # if the proposition/node is a promotion of a lower one, we the generation
            # to the _promoted_proposition_walker
            return _promoted_proposition_chain(path_to_node)
        else:
            proposition_data = _build_data_field(path_to_node, current_node.metadata["TAGS"])

            if isinstance(current_node, (Sentence, SuperSentence)):
                children_data = [_ast_walker(subpath) for subpath in path_to_node.get_children_subpaths(depth=2)]
            elif isinstance(current_node, Word):
                children_data = []

            return {'id': str(uuid4()),  # unique ID for this node, needed by the client's graph library
                    'name': current_node.metadata['TAGS']['EN'],
                    'data': proposition_data,
                    'children': children_data}

    # Parse the text
    parser = USLParser()
    hypertext = parser.parse(ieml_string)

    ClosedPropositionMetadata.set_connector(propositions_db)
    #  for each proposition, we build the JSON tree data representation of itself and its child closed proposition
    return [_ast_walker(PropositionPath([child])) for child in hypertext.children[0].children]
