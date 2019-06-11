import argparse
import os, sys
import shutil
from itertools import chain

from ieml import IEMLDatabase
from ieml.dictionary.script import script
from ieml.ieml_database.descriptor import DescriptorSet
from ieml.ieml_database.lexicon.lexicon_descriptor import LexiconDescriptorSet
from ieml.ieml_database.lexicon.lexicon_structure import LexiconStructure
from ieml.lexicon.syntax import PolyMorpheme


DOMAINS = {
    'Météorologie': 'meteorology',
    'Temporalité': 'temporality',
    'Géographie humaine': 'human_geography',
    'Géographie': 'geography',
    'Eau': 'water'
}

MIGRATE_SCRIPT={
    'E:.T:.c.-': 'E:T:.c.-',
    'E:.T:.h.-': 'E:T:.h.-',
    'E:.S:.x.-': 'E:S:.x.-'
}


def migrate_morpheme(s):
    if s in MIGRATE_SCRIPT:
        return MIGRATE_SCRIPT[s]
    else:
        return s


def import_old_series(lex, desc, dictionary):
    from pymongo import MongoClient
    db_mongo = MongoClient()['intlekt']
    ms_c = db_mongo['morphemes_series']
    usls_c = db_mongo['usl']

    def get_script(wid):
        res = usls_c.find_one({'_id': wid})
        assert res, "Invalid id " + str(wid)
        return script(migrate_morpheme(res['script']))

    def get_word(wid):
        res = usls_c.find_one({'_id': wid})
        return res

    for ms in ms_c.find():
        print(ms['name'], ms['_id'])
        if 'constants' in ms:
            constant = list(map(get_script, ms['constants']['words']))
        else:
            constant = []
        groups = []
        for g in ms['groups']:
            mult = g['multiplicity']
            if mult is None:
                mult = 1

            groups.append((tuple(map(get_script, g['words'])), mult))

        ms_n = PolyMorpheme(constant=constant, groups=groups)

        _break = False
        for morph in chain.from_iterable([constant, *(g[0] for g in groups)]):
            if morph not in dictionary.scripts:
                print("Error in {}, script not defined {}".format(str(ms_n), str(morph)), file=sys.stderr)
                _break = True

        if _break:
            continue

        domain = DOMAINS[ms['name'].split(':', 1)[0]]

        lex.add_paradigm(ms_n, domain=domain)
        desc.set_value(ms_n, 'fr', 'translations', [ms['name'].split(':', 1)[1].strip()])

        for ms_ss in ms['morphemes_cache']['_value']['morphemes']:
            constant = [script(migrate_morpheme(w)) for w in ms_ss['words']]
            if len(constant) == 1:
                continue
            ms_ss_n = PolyMorpheme(constant=constant)

            _break = False
            for morph in chain.from_iterable([ms_ss_n.constant, *(g[0] for g in ms_ss_n.groups)]):
                if morph not in dictionary.scripts:
                    print("Error in {}, script not defined {}".format(str(ms_ss_n), str(morph)), file=sys.stderr)
                    _break = True

            if _break:
                break

            # print(ms_ss)
            # print(str(ms_ss_n))
            if 'id' in ms_ss:
                w = get_word(ms_ss['id'])
                if not w:
                    print("Error in {}, word not defined {}".format(str(ms_ss_n), str(ms_ss['id'])), file=sys.stderr)
                    continue
                if 'descriptors' in w:
                    if 'fr' in w['descriptors']:
                        desc.set_value(ms_ss_n, 'fr', 'translations',
                                       list(chain.from_iterable((dd.split(',') for dd in w['descriptors']['fr']))))
                    if 'en' in w['descriptors']:
                        desc.set_value(ms_ss_n, 'en', 'translations',
                                       list(chain.from_iterable((dd.split(',') for dd in w['descriptors']['en']))))


def migrate(db, author_name, author_mail):
    folder = db.folder

    # print(paths)

    old_p_desc = os.path.join(folder, 'descriptors/dictionary')
    new_p_desc = os.path.join(folder, 'descriptors')


    old_p_struct = os.path.join(folder, 'structure/dictionary')
    # new_p_struct = os.path.join(folder, 'dictionary/structure')

    # os.mkdir(os.path.join(folder, 'dictionary'))
    # shutil.copy(old_p_desc, new_p_desc)
    # shutil.copy(old_p_struct, new_p_struct)

    dictionary = db.dictionary()
    descriptors = DescriptorSet.from_file(os.path.join(db.folder, 'descriptors/dictionary'))

    lexicon_folder = os.path.join(db.folder, 'lexicons')
    shutil.rmtree(lexicon_folder)
    lexicon_folder = os.path.join(db.folder, 'structure/lexicons')
    os.mkdir(lexicon_folder)

    # os.mkdir(lexicon_folder)
    df = descriptors.descriptors.reset_index()
    df.rename(columns={'script': 'ieml'}, inplace=True)

    lex = LexiconStructure()
    desc = LexiconDescriptorSet(df)
    import_old_series(lex, desc, dictionary)

    lex.write_to_folder(lexicon_folder)
    desc.write_to_folder(folder)


    with open(os.path.join(folder, 'version'), 'w') as fp:
        fp.write('0.3')
    from glob import glob
    os.chdir(folder)
    descriptors_paths = [f[2:] for f in glob('./descriptors/**', recursive=True) if os.path.isfile(f) and
                         not f.endswith('dictionary')]
    structure_path = [f[2:] for f in glob('./structure/**', recursive=True) if os.path.isfile(f)]

    old_lexicon_files = [f[2:] for f in glob('./lexicons/**', recursive=True) if os.path.isfile(f)]

    db.save_changes(author_name, author_mail,
                    "[dictionary] Migrate to format v03",
                    to_add=[*descriptors_paths, 'version', *structure_path],
                    to_remove=['descriptors/dictionary', *old_lexicon_files],
                    check_coherency=True)

    # shutil.rmtree(os.path.join(folder, 'lexicons'))
    # shutil.rmtree(os.path.join(folder, 'descriptors/dictionary'))





if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('author_name', type=str)
    parser.add_argument('author_email', type=str)

    parser.add_argument('--folder', type=str)

    args = parser.parse_args()

    folder = args.folder

    db = IEMLDatabase(db_folder=folder)

    migrate(db, args.author_name, args.author_email)

    # lex.write_to_folder('.')
    # desc.write_to_file('./descriptors')