from .terms import TermsConnector
from random import randint


def get_random_terms(count, only_paradigms=False):
    """Used by the random proposition generator : ouputs n random terms from the dictionary DB, n being count"""
    if only_paradigms:
        filters = {"ROOT" : True}
        total_count = TermsConnector().terms.find(filters).count()
    else:
        filters = {}
        total_count = TermsConnector().terms.count()
    return [term["_id"] for term in TermsConnector().terms.find(filters).limit(count).skip(randint(0, total_count - 1))]


