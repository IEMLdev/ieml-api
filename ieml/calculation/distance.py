import itertools as it
from collections import defaultdict
from fractions import Fraction

from bidict import bidict
from ieml.ieml_objects import Term, Word, Sentence, SuperSentence, Morpheme, Text, Hypertext
from ieml.ieml_objects.hypertexts import Hyperlink
from ieml.usl import usl
from ieml.script.operator import sc
from ieml.script.tables import get_table_rank
from models.relations.relations import RelationsConnector
from models.relations.relations_queries import RelationsQueries

categories = bidict({Term: 1, Word: 2, Sentence: 3, SuperSentence: 4, Text: 5, Hypertext: 6})


def distance(uslA, uslB, weights):

    eo_total = sum(set_proximity_index(i, uslA, uslB) for i in categories if i != Hypertext) / (len(categories) - 1)
    oo_total = sum(object_proximity_index(i, uslA, uslB) for i in categories if i != Term) / (len(categories) - 1)

    return (eo_total + oo_total) / 2


def set_proximity_index(stage, uslA, uslB):
    """

    Parameters
    ----------
    stage
    uslA
    uslB

    Returns
    -------
    Proximity index between two sets of objects of the same layer
    """
    stages_A, children_A, children_multi_A = compute_stages(uslA)
    stages_B, children_B, children_multi_B = compute_stages(uslB)

    if len(stages_A[stage] | stages_B[stage]) == 0:
        return 1.0

    return float(len(stages_A[stage] & stages_B[stage])) / len(stages_A[stage] | stages_B[stage])


def object_proximity_index(stage, uslA, uslB):
    """

    Parameters
    ----------
    stage
    uslA
    uslB

    Returns
    -------
    Proximity index for 2 objects of the same layer
    """
    stages_A, children_A, children_multi_A = compute_stages(uslA)
    stages_B, children_B, children_multi_B = compute_stages(uslB)

    if stage is Term:
        raise ValueError

    size = float(len(stages_A[stage]) * len(stages_B[stage]))
    accum = 0.0
    for a, b in it.product(stages_A[stage], stages_B[stage]):
        accum += len(children_A[a] & children_B[b]) / (size * len(children_A[a] | children_B[b]))

    return accum


def connexity_index(stage, uslA, uslB):

    stages_A, children_A, children_multi_A = compute_stages(uslA)
    stages_B, children_B, children_multi_B = compute_stages(uslB)

    size = float(len(stages_A[stage]) * len(stages_B[stage]))
    accum = 0.0
    values = []

    for a, b in it.product(stages_A[stage], stages_B[stage]):

        if stage == Sentence or stage == SuperSentence:
            intersection = set(a.tree_graph.nodes) & set(b.tree_graph.nodes)
        else:
            intersection = children_A[a] & children_B[b]

        graph = build_graph(a, b, intersection)
        partitions = partition_graph(graph)
        values.append(connexity(partitions, intersection))

    return sum(values) / size


def mutual_inclusion_index(uslA, uslB):

    stages_A, children_A, children_multi_A = compute_stages(uslA)
    stages_B, children_B, children_multi_B = compute_stages(uslB)

    result = {Word: 0, Sentence: 0, SuperSentence: 0, Text: 0, Hypertext: 0}
    for a_st, b_st in it.permutations(categories.keys(), 2):
        size = float(len(stages_A[a_st]) * len(stages_B[b_st]))
        accum = 0.0

        # if true b in a
        direct = categories[a_st] > categories[b_st]

        for a, b in it.product(stages_A[a_st], stages_B[b_st]):
            if direct:
                accum += children_multi_A[a][b] / \
                         (size * len([e for e in children_multi_A[a] if e.__class__ == b.__class__]))
            else:
                accum += children_multi_B[b][a] / \
                         (size * len([e for e in children_multi_B[b] if e.__class__ == a.__class__]))

        if direct:
            result[a_st] += accum / 2.0
        else:
            result[b_st] += accum / 2.0
    return sum(result.values())/len(result)  # Return mean of the matrix cell index values


def compute_stages(usl):
    """
    Get all the elements in the usl by stages, Term, Word, Sentence, SSentence, Text, Hypertext
    :param usl:
    :return:
    """

    def usl_iter(usl):
        yield from usl.ieml_object.tree_iter()

    stages = {c: set() for c in categories}

    for e in (k for k in usl_iter(usl) if isinstance(k, tuple(categories))):
        stages[e.__class__].add(e)

    children = {}
    for cat in stages:
        for e in stages[cat]:
            if isinstance(e, Term):
                children[e] = set()
                continue

            if isinstance(e, (Word, Sentence, SuperSentence, Text, Hypertext)):
                _class = categories.inv[categories[e.__class__] - 1]
                children[e] = set(i for i in e.tree_iter() if isinstance(i, _class))

    result = defaultdict(lambda: defaultdict(lambda: 0))
    stack = []
    for e in usl_iter(usl):
        if e.__class__ not in categories:
            continue

        if stack:
            while categories[e.__class__] >= categories[stack[-1].__class__]:
                stack.pop()

        for k in stack:
            result[k][e] += 1

        stack.append(e)

    return stages, children, result


def flatten_dict(dico):

    lineage = []
    if isinstance(dico, list):
        return dico
    for child in dico:
        lineage.extend(flatten_dict(dico[child]))
    return lineage


def partition_graph(graph):

    partitions = []
    explored = set()

    def _explore_graph(node, graph, p):

        if node not in explored:
            p.add(node)
        explored.add(node)
        for adjacent_node in graph[node]:
            if adjacent_node not in explored:
                _explore_graph(adjacent_node, graph, p)
        return

    for node in graph:
        p = set()
        _explore_graph(node, graph, p)

        if p:
            partitions.append(p)

    return partitions


def build_graph(object_set_a, object_set_b, intersection):
    # See IEML pour l'ingenieur section 6.7.4.2 for the graph building algorithm

    graph = {node: [] for node in intersection}

    if isinstance(object_set_a, (Text, Hypertext)):

        combos = it.combinations(intersection, 2)
        for combination in combos:
            if combination[0].__class__ == combination[1].__class__:
                graph = _build_proposition_graph(combination, graph)
            elif combination[0].__class__ < combination[1].__class__:
                graph = _build_proposition_graph(combination, graph)
            elif combination[0].__class__ > combination[1].__class__:
                graph = _build_proposition_graph(combination, graph)

    if isinstance(object_set_a, (Sentence, SuperSentence)):
        # In this case the nodes are of type Word

        node_pairs = it.combinations(intersection, 2)

        for pair in node_pairs:
            node_1_addr_a = object_set_a.tree_graph.nodes.index(pair[0])
            node_2_addr_a = object_set_a.tree_graph.nodes.index(pair[1])
            node_1_addr_b = object_set_b.tree_graph.nodes.index(pair[0])
            node_2_addr_b = object_set_b.tree_graph.nodes.index(pair[1])

            if ((object_set_a.tree_graph.array[node_1_addr_a][node_2_addr_a] or
                 object_set_a.tree_graph.array[node_2_addr_a][node_1_addr_a]) and
                (object_set_b.tree_graph.array[node_1_addr_b][node_2_addr_b] or
                 object_set_b.tree_graph.array[node_2_addr_b][node_1_addr_b])):

                graph[pair[0]].append(pair[1])
                graph[pair[1]].append(pair[0])

    if isinstance(object_set_a, Word):
        # The nodes in the intersection set are Terms

        combos = it.combinations(intersection, 2)

        for combination in combos:
            if combination[0] in object_set_a.root.children and combination[1] in object_set_a.flexing.children and \
               combination[0] in object_set_b.root.children and combination[1] in object_set_b.flexing.children:
                graph[combination[0]].append(combination[1])
                graph[combination[1]].append(combination[0])
            elif combination[0] in object_set_a.flexing.children and combination[1] in object_set_a.root.children and \
                 combination[0] in object_set_b.flexing.children and combination[1] in object_set_b.root.children:
                graph[combination[0]].append(combination[1])
                graph[combination[1]].append(combination[0])

    return graph


def parents_index(usl_a, usl_b, index="EO"):

    parents_a, parents_b = get_parents(usl_a, usl_b)

    if index == 'EO':
        return len(parents_a & parents_b) / len(parents_a | parents_b)
    elif index == 'OO':
        return sum(len(a & b)/len(a | b) for a, b in it.product(parents_a, parents_b))/(len(parents_a) * len(parents_b))

    else:
        # TODO: create an invalid index exception and throw it here
        print("Wrong index")


def _build_proposition_graph(combination, graph):

    if isinstance(combination[0], (Sentence, SuperSentence)):
        prop_a = {elem for elem in combination[0].tree_iter() if isinstance(elem, Word)}
        prop_b = {elem for elem in combination[1].tree_iter() if isinstance(elem, Word)}
        if prop_a <= prop_b or prop_b <= prop_a or prop_a & prop_b:
            graph[combination[0]].append(combination[1])
            graph[combination[1]].append(combination[0])
    elif isinstance(combination[0], Word):
        prop_a = {elem for elem in combination[0].tree_iter() if isinstance(elem, Term)}
        prop_b = {elem for elem in combination[1].tree_iter() if isinstance(elem, Term)}
        if prop_a <= prop_b or prop_b <= prop_a or prop_a & prop_b:
            graph[combination[0]].append(combination[1])
            graph[combination[1]].append(combination[0])
    return graph


def get_parents(usl_a, usl_b):

    stages_A, children_A, children_multi_A = compute_stages(usl_a)
    stages_B, children_B, children_multi_B = compute_stages(usl_b)

    def tupleize(arr):
        return frozenset({(elem, arr.count(elem)) for elem in arr})

    rc = RelationsConnector()
    parents_a = {tupleize(flatten_dict(RelationsQueries.relations(term.script, 'FATHER_RELATION'))) for term in stages_A[Term]}
    parents_b = {tupleize(flatten_dict(RelationsQueries.relations(term.script, 'FATHER_RELATION'))) for term in stages_B[Term]}

    return parents_a, parents_b


def get_paradigms(object_set_a):

    if isinstance(object_set_a, Word) or isinstance(object_set_a, Sentence) or isinstance(object_set_a, SuperSentence):
        term_list = [elem for elem in object_set_a.tree_iter() if isinstance(elem, Term)]
    else:
        stages_A, children_A, children_multi_A = compute_stages(object_set_a)
        term_list = stages_A[Term]

    paradigms = {i: [] for i in range(1, 6)}

    rc = RelationsConnector()

    for term in term_list:
        for paradigm in RelationsQueries.relations(term.script, "CONTAINED"):
            paradigms[RelationsQueries.rank(paradigm)].append(paradigm)

    return paradigms


def get_grammar_class(uslA, uslB):
    stages_A, children_A, children_multi_A = compute_stages(uslA)
    stages_B, children_B, children_multi_B = compute_stages(uslB)

    grammar_classes_A = [term.script.script_class for term in stages_A[Term]]
    grammar_classes_B = [term.script.script_class for term in stages_B[Term]]

    return grammar_classes_A, grammar_classes_B


def connexity(partitions, node_intersection):

    if len(node_intersection) == 0:
        return 0

    return Fraction(sum(len(p) for p in partitions if len(p) > 1), (len(partitions) * len(node_intersection)))


def print_graph(graph):

    for k, v in graph.items():
        print(str(k) + ": ")
        print("[", end="")
        for elem in v:
            print(str(elem), end=", ")
        print("]")


def list_intersection_cardinal(list_a, list_b):
    """
    The purpose of this method is to perform the intersection of two lists.
    The reason why we need this method is because we have a use case where we need to keed repeted element in memory
    and also use the list as a set.
    :return:
    """
    intersection_cardinal = 0

    if len(list_a) >= len(list_b):
        tmp = list_a
        iteration_list = list_b

    else:
        tmp = list_b
        iteration_list = list_a


    for element in iteration_list:
        if element in tmp:
            intersection_cardinal += 1
            tmp.remove(element)

    return intersection_cardinal


def list_union_cardinal(list_a, list_b):
    union_cardinal = len(list_a) + len(list_b)
    return union_cardinal


def grammatical_class_index(uslA, uslB, index, stage):
    """

    :param uslA:
    :param uslB:
    :param index:must be the set proximity index : "EO" or the object proximity index : "OO"
    :param stage:must be Term, Word, Sentence or SuperSentence
    :return:the value of the index
    """
    stages_A, children_A, children_multi_A = compute_stages(uslA)
    stages_B, children_B, children_multi_B = compute_stages(uslB)

    grammar_classes_a = [elem.grammatical_class for elem in stages_A[stage]]
    grammar_classes_b = [elem.grammatical_class for elem in stages_B[stage]]

    if index == 'EO':
        index_value = (list_intersection_cardinal(grammar_classes_a, grammar_classes_b) /
                      list_union_cardinal(grammar_classes_a, grammar_classes_b))

    elif index == 'OO':
        if stage is Term:
            raise ValueError

        size = float(len(stages_A[stage]) * len(stages_B[stage]))
        index_value = 0.0
        for a, b in it.product(stages_A[stage], stages_B[stage]):
            # we replace every child of A and B by their grammatical class, and create a list of it
            grammar_list_a = [e.grammatical_class for e in children_A[a]]
            grammar_list_b = [e.grammatical_class for e in children_B[b]]

            # we sort the list in order to do the intersection and union of lists
            grammar_list_a.sort()
            grammar_list_b.sort()

            index_value += (list_intersection_cardinal(grammar_list_a, grammar_list_b) /
                           (size * list_union_cardinal(grammar_list_a, grammar_list_b)))
    else:
        raise ValueError

    return index_value


#TODO complete this function with loulou functions
def paradigmatic_equivalence_class_index(uslA, uslB, paradigm_rank, index):
    """

    :param uslA:
    :param uslB:
    :param paradigm_rank: rank of the paradigm wanted, must be 1 (root paradigm), 2, 3, 4 or 5
    :param index: must be the set proximity index (EO) or the object proximity index (OO)
    :return the paradigmatic equivalence class of the choosen index (EO or OO)
    """
    index_value = 0

    stages_A, children_A, children_multi_A = compute_stages(uslA)
    stages_B, children_B, children_multi_B = compute_stages(uslB)
    paradigms_a = get_paradigms(uslA)
    paradigms_b = get_paradigms(uslB)

    #faire l inverse, d abord if table_rank puis if index ?
    if index == 'EO':
        index_value = (list_intersection_cardinal(paradigms_a[paradigm_rank], paradigms_b[paradigm_rank]) /
                       list_union_cardinal(paradigms_a[paradigm_rank], paradigms_b[paradigm_rank]))

    elif index == 'OO':
        #  We can only find paradigms of terms.
        # So we have to build the '00' matrix with the words of uslA and uslB as rows and columns
        size = float(len(stages_A[Word]) * len(stages_B[Word]))
        if size == 0:
            raise ValueError

        for a, b in it.product(stages_A[Word], stages_B[Word]):
            paradigms_a = get_paradigms(a)
            paradigms_b = get_paradigms(b)

            index_value += (list_intersection_cardinal(paradigms_a[paradigm_rank], paradigms_b[paradigm_rank]) /
                            list_union_cardinal(paradigms_a[paradigm_rank], paradigms_b[paradigm_rank]))
        index_value /= size

    return index_value


if __name__ == '__main__':
    a = "{/[([a.i.-]+[i.i.-])*([E:A:T:.]+[E:S:.wa.-]+[E:S:.o.-])]//[([([a.i.-]+[i.i.-])*([E:A:T:.]+[E:S:.wa.-]+[E:S:.o.-])]{/[([a.i.-]+[i.i.-])*([E:A:T:.]+[E:S:.wa.-]+[E:S:.o.-])]/}*[([t.i.-s.i.-'i.B:.-U:.-'we.-',])*([E:O:.wa.-])]*[([E:E:T:.])])+([([a.i.-]+[i.i.-])*([E:A:T:.]+[E:S:.wa.-]+[E:S:.o.-])]*[([t.i.-s.i.-'u.B:.-A:.-'wo.-',])]*[([E:T:.f.-])])]/}"
    b = usl(a)
    c = usl(a)
    print(distance(b, c, None))

    word_a = Word(Morpheme(
        [Term(sc('wa.')), Term(sc("l.-x.-s.y.-'")), Term(sc("e.-u.-we.h.-'")), Term(sc("M:.E:A:M:.-")),
         Term(sc("E:A:.k.-"))]), Morpheme([Term(sc('wo.')), Term(sc("T:.E:A:T:.-")), Term(sc("E:A:.k.-")),
                                           Term(sc("T:.-',S:.-',S:.-'B:.-'n.-S:.U:.-',_"))]))
    word_b = Word(Morpheme([Term(sc("l.-x.-s.y.-'")), Term(sc("e.-u.-we.h.-'"))]), Morpheme([Term(sc("T:.E:A:T:.-"))]))

    ht_a = Hypertext(Text([word_a]))
    ht_b = Hypertext(Text([word_b]))
    connexity_index(Word, ht_a, ht_b)

    # rc = RelationsConnector()
    # parser = rc.get_script("E:M:.M:O:.-")
    # d = flatten_dict(parser['RELATIONS']['FATHER_RELATION'])
    # print(d)
    #
    # term1 = Term(sc("T:.E:A:T:.-"))
    # term2 = Term(sc("e. - u. - we.h. - '"))
    # term3 = Term(sc("l. - x. - s.y. - '"))
    #
    # term1.check()
    # term2.check()
    # term3.check()
    #
    # graph = {term1: [term2, term3], term2: [term1], term3: [term2]}
    #
    # partition_graph(graph)
