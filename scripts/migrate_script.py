import os
import shutil
from functools import partial

import pygit2

from ieml.ieml_database import IEMLDatabase, GitInterface
from ieml.dictionary import Dictionary
from ieml.dictionary.script import script, AdditiveScript, m
from ieml.dictionary.script.tools import promote
from ieml.ieml_database.transactions.DBTransaction import DBTransactions


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


def migrate_EOETI(scri):
    "E:.O:.E:T:.+I:.- => O:.E:T:.+I:.-"
    if not set(scri.singular_sequences).issubset(script("E:.O:.E:T:.+I:.-").singular_sequences_set):
        return scri

    s, a, _m = scri.children
    return m(script('S:.'), a, _m)


    # assert migrate_EMOto(script("E:M:O:.t.o.-")) == script("E:M:.-O:.-t.o.-'")
    #
    # assert migrate_EOOMt0(script("E:.-'O:O:.-M:.t.o.-',")) == script("E:.-'O:O:.-M:.-'t.o.-',")



def migrate(function, _s_old, _s_new):
    assert function(_s_old) == _s_new


    folder = '/tmp/migrate_script_iemldb'
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    # os.mkdir(folder)
    git_address = "https://github.com/IEMLdev/ieml-language.git"

    credentials = pygit2.Keypair('ogrergo', '~/.ssh/id_rsa.pub', '~/.ssh/id_rsa', None)
    gitdb = GitInterface(origin=git_address,
                         credentials=credentials,
                         folder=folder)

    signature = pygit2.Signature("Louis van Beurden", "louis.vanbeurden@gmail.com")

    db = IEMLDatabase(folder=folder, use_cache=False)

    to_migrate = {}
    desc = db.get_descriptors()
    struct = db.get_structure()

    for s in db.get_dictionary().scripts:
        s2 = function(s)
        if s2 != s:
            to_migrate[s] = s2

    print(to_migrate)

    with gitdb.commit(signature, "[Translate script] Translate paradigm from '{}' to '{}".format(str(_s_old), str(_s_new))):
        for s_old, s_new in to_migrate.items():
            db.remove_structure(s_old)
            for (_, key), values in struct.get_values_partial(s_old).items():
                for v in values:
                    db.add_structure(s_new, key, v)

            db.remove_descriptor(s_old)
            for (_, lang, d), values in desc.get_values_partial(s_old).items():
                for v in values:
                    db.add_descriptor(s_new, lang, d, v)

def add_empty_science_humaine():
    """
    M:M:.-O:M:.+M:O:.-E:.-+s.y.-‘
        —>
    M:M:.-O:M:.+M:O:.-E:.-+s.y.-‘ + M:O:.-we.-s.y.-' + M:M:.-we.-s.y.-'
        """
    src = script("M:M:.-O:M:.+M:O:.-E:.-+s.y.-'")
    tgt = script("M:M:.-O:M:.+M:O:.-E:.-+s.y.-'+M:O:.-we.-s.y.-'+M:M:.-we.-s.y.-'")

    to_update = {}
    to_remove = []

    to_update[src] = tgt
    to_add = [script("M:O:.-we.-s.y.-'"), script("M:M:.-we.-s.y.-'")]
    return to_update, to_add, to_remove


def add_row_evolution_culturel():
    """
    M:O:.-'F:.-'k.o.-t.o.-', => M:O:.-+S:.-'F:.-'k.o.-t.o.-',
    :return:
    """
    src = script("M:O:.-'F:.-'k.o.-t.o.-',")
    s, a, _m = src
    tgt = m(s + script("S:.-'"), a, _m)

    to_update = {}
    to_remove = []

    to_update[src] = tgt

    # for ss_s in s.singular_sequences:
    #     to_update[m(ss_s, a, _m)] = m(ss_s, a, _m)

    for ss_a in a.singular_sequences:
        to_update[m(s, ss_a, _m)] = m(script("S:.-'"), ss_a, _m)
        # to_update[m(s, ss_a, _m)] = m(s + script("S:.-'"), ss_a, _m)

    # to_add.append()
    #
    # to_remove.append()
    #
    # res.append(tgt)

    # for r in tgt.singular_sequences:
    return to_update, to_remove

def translate_temps(s):
    """
    t.o. - n.o. - 'M:O:.-',
    """
    root = script("t.o.-n.o.-M: O:.-'")
    if not s.singular_sequences_set.issubset(root.singular_sequences):
        return s

    _s, _a, _m = s
    return m(m(_s, _a), m(_m))





def add_row_(_s):
    """M:M:.-O:M:.+M:O:.-E:.-+s.y.-'
       S:E:.+M:M:.-E:.+O:M:.+M:O:.-E:.-+s.y.-'"""



    s, a, _m = _s.children

    # return m(m(script("S:E:.") + s.children[0]), m(script("E:.") + a.children[0]), _m)


    res = []
    for ss_m in _m.singular_sequences:
        for ss_s in s.children[0].singular_sequences:
            res.append([
                m(m(ss_s), m(script("E:.")), ss_m),
                m(m(ss_s), m(a.children[0]), ss_m)
            ])


        for ss_a in a.children[0].singular_sequences:
            res.append([
                m(m(script("S:E:.")), m(ss_a), ss_m),
                m(m(s.children[0]), m(ss_a), ss_m)
            ])

    res.append([
        m(m(script("S:E:.")), m(script("E:.")), _m),
        m(m(s.children[0]), m(a.children[0]), _m)
    ])
    return res



# TODO :
# M:M:.-O:M:.+M:O:.-E:.-+s.y.-‘ =>



if __name__ == '__main__':

    # assert migrate_EOETI(script("E:.O:.E:T:.+I:.-")) == script("S:.O:.E:T:.+I:.-")

    #
    # folder = '/tmp/migrate_script_iemldb'
    # if os.path.isdir(folder):
    #     shutil.rmtree(folder)
    # # os.mkdir(folder)
    # git_address = "https://github.com/IEMLdev/ieml-language.git"
    #
    # credentials = pygit2.Keypair('ogrergo', '~/.ssh/id_rsa.pub', '~/.ssh/id_rsa', None)
    # gitdb = GitInterface(origin=git_address,
    #                      credentials=credentials,
    #                      folder=folder)
    #
    # signature = pygit2.Signature("Louis van Beurden", "louis.vanbeurden@gmail.com")
    #
    # db = IEMLDatabase(folder=folder, use_cache=False)
    #
    # # to_migrate = {}
    # desc = db.get_descriptors()
    # struct = db.get_structure()
    #
    # # for s in db.get_dictionary().scripts:
    # #     s2 = function(s)
    # #     if s2 != s:
    # #         to_migrate[s] = s2
    # #
    # # print(to_migrate)
    #
    # src = script("M:M:.-O:M:.+M:O:.-E:.-+s.y.-'")
    # tgt = script("M:M:.-O:M:.+M:O:.-E:.-+s.y.-'+M:O:.-we.-s.y.-'+M:M:.-we.-s.y.-'")
    # #
    # # root_to_migrate = script("M:M:.-O:M:.+M:O:.-E:.-+s.y.-'")
    # # new_root = script("S:E:.+M:M:.-E:.+O:M:.+M:O:.-E:.-+s.y.-'")
    #
    # to_update, to_add, to_remove = add_empty_science_humaine()
    #
    # with gitdb.commit(signature, "[Translate script] Translate paradigm from \"{}\" to \"{}\"".format(str(src), str(tgt))):
    #     for r in to_remove:
    #         db.remove_structure(r)
    #         db.remove_descriptor(r)
    #
    #     for a in to_add:
    #         db.add_descriptor(a, 'fr', 'translations', 'à traduire')
    #         db.add_descriptor(a, 'en', 'translations', 'to translate')
    #
    #     for old, new in to_update.items():
    #         db.remove_structure(old)
    #         db.remove_descriptor(old)
    #
    #         for (_, key), values in struct.get_values_partial(old).items():
    #             for v in values:
    #                 db.add_structure(new, key, v)
    #
    #         for (_, lang, d), values in desc.get_values_partial(old).items():
    #             for v in values:
    #                 db.add_descriptor(new, lang, d, v)
    #
    #
    #
    migrate(translate_temps, script("t.o.-n.o.-M:O:.-'"), script("t.o.-n.o.-'M:O:.-',"))
    # dictionary = db.get_dictionary()

#     db = IEMLDatabase(=git_address,
#                          credentials=credentials,
#                          # db_folder=folder,
#                       cache_folder='/tmp/')
#
#     dic = db.dictionary()
#     desc = db.descriptors()
#     dic_struct = db.dictionary_structure()
#
#     gitdb = GitInterface(origin=git_address,
#                          credentials=credentials,
#                          folder=db.folder,
#                          )
#     to_translate = [("E:.-'O:O:.-M:.t.o.-',", migrate_EOOMt0),
#                     ("s.O:O:.-F:.-'", migrate_sOOF),
#                     ("E:M:O:.t.o.-", migrate_EMOto)]
#     signature = pygit2.Signature("Louis van Beurden", "louis.vanbeurden@gmail.com")
#     for s, migrate in to_translate:
#         for ss in dic.scripts:
#             ss_ = migrate(ss)
#             if ss == ss_:
#                 continue
#
#             old_d = desc.get(ss)
#             for (ieml, l, k), v in old_d.items():
#                 desc.set_value(ss_, l, k, v)
#                 desc.set_value(ss, l, k, [])
#                 # desc.descriptors.drop([ieml, l, k], inplace=True)
#
#             if ss in dic.tables.roots:
#                 paradigms, inhibitions = dic_struct.get(ss)
#                 dic_struct.set_value(ss_, [str(migrate(script(ps))) for ps in paradigms], inhibitions)
#                 dic_struct.structure.drop([str(ss)], inplace=True)
#
#         print("Migrating", str(s))
#         with gitdb.commit(signature, "[Translate script] Translate paradigm {}".format(str(s))):
#             desc.write_to_folder(gitdb.folder)
#             dic_struct.write_to_file(os.path.join(gitdb.folder, 'structure/dictionary'))
#
#     paradigms = []
#     for s in ("s.M:O:.O:O:.-", "O:O:.M:O:.s.-"):
#         _paradigms, _ = dic_struct.get(s)
#         paradigms.extend(_paradigms + [str(s)])
#         # dic_struct.set_value(ss_, [str(migrate(script(ps))) for ps in paradigms], inhibitions)
#         dic_struct.structure.drop([str(s)], inplace=True)
#
#     root = script("O:O:.M: O:.s.-+s.M:O:.O:O:.-")
#     dic_struct.set_value(root, paradigms, [])
#
#     desc.set_value(root, 'fr', 'translations', ["noms et verbes noétiques"])
#     desc.set_value(root, 'en', 'translations', ["noetics nouns and verbs"])
#
#     with gitdb.commit(signature, "[Translate script] Merging paradigms s.M:O:.O:O:.- and O:O:.M:O:.s.-"):
#         desc.write_to_folder(gitdb.folder)
#         dic_struct.write_to_file(os.path.join(gitdb.folder, 'structure/dictionary'))
#
#     db = IEMLDatabase(git_address=git_address,
#                          credentials=credentials,
#                          # db_folder=folder,
#                       cache_folder='/tmp/')
#
#     dic = db.dictionary()
#     desc = db.descriptors()
#
#     gitdb.push('origin')
# # def find_transform(previous, next):
# #     """map root paradigm previous to next # same table structure"""
# #     previous = script(previous, factorize=True)
# #     next = script(next, factorize=True)
# #
# #     assert previous in dic.tables.roots
# #
# #     if previous.layer != next.layer:
# #         if previous.layer < next.layer:
#             return partial(promote, layer=
#
#     return
#
# if __name__ == '__main__':
#     dic = IEMLDatabase().dictionary()
#     previous = "s.o.-O:O:.-'F:.-',"
#     trans = find_transform(previous, " s.O:O:.-F:.-'")

    # mapping = {}
    #
    # for s in dic.tables.roots[previous]:
    #     mapping[s] = trans(s)
