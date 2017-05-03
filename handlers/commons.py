import functools

from ieml.commons import GRAMMATICAL_CLASS_NAMES
from ieml.ieml_objects.terms import Term
from models.exceptions import InvalidRelationCollectionState, TermNotFound
from models.relations.relations import RelationsConnector
from models.relations.relations_queries import RelationsQueries
from models.terms.terms import TermsConnector


def exception_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            return {'success': False, 'message': e.__class__.__name__ + ': ' + str(e)}
        else:
            return result

    return wrapper


def ieml_term_model(term):
    term = Term(term)

    term_entry = TermsConnector().get_term(str(term.script))
    if term_entry is None:
        raise ValueError("Term %s not found in the dictionary."%str(term))

    entry = RelationsConnector().get_script(term_entry["_id"])
    rank = entry['RANK'] if term.script.paradigm else 0
    index = entry['INDEX']

    return {
        'CLASS': GRAMMATICAL_CLASS_NAMES[term.grammatical_class],
        'EN': term_entry["TAGS"]["EN"],
        'FR': term_entry["TAGS"]["FR"],
        'IEML': term_entry["_id"],
        'LAYER': term.script.layer,
        'PARADIGM': term.script.paradigm,
        'ROOT_PARADIGM': term_entry['ROOT'],
        'SIZE': term.script.cardinal,
        'INDEX': index,
        'RANK': rank
    }