import pprint
import itertools as it
from collections import defaultdict

from ieml.AST.propositions import Word, Sentence, SuperSentence
from ieml.AST.terms import Term
from ieml.AST.usl import Text, HyperText
from ieml.operator import usl
from bidict import bidict
from models.relations import RelationsConnector


def distance(uslA, uslB, weights):
    categories = bidict({Term: 1, Word: 2, Sentence: 3, SuperSentence: 4, Text: 5, HyperText: 6})

    def compute_stages(usl):
        '''
        Get all the elements in the usl by stages, Term, Word, Sentence, SSentence, Text, Hypertext
        :param usl:
        :return:
        '''
        def usl_iter(usl):
            for t in usl.texts:
                yield from t.tree_iter()

        stages = {c: set() for c in categories}

        for e in (k for k in usl_iter(b) if isinstance(k, tuple(categories))):
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

    stages_A, children_A, children_multi_A = compute_stages(uslA)
    stages_B, children_B, children_multi_B = compute_stages(uslB)

    def EO(stage):
        if len(stages_A[stage] | stages_B[stage]) == 0:
            return 1.0

        return float(len(stages_A[stage] & stages_B[stage])) / len(stages_A[stage] | stages_B[stage])

    def OO(stage):
        if stage is Term:
            raise ValueError

        size = float(len(stages_A[stage]) * len(stages_B[stage]))
        accum = 0.0
        for a, b in it.product(stages_A[stage], stages_B[stage]):
            accum += len(children_A[a] & children_B[b]) / (size * len(children_A[a] | children_B[b]))

        return accum

    def O_O(stage):

        size = float(len(stages_A[stage]) * len(stages_B[stage]))
        accum = 0.0

        for a, b in it.product(stages_A[stage], stages_B[stage]):
            intersection = children_A[a] & children_B[b]
            graph = build_graph(children_A[a], children_B[b], intersection)
            partitions = partition_graph(graph)
            accum += sum(len(p) for p in partitions if len(p) > 1)/(len(partitions) * len(intersection))

        return accum/size

    def Oo(stage):
        result = {Sentence: 0, SuperSentence: 0, Text: 0, HyperText: 0}
        for a_st, b_st in it.permutations(categories.values(), 2):
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
        return result

    def get_parents():

        def tupleize(arr):
            return frozenset({(elem, arr.count(elem)) for elem in arr})

        rc = RelationsConnector()
        parents_A = {tupleize(flatten_dict(rc.get_script(terms)['RELATIONS']['FATHER_RELATION'])) for terms in stages_A['Terms']}
        parents_B = {tupleize(flatten_dict(rc.get_script(terms)['RELATIONS']['FATHER_RELATION'])) for terms in stages_B['Terms']}

        return parents_A, parents_B

    def get_paradigm():
        rc = RelationsConnector()
        paradigms_A = {rc.get_script(term)['ROOT'] for term in stages_A['Terms']}
        paradigms_B = {rc.get_script(term)['ROOT'] for term in stages_B['Terms']}

        return paradigms_A, paradigms_B

    def get_grammar_class():

        grammar_classes_A = [term.script.script_class for term in stages_A['Terms']]
        grammar_classes_B = [term.script.script_class for term in stages_B['Terms']]

        return grammar_classes_A, grammar_classes_B

    eo_total = sum(EO(i) for i in categories if i != HyperText)/(len(categories) - 1)
    oo_total = sum(OO(i) for i in categories if i != Term)/(len(categories) - 1)

    return (eo_total + oo_total) / 2

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

        explored.add(node)
        p.add(node)
        for adjacent_node in graph[node]:
            if adjacent_node not in explored:
                return _explore_graph(adjacent_node, graph)
        return

    for node in graph:
        p = set()
        _explore_graph(node, graph, p)
        partitions.append(p)

    return partitions


def build_graph(usl_a, usl_b, intersection):

    graph = {node: [] for node in intersection}

    if isinstance(usl_a, (Sentence, SuperSentence)):
        for node in intersection:
            node_addr = usl_a.graph.nodes_list.index(node)
            for i, n in enumerate(zip(usl_a.graph.adjacency_matrix[node_addr], usl_b.graph.adjacency_matrix[node_addr])):
                if all(n):
                    graph[node].append(usl_a.graph.nodes_list[i])
                    graph[usl_a.graph.nodes_list[i]].append(node)

    if isinstance(usl_a, Word):

        combos = it.combinations(intersection, 2)

        for combination in combos:
            if combination == (usl_a.subst, usl_a.mode) and combination == (usl_b.subst, usl_b.mode):
                graph[combination[0]].append(combination[1])
                graph[combination[1]].append(combination[0])
            elif combination == (usl_a.mode, usl_a.subst) and combination == (usl_b.mode, usl_b.subst):
                graph[combination[0]].append(combination[1])
                graph[combination[1]].append(combination[0])

    if isinstance(usl_a, (Text, HyperText)):

        combos = it.combinations(intersection, 2)
        for combination in combos:
            if combination[0].__class__ == combination[1].__class__:
                graph = _build_proposition_graph(combination, graph)
            elif combination[0].__class__ < combination[1].__class__:
                graph = _build_proposition_graph(combination, graph)
            elif combination[0].__class__ > combination[1].__class__:
                graph = _build_proposition_graph(combination, graph)

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

if __name__ == '__main__':
    a = "{/[([a.i.-]+[i.i.-])*([E:A:T:.]+[E:S:.wa.-]+[E:S:.o.-])]//[([([a.i.-]+[i.i.-])*([E:A:T:.]+[E:S:.wa.-]+[E:S:.o.-])]{/[([a.i.-]+[i.i.-])*([E:A:T:.]+[E:S:.wa.-]+[E:S:.o.-])]/}*[([t.i.-s.i.-'i.B:.-U:.-'we.-',])*([E:O:.wa.-])]*[([E:E:T:.])])+([([a.i.-]+[i.i.-])*([E:A:T:.]+[E:S:.wa.-]+[E:S:.o.-])]*[([t.i.-s.i.-'u.B:.-A:.-'wo.-',])]*[([E:T:.f.-])])]/}"
    b = usl(a)
    c = usl(a)
    print(distance(b, c, None))

    rc = RelationsConnector()
    script = rc.get_script("E:M:.M:O:.-")
    d = flatten_dict(script['RELATIONS']['FATHER_RELATION'])
    print(d)
