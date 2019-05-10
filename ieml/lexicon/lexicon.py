from typing import List, Union
from collections import defaultdict
from ieml.dictionary import Dictionary
from ieml.ieml_database.lexicon.lexicon_structure import LexiconStructure
from ieml.lexicon.grammar.parser2 import IEMLParser
from ieml.lexicon.relations.lattice_sctrucure import LatticeStructure


class Lexicon:
    # @classmethod
    # def load(cls, root_folder: str, names: Union[List[str], None] = None):
    #     if names is None:
    #         # add all
    #         names = os.listdir(root_folder)
    #
    #     usls = []
    #     translations = {}
    #     metadatas = {}
    #     for n in names:
    #         name = os.path.join(root_folder, n)
    #
    #         if os.path.isdir(name):
    #             files = [os.path.join(name, f) for f in os.listdir(name)]
    #         else:
    #             files = [name]
    #
    #         files = [os.path.abspath(f) for f in files]
    #
    #         for file in files:
    #             with open(file) as fp:
    #                 file_cnt = yaml.load(fp)
    #
    #             words = file_cnt['Words'] if file_cnt['Words'] else []
    #
    #             for w in words:
    #                 u = usl(w['ieml'])
    #
    #                 translations[u] = {}
    #                 for l in LANGUAGES:
    #                     translations[u][l] = w['translations'][l] if l in w['translations'] and w['translations'][l] \
    #                         else []
    #
    #                 folder = os.path.basename(os.path.dirname(file))
    #                 _file = os.path.basename(file)
    #                 metadatas[u] = {'path': _file,
    #                                 'name': os.path.join(folder, _file),
    #                                 'folder': folder,
    #                                 'file': _file}
    #
    #                 # metadatas[u]['file'] = file
    #
    #                 usls.append(u)
    #
    #     lexicon = Lexicon(usls=usls, translations=translations, metadatas=metadatas)
    #     return lexicon
    #
    # @property
    # def names(self):
    #     return sorted(set(u['folder'] + '/' + u['file'] for u in self.metadatas.values()))

    def __init__(self, lexicon_structure: LexiconStructure,  dictionary: Dictionary, descriptors):
        self.structure = lexicon_structure
        paradigms_to_ss, singular_sequences, paradigms_to_domain = self.define_singular_sequences(dictionary, descriptors)

        self.paradigms = tuple(sorted(paradigms_to_ss))
        self.singular_sequences = tuple(sorted(singular_sequences))
        self.paradigms_to_domain = paradigms_to_domain
        self.items = tuple(sorted(self.paradigms + self.singular_sequences))

        self.lattice = LatticeStructure(self.items)

    def define_singular_sequences(self, dictionary, descriptors):
        parser = IEMLParser(dictionary=dictionary)

        paradigms_to_ss = defaultdict(list)
        paradigms_to_domain = {}

        singular_sequences = set()
        for (ieml), (domain) in self.structure:
            paradigm = parser.parse(ieml)
            assert len(paradigm) != 1

            paradigms_to_domain[paradigm] = domain

            for ss in paradigm.singular_sequences:
                if descriptors.is_defined(ss):
                    if ss not in singular_sequences:
                        singular_sequences.add(ss)

                    paradigms_to_ss[paradigm].append(ss)

        return paradigms_to_ss, singular_sequences, paradigms_to_domain

    @staticmethod
    def get_contains(item, desc):
        contains = []
        for ss in item.singular_sequences:
            if desc.get(ss):
                contains.append(ss)

        return contains

    def display(self, u, metadatas=True, parents=True, descendents=True, recurse=True, indent=0):
        def _print(*e):
            print('\t'*indent, *e)

        def _display(e, ind):
            if recurse:
                self.display(e, metadatas=False, parents=False, indent=indent + ind, recurse=False)
            else:
                _print("ieml:", e)

        _print("ieml:", u)
        if not u in self.usls:
            _print(" ! not defined in lexicon")
        else:
            _print("*translations:")
            for l, keys in self.translations[u].items():
                _print("  ", l, ':')
                for k in keys:
                    _print('\t>', k)

            if metadatas:
                _print("*metadatas:")
                for m, key in self.metadatas[u].items():
                    _print('\t',m , ':', key)

        if parents:
            _print("*parents:")
            for p in self.lattice[u].parents:
                _display(p, 1)

            _print("*child:")
            for p in self.lattice[u].child:
                _display(p, 1)

        if descendents:
            _print("*descendents:")
            for p in self.lattice[u].descendents:
                _display(p, 1)

            _print("*ancestors:")
            for p in self.lattice[u].ancestors:
                _display(p, 1)

