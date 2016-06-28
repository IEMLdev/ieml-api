import re

from ieml.exceptions import NoRemarkableSiblingForAdditiveScript, InvalidScript
from ieml.script.constants import LAYER_MARKS, REMARKABLE_ADDITION, PRIMITVES, OPPOSED_SIBLING_RELATION, \
    ASSOCIATED_SIBLING_RELATION, CROSSED_SIBLING_RELATION, TWIN_SIBLING_RELATION, MAX_LAYER, character_value
from ieml.script.script import MultiplicativeScript, REMARKABLE_MULTIPLICATION_SCRIPT, Script, NullScript, AdditiveScript, remarkable_multiplication_lookup_table
import itertools as it
import math
import collections

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


# map_byte_to_old_canonical = {}
# list_value = []
# for c in product((True, False), repeat=len(PRIMITVES)):
#     if not any(c):
#         # no empty addition
#         continue
#     e = 0
#     for b, k in zip(c, PRIMITVES):
#         if not b:
#             continue
#         e |= character_value[k]
#     list_value.append(e)
# list_value.sort()
#
# for v, l in zip(list_value, ascii_lowercase):
#     map_byte_to_old_canonical[v] = l
#
# # map_byte_to_old_canonical = {16: 'f', 1: 'a', 2: 'b', 4: 'c', 56: 'h', 6: 'd', 32: 'g', 8: 'e', 62: 'i', 63: 'j'}
#


def old_canonical(script_ast):
    result = ''
    for byte in script_ast.canonical:
        result += chr(byte + ord('a') - 1)
    return [result]


def factorize(seqs):
    if not seqs:
        return None, 0

    if next(iter(seqs)).layer == 0:
        return seqs, 0

    factorize_set = {}
    for s in seqs:
        if isinstance(s, NullScript):
            continue
        for i in range(3):
            key = tuple([s.children[j] if i != j else None for j in range(3)])
            if key not in factorize_set:
                factorize_set[key] = set()
            factorize_set[key].add(s.children[i])
            # now factorize_set = {(script|None,script|None,script|None) -> [script, ...]}

    # create a list ordered by the biggest factorisation to the smallest
    fa_list = [(key, factorize_set[key]) for key in factorize_set if len(factorize_set[key]) > 1 ]
    fa_list.sort(key=lambda k: len(k[1]), reverse=True)

    def _script(key, script):
        return tuple((i if i is not None else script for i in key))

    def solutions(factors_sets, max_score=math.inf):
        if not factors_sets:
            raise StopIteration

        f = factors_sets[0]
        elem = (f[0], *factorize(f[1]))

        script_elem = [_script(elem[0], e) for e in elem[1]]
        # pprint.pprint(script_elem)
        # script_elem = {_script(elem[0], e) for e in elem[1]}
        remaining = ((key, {e for e in x if _script(key, e) not in script_elem}) for key, x in factors_sets if key != elem[0])
        # remove empty factorisation
        remaining = [e for e in remaining if e[1]]
        # sorting
        remaining.sort(key=lambda e: len(e[1]), reverse=True)

        for sol, score in solutions(remaining):
            current = score + 1 + elem[2]
            if current < max_score:
                max_score = current
            if current == max_score:
                yield sol + [elem], current

        yield from solutions(factors_sets[1:], max_score=max_score)
        # for sol, score in solutions(factors_sets[1:], max_score=max_score):
            # current = score
            # if current < max_score:
            #     max_score = current
            # if current == max_score:
            #     yield sol, score



    _max_score = math.inf
    solutions_list = []
    for _sol, _score in solutions(fa_list):
        pprint.pprint(_sol)
        if _score < _max_score:
            _max_score = _score
            solutions_list = []
        if _score == _max_score:
            solutions_list.append(_sol)

    return list(solutions_list[0]), _max_score


def unpack(result):
    script_elem = []
    for e in result:
        if isinstance(e, Script):
            script_elem.append(e)
        else:
            script_elem.append(MultiplicativeScript(children=tuple((i if i is not None else unpack(e[1]) for i in e[0]))))
    if len(script_elem) == 1:
        return script_elem[0]
    return AdditiveScript(children=script_elem)



def factorize3(seqs):
    if next(iter(seqs)).layer == 0:
        return seqs, 0

    triplets = [((tuple((k,) for k in s.children), (s,))) for s in seqs]

    def _factor(factor, seq):
        count = 0
        result = []
        for f, s in zip(factor[0], seq[0]):
            if set(f) == set(s):
                count += 1
                result.append(s)
            elif s in f or f in s:
                count += 1
                result.append(s)
            else:
                result.append(f + s)

        if count == 2:
            return tuple(result)
        return None

    map_seq_to_factors = {}
    factors = []
    for s in triplets:
        stack = [s]
        i = 0
        while len(stack) > i:
            for f in factors:
                if set(f[1]).intersection(set(stack[i][1])):
                    continue

                list_seqs = list(f[1] + stack[i][1])
                list_seqs.sort()
                list_seqs = tuple(list_seqs)
                if list_seqs in map_seq_to_factors:
                    continue

                new_factor = _factor(f, stack[i])
                if new_factor is not None:
                    new_factor = (new_factor, list_seqs)
                    map_seq_to_factors[list_seqs] = new_factor
                    stack.append(new_factor)
            i += 1
        factors.extend(stack)

    def _score(s):
        return pow(3, s.layer) * 0.5 - 0.5

    def _sol(factorization):
        result = []
        score = 1
        for operand in factorization[0]:
            if len(operand) == 1:
                score += _score(operand[0])
                result.append(operand)
            else:
                f, s = factorize3(operand)
                score += s
                result.append(tuple(f))

        return tuple(result), score

    def unpack(solution):
        script_elem = []
        for t in solution:
            if isinstance(t, Script):
                script_elem.append(t)
            else:
                # otherwise it is a tuple
                script_elem.append(
                    MultiplicativeScript(children=tuple(unpack(t[i]) for i in range(3))))

        if len(script_elem) == 1:
            return script_elem[0]
        return AdditiveScript(children=script_elem)

    def _sub_factorization(factorization, all_factorization):
        seq_set = set(factorization[1])
        sub_factorization = [f for f in all_factorization if not set(f[1]).intersection(seq_set)]
        sub_factorization.sort(key=lambda e: len(e[1]), reverse=True)
        return sub_factorization

    def solutions(factors_list, max_score=math.inf):
        if not factors_list:
            raise StopIteration

        # f is the factorisation we gonna use
        f = factors_list[0]

        solution, sol_score = _sol(f)

        sub_factors = _sub_factorization(f, factors_list)

        if not sub_factors:
            yield [solution], sol_score

        for sol, score in solutions(sub_factors):
            current = score + sol_score
            if current < max_score:
                max_score = current
            if current == max_score:
                yield sol + [solution], current

        yield from solutions(factors_list[1:], max_score=max_score)

    # factors are all possible factorisation available.
    # we iterate over them to build a complete factorization.
    factors.sort(key=lambda e: len(e[1]), reverse=True)
    max_score = math.inf
    solutions_list = []
    for s, score in solutions(factors):
        if score < max_score:
            max_score = score
            solutions_list = []
        if score == max_score:
            solution = unpack(s)
            solution.check()
            print('%s - %d'%(str(solution), score))
            solutions_list.append(solution)

    return solutions_list[0], max_score


if __name__ == '__main__':
    from ieml.parsing.script import ScriptParser
    import pprint
    script = ScriptParser().parse("M:M:.U:M:.-")
    l = ['S:A:A:.','B:A:A:.','T:A:A:.', 'S:A:B:.', 'B:A:B:.', 'T:A:B:.']
    _fail = ['S:A:A:.', 'T:A:B:.', 'B:A:B:.', 'S:A:B:.', 'T:A:A:.', 'B:A:A:.']
#list({'B:A:B:.', 'S:A:A:.', 'B:A:A:.', 'T:A:A:.', 'T:A:B:.', 'S:A:B:.'})
    l2 = map(lambda e: e + '.', remarkable_multiplication_lookup_table.values())
    seq_ences = [ScriptParser().parse(d) for d in l2]
    r = factorize3(seq_ences)
    #result = unpack(r)
    #result.check()
    from random import shuffle
    # best = max(r, key=lambda e: len(e[1]))
    # diff = set()
    # for i in range(100):
    #     shuffle(seq_ences)
    #     if max(factorize3(seq_ences), key=lambda e: len(e[1])) != max:
    #         diff.add(tuple(seq_ences))

    # pprint.pprint([[str(e) for e in lit] for lit in diff])
    # pprint.pprint(_fail)
    # pprint.pprint(len(diff))
    # pprint.pprint([str(b) for b in best[1]])
    # pprint.pprint({'s' : [str(b) for b in best[0][0]],
    #                'a' : [str(b) for b in best[0][1]],
    #                'm' : [str(b) for b in best[0][2]]})