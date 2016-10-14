import hashlib
import re

from models.exceptions import USLNotFound
from models.commons import DBConnector, check_tags, check_keywords
from models.constants import USLS_COLLECTION
from models.exceptions import InvalidTags, DuplicateTag


def usl_index(usl):
    return hashlib.sha1(str(usl).encode('utf-8')).hexdigest()


class USLConnector(DBConnector):
    def __init__(self):
        super().__init__()
        self.usls = self.db[USLS_COLLECTION]

    def save(self, usl, tags, keywords):

        if not self._check_tags(tags):
            raise InvalidTags

        self.usls.insert({
            '_id': usl_index(usl),
            'IEML': str(usl),
            'TAGS': {
                "FR": tags['FR'],
                "EN": tags['EN']},
            'KEYWORDS': {
                "FR": keywords['FR'],
                "EN": keywords['EN']
            }
        })

    def get(self, usl=None, tag=None, language=None):
        if usl:
            return self.usls.find_one({'_id': usl_index(usl)})

        if tag and language:
            return self.usls.find_one({'TAGS.%s'%language: tag})

        raise ValueError()

    def remove(self, usl):
        self.usls.remove({'_id': usl_index(usl)})

    def update(self, usl, tags=None, keywords=None):

        update = {}

        if tags and self._check_tags(tags, all_present=False):
            for l in tags:
                update['TAGS.%s'%l] = tags[l]

        if keywords and check_keywords(keywords):
            for l in keywords:
                update['KEYWORDS.%s'%l] = keywords[l]

        if not self.get(usl):
            raise USLNotFound(usl)

        self.usls.update_one({'_id': usl_index(usl)}, {'$set': update})

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