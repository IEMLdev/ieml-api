from functools import partial
from itertools import chain, groupby


from ieml.dictionary.distance import get_matrix
from ieml.dictionary.version import latest_dictionary_version


def w_associate(w0, w1):
    return w0.root == w1.root


def w_opposed(w0, w1):
    return w0.root == w1.flexing and w0.flexing == w1.root


def m_opposed(m0, m1):
    return len(m0) == len(m1) == 1 and m1[0] in m0[0].relations.opposed


def w_crossed(w0, w1):
    return m_opposed(w0.root, w1.root) and m_opposed(w0.flexing, w1.flexing)


def count_id(w0):
    """
    0 -> no terms idd
    1 -> most term idd are shared in root morphem
    2 -> most term idd are shared in flexing morphem
    3 -> most term idd are shared root <-> flexing (crossed)
    :param w0:
    :param w1:
    :return:
    """

    def f(w1):
        count = [set(w0.root).intersection(w1.root),
                 set(w0.flexing).intersection(w1.flexing),
                 set(w0.root).intersection(w1.flexing) | set(w1.root).intersection(w0.flexing)]

        if any(count):
            return max((1,2,3), key=lambda i: len(count[i - 1]))
        else:
            return 0

    return f

relations = get_matrix('relation', latest_dictionary_version())


def count_relations(w0):
    """
    0 -> no terms idd
    1 -> most term idd are shared in root morphem
    2 -> most term idd are shared in flexing morphem
    3 -> most term idd are shared root <-> flexing (crossed)
    :param w0:
    :param w1:
    :return:
    """

    root_w0_relations = set(chain.from_iterable(relations[t.index, :].indices for t in w0.root))
    flexing_w0_relations = set(chain.from_iterable(relations[t.index, :].indices for t in w0.flexing))

    def f(w1):
        root_w1 = set(t.index for t in w1.root)
        flexing_w1 = set(t.index for t in w1.flexing)

        count = [root_w0_relations.intersection(root_w1),
                 flexing_w0_relations.intersection(flexing_w1),
                 root_w0_relations.intersection(flexing_w1) | flexing_w0_relations.intersection(root_w1)]

        if any(count):
            return max((1,2,3), key=lambda i: len(count[i - 1]))
        else:
            return 0
    return f

def w_twin(w0):
    return w0.root == w0.flexing


def order_word_list(w0, word_list):
    klass = {'A': [partial(w_associate, w0=w0), partial(w_opposed, w0=w0), partial(w_crossed, w0=w0)],
             'B': count_id(w0),
             'C': count_relations(w0),
             'D': w_twin}

    SUB_KLASS = {1: '0', 2: '1', 3: '2'}

    def get_mark(w):
        for k in ('A', 'B', 'C', 'D'):
            if isinstance(klass[k], list):
                for i, f in enumerate(klass[k]):
                    if f(w1=w):
                        return k + SUB_KLASS[i + 1]
            else:
                o = klass[k](w)
                if o != 0:
                    return k + SUB_KLASS[o]

        return 'E'

    res = sorted(((w, get_mark(w)) for w in word_list), key=lambda k: k[1])
    return {k: [w[0] for w in v] for k, v in groupby(res,  key=lambda k: k[1])}


def display_ranking(w0, word_list):
    print("Ranking from %s"%str(w0))

    res = order_word_list(w0, word_list)
    for k in sorted(res):
        print("-- Rank %s --"%k)
        for w in res[k]:
            print('\t %s'%str(w))

