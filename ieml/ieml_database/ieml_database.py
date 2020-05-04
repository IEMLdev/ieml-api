import logging
import operator
from collections import defaultdict
from shlex import quote
from sys import stdout

import pandas
from functools import reduce

import os
import json
from hashlib import sha224
import subprocess

import sys

from pandas.errors import ParserError, EmptyDataError
from tqdm import tqdm

from ieml import error
from ieml.commons import monitor_decorator, cache_results_watch_files
from ieml.constants import INHIBITABLE_RELATIONS, STRUCTURE_KEYS, GRAMMATICAL_CLASS_NAMES, \
    TYPES, LANGUAGES, DESCRIPTORS_CLASS
from ieml.dictionary.dictionary import Dictionary
from ieml.dictionary.script import NullScript, MultiplicativeScript, AdditiveScript, Script
from ieml.exceptions import CannotParse
from ieml.ieml_database.descriptors import Descriptors, normalize_key
from ieml.ieml_database.git_interface import logger
from ieml.usl.decoration.instance import InstancedUSL
from ieml.usl.lexeme import Lexeme
from ieml.usl.parser import IEMLParser
from ieml.usl import PolyMorpheme, Word, get_index



def _normalize_value(value):
    if not isinstance(value, str):
        raise ValueError("Expected a string, not a {}".format(value.__class__.__name__))

    # TODO normalize accent encoding
    return value.strip()


def _normalize_inhibitions(inhibitions):
    return inhibitions


class Structure:
    def __init__(self, df):
        assert list(df.columns) == ['ieml', 'key', 'value']
        self.df = df.set_index(['ieml', 'key']).sort_index()

    @monitor_decorator('get_structure_values')
    def get_values(self, ieml, key):
        ieml, key, _ = normalize_key(ieml, key, None, parse_ieml=False, partial=False, structure=True)

        try:
            return self.df.loc(axis=0)[(ieml, key)].to_dict('list')['value']
        except KeyError:
            return []

    @monitor_decorator('get_values_partial')
    def get_values_partial(self, ieml, key=None):
        ieml, key, _ = normalize_key(ieml, key, None, parse_ieml=False, partial=True, structure=True)

        key = {'ieml': ieml, 'key': key}
        key = reduce(operator.and_,
                     [self.df.index.get_level_values(k) == v for k, v in key.items() if v is not None],
                     True)

        res = defaultdict(list)
        for k, (v,) in self.df[key].iterrows():
            res[k].append(v)

        return dict(res)


class IEMLDatabase:
    CLASS_TO_FOLDER={
        NullScript: ('morpheme', 0),
        AdditiveScript: ('morpheme', 0),
        MultiplicativeScript: ('morpheme', 0),
        PolyMorpheme: ('polymorpheme', 5),
        Lexeme: ('lexeme', 8),
        Word: ('word', 10)
    }

    MAX_IEML_NAME_SIZE = 100
    HASH_SIZE = 10

    def __init__(self, folder,
                 cache_folder=None,
                 use_cache=True):
        self.folder = folder

        self.use_cache = use_cache
        self.cache_folder = cache_folder
        if self.use_cache:
            if cache_folder is None:
                self.cache_folder = self.folder
            elif not os.path.isdir(self.cache_folder):
                os.makedirs(self.cache_folder)
                # raise ValueError("Folder '{}' does not exists.".format(self.cache_folder))
        else:
            self.cache_folder = None

    def __str__(self):
        return "<{} ({} cache={})>".format(self.__module__, self.folder, self.cache_folder)


    def filename_of(self, ieml):
        l = str(ieml)
        if len(l) > self.MAX_IEML_NAME_SIZE:
            l = "{}|{}".format(l[:self.MAX_IEML_NAME_SIZE - self.HASH_SIZE - 1],
                               sha224(l.encode('utf8')).hexdigest()[:self.HASH_SIZE])
        return l

    def path_of(self, _ieml, descriptor=True, mkdir=False, normalize=True):
        if isinstance(_ieml, str):
            ieml = IEMLParser().parse(_ieml)
        else:
            ieml = _ieml

        if descriptor:
            ext = '.desc'
        else:
            ext = '.ieml'

        if isinstance(ieml, InstancedUSL):
                class_folder, prefix_sixe = self.CLASS_TO_FOLDER[ieml.usl.__class__]
        else:
            class_folder, prefix_sixe = self.CLASS_TO_FOLDER[ieml.__class__]

        if normalize:
            filename = self.filename_of(ieml)
        else:
            filename = self.filename_of(_ieml)

        prefix = filename[:prefix_sixe]

        p = os.path.join(self.folder, class_folder,
                         'singular' if len(ieml) == 1 else 'paradigm', prefix)
        if mkdir:
            os.makedirs(p, exist_ok=True)

        return os.path.join(p, filename + ext)

    @monitor_decorator("list content")
    def list(self, type=None, paradigm=None, parse=False, ):
        p = self.folder
        if type:
            if not isinstance(type, str):
                type = type.__name__.lower()
            p = os.path.join(p, type)
            if paradigm is not None:
                p = os.path.join(p, 'paradigm' if paradigm else 'singular')

        p1 = subprocess.Popen("find -path *.desc -print0".split(), stdout=subprocess.PIPE, cwd=p)
        p2 = subprocess.Popen("xargs -0 cat".split(), stdin=p1.stdout, stdout=subprocess.PIPE, cwd=p)
        p3 = subprocess.Popen(["cut", "-f2", '-d', '"'], stdin=p2.stdout, stdout=subprocess.PIPE, cwd=p)
        p4 = subprocess.Popen(["uniq"], stdin=p3.stdout, stdout=subprocess.PIPE, cwd=p)

        res = [s.strip().decode('utf8') for s in p4.stdout.readlines() if s.strip()]

        if parse:
            parser = IEMLParser(dictionary=self.get_dictionary())
            _res = []
            for s in res:
                try:
                    _res.append(parser.parse(s))
                except CannotParse as e:
                    error("Cannot parse {} : {}".format(s, repr(e)))
            return _res

        return res

    def _process_line(self, lines_iter, parse=False):

        if parse:
            parser = IEMLParser(dictionary=self.get_dictionary())

        for l in lines_iter:
            if not l.strip():
                continue

            l = l.strip().decode('utf8')
            if parse:
                return parser.parse(l)
            else:
                return l


    @monitor_decorator("Get descriptors")
    def get_descriptors(self, files_list=None):
        if files_list is not None:
            p1 = subprocess.Popen(['echo', '-ne', r'\0'.join(files_list)],
                                  stdout=subprocess.PIPE, cwd=self.folder)
            # p1 = subprocess.Popen(['sed', '-e', r's/\n/\x0/g'], stdin=p0.stdout,
            #                       stdout=subprocess.PIPE, cwd=self.folder)
        else:
            p1 = subprocess.Popen("find -path *.desc -print0".split(),
                                  stdout=subprocess.PIPE, cwd=self.folder)

        p2 = subprocess.Popen("xargs -0 cat".split(), stdin=p1.stdout, stdout=subprocess.PIPE, cwd=self.folder)
        try:
            r = pandas.read_csv(p2.stdout, sep=' ', header=None)
            r.columns=['ieml', 'language', 'descriptor', 'value']
        except EmptyDataError:
            r = pandas.DataFrame(columns=['ieml', 'language', 'descriptor', 'value'])

        return Descriptors(r)

    @monitor_decorator("Get structure")
    def get_structure(self):
        p1 = subprocess.Popen("find -path *.ieml -print0".split(), stdout=subprocess.PIPE, cwd=self.folder)
        p2 = subprocess.Popen("xargs -0 cat".split(), stdin=p1.stdout, stdout=subprocess.PIPE, cwd=self.folder)
        r = pandas.read_csv(p2.stdout, sep=' ', header=None)
        r.columns = ['ieml', 'key', 'value']
        return Structure(r)

    @monitor_decorator("Get dictionary")
    @cache_results_watch_files("morpheme/paradigm/*", 'dictionary')
    def get_dictionary(self):
        return Dictionary(self.list('morpheme', paradigm=True), self.get_structure())

    @monitor_decorator("Get list of all usls")
    @cache_results_watch_files("morpheme/*/*.desc", 'all_usls')
    def get_list(self):
        res = {}
        dictionary = self.get_dictionary()
        parser = IEMLParser(dictionary=dictionary)

        for (ieml, lang, desc), (v,) in tqdm(self.get_descriptors().df.iterrows(),
                                             "List all descriptors at {}".format(self.folder)):
            if ieml not in res:
                try:
                    pieml = parser.parse(ieml)
                except CannotParse:
                    continue

                assert str(pieml) == ieml
                i, r = get_index(pieml, dictionary)
                if i == 0 and isinstance(pieml, PolyMorpheme):
                    pieml = pieml.constant[0]
                res[ieml] = {'ieml': str(pieml),
                             'type': TYPES[i],
                             'paradigm': len(pieml) != 1,
                             'class': GRAMMATICAL_CLASS_NAMES[pieml.grammatical_class].lower().capitalize(),
                             'index': r,
                             'cardinality': 'singular_sequence' if pieml.cardinal == 1 else \
                                 ('paradigm' if not isinstance(pieml,
                                                               Script) or pieml not in dictionary.tables.roots
                                 else 'root_paradigm'),
                             'domains': []
                             }
            if desc not in res[ieml]:
                res[ieml][desc] = {l: [] for l in LANGUAGES}

            res[ieml][desc][lang].append(v)

        return sorted(res.values(), key=lambda e: e['index'])

    def add_descriptor(self, ieml, language, descriptor, value):
        ieml, language, descriptor = normalize_key(ieml, language, descriptor,
                                                   parse_ieml=True, partial=False)
        value = _normalize_value(value)
        if not value:
            return

        with open(self.path_of(ieml, mkdir=True), 'a', encoding='utf8') as fp:
            fp.write('"{}" {} {} "{}"\n'.format(
                self.escape_value(str(ieml)),
                language,
                descriptor,
                self.escape_value(value)))

    @monitor_decorator('remove_key')
    def remove_descriptor(self, ieml, language=None, descriptor=None, value=None, normalize=True):
        ieml, language, descriptor = normalize_key(ieml, language, descriptor,
                                                   parse_ieml=True, partial=True)

        path = self.path_of(ieml, mkdir=True, normalize=normalize)
        if not os.path.isfile(path):
            return

        if descriptor is None and language is None and value is None:
            os.remove(path)
            return

        if descriptor is None or language is None:
            if language is None:
                for l in LANGUAGES:
                    self.remove_descriptor(ieml, l, descriptor)
            else:
                for d in DESCRIPTORS_CLASS:
                    self.remove_descriptor(ieml, language, d)
            return

        if value:
            value = _normalize_value(value)

        with open(path, "r", encoding='utf8') as f:
            lines = [l for l in f.readlines()
                     if not l.startswith('"{}" {} {} '.format(str(ieml), language, descriptor) + \
                                        ('"{}"'.format(self.escape_value(value)) if value is not None else ''))]

        with open(path, "w", encoding='utf8') as f:
            f.writelines(lines)

    def add_structure(self, ieml, key, value):
        ieml, key, value = normalize_key(ieml, key, value, parse_ieml=True, partial=False, structure=True)

        with open(self.path_of(ieml, descriptor=False, mkdir=True), 'a', encoding='utf8') as fp:
            fp.write('"{}" {} "{}"\n'.format(str(ieml), key, value))

    def remove_structure(self, ieml, key=None, value=None, normalize=True):
        ieml, key, value = normalize_key(ieml, key, value, parse_ieml=True, partial=True, structure=True)

        path = self.path_of(ieml, descriptor=False, mkdir=True, normalize=normalize)

        if not os.path.isfile(path):
            return

        if key is None:
            os.remove(path)
            return

        with open(path, "r", encoding='utf8') as f:
            lines = [l for l in f.readlines()
                     if not l.startswith('"{}" {} '.format(str(ieml), key) + \
                                        ('"{}"'.format(value) if value else ''))]

        with open(path, "w", encoding='utf8') as f:
            f.writelines(lines)

    def escape_value(self, v):
        return v.replace('"', '""').replace('\n', '\\n')
