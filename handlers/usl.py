from ieml import USLParser, PropositionsParser
from ieml.AST import Term, Text,HyperText, AbstractProposition, Word, Sentence, SuperSentence
from models import DictionaryQueries, TextQueries, PropositionsQueries, HyperTextQueries
from .base import BaseDataHandler, BaseHandler
import json
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

    def _entry(self, node):
        ieml = str(node)

        if isinstance(node, AbstractProposition):
            if isinstance(node, (Term, Word, Sentence, SuperSentence)):
                elem = self.db_connector_proposition.exact_ieml_search(node)
                # Getting the children of the node.
                # If the node is from a promotion, the child is the promoted proposition.
                if "PROMOTION" in elem:
                    children = [self.proposition_parser.parse(elem["PROMOTION"]["IEML"])]
                else:
                    children = node.childs
            else:
                elem = None
                children = node.childs
        else:
            elem = self.db_connector_term.exact_ieml_term_search(ieml)
            children = []

        entry = {
            "IEML": [ieml],
            "TAGS": elem['TAGS'] if elem else {"FR": "Inconnu", "EN": "Unknown"}
        }

        return children, entry

    def _prefix_walker(self, node):
        children, entry = self._entry(node)
        result = [entry] if isinstance(node, (Term, Word, Sentence, SuperSentence)) else []

        if not isinstance(node, Term):
            n_ieml = str(node)
            for n in children:
                for child in self._prefix_walker(n):
                    child["IEML"].insert(0, n_ieml)
                    result.append(child)
        return result

    def post(self):
        self.do_request_parsing()

        # Parse the text
        parser = USLParser()
        hypertext = parser.parse(self.args['data'])

        result = [e for child in hypertext.childs[0].childs for e in self._prefix_walker(child)]

        # Transform the list into a node hierachie and only keep closed proposition
        # Sorting in growing size of list of ieml (tree hierachie)
        result.sort(key=lambda e: len(e['IEML']))

        # Build the tree structure
        root = {
            'data': {
                "IEML": [self.args['data']],
                "TAGS": {"FR": "Inconnu", "EN": "Unknown"}
            }
        }
        for r in result:
            current = root
            for e in r['IEML']:
                if e in current:
                    current = current[e]
                else:
                    current[e] = {'data': r}

        # Build the json structure
        def build_tree(node):
            # if isinstance(node, dict):
            data = node['data']

            return {
                'id': id(data['IEML']),
                'name': data['TAGS']['EN'],
                'data': data,
                'children': [build_tree(node[key]) for key in node if key != 'data']
            }

        tree = build_tree(root)

        return tree


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
                'IEML': e['_id'],
                'ORIGINAL': 'TEXT',
                'TAGS': e['TAGS'],
                'ORIGINAL_IEML': 'TEXT'
            } for e in result]

