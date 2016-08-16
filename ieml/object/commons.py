from ieml.exceptions import CannotRenderElementWithoutOrdering, PathCannotBeEmpty, CannotRetrieveMetadata
from functools import total_ordering

@total_ordering
class AbstractPropositionMetaclass(type):
    """This metaclass enables the comparison of class times, such as (Sentence > Word) == True"""

    def __gt__(self, other):
        from ieml.AST import Term, Morpheme, Word, Clause, Sentence, SuperClause, SuperSentence
        child_list = [Term, Morpheme, Word, Clause, Sentence, SuperClause, SuperSentence]
        return child_list.index(self) > child_list.index(other)

    def __lt__(self, other):
        from ieml.AST import Term, Morpheme, Word, Clause, Sentence, SuperClause, SuperSentence
        child_list = [Term, Morpheme, Word, Clause, Sentence, SuperClause, SuperSentence]
        return child_list.index(self) < child_list.index(other)


def requires_not_empty(method):
    """Decorator used by propositions paths that checks if the path is not empty"""
    def wrapper(*args, **kwargs):
        if not args[0].path:
            raise PathCannotBeEmpty("This method cannot work on an empty path")
        else:
            return method(*args, **kwargs)
    return wrapper


class PropositionPath:
    """Stores a path to a 'closable' proposition *inside* another closed proposition, in a text.
    Used by hyperlinks to figure out which proposition is the right one"""

    def __init__(self, path=None, proposition=None):
        self.path = []
        if path:
            self.path += path
        if proposition:
            self.path.append(proposition)

    def __str__(self):
        return '/'.join(self.to_ieml_list())

    def __hash__(self):
        return self.__str__().__hash__()

    def __eq__(self, other):
        return self.path == other.path

    def to_ieml_list(self):
        return [str(e) for e in self.path]

    @requires_not_empty
    def get_children_subpaths(self, depth=1): # depth indicate how make times the function should go down
        """Generates the subpaths to the child of a proposition"""
        if depth == 0:
            return [self]
        else:
            result = []
            for child in self.path[-1].children:
                result += PropositionPath(self.path, child).get_children_subpaths(depth - 1)
            return result


class AbstractProposition(TreeStructure, metaclass=AbstractPropositionMetaclass):
    """This class is the parent class of all propositions, namely Morpheme, Word,
    Clause, Sentence, Superclause, Supersentence"""

    class RenderSymbols:
        """This class is just a container for the rendering symbols"""
        times = "*"
        left_parent = "("
        right_parent = ")"
        plus = "+"
        left_bracket = "["
        right_bracket = "]"

    def __init__(self):
        super().__init__()

    def __contains__(self, proposition):
        """Tests if the input proposition is contained in the current one, or in one of its child"""
        if proposition == self:
            return True
        else: # could be contained in the children proposition
            if proposition.__class__ < self.__class__:
                # testing if it's contained in one of the child
                for child in self.children:
                    if proposition in child:
                        return True
                # contained nowhere!
                return False
            else:
                # can't be contained if the level is higher
                return False

    def _gather_child_links(self, current_path):
        path = current_path + [self]
        return [couple for sublist in [child.gather_hyperlinks(path) for child in self.children]
                for couple in sublist]

    def render_hyperlinks(self, hyperlinks, path):
        current_path = PropositionPath(path.path, self)
        result = self._do_render_hyperlinks(hyperlinks, current_path)

        if current_path in hyperlinks:
            result += ''.join(map(lambda t: "<" + str(t[0]) + ">" + str(t[1]), hyperlinks[current_path]))

        return result