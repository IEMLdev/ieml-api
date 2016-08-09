import functools

from models.terms.terms import TermsConnector


def terms_db():
    return TermsConnector()


def exception_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            return {'success': False, 'message': str(e)}
        else:
            return result

    return wrapper



