# TODO: Give variables meaningful names

def regroup(*headers):
    """Takes in multiple table headers added together and regroups them"""


def factorize(script):
    """Method to factorize a given script.
    We want to minimize the number of multiplications in a IEML term"""
    term_set = set(script.singular_sequences)
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
    c = set()

    for term_a in term_set:
        matched_sets = [{term_a} for x in range(3)]
        for term_b in (term_set - {term_a}):
            if term_a[0] == term_b[0]:
                if term_a[1] == term_b[1]:
                    matched_sets[2].add(term_b)
                if term_a[2] == term_b[2]:
                    matched_sets[1].add(term_b)
            if term_a[1] == term_b[1]:
                if term_a[2] == term_b[2]:
                    matched_sets[0].add(term_b)
        for s in matched_sets:
            if len(s) >= 2 and frozenset(s) not in c:
                c.add(frozenset(s))
    return c


def _script_solver(C, term_set, R, Q):
    term_set_bar, C_bar, R_bar = set(), set(), set()

    if _pairwise_disjoint(C):  # Must include C = empty set
        for sc in C:
            R.add(frozenset(sc))
            term_set = term_set - sc
        for term in term_set:
            R.add({term})
        if all([r in Q for r in R]) and Q != R:  # Check if R is a proper subset of Q
            Q.add(frozenset(R))
        return Q
    else:
        for sc in C:
            if _pairwise_disjoint(C - frozenset(sc)):
                term_set = term_set - sc
                C = C - frozenset(sc)
                R.add(frozenset(sc))
        for sc in C:
            S_bar = term_set - sc
            C_bar = C - frozenset(sc)

            for set_bar in C_bar:
                if not set_bar.intersection(sc):
                    C_bar = C_bar - frozenset(set_bar)
            R_bar = R.union(frozenset(sc))

        return _script_solver(C_bar, S_bar, R_bar, Q)


def _pairwise_disjoint(sets):
    all_elems = set()

    for sc in sets:
        for x in sc:
            if x in all_elems: return False
            all_elems.add(x)

    return True


if __name__ == '__main__':
    from ieml.parsing.script import ScriptParser

    sp = ScriptParser()
    s = sp.parse("O:M:.")
    K = factorize(s)
    print(str(K))
