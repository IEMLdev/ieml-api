import bidict
""""This module is kind of used as a config file, may be replaced by a configuration file in the future"""


DB_ADDRESS = "mongodb://localhost:27017/"
DB_NAME = "ieml_db"
DB_NAME_TERM = "db3"

SCRIPTS_COLLECTION = "scripts"
TERMS_COLLECTION = "terms"
PROPOSITION_COLLECTION = "propositions"
TEXT_COLLECTION = "texts"
HYPERTEXT_COLLECTION = "hypertexts"


TAG_LANGUAGES = ["FR", "EN"]

DB_NAME_USERS = ""

USERS_COLLECTIONS = ""

# RELATIONS = bidict({
#     'ASCENDING': 'DESCENDING',
#     'GERMAN': 'GERMAN'
# })


# Script specific
ROOT_PARADIGM_TYPE = 'ROOT_PARADIGM'
SINGULAR_SEQUENCE_TYPE = 'SINGULAR_SEQUENCE'
PARADIGM_TYPE = 'PARADIGM'

