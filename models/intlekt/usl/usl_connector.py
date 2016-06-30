from models.intlekt.connector import DemoConnector
from models.intlekt.constants import COLLECTION_USL


class UslConnector(DemoConnector):
    """
    Connector to add and remove usl and keywords association.
    The document are :
    {
        '_id': str(usl),
        'keywords': [str(keyword)]
    }
    """

    def __init__(self):
        super().__init__()

        self.usls = self.demo_db[COLLECTION_USL]

    def save_keyword(self, usl, keyword):
        if not self.check_usl_exists(usl):
            self.usls.insert({
                '_id': usl if isinstance(usl, str) else str(usl),
                'KEYWORDS': [keyword]
            })
        else:
            self.usls.update({
                '_id': usl if isinstance(usl, str) else str(usl)
            }, {
                '$addToSet': {'KEYWORDS': keyword}
            })

    def check_usl_exists(self, usl):
        return self.usls.find_one({
            '_id': usl if isinstance(usl, str) else str(usl)
        }) is not None
