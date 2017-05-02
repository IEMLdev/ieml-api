from models.commons import DBConnector
from models.constants import SOURCE_COLLECTION


class SourcesConnector(DBConnector):
    def __init__(self):
        super().__init__()
        self.sources = self.db[SOURCE_COLLECTION]

    def save_sources(self, url, tags):
        if not url or not isinstance(url, str):
            raise ValueError("Can't save the url %s as a source."%url)

        try:
            tags = list(tags)
        except:
            raise ValueError("Tags to save must be iterable")

        if any(not isinstance(s, str) for s in tags):
            raise ValueError("All tags must be str.")

        self.sources.insert_one({
            '_id': url,
            'tags': tags
        })

