import os
import shutil
from functools import partial

import pygit2

from ieml import IEMLDatabase
from ieml.dictionary import Dictionary
from ieml.dictionary.script import script, AdditiveScript, m
from ieml.dictionary.script.tools import promote
from scripts.migrate_versions.migrate_v03Tov04 import GitInterface


def migrate_merge(s0, s1):
    """migrate just the root
    s.M:O:.O:O:.- O:O:.M:O:.s.-  => O:O:.M:O:.s.- + s.M:O:.O:O:.-"""

    return AdditiveScript(children=[s0, s1])

def migrate_sOOF(scri):
    "s.O:O:.-F:.-' => s.o.-O:O:.-'F:.-',"
    if not set(scri.singular_sequences).issubset(script("s.O:O:.-F:.-'").singular_sequences_set):
        return scri

    s, a, _ = scri.children
    ss, sa, _ = s.children

    return m(m(m(ss, script('o.')), m(sa)), m(a))

def migrate_EMOto(scri):
    " E:M:O:.t.o.- =>  E:M:.-O:.-t.o.-'"
    if not set(scri.singular_sequences).issubset(script("E:M:O:.t.o.-").singular_sequences_set):
        return scri

    s, a, _m = scri.children
    ss, sa, sm = s.children

    return m(m(m(ss, sa)), m(m(sm)), m(a, _m))

def migrate_EOOMt0(scri):
    "E:.-'O:O:.-M:.t.o.-', => E:.-'O:O:.-M:.-'t.o.-',"
    if not set(scri.singular_sequences).issubset(script("E:.-'O:O:.-M:.t.o.-',").singular_sequences_set):
        return scri

    s, a, _ = scri.children
    _as, aa, _ = a.children
    aas, aaa, aam = aa.children

    return m(s, m(_as, m(aas)) ,m(m(aaa, aam)))

if __name__ == '__main__':

    assert migrate_sOOF(script("s.O:O:.-F:.-'")) == script("s.o.-O:O:.-'F:.-',")
    assert migrate_EMOto(script("E:M:O:.t.o.-")) == script("E:M:.-O:.-t.o.-'")

    assert migrate_EOOMt0(script("E:.-'O:O:.-M:.t.o.-',")) == script("E:.-'O:O:.-M:.-'t.o.-',")


if __name__ == '__main__':

    # folder = '/tmp/migrate_script_iemldb'
    # if os.path.isdir(folder):
    #     shutil.rmtree(folder)
    # os.mkdir(folder)
    git_address = "https://github.com/IEMLdev/ieml-language.git"

    db = IEMLDatabase(git_address=git_address,
                         credentials=credentials,
                         # db_folder=folder,
                      cache_folder='/tmp/')

    dic = db.dictionary()
    desc = db.descriptors()
    dic_struct = db.dictionary_structure()

    gitdb = GitInterface(origin=git_address,
                         credentials=credentials,
                         folder=db.folder,
                         )
    to_translate = [("E:.-'O:O:.-M:.t.o.-',", migrate_EOOMt0),
                    ("s.O:O:.-F:.-'", migrate_sOOF),
                    ("E:M:O:.t.o.-", migrate_EMOto)]
    signature = pygit2.Signature("Louis van Beurden", "louis.vanbeurden@gmail.com")
    for s, migrate in to_translate:
        for ss in dic.scripts:
            ss_ = migrate(ss)
            if ss == ss_:
                continue

            old_d = desc.get(ss)
            for (ieml, l, k), v in old_d.items():
                desc.set_value(ss_, l, k, v)
                desc.set_value(ss, l, k, [])
                # desc.descriptors.drop([ieml, l, k], inplace=True)

            if ss in dic.tables.roots:
                paradigms, inhibitions = dic_struct.get(ss)
                dic_struct.set_value(ss_, [str(migrate(script(ps))) for ps in paradigms], inhibitions)
                dic_struct.structure.drop([str(ss)], inplace=True)

        print("Migrating", str(s))
        with gitdb.commit(signature, "[Translate script] Translate paradigm {}".format(str(s))):
            desc.write_to_folder(gitdb.folder)
            dic_struct.write_to_file(os.path.join(gitdb.folder, 'structure/dictionary'))

    paradigms = []
    for s in ("s.M:O:.O:O:.-", "O:O:.M:O:.s.-"):
        _paradigms, _ = dic_struct.get(s)
        paradigms.extend(_paradigms + [str(s)])
        # dic_struct.set_value(ss_, [str(migrate(script(ps))) for ps in paradigms], inhibitions)
        dic_struct.structure.drop([str(s)], inplace=True)

    root = script("O:O:.M: O:.s.-+s.M:O:.O:O:.-")
    dic_struct.set_value(root, paradigms, [])

    desc.set_value(root, 'fr', 'translations', ["noms et verbes noétiques"])
    desc.set_value(root, 'en', 'translations', ["noetics nouns and verbs"])

    with gitdb.commit(signature, "[Translate script] Merging paradigms s.M:O:.O:O:.- and O:O:.M:O:.s.-"):
        desc.write_to_folder(gitdb.folder)
        dic_struct.write_to_file(os.path.join(gitdb.folder, 'structure/dictionary'))

    db = IEMLDatabase(git_address=git_address,
                         credentials=credentials,
                         # db_folder=folder,
                      cache_folder='/tmp/')

    dic = db.dictionary()
    desc = db.descriptors()

    gitdb.push('origin')
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
