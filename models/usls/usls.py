import datetime
import hashlib
import re
import uuid
from _operator import mul
from functools import reduce

import itertools
from pymongo.errors import DuplicateKeyError

from ieml.ieml_objects.terms import Term
from ieml.paths.tools import path
from ieml.script.constants import CONTAINS_RELATION
from ieml.usl.tools import replace_paths
from ieml.usl.usl import Usl
from models.exceptions import USLNotFound
from models.commons import DBConnector, check_tags, check_keywords, create_tags_indexes, generate_tags
from models.constants import USLS_COLLECTION, MAX_SIZE_TEMPLATE, TAG_LANGUAGES
from models.exceptions import InvalidTags, DuplicateTag
from models.terms.terms import TermsConnector


def usl_index(usl):
    return hashlib.sha1(str(usl).encode('utf-8')).hexdigest()


class USLConnector(DBConnector):
    def __init__(self):
        super().__init__()
        collections = self.db.collection_names()
        self.usls = self.db[USLS_COLLECTION]

        if USLS_COLLECTION not in collections:
            self.usls.create_index('USL.INDEX', unique=True)
            create_tags_indexes(self.usls)

    def save(self, usl, tags, keywords=None, template=None):
        if not isinstance(usl, (str, Usl)):
            raise ValueError('The usl to save must be an instance of Usl type, not %s.'%str(usl))

        if not self._check_tags(tags):
            raise InvalidTags(tags)

        if keywords:
            if not check_keywords(keywords):
                raise ValueError('The keywords are invalid : %s.'%str(keywords))
        else:
            keywords = {l: [] for l in TAG_LANGUAGES}

        usl_id = self._generate_id()

        if template is not None and self.get(id=template) is None:
            raise ValueError("Invalid parent template argument.")

        self.usls.insert({
            '_id': usl_id,
            'USL': {
                'INDEX': usl_index(usl),
                'IEML': str(usl)
            },
            'TAGS': {
                "FR": tags['FR'],
                "EN": tags['EN']},
            'KEYWORDS': {
                "FR": keywords['FR'],
                "EN": keywords['EN']
            },
            'PARENTS': [template] if template is not None else [],
            'TEMPLATES': [],
            'LAST_MODIFIED': datetime.datetime.utcnow()

        })

        return usl_id

    def add_template(self, _usl, paths, _tags=None, tags_rule=None, _keywords=None):
        """
        save a template for the given usl, varying the terms specified in rules.

        :param _usl:
        :param rules: list of paths
        :param tags_rule: a string where the declinaison of each variying term will be inserred a the place of the $i.
        :return:
        """
        paths = [path(p) for p in paths]

        terms = [_usl[p] for p in paths]

        if _tags is not None and not self._check_tags(_tags):
            raise InvalidTags(_tags)

        if _keywords:
            if not check_keywords(_keywords):
                raise ValueError('The keywords are invalid : %s.'%str(_keywords))
        else:
            _keywords = {l: [] for l in TAG_LANGUAGES}

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
            terms_tags = {str(term): TermsConnector().get_term(term.script)['TAGS']
                          for term in set(itertools.chain.from_iterable(paradigms.values()))}

            for u in expansion:
                tags = {l: tags_rule[l] for l in TAG_LANGUAGES}
                for i, e in enumerate(expansion[u]['ELEMENTS']):
                    for l in tags:
                        tags[l] = tags[l].replace('$%d'%i, terms_tags[e][l])
                expansion[u]['TAGS'] = tags

            if _tags is None:
                _tags = {l: tags_rule[l] for l in TAG_LANGUAGES}
                for i, p in enumerate(paths):
                    term_tag = TermsConnector().get_term(terms[i].script)['TAGS']
                    for l in _tags:
                        _tags[l] = _tags[l].replace('$%d'%i, term_tag[l])

        else:
            for u in expansion:
                expansion[u]['TAGS'] = generate_tags(u)

            if _tags is None:
                _tags = generate_tags(_usl)

        # now we save the usl-template
        entry = self.get(usl=_usl)
        if entry is None:
            _id = self.save(_usl, _tags, _keywords)
        else:
            _id = entry['_id']

        # save all usls
        for u in expansion:
            expansion[u]['id'] = self.save(u, expansion[u]['TAGS'], template=_id)

        template = {
            'PATHS': [str(p) for p in paths],
            'EXPANSIONS': list(expansion.values())
        }

        if tags_rule:
            template['TAGS_RULE'] = tags_rule

        self.usls.update({'_id': _id}, {'$push': {'TEMPLATES': template}})

    def get(self, id=None, usl=None, tag=None, language=None):
        if id and isinstance(id, str):
            return self.usls.find_one({'_id': id})

        if usl and isinstance(usl, (str, Usl)):
            return self.usls.find_one({'USL.INDEX': usl_index(usl)})

        if tag and language:
            return self.usls.find_one({'TAGS.%s'%language: tag})

        raise ValueError("Must specify at least one of the following args : id, usl or (tag and language).")

    def remove(self, id=None, usl=None):
        if id and isinstance(id, str):
            self.usls.remove({'_id': id})
            return

        if usl and isinstance(usl, (str, Usl)):
            self.usls.remove({'USL.INDEX': usl_index(usl)})
            return

        raise ValueError("Must specify a id or an usl to remove.")

    def update(self, id, usl=None, tags=None, keywords=None):

        update = {}

        if usl and isinstance(usl, Usl):
            update['USL'] = {
                'INDEX': usl_index(usl),
                'IEML': str(usl)
            }

        if tags and self._check_tags(tags, all_present=False, except_id=id):
            for l in tags:
                update['TAGS.%s'%l] = tags[l]

        if keywords and check_keywords(keywords):
            for l in keywords:
                update['KEYWORDS.%s'%l] = keywords[l]

        entry = self.get(id=id)
        if entry is None:
            raise USLNotFound(id)

        if 'USL' in update and not self._is_editable(entry):
            raise ValueError("Can't edit the ieml of this usl, it has a parent template or template children.")

        if update:
            update['LAST_MODIFIED'] = datetime.datetime.utcnow()
            self.usls.update_one({'_id': id}, {'$set': update})

    def query(self, tags=None, keywords=None, union=False):
        query = {}
        if tags:
            if 'FR' in tags:
                query['TAGS.FR'] = re.compile(re.escape(str(tags['FR'])))
            if 'EN' in tags:
                query['TAGS.EN'] = re.compile(re.escape(str(tags['EN'])))
        if keywords:
            if 'FR' in keywords:
                if keywords['FR']:
                    query['KEYWORDS.FR'] = {'$in': [re.compile(re.escape(str(k))) for k in keywords['FR']]}
            if 'EN' in keywords:
                if keywords['EN']:
                    query['KEYWORDS.EN'] = {'$in': [re.compile(re.escape(str(k))) for k in keywords['EN']]}

        if union:
            query = {'$or': [{k: query[k]} for k in query]}

        return self.usls.find(query)

    def most_recent(self, number):
        return list(itertools.islice(self.usls.find().sort("LAST_MODIFIED", 1), number))

    def _check_tags(self, tags, all_present=True, except_id=None):
        if not check_tags(tags, all_present=all_present):
            raise InvalidTags(tags)

        for l in tags:
            entry = self.get(tag=tags[l], language=l)
            if entry and entry['_id'] != except_id:
                raise DuplicateTag(tags[l])

        return True

    def drop(self):
        self.usls.drop()

    def _generate_id(self):
        free = False
        while not free:
            _id = uuid.uuid4().hex
            free = self.usls.find_one({'_id': _id}) is None
        return _id

    def _is_editable(self, entry):
        return entry['TEMPLATES'] == [] and entry['PARENTS'] == []