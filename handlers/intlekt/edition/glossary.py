from handlers.commons import ieml_term_model, exception_handler
from models.intlekt.edition.glossary import GlossaryConnector


@exception_handler
def get_glossary_list(split=None):
    # print(split)

    if split is not None:
        return {'success': True,
                'favorites': GlossaryConnector().all_glossaries(favorite=True),
                'others': GlossaryConnector().all_glossaries(favorite=False)}
    else:
        return {
            'success': True,
            'glossaries': sorted(GlossaryConnector().all_glossaries(), key=lambda g: g['name'])}


@exception_handler
def set_glossary_favorite(body):
    names = body['names']
    GlossaryConnector().set_favorites(names)
    return {'success': True}


@exception_handler
def new_glossary(body):
    name = body['name']
    id = GlossaryConnector().add_glossary(name)

    return {'success': True, 'id': id}


@exception_handler
def delete_glossary(body):
    id = body['id']
    success = GlossaryConnector().remove_glossary(id=id)

    return {'success': success}


@exception_handler
def add_term_to_glossary(glossary_id, body):
    term = body['term']

    modified = GlossaryConnector().add_terms([term], id=glossary_id)
    if modified:
        return {'success': True}
    else:
        return {'success': False, 'message': 'Term "%s" already present in this glossary.'%term}


@exception_handler
def remove_terms_to_glossary(glossary_id, body):
    terms = list(body['terms'])

    GlossaryConnector().remove_terms(terms, id=glossary_id)
    return {'success': True}

@exception_handler
def get_terms_of_glossary(glossary_id):
    glossary = GlossaryConnector().get(id=glossary_id)

    return {'success': True,
            'terms': sorted((ieml_term_model(t) for t in glossary['terms']),
                            key=lambda c: c['INDEX']),
            'id': glossary['id'],
            'name': glossary['name']}

