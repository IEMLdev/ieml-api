import functools
import os
import random

import pymongo.errors

from helpers.metaclasses import Singleton
from models.base_queries import DBConnector
from models.constants import RELATIONS_COLLECTION, ROOT_PARADIGM_TYPE, SINGULAR_SEQUENCE_TYPE, PARADIGM_TYPE, \
    RELATIONS_LOCK_COLLECTION, DROP_RELATIONS, SCRIPT_INSERTION, SCRIPT_DELETION
from models.exceptions import NotAParadigm, RootParadigmIntersection, \
    ParadigmAlreadyExist, RootParadigmMissing, SingularSequenceAlreadyExist, NotASingularSequence, TermNotFound, \
    CollectionAlreadyLocked
import logging


def safe_execution(role):
    """ Decorator to ensure the atomic access at the relation collection
    must be used for any write operation."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*arg, **kwrag):
            key = os.urandom(10)
            try:
                RelationsConnector().set_lock(role, key=key)
                return func(*arg, **kwrag)
            finally:
                RelationsConnector().free_lock(key=key)
        return wrapper
    return decorator


class RelationsConnector(DBConnector, metaclass=Singleton):
    def __init__(self):
        super().__init__()
        self.relations = self.db[RELATIONS_COLLECTION]
        self.relations_lock = self.db[RELATIONS_LOCK_COLLECTION]

    def lock_status(self):
        """
        Return the status of the lock or None if the lock is free.
        :return: dict of 'role' : the role the application have given to that lock
                         'pid'  : the process id of the lock taker.
        """
        return self.relations_lock.find_one({'_id': 0}, {'role': 1, 'pid': 1, 'key': 1})

    def set_lock(self, role, key=None):
        """
        Try to take the lock with the given role. It must be a string explaining why the lock is taken.
        If we can't take the lock, raise CollectionAlreadyLocked.
        :param role:
        :return:
        """
        pid = os.getpid()
        try:
            self.relations_lock.insert({'_id': 0, 'pid': pid, 'role': role, 'key': (key if key is not None else 0)})
        except pymongo.errors.DuplicateKeyError:
            status = self.lock_status()
            if status:
                if status['pid'] == pid:
                    #update the role
                    self.relations_lock.update({'_id': 0}, {'$set' : {'role': role}})
                    return

                raise CollectionAlreadyLocked(status['pid'], status['role'])

    def free_lock(self, force=False, key=None):
        """
        Try to free the lock. If the lock is already free, do nothing. If the lock belongs to another proccess, do
         nothing and raise a warning.
        :param force: Force delete the lock, even if the process doesn't own it.
        :param key: if specified, the lock must have the same id.
        :return: The success of the free
        """
        status = self.lock_status()
        if status is None:
            return True

        pid = os.getpid()
        if status['pid'] != pid and not force:
            logging.error('Error deleting the relations collection lock, the lock belong to '
                          'process id:%d for role:%s.'%(status['pid'], status['role']))
            return False
        else:
            if key is not None and status['key'] != key and not force:
                return False

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

    @safe_execution(DROP_RELATIONS)
    def empty_collection(self):
        self.relations.drop()

    def singular_sequences(self, paradigm=None):
        """
        Get all singular sequences of the all terms or of a given paradigm.
        :param paradigm: optional, the paradigm to get the singular sequence, if not, get all the singular sequence of
        the saved script.
        :return: a list of singular sequences.
        """
        if paradigm:
            return self.relations.find({'_id': paradigm})['SINGULAR_SEQUENCES']

        result = list(self.relations.aggregate([
            {'$match': {'TYPE': ROOT_PARADIGM_TYPE}},
            {'$unwind': '$SINGULAR_SEQUENCES'},
            {'$group': {'_id': 0, 'RESULT': {'$push': '$SINGULAR_SEQUENCES'}}},
        ]))

        if result:
            return result[0]['RESULT']
        else:
            return []

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
            #TODO : merge SingularSequenceAlreadyExsit and ParadigmAlreadyExist into one ScriptAlreadyExist ?
            raise SingularSequenceAlreadyExist(script_ast)

        # get all the singular sequence of the db to see if the singular sequence can be created
        root_paradigm = self._compute_root(script_ast)

        # save the singular sequence
        insertion = {
            '_id': str(script_ast),
            'TYPE': SINGULAR_SEQUENCE_TYPE,
            'ROOT': root_paradigm,
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
        root_paradigm = self._compute_root(script_ast)

        insertion = {
            '_id': str(script_ast),
            'TYPE': PARADIGM_TYPE,
            'ROOT': root_paradigm,
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
