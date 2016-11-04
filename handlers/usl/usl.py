from collections import defaultdict

from models.exceptions import USLNotFound
from handlers.commons import exception_handler
from ieml.usl import usl
from models.usls.usls import USLConnector


@exception_handler
def save_usl(body):
    _usl = usl(body['ieml'])
    tags = {'FR': body['tags']['fr'], 'EN': body['tags']['en']}
    keywords = defaultdict(lambda : list())
    if 'keywords' in body:
        if 'fr' in body['keywords']:
            keywords['FR'] = body['keywords']['fr']
        if 'en' in body['keywords']:
            keywords['EN'] = body['keywords']['en']

    _id = USLConnector().save(_usl, tags=tags, keywords=keywords)
    return {'success': True, 'id': _id}


@exception_handler
def get_usl_ieml(ieml):
    _usl = USLConnector().get(usl=ieml)
    if not _usl:
        raise USLNotFound(ieml)

    return {'success': True,
            'id': _usl['_id'],
            'ieml': _usl['USL']['IEML'],
            'tags': _usl['TAGS'],
            'keywords': _usl['KEYWORDS']}


@exception_handler
def get_usl_id(id):
    _usl = USLConnector().get(id=id)
    if not _usl:
        raise USLNotFound(id)

    return {'success': True,
            'id': _usl['_id'],
            'ieml': _usl['USL']['IEML'],
            'tags': _usl['TAGS'],
            'keywords': _usl['KEYWORDS']}


@exception_handler
def delete_usl(id):
    USLConnector().remove(id=id)
    return {'success': True}


@exception_handler
def query_usl(fr=None, en=None, fr_keywords=None, en_keywords=None, query=None):
    _query = {}

    if query:
        fr = query
        en = query
        fr_keywords = [query]
        en_keywords = [query]
        _query['union'] = True

    if fr or en:
        _query['tags'] = {}
        if fr:
            _query['tags']['FR'] = fr
        if en:
            _query['tags']['EN'] = en

    if fr_keywords or en_keywords:
        _query['keywords'] = {}
        if fr_keywords:
            _query['keywords']['FR'] = list(fr_keywords)
        if en_keywords:
            _query['keywords']['EN'] = list(en_keywords)

    result = USLConnector().query(**_query)

    return {'success': True,
            'match': [{
                'id': e['_id'],
                'ieml': e['USL']['IEML'],
                'tags': e['TAGS'],
                'keywords': e['KEYWORDS']} for e in result]}


@exception_handler
def update_usl(id, body):
    query = {}

    if 'ieml' in body:
        query['usl'] = body['ieml']

    if 'tags' in body:
        if 'fr' in body['tags'] or 'en' in body['tags']:
            query['tags'] = {}
            if 'fr' in body['tags']:
                query['tags']['FR'] = body['tags']['fr']
            if 'en' in body['tags']:
                query['tags']['EN'] = body['tags']['en']

    if 'keywords' in body:
        query['keywords'] = {}
        if 'fr' in body['keywords']:
            query['keywords']['FR'] = list(body['keywords']['fr'])
        if 'en' in body['keywords']:
            query['keywords']['EN'] = list(body['keywords']['en'])

    USLConnector().update(id=id, **query)

    return {'success': True}