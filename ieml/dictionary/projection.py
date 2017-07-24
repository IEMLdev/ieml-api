from collections import defaultdict

from .table import Table
from .terms import Term
from .tools import term


class ProjectionSet:
    def __init__(self, table, usls):
        super().__init__()
        self.table = table

        self.terms = defaultdict(list)
        self.projection = defaultdict(list)

        for u in usls:
            for t in u.objects(Term).intersection(self.table):
                self.terms[t].append(u)
                self.projection[u].append(t)

    @property
    def ratio(self):
        return len(self.projection) * len(self.terms) / len(self.table)


if __name__ == '__main__':
    from ieml.usl.tools import random_usl
    from .table import Cell, Table1D, Table2D
    from . import Dictionary

    usls = [random_usl() for _ in range(100)]
    terms = {t for u in usls for t in u.objects(Term) if isinstance(t, Cell)}
    print([str(t) for t in terms])
    # one table
    p = ProjectionSet(term('O:M:.O:M:.-'), usls)
    print(p.ratio)

    # all table 2d and 1d
    tables = [t for t in Dictionary() if isinstance(t, (Table1D, Table2D))]
    projections = sorted(map(lambda t: ProjectionSet(t, usls), tables), key=lambda proj: proj.ratio, reverse=True)

