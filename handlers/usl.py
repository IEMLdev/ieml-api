from uuid import uuid4

from ieml import USLParser, PropositionsParser
from ieml.AST import Term, Text,HyperText, AbstractProposition, Word, Sentence, SuperSentence
from ieml.AST.tools import demote_once
from models import DictionaryQueries, TextQueries, PropositionsQueries, HyperTextQueries
from .base import BaseDataHandler, BaseHandler
from .exceptions import InvalidIEMLReference


class TextValidatorHandler(BaseDataHandler):
    """Validates an IEML text, stores it in the text database collection, and returns its IEML form"""

    def __init__(self):
        super().__init__()
        self.db_connector_text = TextQueries()
        self.db_connector_proposition = PropositionsQueries()

    def post(self):
        self.do_request_parsing()

        #create the list of proposition (sould we parse or retrieve from the db ?)
        parser = PropositionsParser()
        proposition_list = [parser.parse(proposition['ieml']) for proposition in self.json_data["propositions"]]

        #create the text and check
        text = Text(proposition_list)
        text.check()

        # check all propositions are stored in database
        if not all(map(self.db_connector_proposition.check_proposition_stored, proposition_list)):
            raise InvalidIEMLReference()

        #save the text to the db
        self.db_connector_text.save_text(text, self.json_data["tags"])

        return {"valid" : True, "ieml" : str(text)}


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

        #get the list of text from the db
        hypertexts = {}
        for text in self.json_data["texts"]:
            hypertexts[text["id"]] = self.parser.parse(text["ieml_string"])

        #parse the graph and add hyperlink, check the cycle
        for hyperlink in self.json_data["graph"]:
            path = hypertexts[hyperlink['substance']].get_path_from_ieml(hyperlink['mode']['data']['IEML'])
            hypertexts[hyperlink['substance']].add_hyperlink(path, hypertexts[hyperlink['attribut']])

        #get the root hypertext, the one with the biggest strate
        root = hypertexts[max(hypertexts, key=lambda key: hypertexts[key].strate)]

        #verification of the usl
        root.check()

        #save to db
        self.db_connector_text.save_hypertext(root, self.json_data["tags"])

        return {'valid': True, "ieml": str(root)}


class TextDecompositionHandler(BaseHandler):

    def __init__(self):
        super().__init__()

        self.reqparse.add_argument("data", required=True, type=str)
        self.db_connector_term = DictionaryQueries()
        self.db_connector_proposition = PropositionsQueries()
        self.proposition_parser = PropositionsParser()

    def _build_data_field(self, proposition, tags, parent_proposition_data=None):
        """Returns the representation of the ieml *closed* proposition JSON, loading it from the database"""
        return {"IEML": [str(proposition)] if parent_proposition_data is None
                         else parent_proposition_data["IEML"] + str(proposition),
                "TAGS": tags,
                "TYPE" : proposition.level}

    def _promoted_proposition_walker(self, node, highest_promotion_data, parent_proposition_data):
        """Recursive function. builds the JSON tree repr of a promoted proposition. Basically the node
        it until it reaches the "real" version"""
        if isinstance(node, Word):
            # the current node is a Word, we can't go further down, so that's the last iteration
            current_data = self._build_data_field(node, highest_promotion_data["TAGS"], parent_proposition_data)
            children_data = []
        else: # either it's the "highest" promotion data, or it's an intermediate level
            if highest_promotion_data["IEML"] == str(node):
                current_data = highest_promotion_data
                children_data = [self._promoted_proposition_walker(demote_once(demote_once(node)),
                                                                   highest_promotion_data,
                                                                   highest_promotion_data)]
            else:
                # if we're at an intermediate level, we should check if there's anything in the DB
                node_db_entry = self.db_connector_proposition.exact_ieml_search(node)
                if node_db_entry is None:
                    current_data = self._build_data_field(node, highest_promotion_data["TAGS"], parent_proposition_data)
                    children_data = [self._promoted_proposition_walker(demote_once(demote_once(node)),
                                                                       highest_promotion_data,
                                                                       current_data)]
                else: #we've reached the non-promoted version of the proposition
                    current_data = self._build_data_field(node, node_db_entry["TAGS"], parent_proposition_data)
                    children_data = [self._ast_walker(child, current_data) for child in node.get_closed_childs()]

        return {'id': str(uuid4()),  # unique ID for this node, needed by the client's graph library
                'name': highest_promotion_data['TAGS']['EN'],
                'data': current_data,
                'children': children_data}

    def _ast_walker(self, ast_node, parent_node_data=None):
        """Recursive function. Returns a JSON "tree" of the closed propositions for and IEML node,
        each node of that tree containing data for that proposition and its closed children"""
        node_db_entry = self.db_connector_proposition.exact_ieml_search(ast_node)
        proposition_data = self._build_data_field(ast_node, node_db_entry["tags"], parent_node_data)

        if "PROMOTION" in node_db_entry:
            # if the proposition/node is a promotion of a lower one, we the generation
            # to the _promoted_proposition_walker
            return self._promoted_proposition_walker(ast_node, node_db_entry, proposition_data)
        else:
            if isinstance(ast_node, (Sentence, SuperSentence)):
                children_data = [self._ast_walker(child, proposition_data) for child in ast_node.get_closed_childs()]
            elif isinstance(ast_node, Word):
                children_data = []

            return {'id': str(uuid4()), #unique ID for this node, needed by the client's graph library
                    'name': proposition_data['TAGS']['EN'],
                    'data': proposition_data,
                    'children': children_data}

    def post(self):
        self.do_request_parsing()

        # Parse the text
        parser = USLParser()
        hypertext = parser.parse(self.args['data'])

        # for each proposition, we build the JSON tree data representation of itself and its child closed proposition
        return [self._ast_walker(child) for child in hypertext.childs[0]]


class SearchTextHandler(BaseHandler):
    def __init__(self):
        super().__init__()

        self.reqparse.add_argument("searchstring", required=True, type=str)
        self.db_connector_text = TextQueries()

    def post(self):
        self.do_request_parsing()

        result = self.db_connector_text.search_text(self.args['searchstring'])
        return [
            {
                'IEML': text['_id'],
                'ORIGINAL': 'TEXT',
                'TAGS': text['TAGS'],
                'ORIGINAL_IEML': 'TEXT'
            } for text in result]

