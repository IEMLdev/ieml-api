from ieml.exceptions import InvalidPathException, EmptyTextException
from .propositions import ClosedProposition
from .propositional_graph import HyperTextGraph
from .utils import PropositionPath

class Tag:
    def __init__(self, tag_content):
        self.content = tag_content


class Text:
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
        return self.childs == other

    def check(self):
        for p in self.childs:
            if not isinstance(p, ClosedProposition):
                raise InvalidPathException()
            p.check()

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


class HyperText:

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
        self._hyperlinks = {}
        for hyperlink in self.childs[0].get_hyperlinks():
            self._add_hyperlink(*hyperlink)

    def _add_hyperlink(self, path, hypertext):
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
        graph = HyperTextGraph(self)
        graph.check()

    def get_path_from_ieml(self, ieml_list):
        return self.childs[0].get_path_from_ieml(ieml_list)

    def _build_graph(self):
        self.texts = [self.childs[0]]
        self.strate = 0
        self.transitions = set()
        for path in self._hyperlinks:
            for child in self._hyperlinks[path]:
                offset = len(self.text)
                # append the text list of the child at the end of the text list, the child text is at offset position
                # the parent (this text) is still at index 0
                self.text += child.text

                # We had the transitions from the child to ours, with the offset to match the index of ours text list
                self.transitions.update(map(lambda t : (t[0] + offset, t[1] + offset, t[2]), child.transitions))

                # We had this transition to the child hypertext
                self.transitions.add((0, offset, path))

                self.strate = max((child.strate + 1, self.strate))