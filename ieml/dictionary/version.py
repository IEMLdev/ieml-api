import copy
import logging
import pickle
from functools import lru_cache
from urllib.request import urlretrieve
import datetime
import urllib.parse
import json
import os
import re

from collections import defaultdict

from ieml.constants import LAYER_MARKS
from ieml.dictionary.relations import RelationsGraph
from .. import get_configuration, ieml_folder
from ..constants import LANGUAGES

logger = logging.getLogger(__name__)
VERSIONS_FOLDER = os.path.join(ieml_folder, get_configuration().get('VERSIONS', 'versionsfolder'))

if not os.path.isdir(VERSIONS_FOLDER):
    os.mkdir(VERSIONS_FOLDER)


def get_available_dictionary_version():
    version_url = get_configuration().get('VERSIONS', 'versionsurl')
    from ieml.tools import list_bucket
    return [v[:-5] for v in list_bucket(version_url)]


def latest_dictionary_version():
    return DictionaryVersion(get_available_dictionary_version()[0])


def _date_to_str(date):
    return date.strftime('%Y-%m-%d_%H:%M:%S')


def _str_to_date(string):
    return datetime.datetime.strptime(string, '%Y-%m-%d_%H:%M:%S')


def version_name(date):
    return "dictionary_{0}".format(_date_to_str(date))

def phonetic(string):
    for r in LAYER_MARKS:
        string = string.replace(r, '')
    return string


class DictionaryVersionSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        date = args[0] if len(args) == 1 else kwargs['date']

        if date is None:
            date = get_configuration().get('VERSIONS', 'defaultversion')

        if isinstance(date, DictionaryVersion):
            return date

        if isinstance(date, str):
            if date.startswith('dictionary_'):
                date = _str_to_date(date.split('.')[0].split('_', maxsplit=1)[1])
            else:
                date = _str_to_date(date)
        elif isinstance(date, datetime.date):
            date = _str_to_date(_date_to_str(date))
        else:
            raise ValueError("Invalid date format for dictionary version %s." % _date_to_str(date))

        if date not in cls._instances:
            cls._instances[date] = super(DictionaryVersionSingleton, cls).__call__(date)

        return cls._instances[date]


class DictionaryVersion(metaclass=DictionaryVersionSingleton):
    """
    Track the available versions
    """
    def __init__(self, date):
        super(DictionaryVersion, self).__init__()

        self.date = date

        # A list of str. All the script defined in this dictionary.
        self.terms = None

        # The list of root paradigms defined
        self.roots = None

        # A map root -> list of str. The list of relations to inhibate in this root paradigm
        self.inhibitions = None

        # A map term str -> map fr|en -> str
        # The translations of each terms in fr and en (can add more languages)
        self.translations = None

        # A map version str -> map old term str -> new term str
        # To translate old dictionary terms into new ones.
        # Each keys is a version that modify terms (change theirs script)
        # The change must be applied in chronological order (from the old version to new one)
        self.diff = None

        # A edition history
        # version str -> term str -> '+' if added in this version or '-' if removed in this version
        self.history = None

        self.loaded = False

    def __str__(self):
        return version_name(self.date)

    def __getstate__(self):
        self.load()

        return {
            'version': _date_to_str(self.date),
            'terms': self.terms,
            'roots': self.roots,
            'inhibitions': self.inhibitions,
            'translations': self.translations,
            'diff': self.diff
        }

    def __setstate__(self, state):
        self.date = _str_to_date(state['version'])
        self.terms = state['terms']
        self.roots = state['roots']
        self.inhibitions = state['inhibitions']
        self.translations = state['translations']
        self.diff = state['diff'] if 'diff' in state else {}

        self.history = state['history'] if 'history' in state and state['history'] is not None else {str(self): {t: '+' for t in self.terms}}

        self.loaded = True

    def json(self):
        return json.dumps(self.__getstate__())

    def load(self):
        """
        Download the dictionary version and cache the retrieved file.
        :return: None
        """
        if self.loaded:
            return

        file_name = "%s.json" % str(self)
        file = os.path.join(VERSIONS_FOLDER, file_name)

        if not os.path.isfile(file):
            DICTIONARY_BUCKET_URL = get_configuration().get('VERSIONS', 'versionsurl')
            url = urllib.parse.urljoin(DICTIONARY_BUCKET_URL, file_name)
            logger.log(logging.INFO, "Downloading dictionary %s at %s" % (file_name, url))

            urlretrieve(url, file)

        with open(file, 'r') as fp:
            self.__setstate__(json.load(fp))

    def __eq__(self, other):
        return self.date == DictionaryVersion(other).date

    def __hash__(self):
        return str(self).__hash__()

    def __lt__(self, other):
        return self.date.__lt__(DictionaryVersion(other).date)

    def __gt__(self, other):
        return self.date.__gt__(DictionaryVersion(other).date)

    def __le__(self, other):
        return self.date.__le__(DictionaryVersion(other).date)

    def __ge__(self, other):
        return self.date.__ge__(DictionaryVersion(other).date)

    @property
    def cache(self):
        file_name = "cache_%s.pkl" % str(self)
        return os.path.join(VERSIONS_FOLDER, file_name)

    @property
    def is_cached(self):
        return os.path.isfile(self.cache)

    @lru_cache(5)
    def diff_for_version(self, older_version):
        older_version.load()
        self.load()

        result = {
            sc: sc for sc in older_version.terms
        }

        chronology = sorted(filter(lambda v: v >= older_version, (DictionaryVersion(v) for v in self.diff)))

        for v in chronology:
            for sc_old, sc_new in result.items():
                if sc_new in self.diff[str(v)]:
                    result[sc_old] = self.diff[str(v)][sc_new]

        return result

    def get_phonetic_mapping(self):
        phonetic_to_terms = defaultdict(list)

        for i, v in enumerate(sorted(self.history)):
            for t in self.history[v]:
                phonetic_to_terms[phonetic(t)].append((i, t))

        result = {}
        for phon, l_t in phonetic_to_terms.items():
            if len(l_t) > 1:
                for i, c in enumerate(sorted(l_t, key=lambda c: (c[0], LAYER_MARKS.index(c[1][-1])))):
                    _key = phon
                    if i > 0:
                        _key = _key + "." + str(i)

                    result[_key] = c[1]
            else:
                result[phon] = l_t[0][1]

        return result

def _latest_installed_version():
    version_file_pattern = re.compile("^dictionary_\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2}\.json")

    all_versions = sorted((file for file in os.listdir(VERSIONS_FOLDER) if version_file_pattern.match(file)))

    if all_versions:
        return DictionaryVersion(all_versions[-1])
    else:
        return None


_default_version = _latest_installed_version()


def get_default_dictionary_version():
    """
    Return the default dictionary version. The version is the latest version installed on
    the system. If there is none installed yet, it download and install the latest version
    available online.
    To upgrade to a newer version, you can run `set_default_dictionary_version(latest_dictionary_version())`

    :return: the default dictionary version
    """
    if _default_version is None:
        set_default_dictionary_version(latest_dictionary_version())

    return _default_version


def set_default_dictionary_version(version):
    global _default_version
    if not isinstance(version, DictionaryVersion):
        version = DictionaryVersion(version)

    _default_version = version


def create_dictionary_version(old_version=None, add=None, update=None, remove=None):
    """

    :param old_version: the dictionary version to build the new version from
    :param add: a dict with the element to add {'terms': list of script to add,
                                                'roots': list of script to add root paradigm,
                                                'inhibitions': dict {root_p: list of relations to inhibits in this root p}
                                                'translations': dict {language: {script: traduction}}}
    :param update: a dict to update the translations and inhibtions or the terms (new mapping)
            map terms|inhibitions|translations -> old -> new
    :param remove: a list of term to remove, they are removed from root, terms, inhibitions and translations
    :return:
    """
    v = latest_dictionary_version()
    last_date = v.date

    while True:
        new_date = datetime.datetime.utcnow()
        if new_date != last_date:
            break

    new_version_name = version_name(new_date)

    if old_version is None:
        old_version = v

    old_version.load()

    state = {
        'version': _date_to_str(new_date),
        'terms': copy.deepcopy(old_version.terms),
        'roots': copy.deepcopy(old_version.roots),
        'inhibitions': copy.deepcopy(old_version.inhibitions),
        'translations': copy.deepcopy(old_version.translations),
        'diff': {**copy.deepcopy(old_version.diff),
                 str(old_version): {}},
        'history': {**copy.deepcopy(old_version.history),
                    new_version_name: {}}
    }

    # if merge is not None:
    #     for m_version in merge:
    #         m_version.load()
    #
    #         terms_to_add = set(m_version.terms).difference(state['terms'])
    #         roots_to_add = set(m_version.roots).difference(state['roots'])
    #
    #         state['terms'].extend(terms_to_add)
    #         state['roots'].extend(roots_to_add)
    #         state['inhibitions'].update({r: m_version.inhibitions[r] for r in roots_to_add if r in m_version.inhibitions})
    #         for l in LANGUAGES:
    #             state['translations'][l].update({s: m_version.translations[l][s] for s in terms_to_add})

    if remove is not None:
        state['terms'] = list(set(state['terms']).difference(remove))
        state['roots'] = list(set(state['roots']).difference(remove))
        for r in remove:
            if r in state['inhibitions']:
                del state['inhibitions'][r]

            for l in LANGUAGES:
                if r in state['translations'][l]:
                    del state['translations'][l][r]

            state['diff'][str(old_version)][r] = None
            state['history'][new_version_name][r] = '-'

    if add is not None:
        if 'terms' in add:
            state['terms'] = list(set(state['terms']).union(add['terms']))
            for t in add['terms']:
                state['history'][new_version_name][t] = '+'

        if 'roots' in add:
            state['roots'] = list(set(state['roots']).union(add['roots']))
            for t in add['roots']:
                state['history'][new_version_name][t] = '+'

        if 'inhibitions' in add:
            if set(state['inhibitions']).intersection(set(add['inhibitions'])):
                raise ValueError("Error in creating a new dictionary versions, trying to add multiples "
                                 "inhibitions rules for the same script.")

            state['inhibitions'] = {**state['inhibitions'], **add['inhibitions']}
        if 'translations' in add:
            if any(set(state['translations'][l]).intersection(set(add['translations'][l])) for l in LANGUAGES):
                raise ValueError("Error in creating a new dictionary version, trying to add multiples "
                                 "translation for the script {%s}. Those script may already exists in the dictionary."%', '.join(['"%s": [%s]'%(l, ', '.join('"%s"'%str(t) for t in set(state['translations'][l]).intersection(set(add['translations'][l])))) for l in LANGUAGES]))

            state['translations'] = {l: {**state['translations'][l], **add['translations'][l]} for l in LANGUAGES}

    if update is not None:
        if 'inhibitions' in update:
            for s, l in update['inhibitions'].items():
                if s not in state['inhibitions']:
                    continue
                state['inhibitions'][s] = l

        if 'translations' in update:
            state['translations'] = {l: {**state['translations'][l], **update['translations'][l]} for l in LANGUAGES}

        if 'terms' in update:

            state['terms'] = set(t for t in state['terms'] if t not in update['terms'])

            roots = set(state['roots']).intersection(update['terms'])
            state['roots'] = set(t for t in state['roots'] if t not in update['terms'])

            for t_old in update['terms']:
                t_new = update['terms'][t_old]

                # a modify is like an add and delete.
                state['history'][new_version_name][t_old] = '-'
                state['history'][new_version_name][t_new] = '+'

                state['diff'][str(old_version)][t_old] = t_new
                state['terms'].add(t_new)

                if t_old in roots:
                    state['roots'].add(t_new)

                for l in LANGUAGES:
                    state['translations'][l][t_new] = state['translations'][l][t_old]
                    del state['translations'][l][t_old]

                if t_old in state['inhibitions']:
                    state['inhibitions'][t_new] = state['inhibitions'][t_old]
                    del state['inhibitions'][t_old]

    dictionary_version = DictionaryVersion(new_date)
    dictionary_version.__setstate__(state)

    from ieml.dictionary import Dictionary

    if set(old_version.terms) == set(state['terms']) and set(old_version.roots) == set(state['roots']) and \
       all(old_version.inhibitions[s] == state['inhibitions'][s] for s in old_version.inhibitions):

        old_dict_state = Dictionary(old_version).__getstate__()

        d = Dictionary.__new__(Dictionary)
        rel_graph = RelationsGraph.__new__(RelationsGraph)
        rel_graph.__setstate__({
            'dictionary': d,
            'relations': old_dict_state['relations'].__getstate__()['relations']
        })

        state = {
            'version': dictionary_version,
            'relations': rel_graph,
            'scripts': old_dict_state['scripts'],
        }

        d.__setstate__(state)
        save_dictionary_to_cache(d)
    else:
        # graph is updated, must check the coherence
        Dictionary(dictionary_version)

    return dictionary_version


def save_dictionary_to_cache(dictionary):
    logger.log(logging.INFO, "Saving dictionary cache to disk (%s)" % dictionary.version.cache)

    with open(dictionary.version.cache, 'wb') as fp:
        pickle.dump(dictionary, fp, protocol=4)


def load_dictionary_from_cache(version):
    logger.log(logging.INFO, "Loading dictionary from disk (%s)" % version.cache)

    with open(version.cache, 'rb') as fp:
        return pickle.load(fp)
