import hashlib
import re
import uuid

from pymongo.errors import DuplicateKeyError

from ieml.usl.usl import Usl
from models.exceptions import USLNotFound
from models.commons import DBConnector, check_tags, check_keywords, create_tags_indexes
from models.constants import USLS_COLLECTION
from models.exceptions import InvalidTags, DuplicateTag


def usl_index(usl):
    return hashlib.sha1(str(usl).encode('utf-8')).hexdigest()


class USLConnector(DBConnector):
    def __init__(self):
        super().__init__()
        collections = self.db.collection_names()
        self.usls = self.db[USLS_COLLECTION]

        if USLS_COLLECTION not in collections:
            self.usls.create_index('USL.INDEX', unique=True)
            create_tags_indexes(self.usls)

    def save(self, usl, tags, keywords):
        if not isinstance(usl, (str, Usl)):
            raise ValueError('The usl to save must be an instance of Usl type, not %s.'%str(usl))

        if not self._check_tags(tags):
            raise InvalidTags

        if not check_keywords(keywords):
            raise ValueError('The keywords are invalid : %s.'%str(keywords))

        usl_id = self._generate_id()

        self.usls.insert({
            '_id': usl_id,
            'USL': {
                'INDEX': usl_index(usl),
                'IEML': str(usl)
            },
            'TAGS': {
                "FR": tags['FR'],
                "EN": tags['EN']},
            'KEYWORDS': {
                "FR": keywords['FR'],
                "EN": keywords['EN']
            }
        })

        return usl_id

    def get(self, id=None, usl=None, tag=None, language=None):
        if id and isinstance(id, str):
            return self.usls.find_one({'_id': id})

        if usl and isinstance(usl, (str, Usl)):
            return self.usls.find_one({'USL.INDEX': usl_index(usl)})

        if tag and language:
            return self.usls.find_one({'TAGS.%s'%language: tag})

        raise ValueError("Must specify at least one of the following args : id, usl or (tag and language).")

    def remove(self, id=None, usl=None):
        if id and isinstance(id, str):
            self.usls.remove({'_id': id})
            return

        if usl and isinstance(usl, (str, Usl)):
            self.usls.remove({'USL.INDEX': usl_index(usl)})
            return

        raise ValueError("Must specify a id or an usl to remove.")

    def update(self, id, usl=None, tags=None, keywords=None):

        update = {}

        if usl and isinstance(usl, Usl):
            update['USL'] = {
                'INDEX': usl_index(usl),
                'IEML': str(usl)
            }

        if tags and self._check_tags(tags, all_present=False):
            for l in tags:
                update['TAGS.%s'%l] = tags[l]

        if keywords and check_keywords(keywords):
            for l in keywords:
                update['KEYWORDS.%s'%l] = keywords[l]

        if not self.get(id=id):
            raise USLNotFound(id)

        if update:
            self.usls.update_one({'_id': id}, {'$set': update})

    def query(self, tags=None, keywords=None):
        query = {}
        if tags:
            if 'FR' in tags:
                query['TAGS.FR'] = re.compile(re.escape(str(tags['FR'])))
            if 'EN' in tags:
                query['TAGS.EN'] = re.compile(re.escape(str(tags['EN'])))
        if keywords:
            if 'FR' in keywords:
                if keywords['FR']:
                    query['KEYWORDS.FR'] = {'$in': [re.compile(re.escape(str(k))) for k in keywords['FR']]}
            if 'EN' in keywords:
                if keywords['EN']:
                    query['KEYWORDS.EN'] = {'$in': [re.compile(re.escape(str(k))) for k in keywords['EN']]}

        return self.usls.find(query)

    def _check_tags(self, tags, all_present=True):
        if not check_tags(tags, all_present=all_present):
            raise InvalidTags(tags)

        for l in tags:
            if self.get(tag=tags[l], language=l):
                raise DuplicateTag(tags[l])

        return True

    def drop(self):
        self.usls.drop()

    def _generate_id(self):
        free = False
        while not free:
            _id = uuid.uuid4().hex
            free = self.usls.find_one({'_id': _id}) is None
        return _id
