from .terms import TermsConnector
from random import randint


def get_random_terms(count):
    """Used by the random proposition generator : ouputs n random terms from the dictionary DB, n being count"""
    total_count = TermsConnector().terms.count()
    return [term["_id"] for term in TermsConnector().terms.find().limit(count).skip(randint(0, total_count - 1))]

