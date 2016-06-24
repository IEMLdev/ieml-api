from models.base_queries import DBConnector
from models.constants import SCRIPTS_COLLECTION, ROOT_PARADIGM_TYPE, SINGULAR_SEQUENCE_TYPE, PARADIGM_TYPE
from models.exceptions import InvalidScript, NotAParadigm, RootParadigmIntersection, \
    ParadigmAlreadyExist, RootParadigmMissing, SingularSequenceAlreadyExist, NotASingularSequence
from ieml.script import Script
import logging


class RelationsConnector(DBConnector):
    def __init__(self):
        super().__init__()
        self.scripts = self.db[SCRIPTS_COLLECTION]

    def get_script(self, ieml):
        return self.scripts.find_one({"_id": ieml if isinstance(ieml, str) else str(ieml)})

    def db_singular_sequences(self, paradigm=None):
        if paradigm:
            return self.scripts.find({'_id': paradigm})['SINGULAR_SEQUENCES']

        result = list((self.scripts.aggregate([
            {'$match': {'TYPE': ROOT_PARADIGM_TYPE}},
            {'$unwind': '$SINGULAR_SEQUENCES'},
            {'$group': {'_id': 0, 'RESULT': {'$push': '$SINGULAR_SEQUENCES'}}},
        ])))

        if result:
            return result[0]['RESULT']
        else:
            return []

    def save_script(self, script_ast, root=False):
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
            raise NotAParadigm()

        if root:
            self._save_root_paradigm(script_ast)
        else:
            self._save_paradigm(script_ast)

    def root_paradigms(self):
        return list(self.scripts.aggregate([
            {'$group': {'_id': '$ROOT'}}
        ])['_id'])

    def _save_singular_sequence(self, script_ast):
        """

        :param script_ast:
        :return:
        """
        # check if a singular sequence
        if script_ast.cardinal != 1:
            raise NotASingularSequence()

        # check if already exist
        if self.get_script(str(script_ast)):
            raise SingularSequenceAlreadyExist()

        # get all the singular sequence of the db to see if the singular sequence can be created
        if str(script_ast) not in self.db_singular_sequences():
            raise RootParadigmMissing()

        # save the singular sequence
        insertion = {
            '_id': str(script_ast),
            'TYPE': SINGULAR_SEQUENCE_TYPE,
            'ROOT': self._compute_root(script_ast),
            'RELATIONS': {},
            'SINGULAR_SEQUENCES': [str(script_ast)]
        }
        self.scripts.insert(insertion)

    def _save_root_paradigm(self, script_ast):
        """
         Save a root paradigm :
            - save the root paradigm
            - save all the singular sequence

        :param script_ast: the paradigm ast
        :return: None
        """
        # defensive check

        # check if paradigm already saved
        if self.get_script(str(script_ast)):
            raise ParadigmAlreadyExist()

        # get all the singular sequence of the db to avoid intersection
        if set.intersection(set(str(seq) for seq in script_ast.singular_sequences), self.db_singular_sequences()):
            raise RootParadigmIntersection()

        # save the root paradigm
        insertion = {
            '_id': str(script_ast),
            'TYPE': ROOT_PARADIGM_TYPE,
            'ROOT': str(script_ast),
            'RELATIONS': {},
            'SINGULAR_SEQUENCES': [str(seq) for seq in script_ast.singular_sequences]
        }
        self.scripts.insert(insertion)

    def _save_paradigm(self, script_ast):
        # defensive check
        if self.get_script(str(script_ast)):
            raise ParadigmAlreadyExist()

        # get all the singular sequence of the db to check if we can create the paradigm
        if not set(str(seq) for seq in script_ast.singular_sequences).issubset(self.db_singular_sequences()):
            raise RootParadigmMissing()

        insertion = {
            '_id': str(script_ast),
            'TYPE': PARADIGM_TYPE,
            'ROOT': self._compute_root(script_ast),
            'RELATIONS': {},
            'SINGULAR_SEQUENCES': [str(seq) for seq in script_ast.singular_sequences]
        }
        self.scripts.insert(insertion)

    def _compute_root(self, script_ast):
        """Prerequisite: root exist"""
        result = self.scripts.find_one({
            'TYPE': ROOT_PARADIGM_TYPE,
            'SINGULAR_SEQUENCES': {'$all': [str(seq) for seq in script_ast.singular_sequences]}})
        if result is None:
            raise RootParadigmMissing()

        return result['_id']

    def remove_script(self, script_ast):
        """
        Remove a script from the relations collection
        :param script_ast: the script to remove
        :return: None
        """
        if self.get_script(script_ast) is None:
            logging.warning("Deletion of a non existent script %s from the collection relation." % str(script_ast))
            return

        self.scripts.remove({'_id': str(script_ast)})