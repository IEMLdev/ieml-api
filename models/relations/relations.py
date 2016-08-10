import os
import random

from pymongo.errors import DuplicateKeyError

from helpers.metaclasses import Singleton
from models.base_queries import DBConnector
from models.constants import RELATIONS_COLLECTION, ROOT_PARADIGM_TYPE, SINGULAR_SEQUENCE_TYPE, PARADIGM_TYPE, \
    RELATIONS_LOCK_COLLECTION
from models.exceptions import NotAParadigm, RootParadigmIntersection, \
    ParadigmAlreadyExist, RootParadigmMissing, SingularSequenceAlreadyExist, NotASingularSequence, TermNotFound, \
    CollectionAlreadyLocked
import logging


class RelationsConnector(DBConnector, metaclass=Singleton):
    def __init__(self):
        super().__init__()
        self.relations = self.db[RELATIONS_COLLECTION]
        self.relations_lock = self.db[RELATIONS_LOCK_COLLECTION]

    def lock_status(self):
        return self.relations_lock.find_one({'_id': 0}, {'role': 1, 'pid': 1})

    def set_lock(self, role):
        pid = os.getpid()
        try:
            self.relations_lock.insert({'_id': 0, 'pid': pid, 'role': role})
        except DuplicateKeyError:
            status = self.lock_status()
            if status:
                raise CollectionAlreadyLocked(status['pid'], status['role'])

    def free_lock(self, force=False):
        status = self.lock_status()
        if status is None:
            return True

        pid = os.getpid()
        if status['pid'] != pid and not force:
            logging.error('Error deleting the relations collection, the lock belong to process id:%d for role:%s.'%(status['pid'], status['role']))
            return False
        else:
            request = {'_id': 0}
            if not force:
                request['pid'] = pid
            return self.relations_lock.delete_one(request).deleted_count == 1


    def get_script(self, script):
        """
        Get the relations collection entry for the given script.
        :param script: the script to get, str or Script instance.
        :return: the script entry.
        """
        entry = self.relations.find_one({"_id": str(script)})
        if not entry:
            raise TermNotFound(str(script))

        return entry

    def exists(self, script):
        try:
            self.get_script(script)
        except TermNotFound:
            return False
        else:
            return True

    def singular_sequences(self, paradigm=None):
        """
        Get all singular sequences of the all terms or of a given paradigm.
        :param paradigm: optional, the paradigm to get the singular sequence, if not, get all the singular sequence of
        the saved script.
        :return: a list of singular sequences.
        """
        if paradigm:
            return self.relations.find({'_id': paradigm})['SINGULAR_SEQUENCES']

        result = list((self.relations.aggregate([
            {'$match': {'TYPE': ROOT_PARADIGM_TYPE}},
            {'$unwind': '$SINGULAR_SEQUENCES'},
            {'$group': {'_id': 0, 'RESULT': {'$push': '$SINGULAR_SEQUENCES'}}},
        ])))

        if result:
            return result[0]['RESULT']
        else:
            return []

    def save_script(self, script_ast, root=False):
        """
        Save a script in the relation collection.
        :param script_ast: the Script instance to save.
        :param root: if this script is a root paradigm.
        :return: None
        """
        if script_ast.paradigm:
            self.save_paradigm(script_ast, root=root)
        else:
            self._save_singular_sequence(script_ast)

    def remove_script(self, script_ast):
        """
        Remove a script from the relations collection.
        :param script_ast: the script to remove
        :return: None
        """
        if not self.exists(script_ast):
            logging.warning("Deletion of a non existent script %s from the collection relation." % str(script_ast))
            return

        self.relations.remove({'_id': str(script_ast)})

    def save_paradigm(self, script_ast, root=False):
        """
        Save a paradigm to the database.

        :param script_ast: the string of the script or an Script object.
        :param root: true if the paradigm is a root paradigm
        :return: None
        """
        if not script_ast.paradigm:
            raise NotAParadigm(script_ast)

        if root:
            self._save_root_paradigm(script_ast)
        else:
            self._save_paradigm(script_ast)

    def _save_singular_sequence(self, script_ast):
        """
        Save a singular sequence (not a paradigm)
        :param script_ast: the script to save
        :return: None
        """
        # check if a singular sequence
        if script_ast.cardinal != 1:
            raise NotASingularSequence(script_ast)

        # check if already exist
        if self.exists(script_ast):
            raise SingularSequenceAlreadyExist(script_ast)

        # get all the singular sequence of the db to see if the singular sequence can be created
        if str(script_ast) not in self.singular_sequences():
            raise RootParadigmMissing(script_ast)

        # save the singular sequence
        insertion = {
            '_id': str(script_ast),
            'TYPE': SINGULAR_SEQUENCE_TYPE,
            'ROOT': self._compute_root(script_ast),
            'RELATIONS': {},
            'LAYER': script_ast.layer,
            'SINGULAR_SEQUENCES': [str(script_ast)]
        }
        self.relations.insert(insertion)

    def _save_root_paradigm(self, script_ast):
        """
         Save a root paradigm :
            - save the root paradigm
            - save all the singular sequence

        :param script_ast: the paradigm ast
        :return: None
        """
        # defensive check

        # check if paradigm already saved.

        if self.exists(script_ast):
            raise ParadigmAlreadyExist(script_ast)

        # get all the singular sequence of the db to avoid intersection
        if set.intersection(set(str(seq) for seq in script_ast.singular_sequences), self.singular_sequences()):
            raise RootParadigmIntersection(script_ast,
                                           set(str(seq) for seq in script_ast.singular_sequences) & set(self.singular_sequences()))

        # save the root paradigm
        insertion = {
            '_id': str(script_ast),
            'TYPE': ROOT_PARADIGM_TYPE,
            'ROOT': str(script_ast),
            'RELATIONS': {},
            'LAYER': script_ast.layer,
            'SINGULAR_SEQUENCES': [str(seq) for seq in script_ast.singular_sequences]
        }
        self.relations.insert(insertion)

    def _save_paradigm(self, script_ast):
        """
        Save a non-root paradigm.
        :param script_ast: the paradigm to save.
        :return: None
        """
        # defensive check
        if self.exists(script_ast):
            raise ParadigmAlreadyExist(script_ast)

        # get all the singular sequence of the db to check if we can create the paradigm
        if not set(str(seq) for seq in script_ast.singular_sequences).issubset(self.singular_sequences()):
            raise RootParadigmMissing(script_ast)

        insertion = {
            '_id': str(script_ast),
            'TYPE': PARADIGM_TYPE,
            'ROOT': self._compute_root(script_ast),
            'RELATIONS': {},
            'LAYER': script_ast.layer,
            'SINGULAR_SEQUENCES': [str(seq) for seq in script_ast.singular_sequences]
        }
        self.relations.insert(insertion)

    def _compute_root(self, script_ast):
        """
        Prerequisite root exist in the collection.
        :param script_ast:
        :return:
        """

        result = self.relations.find_one({
            'TYPE': ROOT_PARADIGM_TYPE,
            'SINGULAR_SEQUENCES': {'$all': [str(seq) for seq in script_ast.singular_sequences]}})
        if result is None:
            raise RootParadigmMissing(script_ast)

        return result['_id']
