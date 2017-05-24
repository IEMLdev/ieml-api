import uuid

from ieml.ieml_objects.terms import Term
from ieml.ieml_objects.tools import term
from models.commons import DBConnector
from models.constants import GLOSSARIES_COLLECTION


class GlossaryConnector(DBConnector):
    def __init__(self):
        super().__init__()
        self.glossary = self.db[GLOSSARIES_COLLECTION]

        # ensure unique names
        if GLOSSARIES_COLLECTION not in self.db.collection_names() or \
                        "name_index" not in self.glossary.index_information():
            self.glossary.create_index('name', unique=True, name="name_index")

    def all_glossaries(self):
        return [{
            'id': g['_id'],
            'name': g['name'],
            'nb_terms': len(g['terms'])
                } for g in self.glossary.find()]

    def get(self, name=None, id=None):
        """
        Return the glossary entry with this id or name.
        :param name: the name of the glossary
        :param id: the id of the glossary
        :return: the glossary entry
        """
        if name is not None:
            request = {'name': str(name)}
        elif id is not None:
            request = {'_id': str(id)}
        else:
            raise ValueError("Unsupported arguments, please supply name or id for getting a glossary. "
                             "Accepts string arguments")

        glossary = self.glossary.find_one(request)
        if glossary is None:
            raise ValueError("No glossary indexed with " + ("name: %s"%name if name is not None else "id: %s"%id))

        return {'id': glossary['_id'],
                'name': glossary['name'],
                'terms': glossary['terms']}

    def add_glossary(self, name):
        """
        Add a glossary to the db with this name.
        :param name: name of the new glossary
        :return: the id of the newly created glossary
        """
        result = self.glossary.insert_one({
            '_id': str(uuid.uuid4()),
            'name': name,
            'terms': []
        })

        return result.inserted_id

    def remove_glossary(self, name=None, id=None):
        """
        Remove one glossary from the collection.
        :param name: the name of the glossary
        :param id: the id of the glossary
        :return: True if the glossary is deleted
        """
        glossary = self.get(name=name, id=id)

        result = self.glossary.delete_one({'_id': glossary['id']})
        return result.deleted_count == 1

    def add_terms(self, terms, id):
        """
        Add a iterable of terms to the id glossary.
        :param terms: the iterable of terms to add
        :param id: the glossary id to add the terms
        :return: the number of terms inserted
        """
        try:
            terms = list(terms)
        except TypeError:
            raise ValueError("Must be a list of terms")

        terms = list(map(str, map(term, terms)))

        result = self.glossary.update_one({'_id': id}, {'$addToSet': {'terms': {'$each': terms}}})

        return result.modified_count == 1

    def remove_terms(self, terms, id):
        """
        Remove a iterable of terms of the id glossary.
        :param terms: the iterable of terms to remove
        :param id: the glossary id to add the terms
        :return: the number of terms removed
        """
        try:
            terms = list(terms)
        except TypeError:
            raise ValueError("Must be a list of terms")

        terms = list(map(str, map(term, terms)))

        result = self.glossary.update_one({'_id': id}, {'$pull': {'terms': {'$in': terms}}})

        return result.modified_count == 1

    def drop(self):
        self.glossary.drop()