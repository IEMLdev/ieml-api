from .base_queries import DBConnector, Tag
from .constants import TEXT_COLLECTION, HYPERTEXT_COLLECTION, TAG_LANGUAGES
from .exceptions import InvalidTags, TextAlreadyExists, HypertextAlreadyExists
from ieml.ieml_objects import Hypertext, Text
import re
from pymongo.errors import DuplicateKeyError


class TextQueries(DBConnector):
    def __init__(self):
        super().__init__()
        self.texts = self.db[TEXT_COLLECTION]

    def _write_text_to_db(self, text, tags):
        try:
            self.texts.insert_one({
                "_id" : str(text),
                "TAGS" : tags,
                "PROPOSITIONS" : [str(e) for e in text.children]
            })
        except DuplicateKeyError:
            raise TextAlreadyExists()

    def get_text_from_ieml(self, text_ieml):
        return self.texts.find_one({"_id" : text_ieml})

    def exact_text_search(self, ieml):
        return self.texts.find_one({"_id": str(ieml)})

    def save_text(self, text, tags):
        if self.exact_text_search(str(text)) is not None:
            raise TextAlreadyExists()

        self._write_text_to_db(text, tags)

    def search_text(self, search_string):
        regex = re.compile(re.escape(search_string))
        result = self.texts.find({'$or': [
                        {'_id': {'$regex': regex}},
                        {'TAGS.FR': {'$regex': regex}},
                        {'TAGS.EN': {'$regex': regex}}]})
        return list(result)

    def check_tag_exist(self, tag, language):
        return self.texts.find_one({'TAGS.' + language: tag}) is not None

    def update_tags(self, ieml, tags_dict):
        """Updates the tag of a text identified by the input IEML"""
        self.texts.update_one({'_id': ieml},
                              {'$set': {'TAGS': tags_dict}})


class HyperTextQueries(TextQueries):
    def __init__(self):
        super().__init__()
        self.hypertexts = self.db[HYPERTEXT_COLLECTION]

    def _write_hypertext_to_db(self, hypertext, tags):
        try:
            self.hypertexts.insert_one({
                "TAGS": tags,
                "_id": str(hypertext),
                "TEXTS": [str(t) for t in hypertext.texts],
                "HYPERLINK": [
                    {
                        'substance': transition[0],
                        'attribute': transition[1],
                        'mode': {
                            'PATH': transition[2].to_ieml_list(),
                            'LITERAL': transition[3]
                        }
                    } for transition in hypertext.transitions
                ]
            })
        except DuplicateKeyError:
            raise HypertextAlreadyExists()

    def exact_hypertext_search(self, ieml):
        return self.hypertexts.find_one({"_id": str(ieml)})

    def save_hypertext(self, hypertext, tag):
        if self.exact_hypertext_search(str(hypertext)) is not None:
            raise HypertextAlreadyExists()

        self._write_hypertext_to_db(hypertext, tag)

    def get_hypertext_from_ieml(self, ieml_string):
        self.hypertexts.find_one({"_id": ieml_string})

    def check_tags_available(self, tags):
        for language in tags:
            if self.check_tag_exist(tags[language], language):
                return False
        return True

    def check_tag_exist(self, tag, language):
        return self.texts.find_one({'TAGS.' + language: tag}) is not None and super().check_tag_exist(tag, language)

    def update_tags(self, ieml, tags_dict):
        """Updates the tag of a text identified by the input IEML"""
        self.hypertexts.update_one({'_id': ieml},
                                   {'$set': {'TAGS': tags_dict}})

    def _format_response(self, response, hypertext=True):
        return {
            "IEML": response['_id'],
            "TAGS": response['TAGS'],
            "TYPE": "HYPERTEXT" if hypertext else "TEXT"
        }

    def search_request(self, search_string, languages, levels):
        query = {}
        regex = {'$regex': re.compile(re.escape(search_string))}

        conditions = [{'_id': regex}]
        if languages:
            for language in languages:
                conditions.append({'TAGS.' + language: regex})
        else:
            for language in TAG_LANGUAGES:
                conditions.append({'TAGS.' + language: regex})

        query['$or'] = conditions

        result = []
        if levels is None or Hypertext in levels:
            result = [self._format_response(entry, False) for entry in self.hypertexts.find(query)]

        if levels is None or Text in levels:
            result.extend([self._format_response(entry, False) for entry in self.texts.find(query)])

        return result
