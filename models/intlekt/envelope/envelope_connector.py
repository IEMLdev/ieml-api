from models.intlekt.connector import DemoConnector
from models.intlekt.constants import COLLECTION_ENVELOPE
from models.intlekt.exceptions import EnvelopeAlreadyExists


class EnvelopeConnector(DemoConnector):
    def __init__(self):
        super().__init__()

        self.envelopes = self.demo_db[COLLECTION_ENVELOPE]

    def save_envelope(self, usl, user, sheets_list):
        if self.check_exists(usl, user):
            raise EnvelopeAlreadyExists

        if not isinstance(sheets_list, list):
            raise ValueError

        self.envelopes.insert({
            '_id': {
                'USL': usl if isinstance(usl, str) else str(usl),
                'USER': user if isinstance(user, str) else str(user)
            },
            'SHEETS': sheets_list
        })

    def check_exists(self, usl, user):
        return self.envelopes.find_one({
            '_id' : {
                'USL': usl if isinstance(usl, str) else str(usl),
                'USER': user if isinstance(user, str) else str(user)
            }
        }) is not None
