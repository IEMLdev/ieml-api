from .script import AdditiveScript, MultiplicativeScript, REMARKABLE_MULTIPLICATION_SCRIPT, Script
from .constants import LAYER_MARKS, REMARKABLE_ADDITION, PRIMITVES, OPPOSED_SIBLING_RELATION, \
    ASSOCIATED_SIBLING_RELATION, CROSSED_SIBLING_RELATION, TWIN_SIBLING_RELATION, MAX_LAYER
from ieml.exceptions import NoRemarkableSiblingForAdditiveScript
import re


class RemarkableSibling:

    @classmethod
    def compute_remarkable_siblings_relations(cls, script_ast_list, regex=True):
        """
        Compute the list of relation for remarkable siblings.
        For the relation associated, opposed and crossed, the list take the form of the tuple: (script_src, script_dest).
        For a tuple (a, b) the symetric (b, a) for a relation is always present in the relation's list.
        For the relation twin, the list is all the script that are in relation together.
        :param script_ast_list: the list of script. must all be in the same layer (paradigm)
        :param regex: optional, if true, use the regex algorithm, otherwise, use the ast based algorithm.
        :return:
        """
        relations = {
            # lists of couple (a, b) if a in relation with b
            OPPOSED_SIBLING_RELATION: [],
            ASSOCIATED_SIBLING_RELATION: [],
            CROSSED_SIBLING_RELATION: [],
            # list of all script that are in relation
            TWIN_SIBLING_RELATION: []
        }

        if len(script_ast_list) == 0:
            return relations

        if regex:
            for i, s_src in enumerate(script_ast_list):
                try:
                    opposed = cls.opposed_sibling_regex(s_src)
                except NoRemarkableSiblingForAdditiveScript:
                    opposed = None
                try:
                    associated = cls.associated_sibling_regex(s_src)
                except NoRemarkableSiblingForAdditiveScript:
                    associated = None
                try:
                    cross = cls.cross_sibling_regex(s_src)
                except NoRemarkableSiblingForAdditiveScript:
                    cross = None

                for s_trg in script_ast_list[i:]:
                    if opposed and opposed.match(str(s_trg)):
                        relations[OPPOSED_SIBLING_RELATION].append((s_src, s_trg))
                        # symetrical
                        relations[OPPOSED_SIBLING_RELATION].append((s_trg, s_src))

                    if associated and associated.match(str(s_trg)):
                        relations[ASSOCIATED_SIBLING_RELATION].append((s_src, s_trg))
                        # symetrical
                        relations[ASSOCIATED_SIBLING_RELATION].append((s_trg, s_src))

                    if cross and cross.match(str(s_trg)):
                        relations[CROSSED_SIBLING_RELATION].append((s_src, s_trg))
                        # symetrical
                        relations[CROSSED_SIBLING_RELATION].append((s_trg, s_src))

            # level -> twin regex map
            twin_regex = {}
            for i in range(MAX_LAYER):
                twin_regex[i] = cls.twin_siblings_regex(i)

            for s in script_ast_list:
                if twin_regex[s.layer].match(str(s)):
                    relations[TWIN_SIBLING_RELATION].append(s)
        else:
            # AST based method
            for i, s_src in enumerate(script_ast_list):
                for s_trg in script_ast_list[i:]:
                    if cls.opposed_siblings(s_src, s_trg):
                        relations[OPPOSED_SIBLING_RELATION].append((s_src, s_trg))
                        # symetrical
                        relations[OPPOSED_SIBLING_RELATION].append((s_trg, s_src))

                    if cls.associated_siblings(s_src, s_trg):
                        relations[ASSOCIATED_SIBLING_RELATION].append((s_src, s_trg))
                        # symetrical
                        relations[ASSOCIATED_SIBLING_RELATION].append((s_trg, s_src))

                    if cls.cross_siblings(s_src, s_trg):
                        relations[CROSSED_SIBLING_RELATION].append((s_src, s_trg))
                        # symetrical
                        relations[CROSSED_SIBLING_RELATION].append((s_trg, s_src))

            for s in script_ast_list:
                if cls.twin_siblings(s):
                    relations[TWIN_SIBLING_RELATION].append(s)

        return relations

    @classmethod
    def opposed_sibling_regex(cls, script_ast):
        if isinstance(script_ast, MultiplicativeScript) and script_ast.layer > 0:
            return re.compile(''.join([
                '^',
                cls._opposed_sibling_string(script_ast),
                '$'
            ]))

        raise NoRemarkableSiblingForAdditiveScript()

    @classmethod
    def _opposed_sibling_string(cls, script_ast):
        if isinstance(script_ast, MultiplicativeScript) and script_ast.layer > 0:
            substance = script_ast.children[0]
            attribute = script_ast.children[1]

            return ''.join([
                '(?:',
                _remarkable_multiplications_opposed_siblings[str(script_ast)] + '|'
                    if script_ast.layer == 1 and script_ast.character else '',
                re.escape(str(attribute)), # substance
                re.escape(str(substance)), # attribute
                cls._regex_layer(attribute.layer, optional=True), # mode
                re.escape(LAYER_MARKS[script_ast.layer]),
                ')'
            ])

    @classmethod
    def associated_sibling_regex(cls, script_ast):
        if isinstance(script_ast, MultiplicativeScript) and script_ast.layer > 0:
            substance = script_ast.children[0]
            attribute = script_ast.children[1]
            mode = script_ast.children[2]

            return re.compile(''.join([
                '^',
                re.escape(str(substance)),
                re.escape(str(attribute)),
                '(?!',
                re.escape(str(mode) + LAYER_MARKS[script_ast.layer]),
                '$)',
                cls._regex_layer(attribute.layer, optional=True),
                re.escape(LAYER_MARKS[script_ast.layer]),
                '$'
            ]))

        raise NoRemarkableSiblingForAdditiveScript()

    @classmethod
    def twin_siblings_regex(cls, layer):

        regex = ''.join([
            '^',
            '$|^'.join(_remarkable_multiplications_twin_siblings) + '$|^'
                if layer == 1 else '',
            '(?P<substance>', # substance
            cls._regex_layer(layer - 1),
            ')(?P=substance)', # attribute == substance
            cls._regex_layer(layer - 1, optional=True),      # mode
            re.escape(LAYER_MARKS[layer]),
            '$'])

        return re.compile(regex)

    @classmethod
    def cross_sibling_regex(cls, script_ast):
        if isinstance(script_ast, MultiplicativeScript) and script_ast.layer > 1 and \
                isinstance(script_ast.children[0], MultiplicativeScript) \
           and isinstance(script_ast.children[1], MultiplicativeScript):

            substance = script_ast.children[0]
            attribute = script_ast.children[1]

            return re.compile(''.join([
                '^',
                cls._opposed_sibling_string(substance),
                cls._opposed_sibling_string(attribute),
                cls._regex_layer(substance.layer, optional=True),
                re.escape(LAYER_MARKS[script_ast.layer]),
                '$'
            ]))

    @classmethod
    def _regex_layer(cls, layer, optional=False):
        primitives = [r'+'] + list(REMARKABLE_ADDITION) + list(PRIMITVES)
        if layer > 0:
            primitives += list(REMARKABLE_MULTIPLICATION_SCRIPT)

        primitives += LAYER_MARKS[:layer]

        return '(?:[' + re.escape(''.join(primitives)) + ']+' + re.escape(LAYER_MARKS[layer]) + ')' + \
               ('*' if optional else '')

_remarkable_multiplications_twin_siblings = [re.escape(t) for t in ['wo.', 'we.', 's.', 'm.', 'l.']]
_remarkable_multiplications_opposed_siblings = \
    {'j.': 'y\\.', 'n.': 'f\\.', 't.': 'd\\.', 'o.': 'h\\.', 'u.': 'g\\.',
     'm.': 'm\\.', 'i.': 'x\\.', 'wo.': 'wo\\.', 'k.': 'b\\.', 'l.': 'l\\.',
     'x.': 'i\\.', 'a.': 'c\\.', 'd.': 't\\.', 'wa.': 'wu\\.', 'we.': 'we\\.',
     'b.': 'k\\.', 'p.': 'e\\.', 'e.': 'p\\.', 'f.': 'n\\.', 'wu.': 'wa\\.',
     'y.': 'j\\.', 'h.': 'o\\.', 's.': 's\\.', 'g.': 'u\\.', 'c.': 'a\\.'}

    @classmethod
    def opposed_siblings(cls, script1, script2):
        if not isinstance(script1, MultiplicativeScript) or not isinstance(script2, MultiplicativeScript):
            return False

        if script1.layer == 0 or script2.layer == 0:
            return False

        return script1.children[0] == script2.children[1] and \
            script1.children[1] == script2.children[0]

    @classmethod
    def associated_siblings(cls, script1, script2):
        if not isinstance(script1, MultiplicativeScript) or not isinstance(script2, MultiplicativeScript):
            return False

        if script1.layer == 0 or script2.layer == 0:
            return False

        return script1.children[0] == script2.children[0] and \
            script1.children[1] == script2.children[1] and \
            script1.children[2] != script2.children[2]

    @classmethod
    def twin_siblings(cls, script):
        if not isinstance(script, MultiplicativeScript):
            return False

        if script.layer == 0:
            return False

        return script.children[0] == script.children[1]

    @classmethod
    def cross_siblings(cls, script1, script2):
        if not isinstance(script1, MultiplicativeScript) or not isinstance(script2, MultiplicativeScript):
            return False

        if script1.layer < 2 or script2.layer < 2:
            return False

        return cls.opposed_siblings(script1.children[0], script2.children[1]) and \
            cls.opposed_siblings(script1.children[1], script2.children[0])
# TODO: Give variables meaningful names


def factorize(script):
    """Method to factorize a given script.
    We want to minimize the number of multiplications in a IEML term"""
    term_set = set(script.children)
    k = set()

    k = _script_compressor(term_set, k)

    return k  # TODO: sort k before returning


def _script_compressor(term_set, k):

    # Set of sets of ieml terms
    c = set()
    q = set()

    c = _seme_matcher(term_set)
    q = _script_solver(c, term_set, set(), set())

    if not q - term_set:
        k.add(term_set)
        return k

    for elem in q:
        _script_compressor(elem, k)

    return k


def _seme_matcher(term_set):
    a = [x for x in range(3)]
    b = [x for x in range(3)]
    D = [set(), set(), set()]
    c = set()

    for term in term_set:
        for i in range(3):
            D[i].add(term)
            a[i] = term[i]

        for term_y in (term_set - term):

            for i in range(3):
                b[i] = term[i]

            if a[1] == b[1]:
                if a[2] == b[2]:
                    D[3].add(term_y)
                if a[3] == b[3]:
                    D[2].add(term_y)
            if a[2] == b[2]:
                if a[3] == b[3]:
                    D[1].add(term_y)
        for d in D:
            if len(d) >= 2 and d not in c:
                c.add(d)
    return c


def _script_solver(C, term_set, R, Q):
    term_set_bar, C,bar, R_bar = {}, {}, {}

    if _pairwise_disjoint(C):  # Must include C = empty set
        for set in C:
            R.add(frozenset(set))
            term_set = term_set - set
        for term in term_set:
            R.add({term})
        if all([r in Q for r in R]) and Q != R:  # Check if R is a proper subset of Q
            Q.add(frozenset(R))
        return Q
    else:
        for set in C:
            if _pairwise_disjoint(C - frozenset(set)):
                term_set = term_set - set
                C = C - frozenset(set)
                R.add(frozenset(set))
        for set in C:
            S_bar = S - set
            C_bar = C - frozenset(set)

            for set_bar in C_bar:
                if not set_bar.intersection(set):
                    C_bar = C_bar - frozenset(set_bar)
            R_bar = R.union(frozenset(set))

        return _script_solver(C_bar, S_bar, R_bar, Q)


def _pairwise_disjoint(sets):
    all_elems = {}

    for s in sets:
        for x in s:
            if x in all_elems: return False
            all_elems.add(x)

    return True
