from ieml.ieml_objects.terms.terms import Term
from ieml.ieml_objects.terms.tools import term
from ieml.ieml_objects.tools import ieml
from ieml.ieml_objects.words import Word
from ieml.paths.paths import Path
from ieml.paths.tools import path
from ieml.usl.tools import usl, replace_paths
import numpy as np

class Template:
    def __init__(self, model, path_list, ):
        super().__init__()

        self.model = usl(model)

        if not isinstance(model, Word):
            raise ValueError("Template only implemented for words.")

        self.paths = [path(p) for p in path_list]
        if any(p.cardinal != 1 for p in self.paths):
            raise ValueError("Can only build a template from singular path (no '+')")

        self.multiples = []
        self.result = []

    def build(self):
        for i, p in enumerate(self.paths):
            t = self.model[p]
            if not isinstance(t, Term) or t.script.cardinal == 1:
                raise ValueError("Invalid path for template creation [%s]->'%s' leading to a non term object,"
                                 "or the term is not a paradigm."%(str(p), str(t)))

            self.multiples.append({
                'index': i,
                'path': p,
                'term': t,
            })

        template = np.zeros(shape=(), dtype=object)
        for m in self.multiples:
            pass


        return replace_paths(self.model, {
            'r'
        })
