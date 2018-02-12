from itertools import islice

from ieml.commons import cached_property
from ieml.syntax.commons import IEMLSyntax

from ieml.syntax.terms import SyntaxTerm
from ieml.syntax.words import Word
from ..constants import LANGUAGES
from ..dictionary import Term
from .paths import Path, enumerate_paths, resolve


class Usl:
    def __init__(self, ieml_object):
        self.ieml_object = ieml_object
        self._rules = None
        self._level = {}

    def __str__(self):
        return str(self.ieml_object)

    def __eq__(self, other):
        if isinstance(other, Usl):
            return self.ieml_object.__eq__(other.ieml_object)

    def __hash__(self):
        return hash(self.ieml_object)

    @property
    def paths(self):
        return self.rules(SyntaxTerm)

    def __getitem__(self, item):
        if isinstance(item, Path):
            if item in self.paths:
                return self.paths[item]

            return resolve(self.ieml_object, item)

        raise NotImplemented

    def auto_translation(self):
        result = {}
        entries = sorted([t for p, t in self.paths.items()])
        for l in LANGUAGES:
            result[l] = ' '.join((e.translations[l] for e in islice(entries, 10)))

        return result

    def rules(self, type):
        if type not in self._level:
            self._level[type] = {path: element for path, element in enumerate_paths(self.ieml_object, level=type)}

        return self._level[type]

    def objects(self, type):
        return set(self.rules(type).values())

    @property
    def glossary(self):
        return {t.term for t in self.rules(SyntaxTerm).values()}

    @property
    def topics(self):
        return set(w for w in self.rules(Word).values() if not w.is_term)

    @property
    def topics_words(self):
        return set(w for w in self.rules(Word).values())

    def __contains__(self, item):
        if isinstance(item, (IEMLSyntax, Term)):
            return item in self.rules(item.__class__).values()

        raise ValueError("Invalid object type, must be a Term or a IEMLSyntax object.")

    def __lt__(self, other):
        if isinstance(other, Usl):
            return self.ieml_object < other.ieml_object

        raise NotImplemented()
