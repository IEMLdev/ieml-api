import traceback

from models.base_queries import DictionaryQueries
from models.propositions import PropositionsQueries
from models.exceptions import DBException
from models.usl import TextQueries, HyperTextQueries

terms_db = DictionaryQueries()
propositions_db = PropositionsQueries()
texts_db = TextQueries()
hypertexts_db = HyperTextQueries()


