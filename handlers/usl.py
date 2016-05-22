from uuid import uuid4

from ieml import USLParser, PropositionsParser
from ieml.AST import Term, Text,HyperText, AbstractProposition, Word, Sentence, SuperSentence, PropositionPath
from ieml.AST.tools import demote_once, promote_to
from models import DictionaryQueries, TextQueries, PropositionsQueries, HyperTextQueries
from .base import BaseDataHandler, BaseHandler
import json
from .exceptions import InvalidIEMLReference
from ieml.AST import ClosedPropositionMetadata


class TextValidatorHandler(BaseDataHandler):
    """Validates an IEML text, stores it in the text database collection, and returns its IEML form"""

    def __init__(self):
        super().__init__()
        self.db_connector_text = TextQueries()
        self.db_connector_proposition = PropositionsQueries()

    def post(self):
        self.do_request_parsing()

        # create the list of propositions
        parser = PropositionsParser()
        proposition_list = [parser.parse(proposition) for proposition in self.json_data["text"]]

        # check all propositions are stored in database
        if not all(map(self.db_connector_proposition.check_proposition_stored, proposition_list)):
            raise InvalidIEMLReference()

        # promoting term to word
        proposition_list = [promote_to(e, Word) if isinstance(e, Term) else e for e in proposition_list]

        # create the text and check
        text = Text(proposition_list)
        text.check()

        # save the text to the db
        self.db_connector_text.save_text(text, self.json_data["tags"])

        return {"valid": True, "ieml": str(text)}


class HyperTextValidatorHandler(BaseDataHandler):
    def __init__(self):
        super().__init__()

        self.db_connector_text = HyperTextQueries()
        self.parser = USLParser()

    def post(self):
        """
            Request :  {    tags : {..}
                            texts : [{ ieml : str, index : str}, ... ] ,
                            graph : [{ substance : str (index), attribute : str(index), mode : [str, str, ... ](path)},...]}
        """
        self.do_request_parsing()

        hypertexts = {}
        for text in self.json_data["nodes"]:
            hypertexts[text["id"]] = self.parser.parse(text["ieml_string"])

        # parse the graph and add hyperlink, check the cycle
        for hyperlink in self.json_data["graph"]:
            path = hypertexts[hyperlink['substance']].get_path_from_ieml(hyperlink['mode']['selection']['ieml'])
            hypertexts[hyperlink['substance']].add_hyperlink(path, hypertexts[hyperlink['attribut']])

        # get the root hypertext, the one with the biggest strate
        root = hypertexts[max(hypertexts, key=lambda key: hypertexts[key].strate)]

        # verification of the usl
        root.check()

        # save to db
        self.db_connector_text.save_hypertext(root, self.json_data["tags"])

        return {'valid': True, "ieml": str(root)}


class TextDecompositionHandler(BaseHandler):

    def __init__(self):
        super().__init__()

        self.reqparse.add_argument("data", required=True, type=str)
        self.db_connector_term = DictionaryQueries()
        self.db_connector_proposition = PropositionsQueries()
        self.proposition_parser = PropositionsParser()

    def _build_data_field(self, proposition_path, tags):
        """Returns the representation of the ieml *closed* proposition JSON, loading it from the database"""
        return {"PATH": proposition_path.to_ieml_list(),
                "TAGS": tags,
                "TYPE" : proposition_path.path[-1].level} # last node is the current node

    def _promoted_proposition_walker(self, path_to_node, end_node, tags):
        """Recursive function. Handles the JSON creation for promoted propositions"""
        current_node = path_to_node.path[-1]
        proposition_data = self._build_data_field(path_to_node, tags)

        if current_node == end_node:
            if isinstance(end_node, Word): # if endnode it's a word, let's stop, else, we go back to the regular walker
                children_data = []
            else:
                children_data = [self._ast_walker(subpath) for subpath in path_to_node.get_childs_subpaths(depth=2)]
        else:
            demoted_current_node = demote_once(current_node)
            new_path = PropositionPath(path_to_node.path + [demoted_current_node, demote_once(demoted_current_node)])
            children_data = [self._promoted_proposition_walker(new_path, end_node, tags)]

        return {'id': str(uuid4()),  # unique ID for this node, needed by the client's graph library
                'name': tags['EN'],
                'data': proposition_data,
                'children': children_data}

    def _promoted_proposition_chain(self, path_to_node):
        """Prepares the call for the recursive _promoted_proposition_walker, which is itself recursive"""
        current_node = path_to_node.path[-1]
        original_proposition_ast = self.proposition_parser.parse(current_node.metadata["PROMOTION"]["IEML"])

        if current_node.metadata["PROMOTION"]["TYPE"] == "TERM":
            # if the original proposition is a term, then we can't go down that far, let's raise end_node to word
            end_node_ast = promote_to(original_proposition_ast, Word)
        else: # else it's probably a word or a sentence
            end_node_ast = original_proposition_ast

        return self._promoted_proposition_walker(path_to_node,
                                                 end_node_ast, current_node.metadata["TAGS"])

    def _ast_walker(self, path_to_node):
        """Recursive function. Returns a JSON "tree" of the closed propositions for and IEML node,
        each node of that tree containing data for that proposition and its closed children"""
        current_node = path_to_node.path[-1] # current node is the last one in the path

        if "PROMOTION" in current_node.metadata: # cannot use the "in" operator on metadata
            # if the proposition/node is a promotion of a lower one, we the generation
            # to the _promoted_proposition_walker
            return self._promoted_proposition_chain(path_to_node)
        else:
            proposition_data = self._build_data_field(path_to_node, current_node.metadata["TAGS"])

            if isinstance(current_node, (Sentence, SuperSentence)):
                children_data = [self._ast_walker(subpath) for subpath in path_to_node.get_childs_subpaths(depth=2)]
            elif isinstance(current_node, Word):
                children_data = []

            return {'id': str(uuid4()), #unique ID for this node, needed by the client's graph library
                    'name': current_node.metadata['TAGS']['EN'],
                    'data': proposition_data,
                    'children': children_data}

    def post(self):
        self.do_request_parsing()

        # Parse the text
        parser = USLParser()
        hypertext = parser.parse(self.args['data'])

        ClosedPropositionMetadata.set_connector(self.db_connector_proposition)
        # for each proposition, we build the JSON tree data representation of itself and its child closed proposition
        return [self._ast_walker(PropositionPath([child])) for child in hypertext.childs[0].childs]

