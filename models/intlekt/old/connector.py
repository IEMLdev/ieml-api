from models.commons import DBConnector
from models.intlekt.old.constants import DEMO_DB_NAME


class DemoConnector(DBConnector):
    def __init__(self):
        super().__init__()

        self.demo_db = self.client[DEMO_DB_NAME]
