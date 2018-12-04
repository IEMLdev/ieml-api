from ieml.commons import TreeStructure
from ieml.dictionary.script import Script, script
from ieml.exceptions import InvalidIEMLObjectArgument
from ieml.lexicon.grammar.usl import Usl


def word(arg, literals=None):
    if isinstance(arg, Word):
        if arg.literals != literals and literals is not None:
            return Word(arg.script, literals=literals)
        else:
            return arg
    else:
        return Word(script(arg), literals=literals)


class Word(Usl):
    def __init__(self, script, literals=None):
        if not isinstance(script, Script):
            raise InvalidIEMLObjectArgument(Word, "Invalid script {0} to create a Word instance.".format(str(script)))

        self.script = script

        super().__init__(literals=literals)

    __hash__ = TreeStructure.__hash__

    def compute_str(self):
        return str(self.script)

    def __getattr__(self, item):
        # make the term api accessible
        if item not in self.__dict__:
            return getattr(self.script, item)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.index == other.index

    def __gt__(self, other):
        if self.__class__ != other.__class__:
            return self.__class__ > other.__class__

        return self.index > other.index

    def _get_cardinal(self):
        return self.cardinal

    def _get_words(self):
        return {self}

    def _get_topics(self):
        return {}

    def _get_facts(self):
        return {}

    def _get_theories(self):
        return {}

    # def _set_version(self, version):
    #     self.term = Dictionary(version).translate_script_from_version(self.term.dictionary.version, self.term.script)

    def __repr__(self, lang='en'):
        return "{} ({})".format(str(self), self.script.translations[lang])
