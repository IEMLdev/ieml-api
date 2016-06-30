from models.base_queries import DBConnector
from models.intlekt.constants import DEMO_DB_NAME


class DemoConnector(DBConnector):
    def __init__(self):
        super().__init__()

        self.demo_db = self.client[DEMO_DB_NAME]
