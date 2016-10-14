from collections import defaultdict

from handlers.commons import exception_handler
from ieml.usl import usl
from models.usls.usls import USLConnector


@exception_handler
def save_usl(body):
    _usl = usl(body['ieml'])
    tags = {'FR': body['fr'], 'EN': body['en']}
    keywords = defaultdict(lambda : list())
    if 'keywords' in body:
        if 'fr' in body['keywords']:
            keywords['FR'] = body['keywords']['fr']
        if 'en' in body['keywords']:
            keywords['EN'] = body['keywords']['en']

    USLConnector().save(_usl, tags=tags, keywords=keywords)
    return {'success': True}


@exception_handler
def get_usl(param):
    _usl = None
    if 'ieml' in param:
        _usl = USLConnector().get(usl=param['ieml'])

    if 'fr' in param:
        _usl = USLConnector().get(tag=param['fr'], language='FR')

    if 'en' in param:
        _usl = USLConnector().get(tag=param['en'], language='EN')

    return {'success': True,
            'ieml': _usl['IEML'],
            'tags': _usl['TAGS'],
            'keywords': _usl['KEYWORDS']}


@exception_handler
def delete_usl(body):
    USLConnector().remove(body['ieml'])
    return {'success': True}


@exception_handler
def query_usl(param):
    query = {}

    if 'fr' in param or 'en' in param:
        query['tags'] = {}
        if 'fr' in param:
            query['tags']['FR'] = param['fr']
        if 'en' in param:
            query['tags']['EN'] = param['en']

    if 'keywords' in param:
        query['keywords'] = {}
        if 'fr' in param['keywords']:
            query['keywords']['FR'] = list(param['keywords']['fr'])
        if 'en' in param['keywords']:
            query['keywords']['EN'] = list(param['keywords']['en'])

    result = USLConnector().query(**query)

    return {'success': True,
            'match': [{
                'ieml': e['IEML'],
                'tags': e['TAGS'],
                'keywords': e['KEYWORDS']} for e in result]}


@exception_handler
def update_usl(body):
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

    USLConnector().update(usl=body['ieml'], **query)

    return {'success': True}