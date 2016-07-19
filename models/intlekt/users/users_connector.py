from models.intlekt.connector import DemoConnector
from models.intlekt.constants import COLLECTION_USERS


class UsersConnector(DemoConnector):
    def __init__(self):
        super().__init__()

        self.users = self.demo_db[COLLECTION_USERS]

    def create_user(self, token_twitter):
        self.users.insert({

        })