from models.base_queries import DBConnector, Tag
from models.constants import TERMS_COLLECTION
from models.exceptions import InvalidInhibitArgument, InvalidScript, InvalidTags, TermAlreadyExists, InvalidMetadata,\
    CantRemoveNonEmptyRootParadigm
from ieml.script.constants import INHIBIT_RELATIONS
from ieml.script import Script
from models.relations.relations_queries import RelationsQueries
import logging
import progressbar


class TermsConnector(DBConnector):
    def __init__(self):
        super().__init__()
        self.terms = self.db[TERMS_COLLECTION]

    def get_term(self, script):
        return self.terms.find_one({'_id': script if isinstance(script, str) else str(script)})

    def add_term(self, script_ast, tags, inhibits, root=False, metadata=None):
        self._save_term(script_ast, tags, inhibits, root, metadata)

        # update the relations of the paradigm in the relation collection
        RelationsQueries.save_script(script_ast, inhibits=inhibits, root=root)

    def save_multiple_terms(self, list_terms):
        bar = progressbar.ProgressBar(max_value=len(list_terms))

        for i, t in enumerate(list_terms):
            self._save_term(t['AST'], t['TAGS'], t['INHIBITS'], t['ROOT'], t['METADATA'])
            bar.update(i + 1)

        RelationsQueries.save_multiple_script(list_terms)

    def remove_term(self, script_ast):
        # Argument check
        if not isinstance(script_ast, Script):
            raise InvalidScript()

        term = self.get_term(script_ast)
        if term is None:
            logging.warning("Deletion of a non existent term %s in the collection terms." % str(script_ast))
            return

        if not RelationsQueries.check_removable(script_ast):
            raise CantRemoveNonEmptyRootParadigm()

        inhibits = None
        if 'INHIBITS' in term:
            inhibits = term['INHIBITS']

        self.terms.remove({'_id': str(script_ast)})
        RelationsQueries.remove_script(script_ast, inhibits=inhibits)

    def update_term(self, script, tags=None, inhibits=None, root=None, metadata=None):
        if inhibits or root:
            RelationsQueries.update_term(script, inhibits, root)

        update = {}
        if tags and Tag.check_tags(tags):
            update['TAGS'] = tags

        if root:
            update['ROOT'] = bool(root)

        if inhibits and isinstance(inhibits, list) and all(r in INHIBIT_RELATIONS for r in inhibits):
            update['INHIBITS'] = inhibits

        if metadata and isinstance(metadata, dict):
            update['METADATA'] = metadata

        if len(update) != 0:
            self.terms.update({'_id': str(script)}, {'$set': update})
        else:
            logging.warning("No update performed for script " + script + ", no argument are matching the update criteria.")

    def root_paradigms(self):
        return list(self.terms.find({'ROOT': True}))

    def _save_term(self, script_ast, tags, inhibits, root=False, metadata=None):
        # Argument check
        if not isinstance(script_ast, Script):
            raise InvalidScript()

        if not isinstance(inhibits, list) or any(r not in INHIBIT_RELATIONS for r in inhibits):
            raise InvalidInhibitArgument()

        if not Tag.check_tags(tags):
            raise InvalidTags()

        if self.get_term(script_ast) is not None:
            raise TermAlreadyExists()

        root = bool(root)

        insertion = {
            '_id': str(script_ast),
            'TAGS': tags,
            'INHIBITS': inhibits,
            'ROOT': root,
        }

        if metadata:
            if not isinstance(metadata, dict):
                raise InvalidMetadata()

            insertion['METADATA'] = metadata

        self.terms.insert(insertion)
