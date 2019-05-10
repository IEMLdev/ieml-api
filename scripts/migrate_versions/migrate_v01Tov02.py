import argparse
import shutil, os
import re, sys
import urllib.parse
from collections import Counter, defaultdict

from multiprocessing import Pool

from tqdm import tqdm
import json
from ieml import IEMLDatabase
from ieml.constants import LANGUAGES
from ieml.dictionary.table import TableSet
from ieml.ieml_database.descriptor import DescriptorSet
from ieml.ieml_database.dictionary_structure import DictionaryStructure
from ieml.ieml_database.versions import IEMLDatabaseIO_factory, IEMLDatabaseIOv01
from ieml.ieml_database.versions.ieml_database_io import IEMLDatabaseIOMeta
from ieml.ieml_database.versions.ieml_database_io_v02 import IEMLDatabaseIOv02
from ieml.dictionary.script import script as sc
from requests import get


relation_name_table = {
    "Crossed siblings": "crossed",
    "Associated siblings": "associated",
    "Twin siblings": "twin",
    "Opposed siblings": "opposed",

    # ancestor : Etymology
    "Ancestors in mode": "father_mode",
    "Ancestors in attribute": "father_attribute",
    "Ancestors in substance": "father_substance",

    "Descendents in mode": "child_mode",
    "Descendents in attribute": "child_attribute",
    "Descendents in substance": "child_substance",

    # Hyperonymes
    "Contained in": "contained",
    "Belongs to Paradigm": 'ROOT',
    # Hyponymes
    "Contains": "contains"
}
COMMENTS_URL = "https://intlekt.io/api/comments/{}/"


def get_last_version():
    with open('/home/louis/code/ieml/backups/dictionary_2019-04-26_18_44_02.json') as fp:
        return json.load(fp)


def _download_comment(script):
    try:
        return get(COMMENTS_URL.format(script)).json()
    except Exception:
        return []


def download_comments(scripts):
    p = Pool(32)
    comments = {'fr': {}, 'en': {}}

    comments_body_l = p.map(_download_comment, tqdm(scripts))

    for script, comments_body in zip(scripts, comments_body_l):
        if 'comments' in comments_body:
            if 'fr' in comments_body['comments'] and comments_body['comments']['fr'].strip():
                comments['fr'][script] = comments_body['comments']['fr'].strip()
            if 'en' in comments_body['comments'] and comments_body['comments']['en'].strip():
                comments['en'][script] = comments_body['comments']['en'].strip()

    return comments



def download_last_version():
    # URL_VERSION='https://dictionary.ieml.io/api/version'
    #
    # version = get(URL_VERSION).json()
    # # print("Downloading dictionary version {}".format(version))
    # # URL = 'https://dictionary.ieml.io/api/all?version={}'.format(version)
    # #
    # URL_INHIBITIONS = 'https://dictionary.ieml.io/api/relations/visibility?version={}&ieml='.format(version)
    all_d = get_last_version()


    translations = all_d['translations']
    comments = defaultdict(list)
    roots = all_d['roots']
    inhibitions = all_d['inhibitions']
    scripts = all_d['terms']

    # for s in :
    #     script = sc(s['IEML'], factorize=True)
        # assert s['IEML'] == str(script), "{} != {}".format(s['IEML'], str(script))

        # if s['ROOT_PARADIGM']:
        #     roots.append(script)
        #     # res = get(URL_INHIBITIONS + urllib.parse.quote_plus(str(s['IEML'])))
        #     # assert res.status_code == 200, res.text
        #     inhibitions[script] = [relation_name_table[i] for i in res.json()]

        # scripts.append(script)
        # translations['fr'][script] = s['FR']
        # translations['en'][script] = s['EN']


    # print(translations)
    return scripts, translations, roots, inhibitions, comments #download_comments(scripts)

def get_script_description(dictionary,desc, script):
    s = sc(script, factorize=True)
    if str(s) != str(script):
        print("Invalid factorisation for {} => {}".format(str(script), str(s)), file=sys.stderr)
    return {
        'ieml': str(s),
        'translations': {
            'fr': desc[script].translations['fr'],
            'en': desc[script].translations['en'],
        },
        'comments': {
            'fr': desc[script].comments['fr'],
            'en': desc[script].comments['en'],
        }
    }


def get_root_script_description(dictionary, desc, script):
    d = get_script_description(dictionary, desc, script)
    d['inhibitions'] = [re.sub(r'-', '_', r) for r in dictionary._inhibitions[script]]
    return d


def add_missing_foot_hand(ds, desc):

    root = sc("f.o.-f.o.-',n.i.-f.i.-',x.-O:.-',_M:.-',_;+f.o.-f.o.-',n.i.-f.i.-',x.-O:.-',_E:F:.-',_;", factorize=True)
    p0 =   sc("f.o.-f.o.-',n.i.-f.i.-',x.-A:.-',_M:.+E:F:.-',_;")
    p1 =   sc("f.o.-f.o.-',n.i.-f.i.-',x.-U:.-',_M:.+E:F:.-',_;")

    # print(str(root))
    assert p0 in root and p1 in root

    paradigms, inhibitions = ds.get(root)
    paradigms.extend([str(p0), str(p1)])
    ds.set_value(root, paradigms, inhibitions)
    # root_def = [s for s in ds.root_paradigms if s.root == root][0]
    # root_def.paradigms = sorted(set(root_def.paradigms) | {p0, p1})

    # old_trans = desc[script]['translations']
    # desc.set_value(p0, 'translations', 'fr', ['parties des pieds'])
    # desc.set_value(p0, 'translations', 'en', ['parts of the feet'])
    # desc.set_value(p1, 'translations', 'fr', ['parties des mains'])
    # desc.set_value(p1, 'translations', 'en', ['parts of the hands'])


def clean_up_translations(desc):

    all_d = desc.descriptors.iterrows()

    for (sc, l, k), (v,) in all_d:

        if k == 'translations':
            v_res = []
            for vv in v:
                for vvv in re.sub(r'\|', ',', vv).split(','):
                    vvv = re.sub(r'\s+', ' ', vvv)
                    vvv = vvv.strip()
                    if vvv not in v_res:
                        v_res.append(vvv)

            desc.set_value(sc, l, k, v_res)


def migrate(db, author_name, author_mail):
    db_folder = db.folder
    old_desc = db.descriptors()
    scripts, translations, roots, inhibitions, comments = download_last_version()#io_old._do_read_dictionary(db_folder=db_folder)

    scripts = sorted(set(sc(s, factorize=True) for s in scripts))
    roots = [sc(r, factorize=True) for r in roots]
    inhibitions = {sc(r, factorize=True): [re.sub('-', '_', rel) for rel in v] for r, v in inhibitions.items()}
    translations = {l: {s: [v[s]] for s in v} for l, v in translations.items()}
    comments = {l: {s: old_desc.get(s, l, 'comments') for s in scripts} for l in LANGUAGES}

    print(inhibitions)
    ds = DictionaryStructure.from_structure(scripts, roots, inhibitions)
    desc = DescriptorSet.build_descriptors(translations=translations, comments=comments)
    add_missing_foot_hand(ds, desc)
    clean_up_translations(desc)

    ds_f = os.path.join(db_folder, ds.file)
    desc_f = os.path.join(db_folder, desc.file)

    ds.write_to_file(ds_f)
    desc.write_to_file(desc_f)

    to_add = [*ds.file, *desc.file]

    with open(os.path.join(folder, 'version'), 'w') as fp:
        fp.write('0.2')

    db.save_changes(author_name, author_mail,
                    "[dictionary] Migrate to format v02",
                    to_add=to_add + ['version'],
                    to_remove=[],
                    check_coherency=True)

    # shutil.rmtree(os.path.join(db_folder, 'dictionary'))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('author_name', type=str)
    parser.add_argument('author_email', type=str)

    parser.add_argument('--folder', type=str)
    parser.add_argument('--github_username', type=str)
    parser.add_argument('--github_password', type=str)

    args = parser.parse_args()

    folder = args.folder

    db = IEMLDatabase(db_folder=folder)

    migrate(db, args.author_name, args.author_email)
