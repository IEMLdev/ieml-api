from ieml.calculation.distance import distance
from ieml.exceptions import CannotParse
from ieml import usl


def distance_usl_group(body):
    try:
        usl_list = [usl(e) for e in body]
    except CannotParse:
        return

    result = [[distance(src, trg, None) for trg in usl_list[i:]] for i, src in enumerate(usl_list)]

    return {
        'usls': list(map(str, usl_list)),
        'distances': result
    }