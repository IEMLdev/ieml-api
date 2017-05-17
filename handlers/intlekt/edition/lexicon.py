from handlers.commons import exception_handler
from handlers.intlekt.edition.visualisation import _ieml_object_to_json
from ieml.ieml_objects.tools import ieml
from models.intlekt.edition.lexicon import LexiconConnector


@exception_handler
def get_lexicon_list():
    return {'success': True, 'lexicons': LexiconConnector().all_lexicons()}


@exception_handler
def new_lexicon(body):
    name = body['name']
    id = LexiconConnector().add_lexicon(name)

    return {'success': True, 'id': id}


@exception_handler
def delete_lexicon(body):
    id = body['id']
    success = LexiconConnector().remove_lexicon(id=id)

    return {'success': success}


@exception_handler
def add_word_to_lexicon(lexicon_id, body):
    word = body['word']

    modified = LexiconConnector().add_words([word], id=lexicon_id)
    if modified:
        return {'success': True}
    else:
        return {'success': False, 'message': 'Word "%s" already present in this lexicon.'%word}


@exception_handler
def remove_words_to_lexicon(lexicon_id, body):
    words = list(body['words'])

    LexiconConnector().remove_words(words, id=lexicon_id)
    return {'success': True}


@exception_handler
def get_words_of_lexicon(lexicon_id):
    lexicon = LexiconConnector().get(id=lexicon_id)

    return {'success': True,
            'terms': [_ieml_object_to_json(ieml(t)) for t in lexicon['words']],
            'id': lexicon['id'],
            'name': lexicon['name']}
