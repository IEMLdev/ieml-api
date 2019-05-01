from ieml.constants import LAYER_MARKS
from ieml.dictionary import Dictionary
from ieml.dictionary.script import Script, script
from ieml.dictionary.table import table_class, TableSet
from ieml.ieml_database.db_interface import Translations, Commentary, Inhibitions
from ieml.ieml_database.versions.ieml_database_io import IEMLDatabaseIO
import os
import yaml
import re

from typing import Dict, List

from ieml.ieml_database.versions.ieml_database_io import ScriptDescription, RootScriptDescription


def serialize_root_paradigm(dictionary: Dictionary, root: Script):
    paradigms = [e for e in dictionary.relations.object(root, 'contains') if len(e) != 1 and e != root]

    r = _serialize_root_paradigm(get_script_description(dictionary, root),
                                 dictionary._inhibitions[root],
                                 [get_script_description(dictionary, sc) for sc in root.singular_sequences],
                                 [get_script_description(dictionary, sc) for sc in paradigms])

    return r


class IEMLDatabaseIOv01(IEMLDatabaseIO):
    """
    Yaml version v0.1
    """

    version = "0.1"

    @staticmethod
    def _serialize_root_paradigm(root: RootScriptDescription,
                                 semes: List[ScriptDescription],
                                 paradigms: List[ScriptDescription]) -> str:
        res = """RootParadigm:
    ieml: "{}"
    translations:
        fr: |-
            {}
        en: |-
            {}
    inhibitions: {}
""".format(root['ieml'],
               _clean(root['translations']['fr']),
               _clean(root['translations']['en']),
               str(sorted(root['inhibitions'])))
        res += _comments(root, indent=1)

        # Semes
        if semes:
            res += "Semes:\n"
        for seme in semes:
            res += """    -   ieml: "{}"
        translations:
            fr: |-
                {}
            en: |-
                {}
""".format(seme['ieml'],
               _clean(seme['translations']['fr']),
               _clean(seme['translations']['en']))
            res += _comments(seme, indent=2)

        # Paradigms
        if paradigms:
            res += "Paradigms:\n"
        for paradigm in paradigms:
            res += """    -   ieml: "{}"
        translations:
            fr: |-
                {}
            en: |-
                {}
""".format(paradigm['ieml'],
               _clean(paradigm['translations']['fr']),
               _clean(paradigm['translations']['en']))
            res += _comments(paradigm, indent=2)

        return res

    @staticmethod
    def _get_dictionary_files(db_folder):
        dic_folder = os.path.join(db_folder, 'dictionary')
        return sorted(os.path.join(dic_folder, f) for f in os.listdir(dic_folder) if f.endswith('.yaml'))

    @staticmethod
    def _do_read_dictionary(db_folder):
        """
        Load a dictionary from a dictionary folder. The folder must contains a list of paradigms
        :param folder: The folder
        :param use_cache:
        :param cache_folder:
        :return:
        """
        scripts = []
        translations = {'fr': {}, 'en': {}}
        comments = {'fr': {}, 'en': {}}

        def _add_metadatas(ieml, c):
            translations['fr'][ieml] = c['translations']['fr'].strip()
            translations['en'][ieml] = c['translations']['en'].strip()
            if 'comments' in c:
                if 'fr' in c['comments']: comments['fr'][ieml] = c['comments']['fr'].strip()
                if 'en' in c['comments']: comments['en'][ieml] = c['comments']['en'].strip()

        roots = []
        inhibitions = {}

        n_ss = 0
        n_p = 0
        for f in IEMLDatabaseIOv01._get_dictionary_files(db_folder):
            with open(f) as fp:
                d = yaml.load(fp)

            try:
                root = d['RootParadigm']['ieml']
                inhibitions[root] = d['RootParadigm']['inhibitions']

                roots.append(root)

                _add_metadatas(root, d['RootParadigm'])
                scripts.append(root)

                if 'Semes' in d and d['Semes']:
                    for c in d['Semes']:
                        n_ss += 1
                        scripts.append(c['ieml'])
                        _add_metadatas(c['ieml'], c)

                if 'Paradigms' in d and d['Paradigms']:
                    for c in d['Paradigms']:
                        n_p += 1
                        scripts.append(c['ieml'])
                        _add_metadatas(c['ieml'], c)

            except (KeyError, TypeError):
                raise ValueError("'{}' is not a valid dictionary yaml file".format(f))

        return scripts, translations, roots, inhibitions, comments

    @staticmethod
    def _do_save_dictionary(db_folder, dictionary: Dictionary):
        # os.makedirs(db_folder, exist_ok=True)

        for root in dictionary.tables.roots:
            r = serialize_root_paradigm(dictionary, root)

            file_out = '{}_{}.yaml'.format(root.layer,
                                           re.sub('[^a-zA-Z0-9\-]+', '_', dictionary.translations[root].en))

            with open(os.path.join(os.path.join(db_folder, 'dictionary'), file_out), 'w') as fp:
                fp.write(r)

    @staticmethod
    def _do_read_lexicon(folder):
        raise NotImplementedError


    @classmethod
    def write_morpheme_root_paradigm(cls, db_folder:str,
                                      root_description,
                                      ss_description,
                                      p_description):

        r = cls._serialize_root_paradigm(root_description,
                                         ss_description,
                                         p_description)

        layer = LAYER_MARKS.index(root_description['ieml'][-1])
        fname = re.sub('[^a-zA-Z0-9\-]+', '_', root_description['translations']['en'])

        file_out = os.path.join('dictionary', '{}_{}.yaml'.format(layer, fname))

        with open(os.path.join(db_folder, file_out), 'w') as fp:
            fp.write(r)

        return [file_out]

    @classmethod
    def delete_morpheme_root_paradigm(cls, db_folder:str, root_description: RootScriptDescription):
        layer = LAYER_MARKS.index(root_description['ieml'][-1])
        fname = re.sub('[^a-zA-Z0-9\-]+', '_', root_description['translations']['en'])
        file_out = os.path.join('dictionary', '{}_{}.yaml'.format(layer, fname))
        os.remove(os.path.join(db_folder, file_out))
        return [file_out]
    #
    # def update_morpheme_translation(cls, db_folder:str, root_description:RootScriptDescription, script: ScriptDescription):
    #     layer = LAYER_MARKS.index(root_description['ieml'][-1])
    #     fname = re.sub('[^a-zA-Z0-9\-]+', '_', root_description['translations']['en'])
    #     file_out = os.path.join('dictionary', '{}_{}.yaml'.format(layer, fname))
    #


    # @classmethod
    # def set_morpheme_translation(cls, db_folder: str, script: Script, translation: Translation):
    #     d = cls.read_dictionary(db_folder)
    #     root = d.tables.root(script)
    #     file_out = '{}_{}.yaml'.format(root.layer,
    #                                    re.sub('[^a-zA-Z0-9\-]+', '_', d.translations[root]['en']))
    #
    #     root_d = get_script_description(d, root)
    #     paradigms = [e for e in d.relations.object(root, 'contains') if len(e) != 1 and e != root and e != script]
    #     para_d = {sc: get_script_description(d, sc) for sc in paradigms}
    #     ss_d = {sc: get_script_description(d, sc) for sc in root.singular_sequences}
    #
    #     if script in d.tables.roots:
    #         root_d['translations'] = translation
    #     elif script.cardinal != 1:
    #         para_d[script]['translations'] = translation
    #     else:
    #         ss_d[script]['translations'] = translation
    #
    #     r = _serialize_root_paradigm(root_d,
    #                                  d._inhibitions[root],
    #                                  list(ss_d.values()),
    #                                  list(para_d.values()))
    #
    #     with open(os.path.join(os.path.join(db_folder, 'dictionary'), file_out), 'w') as fp:
    #         fp.write(r)
    #
    # @classmethod
    # def set_morpheme_comments(cls, db_folder: str, script: Script, comments: Commentary):
    #     d = cls.read_dictionary(db_folder)
    #     root = d.tables.root(script)
    #     file_out = '{}_{}.yaml'.format(root.layer,
    #                                    re.sub('[^a-zA-Z0-9\-]+', '_', d.translations[root]['en']))
    #
    #     root_d = get_script_description(d, root)
    #     paradigms = [e for e in d.relations.object(root, 'contains') if len(e) != 1 and e != root and e != script]
    #     para_d = {sc: get_script_description(d, sc) for sc in paradigms}
    #     ss_d = {sc: get_script_description(d, sc) for sc in root.singular_sequences}
    #
    #     if script in d.tables.roots:
    #         root_d['comments'] = comments
    #     elif script.cardinal != 1:
    #         para_d[script]['comments'] = comments
    #     else:
    #         ss_d[script]['comments'] = comments
    #
    #     r = _serialize_root_paradigm(root_d,
    #                                  d._inhibitions[root],
    #                                  list(ss_d.values()),
    #                                  list(para_d.values()))
    #
    #     with open(os.path.join(os.path.join(db_folder, 'dictionary'), file_out), 'w') as fp:
    #         fp.write(r)
    #
    #
    # @classmethod
    # def set_morpheme_root_paradigm_inhibitions(cls,
    #                                            db_folder: str,
    #                                            script: Script,
    #                                            inhibitions: Inhibitions):
    #     d = cls.read_dictionary(db_folder)
    #
    #     file_out = '{}_{}.yaml'.format(script.layer,
    #                                    re.sub('[^a-zA-Z0-9\-]+', '_', d.translations[script]['en']))
    #
    #     paradigms = [e for e in d.relations.object(script, 'contains') if len(e) != 1 and e != script]
    #     root_d = get_script_description(d, script)
    #     root_d['inhibitions'] = inhibitions
    #
    #     r = _serialize_root_paradigm(root_d,
    #                                  d._inhibitions[script],
    #                                  [get_script_description(d, sc) for sc in script.singular_sequences],
    #                                  [get_script_description(d, sc) for sc in paradigms])
    #
    #     with open(os.path.join(os.path.join(db_folder, 'dictionary'), file_out), 'w') as fp:
    #         fp.write(r)


# ScriptDescription = Dict[str, str]


PAD = '    '


def _clean(s, indent=3):
    indentation = PAD * indent
    s = re.sub('\n\s*', '\n' + indentation, s.strip())
    return s


def _comments(s, indent=1):
    res = ''
    if 'comments' in s and (('fr' in s['comments'] and s['comments']['fr']) or
                            ('en' in s['comments'] and s['comments']['en'])):
        res += PAD * indent + 'comments:\n'

        if 'fr' in s['comments'] and s['comments']['fr']:
            res += PAD * (indent + 1) + 'fr: |-\n'
            res += PAD * (indent + 2) + _clean(s['comments']['fr'], indent=(indent + 2)) + '\n'
        if 'en' in s['comments'] and s['comments']['en']:
            res += PAD * (indent + 1) + 'en: |-\n'
            res += PAD * (indent + 2) + _clean(s['comments']['en'], indent=(indent + 2)) + '\n'

    return res




def normalize_dictionary_file(file, expand_root=False):
    with open(file) as fp:
        d = yaml.load(fp)

    d['Semes'] = d['Semes'] if 'Semes' in d and d['Semes'] else []
    d['Paradigms'] = d['Paradigms'] if 'Paradigms' in d and d['Paradigms'] else []
    d['RootParadigm']['inhibitions'] = d['RootParadigm']['inhibitions'] \
        if 'inhibitions' in d['RootParadigm'] and d['RootParadigm']['inhibitions'] else []

    script_root = script(d['RootParadigm']['ieml'])
    semes_root = {str(ss): ss for ss in script_root.singular_sequences}
    semes_file = {ss['ieml']: ss for ss in d['Semes']}
    paradigms_file = {p['ieml']: p for p in d['Paradigms']}

    if expand_root:
        # remove extra semes
        to_remove = set()
        for ss in d['Semes']:
            if ss['ieml'] not in semes_root:
                to_remove.add(ss['ieml'])

        d['Semes'] = [ss for ss in d['Semes'] if ss['ieml'] not in to_remove]

        # add missing semes
        for ss in set(semes_root) - set(semes_file):
            d['Semes'].append({'ieml': ss, 'translations': {'fr': "", 'en': ""}})

        # add table set paradigms
        table_root = table_class(script_root)(script_root, None)
        if isinstance(table_root, TableSet):
            paradigms = {str(t): t for t in table_root.tables}

            # add missing tables
            for ss in set(paradigms) - set(paradigms_file):
                d['Paradigms'].append({'ieml': ss, 'translations': {'fr': "", 'en': ""}})

    d['Semes'] = sorted(d['Semes'], key=lambda ss: semes_root[ss['ieml']])
    d['Paradigms'] = sorted(d['Paradigms'], key=lambda ss: script(ss['ieml']))

    r = _serialize_root_paradigm(d['RootParadigm'],
                                 d['RootParadigm']['inhibitions'],
                                 d['Semes'],
                                 d['Paradigms'])

    return r


# def normalize_dictionary_folder(folder=DICTIONARY_FOLDER, expand_root=False):
#     for f in get_dictionary_files(folder=folder):
#         r = normalize_dictionary_file(f, expand_root=expand_root)
#
#         with open(f) as fp:
#             r_old = fp.read()
#             if r_old == r:
#                 continue
#
#         print("Normalizing {}".format(f))
#
#         with open(f, 'w') as fp:
#             fp.write(r)


# def serialize_root_paradigm(dictionary: Dictionary, root: Script):
#     paradigms = [e for e in dictionary.relations.object(root, 'contains') if len(e) != 1 and e != root]
#
#     r = _serialize_root_paradigm(get_script_description(dictionary, root),
#                                  dictionary._inhibitions[root],
#                                  [get_script_description(dictionary, sc) for sc in root.singular_sequences],
#                                  [get_script_description(dictionary, sc) for sc in paradigms])
#
#     return r


def serialize_dictionary(dictionary: Dictionary, output_path: str):
    os.makedirs(output_path, exist_ok=True)

    for root in dictionary.tables.roots:
        r = serialize_root_paradigm(dictionary, root)

        file_out = '{}_{}.yaml'.format(root.layer,
                                       re.sub('[^a-zA-Z0-9\-]+', '_', dictionary.translations[root].en))

        with open(os.path.join(output_path, file_out), 'w') as fp:
            fp.write(r)
