import pymongo

from config import DB_ADDRESS


class ScoopIt:
    def __init__(self):
        self.collection = pymongo.MongoClient(DB_ADDRESS)['data']['scoopit']

    def posts(self):
        return [{
            'id': p['_id'],
            'title': p['title'],
            'url': 'http://www.scoop.it/u/pierre-levy/%s'%p['_id'],
            'author': {
                'name': 'pierre-levy',
                'link': 'http://www.scoop.it/u/pierre-levy'
            },
            'text': None,
            'link': p['url'],
            'tags': p['tags']
                } for p in self.collection.find()]