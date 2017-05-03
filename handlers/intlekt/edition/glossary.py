from models.intlekt.edition.glossary import GlossaryConnector


def get_glossary_list():
    return {'success': True, 'glossaries': GlossaryConnector().all_glossaries()}


def new_glossary(body):
    name = body['name']
    id = GlossaryConnector().add_glossary(name)

    return {'success': True, 'id': id}


def delete_glossary(body):
    id = body['id']
    success = GlossaryConnector().remove_glossary(id=id)

    return {'success': success}


def add_terms_to_glossary(glossary_id, body):
    terms = list(body['terms'])

    GlossaryConnector().add_terms(terms, id=glossary_id)
    return {'success': True}


def remove_terms_to_glossary(glossary_id, body):
    terms = list(body['terms'])

    GlossaryConnector().remove_terms(terms, id=glossary_id)
    return {'success': True}


def get_terms_of_glossary(glossary_id):

    return {'success': True,
            'terms': GlossaryConnector().get(id=glossary_id)['terms']}
