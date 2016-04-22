from ieml import USLParser, PropositionsParser
from ieml.AST import Term, Text,HyperText
from models import DictionaryQueries, TextQueries, PropositionsQueries, HyperTextQueries
from .base import BaseDataHandler, BaseHandler


class TextValidatorHandler(BaseDataHandler):

    def __init__(self):
        super().__init__()
        self.db_connector_text = TextQueries()
        self.db_connector_proposition = PropositionsQueries()

    def post(self):
        self.do_request_parsing()

        #create the list of proposition (sould we parse or retrieve from the db ?)
        parser = PropositionsParser()
        proposition_list = [parser.parse(proposition) for proposition in self.json_data["propositions"]]

        #create the text and check
        text = Text(proposition_list)
        text.check()

        #check all propositions are stored in database
        all(map(self.db_connector_proposition.retrieve_proposition_objectid, proposition_list))

        #save the text to the db
        self.db_connector_text.save_text(text, self.json_data["tags"])

        return {"valid" : True, "ieml" : str(text)}


class HyperTextValidatorHandler(BaseDataHandler):
    def __init__(self):
        super().__init__()

        self.db_connector_text = HyperTextQueries()

    def post(self):
        """
            Request :  {    tags : {..}
                            texts : [{ ieml : str, index : str}, ... ] ,
                            graph : [{ substance : str (index), attribute : str(index), mode : [str, str, ... ](path)},...]}
        :return:
        """
        self.do_request_parsing()

        #get the list of text from the db
        hypertexts = {}
        for text in self.json_data["texts"]:
            hypertexts[text["index"]] = HyperText(self.db_connector_text.get_text_from_ieml(text["ieml"]))

        #parse the graph and add hyperlink, check the cycle
        for hyperlink in self.json_data["graph"]:
            path = hypertexts[hyperlink['substance']].get_path_from_ieml(hyperlink['mode'])
            hypertexts[hyperlink['substance']].add_hyperlink(path, hypertexts[hyperlink['attribute']])

        #get the root hypertext, the one with the biggest strate
        root = hypertexts[max(hypertexts, key=lambda key: hypertexts[key].strate)]

        #verification of the usl

        #save to db
        self.db_connector_text.save_hypertext(root, self.json_data["tags"])

        return {'valid' : True, "IEML" : str(root)}


class TextDecompositionHandler(BaseHandler):

    def _entry(self, node):
        ieml = str(node)
        elem = DictionaryQueries().exact_ieml_term_search(ieml)
        if elem:
            return {
                "ieml": ieml,
                "tags": {
                    "FR": elem.get("FR"),
                    "EN": elem.get("EN")
                }
            }
        else:
            return {
                "ieml": ieml
            }

    def _prefix_walker(self, node):
        result = [self._entry(node)]
        if not isinstance(node, Term):
            n_ieml = str(node)
            for n in node.childs:
                for child in self._prefix_walker(n):
                    child["ieml"] = n_ieml + '/' + child["ieml"]
                    result.append(child)
        return result

    def post(self):
        self.reqparse.add_argument("data", required=True, type=str)
        self.do_request_parsing()

        parser = USLParser()
        text = parser.parse(self.args['data'])
        l = [self._prefix_walker(proposition) for proposition in text.propositions]
        result = [item for sublist in l for item in sublist]
        print(result)
        return result

