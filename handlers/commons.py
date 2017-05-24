import functools

from ieml.commons import GRAMMATICAL_CLASS_NAMES
from ieml.ieml_objects.tools import term as _term


def exception_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            return {'success': False, 'message': e.__class__.__name__ + ': ' + str(e)}
        else:
            if 'success' not in result:
                print("Warning 'success' field is not present in %s response."%func.__name__)
            return result

    return wrapper


def ieml_term_model(term):
    term = _term(term)

    return {
        'CLASS': GRAMMATICAL_CLASS_NAMES[term.grammatical_class],
        'EN': term.translation["en"],
        'FR': term.translation["fr"],
        'IEML': str(term.script),
        'LAYER': term.script.layer,
        'PARADIGM': term.script.paradigm,
        'ROOT_PARADIGM': term.root == term,
        'SIZE': term.script.cardinal,
        'INDEX': term.index,
        'RANK': term.rank
    }