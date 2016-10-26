import functools


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