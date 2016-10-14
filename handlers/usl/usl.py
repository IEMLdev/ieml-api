from collections import defaultdict

from exceptions import USLNotFound
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

    USLConnector().save(_usl, tags=tags, keywords=keywords)
    return {'success': True}


@exception_handler
def get_usl(ieml):
    _usl = USLConnector().get(usl=ieml)
    if not _usl:
        raise USLNotFound(ieml)

    return {'success': True,
            'ieml': _usl['IEML'],
            'tags': _usl['TAGS'],
            'keywords': _usl['KEYWORDS']}

@exception_handler
def delete_usl(ieml):
    USLConnector().remove(ieml)
    return {'success': True}


@exception_handler
def query_usl(fr=None, en=None, fr_keywords=None, en_keywords=None):
    query = {}

    if fr or en:
        query['tags'] = {}
        if fr:
            query['tags']['FR'] = fr
        if en:
            query['tags']['EN'] = en

    if fr_keywords or en_keywords:
        query['keywords'] = {}
        if fr_keywords:
            query['keywords']['FR'] = list(fr_keywords)
        if en_keywords:
            query['keywords']['FR'] = list(en_keywords)

    result = USLConnector().query(**query)

    return {'success': True,
            'match': [{
                'ieml': e['IEML'],
                'tags': e['TAGS'],
                'keywords': e['KEYWORDS']} for e in result]}


@exception_handler
def update_usl(ieml, body):
    query = {}
    if 'fr' in body or 'en' in body:
        query['tags'] = {}
        if 'fr' in body:
            query['tags']['FR'] = body['fr']
        if 'en' in body:
            query['tags']['EN'] = body['en']

    if 'keywords' in body:
        query['keywords'] = {}
        if 'fr' in body['keywords']:
            query['keywords']['FR'] = list(body['keywords']['fr'])
        if 'en' in body['keywords']:
            query['keywords']['EN'] = list(body['keywords']['en'])

    USLConnector().update(usl=ieml, **query)

    return {'success': True}