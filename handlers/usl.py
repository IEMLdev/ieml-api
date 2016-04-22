from ieml import USLParser, PropositionsParser
from ieml.AST import Term, Text,HyperText, AbstractProposition
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
        print(self.json_data["propositions"])
        proposition_list = [parser.parse(proposition['IEML']) for proposition in self.json_data["propositions"]]

        #create the text and check
        text = Text(proposition_list)
        text.check()

        # check all propositions are stored in database
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

    def __init__(self):
        super().__init__()

        self.reqparse.add_argument("data", required=True, type=str)
        self.db_connector_term = DictionaryQueries()
        self.db_connector_proposition = PropositionsQueries()

    def _entry(self, node):
        ieml = str(node)
        if isinstance(node, AbstractProposition):
            elem = self.db_connector_proposition.exact_ieml_search(ieml)
        else:
            elem = self.db_connector_term.exact_ieml_term_search(ieml)

        if not elem:
            elem = {"TAGS": {
                "FR": "Inconnu",
                "EN": "Unknown"}}

        return {
           "IEML" : [ieml],
            "TAGS" : elem['TAGS']
        }

    def _prefix_walker(self, node):
        result = [self._entry(node)]

        if not isinstance(node, Term):
            n_ieml = str(node)
            for n in node.childs:
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
        tree = {}

        #transform the list into a node hierachie and only keep closed proposition
        result.sort(key=lambda e : len(e['IEML']))
        root = {}
        for r in result:
            current = root
            for e in r['IEML']:
                if e in current:
                    current = current[e]
                else:
                    current[e] = {'data' : r}

        def build_tree(node):
            if isinstance(node, dict):
                data = node['data']
            return {
                'id' : id(data['IEML']),
                'name' : data['TAGS']['EN'],
                'data' : data,
                'children' : [build_tree(node[key]) for key in node if key != 'data']
            }

        tree = build_tree(root[result[0]['IEML'][0]])


        print(tree)
        return tree
