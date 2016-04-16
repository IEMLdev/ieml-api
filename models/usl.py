from .base_queries import DBConnector
from .constants import TEXT_COLLECTION

class TextQueries(DBConnector):
    def __init__(self):
        super().__init__()
        self.texts = self.db[TEXT_COLLECTION]

    def _write_text_to_db(self, text, tags):
        self.texts.insert_one({
            "IEML" : str(text),
            "TAGS" : tags,
            "PROPOSITIONS" : [proposition for proposition in text.propositions]
        })

