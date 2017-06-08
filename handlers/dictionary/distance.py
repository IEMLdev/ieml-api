from ieml.ieml_objects.terms.distance import ranking_from_term
from ieml.ieml_objects.terms import term


def get_ranking_from_term(ieml):
    _tt = term(ieml)
    return [{
        'ieml': str(t[2].script),
        'ranking': [t[0], t[1]],
        'relations': _tt.relations.to(t[2], relations_types=['inclusion', 'etymology', 'siblings', 'table'])
    } for t in ranking_from_term(_tt, nb_terms=30) if t[0] < 5.0]