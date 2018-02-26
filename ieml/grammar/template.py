import copy
import itertools
import numpy as np

from ieml.grammar import Topic, Word
from ..constants import LANGUAGES
from ..dictionary import Term, term
from .paths import path
from .tools import usl, replace_paths


class Template:
    def __init__(self, model, path_list):
        """

        :param model:
        :param path_list:
        :param translation_rule:
        """
        super().__init__()

        self.model = usl(model)

        if not isinstance(self.model, Topic):
            raise ValueError("Template only implemented for topics.")

        self.paths = [path(p) for p in path_list]
        if any(p.cardinal != 1 for p in self.paths):
            raise ValueError("Can only build a template from singular path (no '+')")

        self.multiples = []
        self.result = []

        self.build()

    def build(self):
        self.multiples = []
        for i, p in enumerate(self.paths):
            t = self.model[p]
            if not isinstance(t, Word) or t.script.cardinal == 1:
                raise ValueError("Invalid path for template creation [%s]->'%s' leading to a non SyntaxTerm object, "
                                 "or the term is not a paradigm."%(str(p), str(t)))

            self.multiples.append({
                'index': i,
                'path': p,
                'term': t,
            })

        self.template = np.zeros(shape=tuple(t['term'].script.cardinal for t in self.multiples), dtype=object)

        for index in itertools.product(*tuple(range(s) for s in self.template.shape)):
            self.template[index] = replace_paths(self.model, {
                m['path']: Word(term(m['term'].script.singular_sequences[index[i]])) for i, m in enumerate(self.multiples)
            })

    def get_translations(self, translation_template, mapping=None):
        """

        :param translation_template: str, a string with special string embedded to determine where to put the variation
        translations
        :param mapping: dict {path -> str} where str is the special string in translation template to replace with the
        term translation
        :return: dict {usl -> dict { str (language) ->  str}}
        """

        if mapping is None:
            mapping = {m['path']: str(m['path']) for m in self.multiples}

        def _replace(u):
            translation = copy.deepcopy(translation_template)
            for m in self.multiples:
                for l in LANGUAGES:
                    translation[l] = translation[l].replace(mapping[m['path']], u[m['path']].translations[l])
            return translation

        return {u: _replace(u) for u in self.__iter__()}


    def __iter__(self):
        return (np.asscalar(w) for w in np.nditer(self.template, flags=['refs_ok']))