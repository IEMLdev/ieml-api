from ieml.exceptions import CannotParse


def distance_usl_group(usl_list):
    try:
        usl_list = [(e) for e in usl_list]
    except CannotParse:
        pass

    return {}