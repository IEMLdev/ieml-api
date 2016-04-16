from handlers.base import BaseHandler
from ieml import USLParser
from ieml.AST import Term
from models import DictionnaryQueries
from .base import BaseDataHandler, BaseHandler

class TextSearchHandler(BaseHandler):

    def post(self):
        pass


class USLValidatorHandler(BaseDataHandler):

    def post(self):
        pass


class TextDecompositionHandler(BaseHandler):

    def _entry(self, node):
        ieml = str(node)
        elem = DictionnaryQueries().exact_ieml_term_search(ieml)
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
        text = parser.parse(self.args['data']);
        l = [self._prefix_walker(proposition) for proposition in text.propositions]
        result = [item for sublist in l for item in sublist]
        print(result)
        return result