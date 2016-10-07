import hashlib

from models.commons import DBConnector, check_tags, check_keywords
from models.constants import USLS_COLLECTION
from models.exceptions import InvalidTags, DuplicateTag


def usl_index(usl):
    return hashlib.sha1(str(usl).encode('utf-8')).hexdigest()


class USLConnector(DBConnector):
    def __init__(self):
        super().__init__()
        self.usls = self.db[USLS_COLLECTION]

    def save_usl(self, usl, tags, keywords):

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

    def get_usl(self, usl=None, tag=None, language=None):
        if usl:
            return self.usls.find_one({'_id': str(usl)})

        if tag and language:
            return self.usls.find_one({'TAGS.%s'%language: tag})

        raise ValueError()

    def remove_usl(self, usl):
        self.usls.remove({'_id': usl_index(usl)})

    def edit_usl(self, usl, tags=None, keywords=None):

        update = {}

        if tags and self._check_tags(tags):
            update['TAGS'] = tags

        if keywords and check_keywords(keywords):
            update['KEYWORDS'] = keywords

        self.usls.update_one({'_id': usl_index(usl)}, {'$set': update})

    def _check_tags(self, tags):
        if not check_tags(tags):
            raise InvalidTags(tags)

        for l in tags:
            if self.get_usl(tag=tags[l], language=l):
                raise DuplicateTag(tags[l])

        return True

    def drop(self):
        self.usls.drop()