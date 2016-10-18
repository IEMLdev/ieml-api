import itertools

from ieml.ieml_objects.terms import Term
from ieml.ieml_objects.tools import replace_from_paths
from ieml.script.constants import CONTAINED_RELATION
from models.commons import DBConnector, generate_tags, check_tags
from models.constants import TEMPLATES_COLLECTION, TAG_LANGUAGES
from models.relations import RelationsQueries
from models.terms import TermsConnector
from models.usls.usls import usl_index


class TemplatesConnector(DBConnector):
    def __init__(self):
        super().__init__()
        self.templates = self.db[TEMPLATES_COLLECTION]

    def save_template(self, usl, paths, tags_rule=None):

        if not all(isinstance(p[-1], Term) for p in paths):
            raise ValueError("The paths must end on a Term.")

        # path -> [terms]
        paradigms = {p: list(RelationsQueries.relations(p[-1], CONTAINED_RELATION)) for p in paths}

        # usl -> elements
        expansion = {replace_from_paths(usl, paths, elements): {'ELEMENTS': elements}
                     for elements in itertools.product(*paradigms.values())}

        # usl -> elements, tags
        if tags_rule and check_tags(tags_rule):
            terms_tags = {term: TermsConnector().get_term(term)['TAGS']
                          for term in set(itertools.chain.from_iterable(paradigms.values()))}

            for u in expansion:
                tags = {l: tags_rule[l] for l in TAG_LANGUAGES}
                for i, e in enumerate(expansion[u]['ELEMENTS']):
                    for l in tags:
                        tags[l].replace('$%d'%i, terms_tags[e][l])
                expansion[u]['TAGS'] = tags

        else:
            for u in expansion:
                expansion[u]['TAGS'] = generate_tags(u)

        entry = {
            '_id': usl_index(usl),
            'IEML': str(usl),
            'CONTAINED': [{
                'IEML': u,
                **expansion[u]
                          } for u in expansion],
            'PATHS': paths
        }

        if tags_rule:
            entry['TAGS_RULE'] = tags_rule

        self.templates.save(entry)



