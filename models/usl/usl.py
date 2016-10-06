import hashlib

from models.commons import DBConnector
from models.constants import USLS_COLLECTION


def usl_index(usl):
    return hashlib.sha1(str(usl).encode('utf-8')).hexdigest()


class USLConnector(DBConnector):
    def __init__(self):
        super().__init__()
        self.usls = self.db[USLS_COLLECTION]

    def save_usl(self, usl, tags, keywords):

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

    def get_usl(self, usl):
        return self.usls.find_one({'_id': str(usl)})

    def remove_usl(self, usl):
        self.usls.remove({'_id': str(usl)})