import pprint
import itertools as it
from collections import defaultdict
import numpy as np
from ieml.AST.propositions import Word, Sentence, SuperSentence, Morpheme
from ieml.AST.terms import Term
from ieml.AST.usl import Text, HyperText
from ieml.operator import usl, sc
from bidict import bidict
from models.relations import RelationsConnector

categories = bidict({Term: 1, Word: 2, Sentence: 3, SuperSentence: 4, Text: 5, HyperText: 6})


def distance(uslA, uslB, weights):

    eo_total = sum(set_proximity_index(i, uslA, uslB) for i in categories if i != HyperText) / (len(categories) - 1)
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

    for a, b in it.product(stages_A[stage], stages_B[stage]):

        if stage == Sentence or stage == SuperSentence:
            intersection = a.graph.nodes_set & b.graph.nodes_set
        else:
            intersection = children_A[a] & children_B[b]

        graph = build_graph(a, b, intersection)
        partitions = partition_graph(graph)
        accum += connexity(partitions, intersection)

    return accum / size


def mutual_inclusion_index(uslA, uslB):

    stages_A, children_A, children_multi_A = compute_stages(uslA)
    stages_B, children_B, children_multi_B = compute_stages(uslB)

    result = {Word: 0, Sentence: 0, SuperSentence: 0, Text: 0, HyperText: 0}
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
        for t in usl.texts:
            yield from t.tree_iter()

    stages = {c: set() for c in categories}

    for e in (k for k in usl_iter(usl) if isinstance(k, tuple(categories))):
        stages[e.__class__].add(e)

    children = {}
    for cat in stages:
        for e in stages[cat]:
            if isinstance(e, Term):
                children[e] = set()
                continue

            if isinstance(e, (Word, Sentence, SuperSentence)):
                _class = categories.inv[categories[e.__class__] - 1]
                children[e] = set(i for i in e.tree_iter() if isinstance(i, _class))

            if isinstance(e, HyperText):
                children[e] = set(e.texts)
                continue

            if isinstance(e, Text):
                children[e] = set(e.children)
                continue

    result = defaultdict(lambda: defaultdict(lambda: 0))
    stack = [usl]
    for e in usl_iter(usl):
        if e.__class__ not in categories:
            continue

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
                return _explore_graph(adjacent_node, graph, p)
        return

    for node in graph:
        p = set()
        _explore_graph(node, graph, p)

        if p:
            partitions.append(p)

    return partitions


def build_graph(usl_a, usl_b, intersection):

    graph = {node: [] for node in intersection}

    if isinstance(usl_a, (Text, HyperText)):

        combos = it.combinations(intersection, 2)
        for combination in combos:
            if combination[0].__class__ == combination[1].__class__:
                graph = _build_proposition_graph(combination, graph)
            elif combination[0].__class__ < combination[1].__class__:
                graph = _build_proposition_graph(combination, graph)
            elif combination[0].__class__ > combination[1].__class__:
                graph = _build_proposition_graph(combination, graph)

    if isinstance(usl_a, (Sentence, SuperSentence)):
        for node in intersection:

            node_addr_a = usl_a.graph.nodes_list.index(node)
            node_addr_b = usl_b.graph.nodes_list.index(node)

            if any(usl_a.graph.adjacency_matrix[node_addr_a]) and any(usl_b.graph.adjacency_matrix[node_addr_b]):
                true_indices_a = np.where(usl_a.graph.adjacency_matrix[node_addr_a])[0]
                true_indices_b = np.where(usl_b.graph.adjacency_matrix[node_addr_b])[0]
                connected_nodes = [usl_a.graph.nodes_list[i] for i in true_indices_a for j in true_indices_b
                                   if usl_a.graph.nodes_list[i] == usl_b.graph.nodes_list[j]]

                for n in connected_nodes:
                    graph[node].append(n)
                    graph[n].append(node)

    if isinstance(usl_a, Word):
        combos = it.combinations(intersection, 2)

        for combination in combos:
            if combination[0] in usl_a.subst.children and combination[1] in usl_a.mode.children and \
               combination[0] in usl_b.subst.children and combination[1] in usl_b.mode.children:
                graph[combination[0]].append(combination[1])
                graph[combination[1]].append(combination[0])
            elif combination[0] in usl_a.mode.children and combination[1] in usl_a.subst.children and \
                 combination[0] in usl_b.mode.children and combination[1] in usl_b.subst.children:
                graph[combination[0]].append(combination[1])
                graph[combination[1]].append(combination[0])

    return graph


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


def get_parents(uslA, uslB):

    stages_A, children_A, children_multi_A = compute_stages(uslA)
    stages_B, children_B, children_multi_B = compute_stages(uslB)

    def tupleize(arr):
        return frozenset({(elem, arr.count(elem)) for elem in arr})

    rc = RelationsConnector()
    parents_A = {tupleize(flatten_dict(rc.get_script(terms)['RELATIONS']['FATHER_RELATION'])) for terms in stages_A['Terms']}
    parents_B = {tupleize(flatten_dict(rc.get_script(terms)['RELATIONS']['FATHER_RELATION'])) for terms in stages_B['Terms']}

    return parents_A, parents_B


def get_paradigm(uslA, uslB):

    stages_A, children_A, children_multi_A = compute_stages(uslA)
    stages_B, children_B, children_multi_B = compute_stages(uslB)
    rc = RelationsConnector()
    paradigms_A = {rc.get_script(term)['ROOT'] for term in stages_A['Terms']}
    paradigms_B = {rc.get_script(term)['ROOT'] for term in stages_B['Terms']}

    return paradigms_A, paradigms_B


def get_grammar_class(uslA, uslB):
    stages_A, children_A, children_multi_A = compute_stages(uslA)
    stages_B, children_B, children_multi_B = compute_stages(uslB)

    grammar_classes_A = [term.script.script_class for term in stages_A['Terms']]
    grammar_classes_B = [term.script.script_class for term in stages_B['Terms']]

    return grammar_classes_A, grammar_classes_B


def connexity(partitions, node_intersection):

    if len(node_intersection) == 0:
        return 0

    return sum(len(p) for p in partitions if len(p) > 1) / (len(partitions) * len(node_intersection))

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

    ht_a = HyperText(Text([word_a]))
    ht_b = HyperText(Text([word_b]))
    ht_a.check()
    ht_b.check()
    connexity_index(Word, ht_a, ht_b)

    # rc = RelationsConnector()
    # script = rc.get_script("E:M:.M:O:.-")
    # d = flatten_dict(script['RELATIONS']['FATHER_RELATION'])
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
