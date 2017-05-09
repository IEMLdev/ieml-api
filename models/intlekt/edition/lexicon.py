import uuid

from ieml.ieml_objects.tools import ieml
from ieml.ieml_objects.words import Word
from models.commons import DBConnector
from models.constants import LEXICONS_COLLECTION


class LexiconConnector(DBConnector):
    def __init__(self):
        super().__init__()
        self.lexicon = self.db[LEXICONS_COLLECTION]

        # ensure unique names
        if LEXICONS_COLLECTION not in self.db.collection_names() or \
                        "name_index" not in self.lexicon.index_information():
            self.lexicon.create_index('name', unique=True, name="name_index")

    def all_lexicons(self):
        return [{
            'id': g['_id'],
            'name': g['name'],
            'nb_words': len(g['words'])
                } for g in self.lexicon.find()]

    def get(self, name=None, id=None):
        """
        Return the lexicon entry with this id or name.
        :param name: the name of the lexicon
        :param id: the id of the lexicon
        :return: the lexicon entry
        """
        if name is not None:
            request = {'name': str(name)}
        elif id is not None:
            request = {'_id': str(id)}
        else:
            raise ValueError("Unsupported arguments, please supply name or id for getting a lexicon. "
                             "Accepts string arguments")

        lexicon = self.lexicon.find_one(request)
        if lexicon is None:
            raise ValueError("No lexicon indexed with " + ("name: %s"%name if name is not None else "id: %s"%id))

        return {'id': lexicon['_id'],
                'name': lexicon['name'],
                'words': lexicon['words']}

    def add_lexicon(self, name):
        """
        Add a lexicon to the db with this name.
        :param name: name of the new lexicon
        :return: the id of the newly created lexicon
        """
        result = self.lexicon.insert_one({
            '_id': str(uuid.uuid4()),
            'name': name,
            'words': []
        })

        return result.inserted_id

    def remove_lexicon(self, name=None, id=None):
        """
        Remove one lexicon from the collection.
        :param name: the name of the lexicon
        :param id: the id of the lexicon
        :return: True if the lexicon is deleted
        """
        lexicon = self.get(name=name, id=id)

        result = self.lexicon.delete_one({'_id': lexicon['id']})
        return result.deleted_count == 1

    def add_words(self, words, id):
        """
        Add a iterable of words to the id lexicon.
        :param words: the iterable of words to add
        :param id: the lexicon id to add the words
        :return: the number of words inserted
        """
        try:
            words = list(words)
        except TypeError:
            raise ValueError("Must be a list of words")

        words = list(map(str, map(ieml, words)))

        result = self.lexicon.update_one({'_id': id}, {'$addToSet': {'words': {'$each': words}}})

        return result.modified_count == 1

    def remove_words(self, words, id):
        """
        Remove a iterable of words of the id lexicon.
        :param words: the iterable of words to remove
        :param id: the lexicon id to add the words
        :return: the number of words removed
        """
        try:
            words = list(words)
        except TypeError:
            raise ValueError("Must be a list of words")

        words = list(map(str, map(ieml, words)))

        result = self.lexicon.update_one({'_id': id}, {'$pull': {'words': {'$in': words}}})

        return result.modified_count == 1

    def drop(self):
        self.lexicon.drop()