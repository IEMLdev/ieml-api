import os

TWITTER_CONSUMER_KEY = 'xxx'
TWITTER_CONSUMER_SECRET = 'xxx'
BASE_HOSTNAME = 'http://intlekt.ieml.lan'

DB_ADDRESS = "mongodb://localhost:27017/"
DB_NAME = "ieml_db"
OLD_DB_NAME = "old_db"

DB_USERS = 'users'
COLLECTION_USERS = 'users'

DICTIONARY_BUCKET_URL = "https://s3.amazonaws.com/ieml-dictionary-versions/"
DICTIONARY_VERSIONS_FOLDER = "data/dictionary/"

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''

DICTIONARY_FOLDER = os.path.join(os.path.dirname(__file__), "data/dictionary")
DICTIONARY_DEFAULT_VERSION = ['2017-06-07', 0]