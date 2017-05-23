from handlers.commons import exception_handler
from ieml.usl.tools import usl
from models.usls.library import LibraryConnector


@exception_handler
def save_to_library(body):
    id = LibraryConnector().save(body['ieml'], body['translations'])
    return {'success': True, 'id': id}


@exception_handler
def update_usl_translation_from_ieml(ieml, body):
    u = usl(ieml)
    record = LibraryConnector().get(usl=u)
    if record is None:
        raise ValueError("The specified ieml %s doesn't correspond to a previously saved usl."%str(ieml))

    update = {}

    if 'ieml' in body:
        update['usl'] = usl(body['ieml'])

    if 'translations' in body:
        if 'FR' in body['translations'] or 'EN' in body['translations']:
            update['translations'] = {}
            if 'FR' in body['translations']:
                update['translations']['FR'] = body['translations']['FR']
            if 'EN' in body['translations']:
                update['translations']['EN'] = body['translations']['EN']

    if update:
        LibraryConnector().update(id=record['_id'], **update)

    return {'success': True, 'id': record['_id']}