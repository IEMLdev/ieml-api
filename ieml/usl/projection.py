from collections import defaultdict
from itertools import chain

from ieml.dictionary.table import Cell, Table3D, TableSet
from ieml.dictionary.terms import Term

# from ..tools import ieml
# from .template import Template

# template = Template(ieml("[([M:M:.a.-]+[M:.-',M:.-',S:.-'B:.-'n.-S:.U:.-',_])*([E:U:T:.]+[E:U:.wa.-])]"), ['r0', 'r1'])
# collection = list(template)
# inverse_terms = defaultdict(list)
#
# for u in collection:
#     for t in u.paths.values():
#         inverse_terms[t].append(u)
#
# inverse_root = defaultdict(list)
# for t in inverse_terms:
#     inverse_root[t.root].extend(inverse_terms[t])
#
# roots = sorted(inverse_root, key=lambda t: len(inverse_root[t]), reverse=True)


def project_usls_on_dictionary(usls, allowed_terms=None):
    """`usls` is an iterable of usl.

    return a mapping term -> usl list
    """

    cells_to_usls = defaultdict(set)
    tables = set()

    for u in usls:
        for t in u.objects(Term):
            for c in t.singular_sequences:
                # This is the first time we meet the cell c
                if not cells_to_usls[c]:
                    tables.update(c.relations.contained)

                cells_to_usls[c].add(u)

    if allowed_terms:
        allowed_terms = set(allowed_terms)
        tables = tables & allowed_terms
        cells_to_usls = {c: l for c, l in cells_to_usls.items() if c in allowed_terms}

    tables_to_usls = {
        table: list(set(u for c in table.singular_sequences for u in cells_to_usls[c]))
            for table in tables if not isinstance(table, TableSet)
    }

    return tables_to_usls


def project_usl_with_data(usls_data, metric=None):
    """
    usls_data: usl => data[]
    :param usls_data:
    :return:
    """

    projection = project_usls_on_dictionary(usls_data)
    all_terms = set(c for u in usls_data for t in u.objects(Term) for c in t.singular_sequences)
    if metric is None:
        metric = lambda e: len(e['posts']) * len(all_terms.intersection(e['table'].singular_sequences))

    return sorted(({
        'table': table,
        'usls': usls,
        'posts': list(set(chain.from_iterable(usls_data[u] for u in usls)))
    } for table, usls in projection.items()), key=metric, reverse=True)