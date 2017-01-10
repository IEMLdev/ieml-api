import datetime
from datetime import date

from pymongo.errors import DuplicateKeyError

from models.commons import DBConnector
SCOOPIT = 'scoopit'

class PostConnector(DBConnector):
    def __init__(self):
        super().__init__()
        self.posts = self.db['posts']

    def save(self, post):
        try:
            self.posts.insert({
                '_id': SCOOPIT + '/post/' + post['id'],
                'title': post['title'],
                'source': {
                    'media': SCOOPIT,
                    'url': post['url']
                },
                'import_date': datetime.datetime.now(),
                'author': {
                    'id': SCOOPIT + '/author/' + post['author']['name'],
                    'name': post['author']['name'],
                    'profile': post['author']['link']
                },
                'content': {
                    'body': post['text'],
                    'link': post['link']
                },
                'tags': {
                    'hashtags': [t['title'] for t in post['tags'] if t['type'] == 'taxonomic'],
                    'sentences': [t['title'] for t in post['tags'] if t['type'] == 'sentence']
                }
            })
        except DuplicateKeyError:
            pass