import argparse, os
import shutil
from collections import defaultdict

import pygit2

from ieml import IEMLDatabase
from ieml.dictionary.script import script
from ieml.ieml_database.git_interface import GitInterface
from ieml.usl.parser import IEMLParser
import tqdm

def migrate(database, out_folder):
    descriptors = database.descriptors()
    dictionary = database.dictionary_structure()
    # 'root', 'paradigms', 'inhibitions'

    shutil.rmtree(out_folder + '/descriptors')
    shutil.rmtree(out_folder + '/structure')
    # os.rmdir(out_folder)

    # os.mkdir(out_folder)

    db2 = IEMLDatabase(out_folder)
    # db2.get_csv()

    if not os.path.isdir(out_folder):
        os.mkdir(out_folder)

    for ieml, (paradigms, inhibitions) in tqdm.tqdm(dictionary.structure.iterrows(), 'migrating structure'):
        l = IEMLParser().parse(ieml, factorize_script=True)

        db2.add_structure(str(l), 'is_root', True)
        for i in inhibitions:
            db2.add_structure(str(l), 'inhibition', i)

    all_db = defaultdict(lambda : defaultdict(dict))

    for (ieml, lang, desc), (v) in descriptors:
        all_db[ieml][(lang,desc)] = v.values[0]

    for ieml, dd in tqdm.tqdm(all_db.items(), 'migrating descriptors'):
        l = IEMLParser().parse(ieml, factorize_script=True)

        path = db2.path_of(l)

        os.makedirs('/'.join(path.split('/')[:-1]), exist_ok=True)


        with open(path, 'w') as fp:
            for (lang, desc), v in dd.items():
                for vv in v:
                    fp.write('"{}" {} {} "{}"\n'.format(str(l), lang, desc, db2.escape_value(vv)))


            # fp.write(json.dumps({'ieml': str(l), **dd}, indent=True))

def ignore_body_parts(gitdb, db):
    root = script("f.o.-f.o.-',n.i.-f.i.-',M:O:.-O:.-',_+f.o.-f.o.-'E:.-U:.S:+B:T:.-l.-',E:.-U:.M:T:.-l.-'E:.-A:.M:T:.-l.-',_")

    to_ignore = []
    for ss in db.list('morpheme', paradigm=False, parse=True):
        if ss in root:
            to_ignore.append(ss)

    for p in db.list('morpheme', paradigm=True, parse=True):
        if set(root.singular_sequences).issuperset(p.singular_sequences):
            to_ignore.append(p)
    print(len(to_ignore))
    with gitdb.commit(pygit2.Signature("Louis van Beurden", 'louis.vanbeurden@gmail.com'), "[Ignore] ignore body part root paradigm"):
        for s in to_ignore:
            db.add_structure(s, 'is_ignored', True)




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('author_name', type=str)
    parser.add_argument('author_email', type=str)

    parser.add_argument('--folder', type=str)

    args = parser.parse_args()

    # folder = args.folder

    #
    folder = '/tmp/iemldb_test'
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    #
    # # r =
    # # # print(json.dumps(r, indent=True))
    # #
    # # d = Descriptors(db2.get_pandas())
    # # print(d.get_values('wa.', 'en', 'translations'))
    # # db2.remove_key('wa.', 'en', 'translations')
    # # d = Descriptors(db2.get_pandas())
    # # print(d.get_values('wa.', 'en', 'translations'))
    gitdb = GitInterface(origin='ssh://git@github.com/ogrergo/ieml-language.git',
                         credentials=pygit2.Keypair('git', '/home/louis/.ssh/id_rsa.pub', '/home/louis/.ssh/id_rsa', ''),
                         folder=folder)

    # gitdb = GitInterface(origin='https://github.com/ogrergo/ieml-language.git',
    #                      credentials=pygit2.Username('git'),
    #                      folder=folder)

    db = IEMLDatabase(folder=folder)

    # d = Descriptors(db2.get_pandas())
    # # print(d.get_values('wa.', 'fr', 'translations'))
    # # db2.remove_key('wa.', 'fr', 'translations', 'agir')
    # # d = Descriptors(db2.get_pandas())
    # # print(d.get_values('wa.', 'fr', 'translations'))
    #
    # # v = d.get_values_partial(None, 'fr', None)
    #
    # # v = d.get_values_partial(None, 'fr', None)
    # # print(v)

    signature = pygit2.Signature(args.author_name, args.author_email)

    with gitdb.commit(signature, '[Migration] migrate from 0.3 to 0.4'):
        migrate(db, folder)

        with open(os.path.join(folder, 'version'), 'w') as fp:
            fp.write('0.4')
    # # #
    db2 = _IEMLDatabase(gitdb.folder)


    # # # #
    with gitdb.commit(signature, '[Descriptor] add missing translations for hands and feet'):
        root = script("f.o.-f.o.-',n.i.-f.i.-',x.-O:.-',_M:.-',_;+f.o.-f.o.-',n.i.-f.i.-',x.-O:.-',_E:F:.-',_;", factorize=True)
        assert str(root) == "f.o.-f.o.-',n.i.-f.i.-',x.-O:.-',_M:.+E:F:.-',_;"
        p0 =   script("f.o.-f.o.-',n.i.-f.i.-',x.-A:.-',_M:.+E:F:.-',_;")
        p1 =   script("f.o.-f.o.-',n.i.-f.i.-',x.-U:.-',_M:.+E:F:.-',_;")

        db2.add_descriptor(root, 'fr', 'translations', 'parties des mains et des pieds')
        db2.add_descriptor(root, 'en', 'translations', 'parts of hands and feet')

        db2.add_descriptor(p0, 'fr', 'translations', 'parties des pieds')
        db2.add_descriptor(p0, 'en', 'translations', 'parts of feet')

        db2.add_descriptor(p1, 'fr', 'translations', 'parties des mains')
        db2.add_descriptor(p1, 'en', 'translations', 'parts of hands')

    # ignore_body_parts(gitdb, db2)

    with gitdb.commit(signature, '[Descriptor] remove old descriptors'):
        sc = script('F:.n.-')
        db2.remove_descriptor(sc, 'fr', 'translations')
        db2.remove_descriptor(sc, 'en', 'translations')
    desc = db2.get_descriptors()
    with gitdb.commit(signature, '[Descriptor] remove Nan values'):
        for key, v in list(desc.df[desc.df.value.isna()].iterrows()):
            db2.remove_descriptor(*key, "")
            print(key, "remove")

    with gitdb.commit(signature, '[Gitignore] ignore cache'):
        with open(os.path.join(gitdb.folder, '.gitignore'), 'w') as fp:
            fp.write(".dictionary-cache.*\n")

    with gitdb.commit(signature, "[Migration] add '.ieml' file for non-root paradigms"):
        d = db2.get_dictionary()
        for s in d.scripts:
            if len(s) != 1 and s not in d.tables.roots:
                db2.add_structure(s, 'is_root', False)

    gitdb.push('origin')
    # # print(db.get_structure().df)
    # # print(len(db.list('morpheme', paradigm=True)))
    # # print(len(db.list('morpheme', paradigm=False)))
    # # print(len(db.list('polymorpheme', paradigm=False)))
    # # from pympler import asizeof
    #
    # # print(asizeof.asizeof(db2.get_dictionary()))
