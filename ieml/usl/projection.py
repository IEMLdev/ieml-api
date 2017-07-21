from collections import defaultdict

from ..tools import ieml
from .template import Template

template = Template(ieml("[([M:M:.a.-]+[M:.-',M:.-',S:.-'B:.-'n.-S:.U:.-',_])*([E:U:T:.]+[E:U:.wa.-])]"), ['r0', 'r1'])
collection = list(template)
inverse_terms = defaultdict(list)

for u in collection:
    for t in u.paths.values():
        inverse_terms[t].append(u)

inverse_root = defaultdict(list)
for t in inverse_terms:
    inverse_root[t.root].extend(inverse_terms[t])

roots = sorted(inverse_root, key=lambda t: len(inverse_root[t]), reverse=True)


def best_partitions(term, collection):

    if len(term.partitions):
        pass

    def nb_in(term):
        _in = set()
        for t in inverse_terms:
            if t in term:
                _in |= set(inverse_terms[t])

        return len(_in)


    sorted(term.partitions, key=nb_in)



class Projection:
    def __init__(self, table, collection):
        self.table = table
        self.collection = collection



        self.table.project(collection, lambda cell, c: c['usl'])