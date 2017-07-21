import itertools as it
import numpy as np
from bidict import bidict

from .script import MultiplicativeScript, Script, AdditiveScript, remarkable_multiplication_lookup_table


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

    # hold the mapping coordinate -> parser
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
    :param facto_list: list of parser or tuple of factorisation
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
    return result


def inverse_relation(relation_name):
    from ..relations import INVERSE_RELATIONS
    return INVERSE_RELATIONS[relation_name]
