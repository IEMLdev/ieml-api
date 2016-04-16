from .base_queries import DBConnector
from .constants import TEXT_COLLECTION, HYPERTEXT_COLLECTION

class TextQueries(DBConnector):
    def __init__(self):
        super().__init__()
        self.texts = self.db[TEXT_COLLECTION]

    def _write_text_to_db(self, text, tags):
        self.texts.insert_one({
            "IEML" : str(text),
            "TAGS" : tags,
            "PROPOSITIONS" : [id(proposition) for proposition in text.propositions]
        })

    def get_text_from_ieml(self, text_ieml):
        return  self.texts.find_one({"IEML" : text_ieml})


class HypertextQueries(TextQueries):
    def __init__(self):
        super().__init__()
        self.hypertexts = self.db[HYPERTEXT_COLLECTION]

    def _write_hypertext_to_db(self, hypertext, tags):

        self.hypertexts.insert_one({
            "TAGS" : tags,
            "IEML" : str(hypertext),
            "HYPERLINK" : [
                {id: hypertext.hyperlinks_table[proposition]} for proposition in hypertext.propositions
            ]
        })