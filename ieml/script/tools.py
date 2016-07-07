import itertools as it
import re

import numpy as np
from bidict import bidict

from ieml.exceptions import NoRemarkableSiblingForAdditiveScript
from ieml.script.constants import LAYER_MARKS, REMARKABLE_ADDITION, PRIMITVES, OPPOSED_SIBLING_RELATION, \
    ASSOCIATED_SIBLING_RELATION, CROSSED_SIBLING_RELATION, TWIN_SIBLING_RELATION, MAX_LAYER
from ieml.script.script import MultiplicativeScript, REMARKABLE_MULTIPLICATION_SCRIPT, Script, NullScript, AdditiveScript, remarkable_multiplication_lookup_table


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

_remarkable_multiplications_twin_siblings = [re.escape(t) for t in ['wo.', 'we.', 's.', 'm.', 'l.']]
_remarkable_multiplications_opposed_siblings = \
    {'j.': 'y\\.', 'n.': 'f\\.', 't.': 'd\\.', 'o.': 'h\\.', 'u.': 'g\\.',
     'm.': 'm\\.', 'i.': 'x\\.', 'wo.': 'wo\\.', 'k.': 'b\\.', 'l.': 'l\\.',
     'x.': 'i\\.', 'a.': 'c\\.', 'd.': 't\\.', 'wa.': 'wu\\.', 'we.': 'we\\.',
     'b.': 'k\\.', 'p.': 'e\\.', 'e.': 'p\\.', 'f.': 'n\\.', 'wu.': 'wa\\.',
     'y.': 'j\\.', 'h.': 'o\\.', 's.': 's\\.', 'g.': 'u\\.', 'c.': 'a\\.'}


def old_canonical(script_ast):
    result = ''
    for byte in script_ast.canonical:
        result += chr(byte + ord('a') - 1)
    return [result]


def factor(sequences):
    layer = next(iter(sequences)).layer

    if layer == 0:
        return list(sequences)

    if len(sequences) == 1:
        return list(sequences)

    # holds the attributes/substances/modes as individual sets in primitives[0]/primitives[1]/primitives[2] respectively
    primitives = (set(seme) for seme in zip(*sequences))

    # same but now there is a bijection between the coordinate system and the primitives semes
    primitives = [bidict({i: s for i, s in enumerate(p_set)}) for p_set in primitives]

    # hold the mapping coordinate -> script
    scripts = {tuple(primitives[i].inv[seme] for i, seme in enumerate(s)):s for s in sequences}

    # hold the primitive as coodinate described in scripts keys
    shape = tuple(len(p) for p in primitives)
    topology = np.full(shape, False, dtype=bool)
    for s in scripts:
        topology[s[0]][s[1]][s[2]] = True

    # calculate the relations, ie for a seq, the others seq that can be factorized with it
    relations = {}
    _computed = set()
    for seq in scripts:
        if not topology[seq[0]][seq[1]][seq[2]]:
            continue

        cubes = {e for e in _computed if
                 topology[e[0]][seq[1]][seq[2]] and
                 topology[seq[0]][e[1]][seq[2]] and
                 topology[seq[0]][seq[1]][e[2]]}

        for c in cubes:
            relations[c].add(seq)

        relations[seq] = cubes
        _computed.add(seq)

    def _neighbours(t1, t2):
        x1, y1, z1 = t1
        x2, y2, z2 = t2
        yield x1, y1, z1
        yield x1, y1, z2
        yield x1, y2, z1
        yield x1, y2, z2
        yield x2, y1, z1
        yield x2, y1, z2
        yield x2, y2, z1
        yield x2, y2, z2

    def _factors(candidate, factorisation):
        # sorting the list of candidate to get the one with the most of potential factors
        candidate.sort(key=lambda e: len(relations[e]), reverse=True)

        for r in candidate:
            _facto = set(it.chain.from_iterable(_neighbours(t, r) for t in factorisation))
            _candidate = set(candidate)
            for i in _facto:
                _candidate &= set(relations[i])

            if _candidate:
                yield from _factors(list(_candidate), _facto)
            else:
                yield _facto

        yield factorisation

    _candidate = [r for r in relations]
    _candidate.sort(key=lambda e: len(relations[e]))

    e = _candidate.pop()
    factorisations = next(iter(_factors(list(relations[e]), [e])))

    remaining = set(sequences) - set(scripts[f] for f in factorisations)
    factorisations = tuple(factor({primitives[i][seme] for seme in semes}) for i, semes in enumerate(zip(*factorisations)))

    if remaining:
        return [factorisations] + factor(remaining)
    else:
        return [factorisations]


def pack_factorisation(facto_list):
    """
    :param facto_list: list of script or tuple of factorisation
    :return:
    """
    _sum = []
    for f in facto_list:
        if isinstance(f, Script):
            _sum.append(f)
        else:
            # tuple of factorisation
            _sum.append(MultiplicativeScript(children=(pack_factorisation(l_f) for l_f in f)))

    if len(_sum) == 1:
        return _sum[0]
    else:
        return AdditiveScript(children=_sum)


def factorize(script):
    if isinstance(script, Script):
        seqs = script.singular_sequences
    elif isinstance(script, list) or hasattr(script, '__iter__'):
        seqs = list(it.chain.from_iterable(s.singular_sequences for s in script))
    else:
        raise ValueError

    result = pack_factorisation(factor(seqs))
    result.check()
    return result

if __name__ == '__main__':
    from ieml.parsing.script import ScriptParser
    script = ScriptParser().parse("M:M:.U:M:.-+F:F:.-+F:O:.A:.T:.-")

    l = ['S:A:A:.','B:A:A:.','T:A:A:.', 'S:A:B:.', 'B:A:B:.', 'T:A:B:.']
    _fail = ['S:A:A:.', 'T:A:B:.', 'B:A:B:.', 'S:A:B:.', 'T:A:A:.', 'B:A:A:.']

    l2 = map(lambda e: e + '.', remarkable_multiplication_lookup_table.values())

    seqs = ['S:A:A:.', 'S:B:T:.', 'S:S:T:.', 'A:U:A:.', 'B:B:T:.']
    saa_ = ScriptParser().parse("t.i.-s.i.-'u.T:.-U:.-'O:O:.-',B:.-',_M:.-',_;")
    sqq_ = ScriptParser().parse("M:M:.o.-M:M:.o.-E:.-+s.u.-'")
    sdd_ = ScriptParser().parse("M:M:.-O:M:.-E:.-+s.y.-'+M:M:.-M:O:.-E:.-+s.y.-'")
    shh_ = ScriptParser().parse("i.B:.-+u.M:.-")
    soo_ = ScriptParser().parse("M:O:.")
    ast_seqs = [script]
    print(str(soo_))
    print(str(factorize(soo_)))
