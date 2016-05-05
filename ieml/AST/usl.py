from ieml.exceptions import InvalidPathException, EmptyTextException
from ieml.AST.propositions import ClosedProposition, Word, Sentence, SuperSentence
from ieml.AST.propositional_graph import HyperTextGraph
from ieml.AST.utils import PropositionPath

class Tag:
    def __init__(self, tag_content):
        self.content = tag_content


class Text:
    """A text is basically a list of *closed* propositions"""

    def __init__(self, propositions):
        super().__init__()
        if len(propositions) == 0:
            raise EmptyTextException()

        self.childs = propositions

    def __str__(self):
        return '{/' + '//'.join(map(str, self.childs)) + '/}'

    def __hash__(self):
        return self.__str__().__hash__()

    def __eq__(self, other):
        return self.childs == other.childs

    def check(self):
        for child in self.childs:
            if not isinstance(child, ClosedProposition):
                raise InvalidPathException()
            child.check()

    def render(self, hyperlinks):
        return '{/' + '//'.join([p.render_hyperlinks(hyperlinks, PropositionPath()) for p in self.childs]) + '/}'

    def get_hyperlinks(self):
        return [hyperlink for proposition in self.childs for hyperlink in proposition.gather_hyperlinks([])]

    def get_path_from_ieml(self, ieml_list):
        proposition_list = []
        current_proposition = self
        for ieml in ieml_list:
            proposition = next(child for child in current_proposition.childs if str(child) == ieml)
            if proposition:
                proposition_list.append(proposition)
                current_proposition = proposition
            else:
                raise InvalidPathException()

        return PropositionPath(proposition_list)

    def order(self):
        """Orders the propositions in a text. First the words, then the sentences, and the super-sentences"""
        # TODO : Test this ordering
        childs_by_level = { Word : [], Sentence : [], SuperSentence : []}
        for child in self.childs:
            childs_by_level[type(child)].append(child)
            child.order()

        childs_by_level[Word].sort()
        childs_by_level[Sentence].sort()
        childs_by_level[SuperSentence].sort()
        self.childs = childs_by_level[Word] + \
                      childs_by_level[Sentence] + \
                      childs_by_level[SuperSentence]


class HyperText:
    """An hypertext contains a list of texts and an hyperlink table"""

    def __init__(self, text):
        super().__init__()
        self.childs = [text]

        self._hyperlinks = None
        self._build_hyperlink()

        # all the text contained in the hypertext
        # the text can be duplicate, because we can put the same hypertext at different path
        self.texts = None
        # all the transition contained in the hypertext (tuple (starting text index, endind text index, path))
        # the index are from the texts attribute
        self.transitions = None
        self._build_graph()

    def _build_hyperlink(self):
        """Gather the hyper links from children texts"""
        self._hyperlinks = {}
        for path, hypertext in self.childs[0].get_hyperlinks():
            self._add_hyperlink(path, hypertext)

    def _add_hyperlink(self, path, hypertext):
        """Adds the hyperlink to the hypertext's hyperlink table,
        with the path as a key and the hypertext as one of the values in the list"""
        if path not in self._hyperlinks:
            self._hyperlinks[path] = []
        self._hyperlinks[path].append(hypertext)

    def add_hyperlink(self, path, hypertext):
        self._add_hyperlink(path, hypertext)
        self._build_graph()

    def __str__(self):
        return self.render()

    def render(self):
        return self.childs[0].render(self._hyperlinks)

    def check(self):
        # Check cycle and root node
        if len(self._hyperlinks) != 0:
            graph = HyperTextGraph(self)
            graph.check()

        for text in self.texts:
            text.check()

    def order(self):
        for text in self.texts:
            text.order()

    def get_path_from_ieml(self, ieml_list):
        return self.childs[0].get_path_from_ieml(ieml_list)

    def _build_graph(self):
        self.texts = [self.childs[0]]
        self.strate = 0
        self.transitions = set()
        for path in self._hyperlinks:
            for child in self._hyperlinks[path]:
                offset = len(self.texts)
                # append the text list of the child at the end of the text list, the child text is at offset position
                # the parent (this text) is still at index 0
                self.texts += child.texts

                # We had the transitions from the child to ours, with the offset to match the index of ours text list
                self.transitions.update(map(lambda t: (t[0] + offset, t[1] + offset, t[2]), child.transitions))

                # We had this transition to the child hypertext
                self.transitions.add((0, offset, path))

                self.strate = max((child.strate + 1, self.strate))