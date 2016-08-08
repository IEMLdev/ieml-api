from ieml.parsing.script.parser import ScriptParser
from ieml.script.tools import factorize
from models.base_queries import DBConnector, Tag
from models.constants import TERMS_COLLECTION, TAG_LANGUAGES
from models.exceptions import InvalidInhibitArgument, InvalidScript, InvalidTags, TermAlreadyExists, InvalidMetadata,\
    CantRemoveNonEmptyRootParadigm, TermNotFound, DuplicateTag
from ieml.script.constants import INHIBIT_RELATIONS
from ieml.script import Script
from models.relations.relations_queries import RelationsQueries
from models.relations.relations import RelationsConnector
import logging
import progressbar


class TermsConnector(DBConnector):
    def __init__(self):
        super().__init__()
        self.terms = self.db[TERMS_COLLECTION]
        self.parser = ScriptParser()

    def get_term(self, script):
        """
        Return the document from the term collection associated with this script.
        :param script: the script to get.
        :return: the document or None
        """
        return self.terms.find_one({'_id': str(script)})

    def get_all_terms(self):
        """
        Returns all the terms contained in the term database
        :return: a list of dictionaries corresponding to the documents
        """
        return self.terms.find()

    def add_term(self, script_ast, tags, inhibits, root=False, metadata=None, recompute_relations=True):
        """
        Save a term in the term collection and update the relations collection accordingly.
        :param script_ast: the script to save.
        :param tags: the tags of this term.
        :param inhibits: the inhibition of the relations for this term.
        :param root: if this term is a root paradigm.
        :param metadata: a dict of metadata (must be serializable)
        :param recompute_relations: if we must recompute the relations after the insertion.
        :return: None
        """

        # make sure to save the factorised form
        script_ast = factorize(script_ast)

        self._check_tags(tags)

        # update the relations of the paradigm in the relation collection
        RelationsQueries.save_script(script_ast, self.get_inhibitions(), root=root, recompute_relations=recompute_relations)

        self._save_term(script_ast, tags, inhibits, root, metadata)

    def save_multiple_terms(self, list_terms, recompute_relations=True):
        """
        Save a list of terms, more efficient than multiple call of save_term for multiple term saving. This method avoid
        extra relations computations.
        :param list_terms: the list of term to save. The list element must be following the given pattern :
         [ {
            'AST' : Script (the script to save),
            'ROOT': bool (if the script is a root paradigm),
            'TAGS': {'FR' : str,
                     'EN' : str } (the tags),
            'INHIBITS': list of str (the list of relation to inhibit),
            'METADATA': dict
         ]
         :param recompute_relations: default True, if after adding the terms a recomputation of relation is performed.
        :return:
        """

        roots = [e for e in list_terms if e['ROOT']]
        other = [e for e in list_terms if not e['ROOT']]

        for r in roots:
            self.add_term(r['AST'], r['TAGS'], root=True, inhibits=r['INHIBITS'], metadata=r['METADATA'], recompute_relations=False)

        for o in other:
            self.add_term(o['AST'], o['TAGS'], root=False, inhibits=o['INHIBITS'], metadata=o['METADATA'], recompute_relations=False)

        if recompute_relations:
            self.recompute_relations()

    def remove_term(self, script_ast, remove_roots_child=True, recompute_relations=True):
        """
        Remove the given term from the term and relation collection. Can fail if not possible (can't remove a non-empty
        root paradigm)
        :param script_ast: the script to remove.
        :param remove_roots_child: if we remove a root paradigm, we remove the contained of the root paradigm.
        :param recompute_relations: if the relations have to be recomputed after the removal.
        :return: None
        """
        # Argument check
        if not isinstance(script_ast, Script):
            raise InvalidScript()

        term = self.get_term(script_ast)
        if term is None:
            logging.warning("Deletion of a non existent term %s in the collection terms." % str(script_ast))
            return

        if not RelationsQueries.check_removable(script_ast):
            if not remove_roots_child:
                raise CantRemoveNonEmptyRootParadigm(script_ast)

            # all the contained script without the root paradigm.
            paradigm = (self.parser.parse(p['_id']) for p in RelationsQueries.paradigm(script_ast) if p['_id'] != str(script_ast))

            # remove all the paradigm without recomputing the relations
            for p in paradigm:
                self.terms.remove({'_id': str(p)})
                RelationsQueries.remove_script(p, self.get_inhibitions(), recompute_relations=False)

        # remove the root paradigm
        self.terms.remove({'_id': str(script_ast)})
        RelationsQueries.remove_script(script_ast, self.get_inhibitions(), recompute_relations=recompute_relations)

    def update_term(self, script, tags=None, inhibits=None, root=None, metadata=None, recompute_relations=True):
        """
        Update the term and relation collection for this term.
        :param script: the script to update
        :param tags: optional, the tags to update
        :param inhibits: optional, the inhibition to update
        :param root: optional, the rootness to update
        :param metadata: optional, the metadata to update
        :param recompute_relations: if the relation must be recomputed after the update.
        :return: None
        """
        if not self.get_term(script):
            raise TermNotFound(script)

        update = {}
        if tags and self._check_tags(tags):
            update['TAGS'] = tags

        if root:
            update['ROOT'] = bool(root)

        if inhibits and isinstance(inhibits, list) and all(r in INHIBIT_RELATIONS for r in inhibits):
            update['INHIBITS'] = inhibits

        if metadata and isinstance(metadata, dict):
            update['METADATA'] = metadata

        if len(update) != 0:
            self.terms.update({'_id': str(script)}, {'$set': update})

            # the inhibition and rootness impact the relations
            if inhibits or root:
                RelationsQueries.update_script(script, self.get_inhibitions(), root, recompute_relations=recompute_relations)
        else:
            logging.warning("No update performed for script " + str(script) +
                            ", no argument are matching the update criteria.")

    def root_paradigms(self, ieml_only=False):
        """
        Get all the roots paradigms stored in this collections.
        :param ieml_only: if True, return a list of the ieml string of the paradigms
        :return: a list of root paradigm documents
        """
        roots = self.terms.find({'ROOT': True})
        if ieml_only:
            return [elem['_id'] for elem in roots]
        return list(roots)

    def _save_term(self, script_ast, tags, inhibits, root=False, metadata=None):
        """
        Save a term, do all coherence checking.
        :param script_ast: the script to save
        :param tags: tags of the script
        :param inhibits: the inhibition
        :param root: if this script is root
        :param metadata: the metadata
        :return: None
        """

        # Argument check
        if not isinstance(script_ast, Script):
            raise InvalidScript()

        if not isinstance(inhibits, list) or any(r not in INHIBIT_RELATIONS for r in inhibits):
            raise InvalidInhibitArgument()

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

    def get_inhibitions(self):
        paradigms = self.terms.find({'ROOT': True, 'INHIBITS': {'$ne': []}})
        return [(p['_id'], p['INHIBITS']) for p in paradigms]

    def search_by_tag(self, tag, language=None):
        """
        returns a list of terms with a matching tag for a
        :param tag: value of the tested tag
        :param language: language of the tag
        :return: list of
        """
        #TODO : IMPROVE THIS
        if language is None:
            return self.terms.find({
                'TAG.%s'%language: tag for language in TAG_LANGUAGES})

        return self.terms.find({"TAGS.%s" % language : tag })

    def recompute_relations(self, all_delete=False):
        """
        Recompute all the relation in the relation collection.
        :param all_delete: if true, the relation collection is recomputed from the term collection.
        :return: None
        """
        if all_delete:
            rc = RelationsConnector()
            rc.relations.drop()

            RelationsQueries.save_multiple_script(
                [{'AST': self.parser.parse(t['_id']),
                  'ROOT': t['ROOT']} for t in self.get_all_terms()], self.get_inhibitions())

        else:
            RelationsQueries.compute_all_relations(paradigms=self.root_paradigms())

    def _check_tags(self, tags):
        if not Tag.check_tags(tags):
            raise InvalidTags()

        for l in tags:
            if self.search_by_tag(tags[l], language=l).count() != 0:
                raise DuplicateTag(tags[l])

        return True