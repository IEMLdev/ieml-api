from functools import partial

from ieml import IEMLDatabase
from ieml.dictionary.script import script
from ieml.dictionary.script.tools import promote


# def find_transform(previous, next):
#     """map root paradigm previous to next # same table structure"""
#     previous = script(previous, factorize=True)
#     next = script(next, factorize=True)
#
#     assert previous in dic.tables.roots
#
#     if previous.layer != next.layer:
#         if previous.layer < next.layer:
#             return partial(promote, layer=
#
#     return
#
# if __name__ == '__main__':
#     dic = IEMLDatabase().dictionary()
#     previous = "s.o.-O:O:.-'F:.-',"
#     trans = find_transform(previous, " s.O:O:.-F:.-'")
#
#     mapping = {}
#
#     for s in dic.tables.roots[previous]:
#         mapping[s] = trans(s)
