from collections import defaultdict

from handlers.commons import exception_handler
from ieml.usl import usl
from models.usl.usl import USLConnector


@exception_handler
def save_usl(body):
    _usl = usl(body['ieml'])
    tags = {'FR': body['fr'], 'EN': body['en']}
    keywords = None
    if 'keywords' in body:
        keywords = defaultdict(lambda : list())
        if 'fr' in keywords:
            keywords['FR'] = body['keywords']['fr']
        if 'en' in keywords:
            keywords['EN'] = body['keywords']['en']

    USLConnector().save_usl(_usl, tags=tags, keywords=keywords)
    return {'success': True}


@exception_handler
def get_usl(param):
    _usl = None
    if 'ieml' in param:
        _usl = USLConnector().get_usl(usl=param['ieml'])

    if 'fr' in param:
        _usl = USLConnector().get_usl(tag=param['fr'], language='FR')

    if 'en' in param:
        _usl = USLConnector().get_usl(tag=param['en'], language='EN')

    return {'success': True,
            'ieml': _usl['IEML'],
            'tags': _usl['TAGS'],
            'keywords': _usl['KEYWORDS']}


@exception_handler
def delete_usl(body):
    USLConnector().remove_usl(body['usl'])
    return {'success': True}


@exception_handler
def query_usl(param):
    query = {}
    if 'ieml' in param:
        query['IEML'] = param['ieml']

    if 'fr' in param or 'en' in param:
        query['TAGS'] = {}
        if 'fr' in param:
            query['TAGS']['FR'] = param['fr']
        if 'en' in param:
            query['TAGS']['EN'] = param['en']

    result = []

    return {'success': True,
            'match': [{
                'ieml': e['IEML'],
                'tags': e['TAGS'],
                'keywords': e['KEYWORDS']} for e in result]}


@exception_handler
def edit_usl(body):
    return {'success': True}