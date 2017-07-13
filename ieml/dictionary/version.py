import copy
from urllib.request import urlretrieve, urlopen
import datetime
import urllib.parse
import json
import os

from .. import get_configuration, ieml_folder
from ..constants import LANGUAGES
import xml.etree.ElementTree as ET

VERSIONS_FOLDER = os.path.join(ieml_folder, get_configuration().get('VERSIONS', 'versionsfolder'))

if not os.path.isdir(VERSIONS_FOLDER):
    os.mkdir(VERSIONS_FOLDER)


def get_available_dictionary_version():
    version_url = get_configuration().get('VERSIONS', 'versionsurl')
    root_node = ET.fromstring(urlopen(version_url).read())
    all_versions_entry = ({k.tag: k.text for k in list(t)} for t in root_node
                          if t.tag == '{http://s3.amazonaws.com/doc/2006-03-01/}Contents')

    # sort by date
    all_versions = sorted(all_versions_entry,
                          key=lambda t: t['{http://s3.amazonaws.com/doc/2006-03-01/}LastModified'], reverse=True)

    all_versions = [v['{http://s3.amazonaws.com/doc/2006-03-01/}Key'][:-5] for v in all_versions]

    return all_versions


def latest_dictionary_version():
    return DictionaryVersion(get_available_dictionary_version()[0])


def _date_to_str(date):
    return date.strftime('%Y-%m-%d_%H:%M:%S')


def _str_to_date(string):
    return datetime.datetime.strptime(string, '%Y-%m-%d_%H:%M:%S')


class DictionaryVersion:
    """
    Track the available versions
    """
    def __init__(self, date=None):
        super(DictionaryVersion, self).__init__()

        self.terms = None
        self.roots = None
        self.inhibitions = None
        self.translations = None
        self.loaded = False

        if date is None:
            date = get_configuration().get('VERSIONS', 'defaultversion')

        if isinstance(date, str):
            if date.startswith('dictionary_'):
                self.date = self.from_file_name(date).date
            else:
                self.date = _str_to_date(date)
        elif isinstance(date, datetime.date):
            self.date = date
        else:
            raise ValueError("Invalid date format for dictionary version %s." % _date_to_str(date))

    def __str__(self):
        return 'dictionary_%s' % _date_to_str(self.date)

    def __getstate__(self):
        self.load()

        return {
            'version': _date_to_str(self.date),
            'terms': self.terms,
            'roots': self.roots,
            'inhibitions': self.inhibitions,
            'translations': self.translations
        }

    def __setstate__(self, state):
        self.date = _str_to_date(state['version'])
        self.terms = state['terms']
        self.roots = state['roots']
        self.inhibitions = state['inhibitions']
        self.translations = state['translations']

        self.loaded = True

    def json(self):
        return json.dumps(self.__getstate__())

    def load(self):
        if self.loaded:
            return

        file_name = "%s.json" % str(self)
        file = os.path.join(VERSIONS_FOLDER, file_name)

        if not os.path.isfile(file):
            DICTIONARY_BUCKET_URL = get_configuration().get('VERSIONS', 'versionsurl')
            url = urllib.parse.urljoin(DICTIONARY_BUCKET_URL, file_name)
            print("\t[*] Downloading dictionary %s at %s" % (file_name, url))

            urlretrieve(url, file)

        with open(file, 'r') as fp:
            self.__setstate__(json.load(fp))

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return str(self).__hash__()

    def __lt__(self, other):
        return self.date < other.date

    def __gt__(self, other):
        return self.date > other.date

    @staticmethod
    def from_file_name(file_name):
        date = _str_to_date(file_name.split('.')[0].split('_', maxsplit=1)[1])
        return DictionaryVersion(date=date)

    @property
    def cache(self):
        file_name = "cache_%s.pkl" % str(self)
        return os.path.join(VERSIONS_FOLDER, file_name)

    @property
    def is_cached(self):
        return os.path.isfile(self.cache)

_default_version = None


def get_default_dictionary_version():
    if _default_version is None:
        set_default_dictionary_version(latest_dictionary_version())

    return _default_version


def set_default_dictionary_version(version):
    global _default_version
    if not isinstance(version, DictionaryVersion):
        version = DictionaryVersion(version)
    _default_version = version


def create_dictionary_version(old_version=None, add=None, update=None, remove=None, merge=None):
    """

    :param old_version: the dictionary version to build the new version from
    :param add: a dict with the element to add {'terms': list of script to add,
                                                'roots': list of script to add root paradigm,
                                                'inhibitions': dict {root_p: list of relations to inhibits in this root p}
                                                'translations': dict {language: {script: traduction}}}
    :param update: a dict to update the translations and inhibtions
    :param remove: a list of term to remove, they are removed from root, terms, inhibitions and translations
    :param merge: a list of dictionary version to merge
    :return:
    """
    v = latest_dictionary_version()
    last_date = v.date

    while True:
        new_date = datetime.datetime.utcnow()
        if new_date != last_date:
            break

    if old_version is None:
        old_version = v

    old_version.load()

    state = {
        'version': _date_to_str(new_date),
        'terms': copy.deepcopy(old_version.terms),
        'roots': copy.deepcopy(old_version.roots),
        'inhibitions': copy.deepcopy(old_version.inhibitions),
        'translations': copy.deepcopy(old_version.translations)
    }

    if merge is not None:
        for m_version in merge:
            m_version.load()

            terms_to_add = set(m_version.terms).difference(state['terms'])
            roots_to_add = set(m_version.roots).difference(state['roots'])

            state['terms'].extend(terms_to_add)
            state['roots'].extend(roots_to_add)
            state['inhibitions'].update({r: m_version.inhibitions[r] for r in roots_to_add if r in m_version.inhibitions})
            for l in LANGUAGES:
                state['translations'][l].update({s: m_version.translations[l][s] for s in terms_to_add})

    if remove is not None:
        state['terms'] = list(set(state['terms']).difference(remove))
        state['roots'] = list(set(state['roots']).difference(remove))
        for r in remove:
            if r in state['inhibitions']:
                del state['inhibitions'][r]

            for l in LANGUAGES:
                if r in state['translations'][l]:
                    del state['translations'][l][r]

    if add is not None:
        if 'terms' in add:
            state['terms'] = list(set(state['terms']).union(add['terms']))
        if 'roots' in add:
            state['roots'] = list(set(state['roots']).union(add['roots']))
        if 'inhibitions' in add:
            if set(state['inhibitions']).intersection(set(add['inhibitions'])):
                raise ValueError("Error in creating a new dictionary versions, trying to add multiples "
                                 "inhibitions rules for the same script.")

            state['inhibitions'] = {**state['inhibitions'], **add['inhibitions']}
        if 'translations' in add:
            if any(set(state['translations'][l]).intersection(set(add['translations'][l])) for l in LANGUAGES):
                raise ValueError("Error in creating a new dictionary version, trying to add multiples "
                                 "translation for the same script.")

            state['translations'] = {l: {**state['translations'][l], **add['translations'][l]} for l in LANGUAGES}


    if update is not None:
        if 'inhibitions' in update:
            for s, l in update['inhibitions'].items():
                if s not in state['inhibitions']:
                    continue
                state['inhibitions'][s] = l
        if 'translations' in update:
            state['translations'] = {l: {**state['translations'][l], **update['translations'][l]} for l in LANGUAGES}

    dictionary_version = DictionaryVersion(new_date)
    dictionary_version.__setstate__(state)

    from ieml.dictionary import Dictionary

    if set(old_version.terms) == set(state['terms']) and set(old_version.roots) == set(state['roots']) and \
       all(old_version.inhibitions[s] == state['inhibitions'][s] for s in old_version.inhibitions):

        old_dict_state = Dictionary(old_version).__getstate__()
        d = Dictionary(dictionary_version)
        d.__setstate__(old_dict_state)
    else:
        # graph is updated, must check the coherence
        Dictionary(dictionary_version)

    return dictionary_version


if __name__ == '__main__':
    print(get_available_dictionary_version())