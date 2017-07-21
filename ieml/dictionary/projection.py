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
            for t in u.objects(Term).intersection([cell.term for cell in self.table]):
                cell = self.table[t]
                self.terms[cell].append(u)
                self.projection[u].append(cell)

    @property
    def ratio(self):
        return len(self.projection) * len(self.terms) / len(self.table)

