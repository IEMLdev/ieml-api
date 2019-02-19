from typing import List, Union
from collections import defaultdict
import yaml
import os

from ieml.constants import LANGUAGES
from ieml.lexicon.grammar import usl, Word
from ieml.lexicon.relations.lattice_sctrucure import LatticeStructure


class MultiTranslations:
    def __init__(self, fr: List[str], en: List[str]):
        self.fr = list(fr)
        self.en = list(en)

    def __getitem__(self, item):
        if item in LANGUAGES:
            return getattr(self, item)

        raise KeyError("Unknown language {}".format(item))


class Lexicon:
    @classmethod
    def load(cls, root_folder: str, names: Union[List[str], None] = None):
        if names is None:
            # add all
            names = os.listdir(root_folder)

        usls = []
        translations = {}
        metadatas = {}
        for n in names:
            name = os.path.join(root_folder, n)

            if os.path.isdir(name):
                files = [os.path.join(name, f) for f in os.listdir(name)]
            else:
                files = [name]

            files = [os.path.abspath(f) for f in files]

            for file in files:
                with open(file) as fp:
                    file_cnt = yaml.load(fp)

                words = file_cnt['Words'] if file_cnt['Words'] else []

                for w in words:
                    u = usl(w['ieml'])

                    translations[u] = {}
                    for l in LANGUAGES:
                        translations[u][l] = w['translations'][l] if l in w['translations'] and w['translations'][l] \
                            else []

                    folder = os.path.basename(os.path.dirname(file))
                    _file = os.path.basename(file)
                    metadatas[u] = {'path': _file,
                                    'name': os.path.join(folder, _file),
                                    'folder': folder,
                                    'file': _file}

                    # metadatas[u]['file'] = file

                    usls.append(u)

        lexicon = Lexicon(usls=usls, translations=translations, metadatas=metadatas)
        return lexicon

    @property
    def names(self):
        return sorted(set(u['folder'] + '/' + u['file'] for u in self.metadatas.values()))

    def __init__(self, usls, translations, metadatas):
        # self.root_folder = root_folder

        self.usls = sorted(usls)

        self.words = [u for u in self.usls if isinstance(u, Word)]
        self.translations = translations
        self.metadatas = metadatas
        assert all(w in self.translations and w in self.metadatas for w in self.words)

        self.inv_translations = {l: defaultdict(list) for l in LANGUAGES}
        for l in LANGUAGES:
            for u in self.usls:
                for trs in self.translations[u][l]:
                    self.inv_translations[l][trs].append(u)

        self.lattice = LatticeStructure(self.words)

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




if __name__ == '__main__':
    file = '/home/louis/code/ieml/ieml-dictionary/definition/lexicons/eau/ms_qualite_de_l_eau.yaml'
    lexicon = Lexicon.load()

    print(list(lexicon.inv_translations['fr']))
    for w in lexicon.words:
        lexicon.display(w)
        print(flush=True)
        # if w.cardinal == 1:
        #     print(lexicon.metadatas[w])

        # print(list(lexicon.inv_translations['fr']))
        # print(w, id(w), w.singular_sequences)
        # if not lexicon.lattice[w].parents:
        #     continue
        # lexicon.display(w)
        # print('*'*80)
        # print(w, "parents:" )
        # for p in lexicon.lattice[w].parents:
        #     print('\t', p)
    # for u in lexicon.usls:
    #     print(str(u), lexicon.translations[u])
