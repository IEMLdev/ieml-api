from models.commons import DBConnector
from models.constants import SOURCE_COLLECTION


class SourcesConnector(DBConnector):
    """ Collection managing the tags and their translation."""


    def __init__(self):
        super().__init__()
        self.sources = self.db[SOURCE_COLLECTION]

    def save_sources(self, url, tags):
        if not url or not isinstance(url, str):
            raise ValueError("Can't save the url %s as a source."%url)

        try:
            tags = [{
                'title': t['title'],
                'count': t['count'],
                'link': t['link'],
                'ieml': None} for t in tags]
        except:
            raise ValueError("Tags to save must be iterable")

        self.sources.insert_one({
            '_id': url,
            'tags': tags
        })

    def get_source(self, url):
        return self.sources.find_one({'_id': url})

    def set_ieml(self, url, tag, ieml):
        r = self.get_source(url)
        if r is None:
            raise ValueError("Can't update this tag ieml, unknown url %s"%url)

        index = None

        for i, _tag in enumerate(r['tags']):
            if _tag['title'] == tag:
                index = i

        if index is None:
            raise ValueError("The tag %s is not present in this collection, can't update ieml" % tag)

        r['tags'][index]['ieml'] = ieml

        self.sources.update_one({'_id': url}, {'$set': {'tags': r['tags']}})
