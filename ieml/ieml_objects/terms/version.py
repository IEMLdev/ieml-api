from urllib.request import urlretrieve
import datetime
import urllib.parse
import io
import boto3
import json
import os

from config import DICTIONARY_BUCKET_URL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, DICTIONARY_FOLDER, \
    DICTIONARY_DEFAULT_VERSION
from ieml.commons import LANGUAGES


def get_available_dictionary_version():
    s3 = boto3.resource(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    bucket_name = 'ieml-dictionary-versions'
    bucket = s3.Bucket(bucket_name)

    result = []
    for obj in bucket.objects.all():
        result.append(DictionaryVersion.from_file_name(obj.key))

    return result


class DictionaryVersion:
    """
    Track the available versions
    """
    def __init__(self, date=None, version_id=0):
        super(DictionaryVersion, self).__init__()

        self.terms = None
        self.roots = None
        self.inhibitions = None
        self.translations = None
        self.loaded = False

        if date is None:
            date, version_id = DICTIONARY_DEFAULT_VERSION

        if isinstance(date, str):
            self.date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        elif isinstance(date, datetime.date):
            self.date = date
        else:
            raise ValueError("Invalid date format for dictionary version %s." % str(date))

        self.version_id = int(version_id)

    def __str__(self):
        return 'dictionary_%s_%d' % (str(self.date), self.version_id)

    def __getstate__(self):
        self.load()

        return {
            'version': [str(self.date), str(self.version_id)],
            'terms': self.terms,
            'roots': self.roots,
            'inhibitions': self.inhibitions,
            'translations': self.translations
        }

    def __setstate__(self, state):
        self.date = datetime.datetime.strptime(state['version'][0], '%Y-%m-%d').date()
        self.version_id = int(state['version'][1])

        self.terms = state['terms']
        self.roots = state['roots']
        self.inhibitions = state['inhibitions']
        self.translations = state['translations']

        self.loaded = True

    def json(self):
        return json.dumps(self.__getstate__())

    def upload_to_s3(self):
        s3 = boto3.resource(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        bucket_name = 'ieml-dictionary-versions'
        bucket = s3.Bucket(bucket_name)
        obj = bucket.Object("%s.json" % str(self))

        obj.upload_fileobj(io.BytesIO(bytes(self.json(), 'utf-8')))
        obj.Acl().put(ACL='public-read')

    def load(self):
        if self.loaded:
            return

        file_name = "%s.json" % str(self)

        if not os.path.isdir(DICTIONARY_FOLDER):
            os.mkdir(DICTIONARY_FOLDER)

        file = os.path.join(DICTIONARY_FOLDER, file_name)

        if not os.path.isfile(file):
            url = urllib.parse.urljoin(DICTIONARY_BUCKET_URL, file_name)
            print("\t[*] Downloading dictionary %s at %s" % (file_name, url))
            urlretrieve(url, file)

        with open(file, 'r') as fp:
            self.__setstate__(json.load(fp))

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return str(self).__hash__()

    @staticmethod
    def from_file_name(file_name):
        date, version_id = file_name.split('.')[0].split('_')[1:3]
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        return DictionaryVersion(date=date, version_id=int(version_id))


_default_version = None


def get_default_dictionary_version():
    global _default_version
    if _default_version is None:
        _default_version = DictionaryVersion()

    return _default_version


def create_dictionary_version(old_version, add=None, update=None):
    v = get_available_dictionary_version()[-1]
    last_date, last_version_id = v.date, v.version_id

    date = datetime.datetime.today()
    if last_date == date:
        version_id = last_version_id + 1
    else:
        version_id = 0

    state = {
        'version': [str(date), str(version_id)],
        'terms': list(set(old_version.terms).union(add['terms'])),
        'roots': list(set(old_version.roots).union(add['roots'])),
        'inhibitions': {**old_version.inhibitions, **add['inhibitions']},
        'translations': {l: {**old_version.translations[l], **add['translations'][l]} for l in LANGUAGES}
    }

    dictionary_version = DictionaryVersion(date, version_id)
    dictionary_version.__setstate__(state)

    return dictionary_version


if __name__ == '__main__':
    print(get_available_dictionary_version())