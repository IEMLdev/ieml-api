from ieml.AST.tree_metadata import TextMetadata, HypertextMetadata
from ieml.exceptions import InvalidPathException, EmptyTextException
from ieml.AST.propositions import ClosedProposition, Word, Sentence, SuperSentence
from ieml.AST.propositional_graph import HyperTextGraph
from ieml.AST.commons import PropositionPath, TreeStructure


class Tag:
    def __init__(self, tag_content):
        self.content = tag_content


class Text(TreeStructure):
    """A text is basically a list of *closed* propositions"""

    def __init__(self, propositions):
        super().__init__()
        if len(propositions) == 0:
            raise EmptyTextException()

        self.children = propositions

    def _do_precompute_str(self):
        self._str = '{/' + '//'.join(map(str, self.children)) + '/}'

    def __hash__(self):
        return self.__str__().__hash__()

    def __eq__(self, other):
        return self.children == other.children

    def _do_checking(self):
        for child in self.children:
            if not isinstance(child, ClosedProposition):
                raise InvalidPathException()

    def _retrieve_metadata_instance(self):
        return TextMetadata(self)

    def render(self, hyperlinks):
        return '{/' + '//'.join([p.render_hyperlinks(hyperlinks, PropositionPath()) for p in self.children]) + '/}'

    def get_hyperlinks(self):
        return [hyperlink for proposition in self.children for hyperlink in proposition.gather_hyperlinks([])]

    def get_path_from_ieml(self, ieml_list):
        proposition_list = []
        current_proposition = self
        for ieml in ieml_list:
            proposition = next(child for child in current_proposition.children if str(child) == ieml)
            if proposition:
                proposition_list.append(proposition)
                current_proposition = proposition
            else:
                raise InvalidPathException()

        return PropositionPath(proposition_list)

    def _do_ordering(self):
        """Orders the propositions in a text. First the words, then the sentences, and the super-sentences"""
        children_by_level = { Word : [], Sentence : [], SuperSentence : []}
        for child in self.children:
            children_by_level[type(child)].append(child)

        children_by_level[Word].sort()
        children_by_level[Sentence].sort()
        children_by_level[SuperSentence].sort()
        self.children = children_by_level[Word] + \
                      children_by_level[Sentence] + \
                      children_by_level[SuperSentence]


class HyperText(TreeStructure):
    """An hypertext contains a list of texts and an hyperlink table"""

    def __init__(self, text):
        super().__init__()
        self.children = [text]

        # we need to ensure that the text is checked to be able to generate the hyperlinks
        text.check()

        self._hyperlinks = None
        self._build_hyperlink()

        # all the text contained in the hypertext
        # the text can be duplicate, because we can put the same hypertext at different path
        self.texts = None
        # all the transition contained in the hypertext (tuple (starting text index, endind text index, path))
        # the index are from the texts attribute
        self.transitions = None
        self._build_graph()

    def _retrieve_metadata_instance(self):
        return HypertextMetadata(self)

    def _build_hyperlink(self):
        """Gather the hyper links from the child text of this hypertext"""
        self._hyperlinks = {}
        for path, hypertext in self.children[0].get_hyperlinks():
            # check the hypertext, it will not be checked otherwise
            hypertext.check()
            self._add_hyperlink(path, hypertext)

    def _add_hyperlink(self, path, hypertext):
        """Adds the hyperlink to the hypertext's hyperlink table,
        with the path as a key and the hypertext as one of the values in the list"""
        if path not in self._hyperlinks:
            self._hyperlinks[path] = []
        self._hyperlinks[path].append(hypertext)

    def get_hyperlinks(self):
        for path, hypertexts in self._hyperlinks.items():
            for hypertext in hypertexts:
                yield (path, hypertext)

    def add_hyperlink(self, path, hypertext):
        self._add_hyperlink(path, hypertext)
        self._build_graph()

    def _do_precompute_str(self):
        self._str = self.render()

    def render(self):
        return self.children[0].render(self._hyperlinks)

    def _do_checking(self):
        # Check cycle and root node
        if len(self._hyperlinks) != 0:
            graph = HyperTextGraph(self)
            graph.check()

    def get_path_from_ieml(self, ieml_list):
        return self.children[0].get_path_from_ieml(ieml_list)

    def _build_graph(self):
        self.texts = [self.children[0]]
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

                # need to recompute the ieml string and redo the checking
                self._do_checking()
                self._do_precompute_str()
