import itertools
from _operator import mul
from functools import reduce

from ieml.ieml_objects.terms import Term
from ieml.ieml_objects.tools import replace_from_paths, ieml
from ieml.paths.tools import path
from ieml.script.constants import CONTAINS_RELATION
from ieml.usl.tools import usl, replace_paths
from models.commons import DBConnector, generate_tags, check_tags
from models.constants import TEMPLATES_COLLECTION, TAG_LANGUAGES, MAX_SIZE_TEMPLATE
from models.terms import TermsConnector
from models.usls.usls import usl_index


class TemplatesConnector(DBConnector):
    def __init__(self):
        super().__init__()
        self.templates = self.db[TEMPLATES_COLLECTION]

    def save_template(self, _usl, paths, tags_rule=None):
        """
        save a template for the given usl, varying the terms specified in rules.

        :param _usl:
        :param rules: list of paths
        :param tags_rule: a string where the declinaison of each variying term will be inserred a the place of the $i.
        :return:
        """
        paths = [path(p) for p in paths]

        terms = [_usl[p] for p in paths]

        if any(len(t) != 1 for t in terms):
            raise ValueError("Invalids path, lead to multiple elements.")

        terms = [t for s in terms for t in s]

        if any(not isinstance(t, Term) for t in terms):
            raise ValueError("Template only support Term variation.")

        # path -> []
        paradigms = {p: t.relations(CONTAINS_RELATION) for p, t in zip(paths, terms)}

        template_size = reduce(mul, map(len, paradigms.values()))

        if template_size > MAX_SIZE_TEMPLATE:
            raise ValueError("Can't generate this template, maximum size of %d and the template size is %d."%
                             (MAX_SIZE_TEMPLATE, template_size))

        if any(not rels for rels in paradigms.values()):
            errors = filter(lambda e: not paradigms[e], paradigms)
            raise ValueError("The terms at the given paths are not paradigms.[%s]"%(', '.join(map(str, errors))))

        # all the combinations with the resulting usl
        expansion = {}
        for product in itertools.product(*([(p, t) for t in paradigms[p]] for p in paradigms)):
            expansion[replace_paths(_usl, product)] = {
                'TAGS': {},
                'ELEMENTS': [str(t) for p, t in product]
            }

        if tags_rule and check_tags(tags_rule):
            terms_tags = {str(term): TermsConnector().get_term(term)['TAGS']
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
            '_id': usl_index(_usl),
            'IEML': str(_usl),
            'CONTAINED': [{
                'IEML': str(u),
                **expansion[u]
                          } for u in expansion],
            'PATHS': [str(p) for p in paths]
        }

        if tags_rule:
            entry['TAGS_RULE'] = tags_rule

        self.templates.save(entry)

    def get_template(self, usl):
        return self.templates.find_one({'_id': usl_index(usl)})

    def drop(self):
        self.templates.drop()

