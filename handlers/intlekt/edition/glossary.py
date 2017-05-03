from handlers.commons import ieml_term_model, exception_handler
from models.intlekt.edition.glossary import GlossaryConnector


@exception_handler
def get_glossary_list():
    return {'success': True, 'glossaries': GlossaryConnector().all_glossaries()}


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
def add_terms_to_glossary(glossary_id, body):
    terms = list(body['terms'])

    GlossaryConnector().add_terms(terms, id=glossary_id)
    return {'success': True}


@exception_handler
def remove_terms_to_glossary(glossary_id, body):
    terms = list(body['terms'])

    GlossaryConnector().remove_terms(terms, id=glossary_id)
    return {'success': True}


def get_terms_of_glossary(glossary_id):
    return {'success': True,
            'terms': [ieml_term_model(t) for t in GlossaryConnector().get(id=glossary_id)['terms']]}
