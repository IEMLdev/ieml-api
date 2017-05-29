from handlers.commons import exception_handler
from ieml.usl import usl
from models.usls.library import LibraryConnector


@exception_handler
def save_usl(body):
    _usl = usl(body['ieml'])
    tags = {'FR': body['tags']['fr'], 'EN': body['tags']['en']}
    _id = LibraryConnector().save(_usl, translations=tags)
    return {'success': True, 'id': _id}


@exception_handler
def get_usl_ieml(ieml):
    _usl = LibraryConnector().get(usl=ieml)
    if not _usl:
        raise ValueError("Usl not found in the library with ieml: %s"%str(ieml))

    return {'success': True,
            'id': _usl['_id'],
            'ieml': _usl['USL']['IEML'],
            'translations': _usl['TRANSLATIONS']}


@exception_handler
def get_usl_id(id):
    _usl = LibraryConnector().get(id=id)
    if not _usl:
        raise ValueError("Usl not found in the library with id: %s" % str(id))

    return {'success': True,
            'id': _usl['_id'],
            'ieml': _usl['USL']['IEML'],
            'tags': _usl['TRANSLATIONS']}


@exception_handler
def delete_usl(id):
    LibraryConnector().remove(id=id)
    return {'success': True}


@exception_handler
def query_usl(fr=None, en=None, query=None):
    _query = {}

    if query:
        fr = query
        en = query
        _query['union'] = True

    if fr or en:
        _query['translations'] = {}
        if fr:
            _query['translations']['FR'] = fr
        if en:
            _query['translations']['EN'] = en

    result = LibraryConnector().query(**_query)

    return {'success': True,
            'match': [{
                'id': e['_id'],
                'ieml': e['USL']['IEML'],
                'translations': e['TRANSLATIONS']} for e in result]}


@exception_handler
def update_usl(id, body):
    query = {}

    if 'ieml' in body:
        query['usl'] = usl(body['ieml'])

    if 'translations' in body:
        if 'fr' in body['translations'] or 'en' in body['translations']:
            query['translations'] = {}
            if 'fr' in body['translations']:
                query['translations']['FR'] = body['translations']['fr']
            if 'en' in body['tags']:
                query['translations']['EN'] = body['translations']['en']

        LibraryConnector().update(id=id, **query)

    return {'success': True}