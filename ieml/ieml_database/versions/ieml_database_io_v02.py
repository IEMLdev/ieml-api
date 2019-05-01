from collections import defaultdict

from ieml.constants import INHIBITABLE_RELATIONS, LANGUAGES
# from ieml.descriptor.descriptor import DescriptorSet
from ieml.dictionary import Dictionary
from ieml.dictionary.script import script
from ieml.exceptions import CannotParse
from ieml.ieml_database.versions.ieml_database_io import IEMLDatabaseIO, RootScriptDescription, ScriptDescription
from typing import List
import os
import re
from glob import glob

class IEMLDatabaseIOv02(IEMLDatabaseIO):
    """
    Separate the descriptors and the structure of the dictionary

    ** Dictionary
        - structure files:
        filename: {layer}_{root script}.txt
        'root: <script>
         inhibitions: <space separated relations name>
         paradigms: <space separated script>'

        - descriptor files:
        filename: {layer}_{root script}.txt
        '<script> <translation> <translation>...'

        '


    """


    version = "0.2"

    @staticmethod
    def _fname(script):
        """Remove forbidden characters"""
        return '{}_{}.txt'.format(script.layer, re.sub(':', '_', str(script)))

    @staticmethod
    def _get_dictionary_files(db_folder):
        d_path = os.path.join(db_folder, 'dictionary', 'structure')
        return [os.path.join(d_path, f) for f in os.listdir(d_path)]

    @staticmethod
    def _get_descriptors_files(db_folder):
        d_path = os.path.join(db_folder, 'dictionary', 'descriptors')
        return [os.path.join(d_path, f) for f in glob(d_path + '/**/', recursive=True) if os.path.isfile(os.path.join(d_path, f))]

    @staticmethod
    def _do_read_descriptors(db_folder):
        descriptors = {}
        for k in ['comments', 'translations']:
            descriptors[k] = {}
            for l in LANGUAGES:
                descriptors[k][l] = {}

                f_path = os.path.join(db_folder, 'dictionary', 'descriptors', l, k)

                for f in os.listdir(f_path):
                    _desc = IEMLDatabaseIOv02._do_read_descriptor_file(os.path.join(f_path, f))
                    descriptors[k][l] = {
                        **descriptors[k][l],
                        **_desc
                    }

        return DescriptorSet(**descriptors)

    @staticmethod
    def _do_read_descriptor_file(dfile):
        descriptors = defaultdict(list)
        with open(dfile) as fp:
            for line in fp:
                try:
                    sc, trans = line.strip().split(' ', 1)
                except ValueError:
                    continue
                for t in re.findall(r'("(?:""|[^"])+")', trans):
                    t = re.sub(r'""', '"', t[1:-1])

                    descriptors[sc].append(t)

        return dict(descriptors)

    @staticmethod
    def _do_write_descriptor_file(dfile, descriptors):
        with open(dfile, 'w') as fp:
            for sc in sorted(descriptors):
                trans = descriptors[sc]
                fp.write("{} {}\n".format(str(sc), ' '.join('"{}"'.format(re.sub('"', '""', t)) for t in trans)))


    @staticmethod
    def _do_read_dictionary(db_folder):
        scripts, roots, inhibitions = [], [], {}

        for f in IEMLDatabaseIOv02._get_dictionary_files(db_folder):
            with open(f) as fp:
                # first line "root: <scritp>"
                line = fp.readline()
                prefix, s = line.split(' ')
                assert prefix.strip() == 'root:'
                root = script(s.strip())
                assert root.cardinal != 1

                # second line "inhibitions: <space separated relations>"
                line = fp.readline()
                prefix, rels = line.split(' ', 1)
                assert prefix.strip() == 'inhibitions:'
                rels = re.sub('\s+', ' ', rels).strip()

                _inhibitions = [r.strip() for r in rels.split(' ') ] if rels else []
                assert all(i in INHIBITABLE_RELATIONS for i in _inhibitions), _inhibitions

                # third line "paradigms: <space separated scripts>"
                line = fp.readline()
                prefix, ps = line.split(' ', 1)
                assert prefix.strip() == 'paradigms:'
                ps = re.sub('\s+', ' ', ps).strip()
                if ps:
                    paradigms = [script(p.strip()) for p in ps.split(' ')]
                else:
                    paradigms = []

                assert all(p in root and p.cardinal != 1 for p in paradigms)

                roots.append(root)
                scripts.extend(root.singular_sequences)
                scripts.extend(paradigms)
                scripts.append(root)
                inhibitions[root] = _inhibitions

        # descriptors = IEMLDatabaseIOv02._do_read_descriptors(db_folder)

        return scripts, roots, inhibitions

    @staticmethod
    def _do_read_lexicon(folder):
        raise NotImplementedError

    @classmethod
    def _do_write_morpheme_root_paradigm_structure_file(cls,
                                                        db_folder:str,
                                                        root_description: RootScriptDescription,
                                                        p_description: List[ScriptDescription]):

        root = script(root_description['ieml'])
        fname = os.path.join(db_folder, 'dictionary', 'structure', cls._fname(root))

        with open(fname, 'w') as fp:
            fp.write("root: {}\n".format(str(root)))
            fp.write("inhibitions: {}\n".format(' '.join(sorted(root_description['inhibitions']))))
            fp.write("paradigms: {}".format(' '.join(p['ieml'] for p in sorted(p_description, key=lambda e: script(e['ieml'])))))

        return os.path.join('dictionary', 'structure', cls._fname(root))

    @classmethod
    def write_morpheme_root_paradigm(cls,
                                     db_folder:str,
                                     root_description: RootScriptDescription,
                                     ss_description: List[ScriptDescription],
                                     p_description: List[ScriptDescription]):

        files = [cls._do_write_morpheme_root_paradigm_structure_file(db_folder, root_description, p_description)]

        root = script(root_description['ieml'])

        for d in ['translations', 'comments']:
            for l in LANGUAGES:
                fname = os.path.join(db_folder, 'dictionary', 'descriptors', l, d, cls._fname(root))

                _desc = {
                    str(root): root_description[d][l],
                    **{p['ieml']: p[d][l] for p in p_description},
                    **{ss['ieml']: ss[d][l] for ss in ss_description},
                }
                files.append(os.path.join('dictionary', 'descriptors', l, d, cls._fname(root)))
                cls._do_write_descriptor_file(fname, _desc)


        return files


    @classmethod
    def delete_morpheme_root_paradigm(cls,
                                      db_folder:str,
                                      root_description: RootScriptDescription):

        root = script(root_description['ieml'])
        # delete structure
        os.remove(os.path.join(db_folder, 'dictionary', 'structure', cls._fname(root)))

        # delete descriptors
        for l in LANGUAGES:
            for d in ['translations', 'comments']:
                os.remove(os.path.join(db_folder, 'dictionary', 'descriptors', l, d, cls._fname(script(root['script']))))



    @classmethod
    def update_morpheme_translation(cls, db_folder:str, root:RootScriptDescription, script: ScriptDescription):
        for l in LANGUAGES:
            fname = os.path.join(db_folder, 'dictionary', 'descriptors', l, 'translations', cls._fname(script(root['script'])))
            _desc = cls._do_read_descriptor_file(fname)
            _desc[script['ieml']] = script['translations'][l]
            cls._do_write_descriptor_file(fname, _desc)


    @classmethod
    def update_morpheme_comments(cls, db_folder:str, root:RootScriptDescription, script: ScriptDescription):
        for l in LANGUAGES:
            fname = os.path.join(db_folder, 'dictionary', 'descriptors', l, 'comments', cls._fname(script(root['script'])))
            _desc = cls._do_read_descriptor_file(fname)
            _desc[script['ieml']] = script['comments'][l]
            cls._do_write_descriptor_file(fname, _desc)
