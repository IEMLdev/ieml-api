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

if __name__ == '__main__':
    from ieml.usl import random_usl
    from ieml.usl.template import Template

    usls = list(Template("[([O:M:.]+[x.M:M:.-])]", ['r0', 'r1']))

    paradigms = [t for t in term("M:O:.M:M:.-").relations.contains if len(t) != 1 and t.ntable == 1]

    projections = [ProjectionSet(Table(p), usls) for p in paradigms]

    projections= sorted(projections, key=lambda p: p.ratio, reverse=True)

    proj = ProjectionSet(Table("M:O:.M:M:.-"), usls)
    print(proj)