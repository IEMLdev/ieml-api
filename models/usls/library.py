import datetime
import hashlib
import json
import re
import uuid
import itertools

from ieml.usl.tools import usl as _usl
from models.commons import DBConnector, check_tags, create_translations_indexes, TAG_LANGUAGES
from models.constants import LIBRARY_COLLECTION


def usl_index(usl):
    return hashlib.sha1(str(usl).encode('utf-8')).hexdigest()


class LibraryConnector(DBConnector):
    def __init__(self):
        super().__init__()
        collections = self.db.collection_names()
        self.usls = self.db[LIBRARY_COLLECTION]

        if LIBRARY_COLLECTION not in collections:
            self.usls.create_index('USL.INDEX', unique=True)
            create_translations_indexes(self.usls)

    def save(self, usl, translations):
        usl = _usl(usl)

        self._check_tags(translations)

        for l in TAG_LANGUAGES:
            if translations[l] == "":
                translations[l] = None

        usl_id = self._generate_id()

        self.usls.insert_one({
            '_id': usl_id,
            'USL': {
                'INDEX': usl_index(usl),
                'IEML': str(usl),
                'TYPE': str(usl.ieml_object.__class__.__name__)
            },
            'TRANSLATIONS': {
                "FR": translations['FR'],
                "EN": translations['EN']},
            'LAST_MODIFIED': datetime.datetime.utcnow()
        })

        return usl_id

    # def add_template(self, _usl, paths, _tags=None, tags_rule=None, _keywords=None):
    #     """
    #     save a template for the given usl, varying the terms specified in rules.
    #     You must provide singular path (cardinality 1) support at most (for the moment) 2 path variation.
    #
    #     :param _usl:
    #     :param rules: list of paths
    #     :param tags_rule: a string where the declinaison of each variying term will be inserred a the place of the $i.
    #     :return:
    #     """
    #     paths = [path(pp) for p in paths for pp in p.develop]
    #
    #
    #     terms = [_usl[p] for p in paths]
    #
    #     if _tags is not None and not self._check_tags(_tags):
    #         raise InvalidTags(_tags)
    #
    #     if _keywords:
    #         if not check_keywords(_keywords):
    #             raise ValueError('The keywords are invalid : %s.'%str(_keywords))
    #     else:
    #         _keywords = {l: [] for l in TAG_LANGUAGES}
    #
    #     if any(not isinstance(t, Term) or t.script.cardinal != 1 for t in terms):
    #         raise ValueError("Invalids path, lead to multiple elements.")
    #
    #     terms = [t for s in terms for t in s]
    #
    #     if any(not isinstance(t, Term) for t in terms):
    #         raise ValueError("Template only support Term variation.")
    #
    #     # path -> []
    #     paradigms = {p: t.relations(CONTAINS_RELATION) for p, t in zip(paths, terms)}
    #
    #     template_size = reduce(mul, map(len, paradigms.values()))
    #
    #     if template_size > MAX_SIZE_TEMPLATE:
    #         raise ValueError("Can't generate this template, maximum size of %d and the template size is %d."%
    #                          (MAX_SIZE_TEMPLATE, template_size))
    #
    #     if any(not rels for rels in paradigms.values()):
    #         errors = filter(lambda e: not paradigms[e], paradigms)
    #         raise ValueError("The terms at the given paths are not paradigms.[%s]"%(', '.join(map(str, errors))))
    #
    #     # all the combinations with the resulting usl
    #     expansion = {}
    #     for product in itertools.product(*([(p, t) for t in paradigms[p]] for p in paradigms)):
    #         expansion[replace_paths(_usl, product)] = {
    #             'TAGS': {},
    #             'ELEMENTS': [str(t) for p, t in product]
    #         }
    #
    #     if tags_rule and check_tags(tags_rule):
    #         terms_tags = {str(term): TermsConnector().get_term(term.script)['TAGS']
    #                       for term in set(itertools.chain.from_iterable(paradigms.values()))}
    #
    #         for u in expansion:
    #             tags = {l: tags_rule[l] for l in TAG_LANGUAGES}
    #             for i, e in enumerate(expansion[u]['ELEMENTS']):
    #                 for l in tags:
    #                     tags[l] = tags[l].replace('$%d'%i, terms_tags[e][l])
    #             expansion[u]['TAGS'] = tags
    #
    #         if _tags is None:
    #             _tags = {l: tags_rule[l] for l in TAG_LANGUAGES}
    #             for i, p in enumerate(paths):
    #                 term_tag = TermsConnector().get_term(terms[i].script)['TAGS']
    #                 for l in _tags:
    #                     _tags[l] = _tags[l].replace('$%d'%i, term_tag[l])
    #
    #     else:
    #         for u in expansion:
    #             expansion[u]['TAGS'] = generate_tags(u)
    #
    #         if _tags is None:
    #             _tags = generate_tags(_usl)
    #
    #     # now we save the usl-template
    #     entry = self.get(usl=_usl)
    #     if entry is None:
    #         _id = self.save(_usl, _tags, _keywords)
    #     else:
    #         _id = entry['_id']
    #
    #     # save all usls
    #     for u in expansion:
    #         expansion[u]['id'] = self.save(u, expansion[u]['TAGS'], template=_id)
    #
    #     template = {
    #         'PATHS': [str(p) for p in paths],
    #         'EXPANSIONS': list(expansion.values())
    #     }
    #
    #     if tags_rule:
    #         template['TAGS_RULE'] = tags_rule
    #
    #     self.usls.update({'_id': _id}, {'$push': {'TEMPLATES': template}})

    def get(self, id=None, usl=None, translation=None, language=None):
        if id:
            return self.usls.find_one({'_id': str(id)})

        if usl:
            usl = _usl(usl)
            return self.usls.find_one({'USL.INDEX': usl_index(usl)})

        if translation and language:
            return self.usls.find_one({'TRANSLATIONS.%s'%str(language): str(translation)})

        raise ValueError("Must specify at least one of the following arguments : "
                         "id, usl or (translation and language).")

    def remove(self, id=None, usl=None):
        if id:
            self.usls.remove({'_id': str(id)})
            return

        if usl:
            self.usls.remove({'USL.INDEX': usl_index(_usl(usl))})
            return

        raise ValueError("Must specify a id or an usl to remove.")

    def update(self, id, usl=None, translations=None):

        update = {}

        if usl:
            usl = _usl(usl)
            update['USL'] = {
                'INDEX': usl_index(usl),
                'IEML': str(usl),
                'TYPE': str(usl.ieml_object.__class__.__name__)
            }

        if translations:
            self._check_tags(translations, all_present=False)
            for l in translations:
                update['TRANSLATIONS.%s'%l] = translations[l] if translations[l] != "" else None

        entry = self.get(id=str(id))
        if entry is None:
            raise ValueError("The usl %s is not present in db."%str(id))

        if 'USL' in update and not self._is_editable(entry):
            raise ValueError("Can't edit the ieml of this usl, it has a parent template or template children.")

        if update:
            update['LAST_MODIFIED'] = datetime.datetime.utcnow()
            self.usls.update_one({'_id': str(id)}, {'$set': update})

    def query(self, translations=None, union=False):
        query = {}
        if translations:
            if 'FR' in translations:
                query['TRANSLATIONS.FR'] = re.compile(re.escape(str(translations['FR'])))
            if 'EN' in translations:
                query['TRANSLATIONS.EN'] = re.compile(re.escape(str(translations['EN'])))

        if union:
            query = {'$or': [{k: query[k]} for k in query]}

        return self.usls.find(query)

    def most_recent(self, number):
        return list(itertools.islice(self.usls.find().sort("LAST_MODIFIED", 1), number))

    def _check_tags(self, tags, all_present=True):
        if not check_tags(tags, all_present=all_present):
            raise ValueError('The translations are not valid %s, either it is missing a language or the type is '
                             'incorrect.' % json.dumps(tags))

    def drop(self):
        self.usls.drop()

    def _generate_id(self):
        free = False
        _id = None
        while not free:
            _id = uuid.uuid4().hex
            free = self.usls.find_one({'_id': _id}) is None
        return _id

    def _is_editable(self, entry):
        return True