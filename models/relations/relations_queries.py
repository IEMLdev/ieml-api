from ieml.parsing.script import ScriptParser
from ieml.script import CONTAINED_RELATION, CONTAINS_RELATION, RemarkableSibling, TWIN_SIBLING_RELATION, \
    ASSOCIATED_SIBLING_RELATION, CROSSED_SIBLING_RELATION, OPPOSED_SIBLING_RELATION, ATTRIBUTE, SUBSTANCE, MODE, \
    ELEMENTS, FATHER_RELATION, CHILD_RELATION, AdditiveScript, NullScript, Script
from models.constants import SINGULAR_SEQUENCE_TYPE
from models.exceptions import NotARootParadigm, InvalidScript, CantRemoveNonEmptyRootParadigm
from models.relations.relations import RelationsConnector
import progressbar

class RelationsQueries:
    script_db = RelationsConnector()
    script_parser = ScriptParser()

    @staticmethod
    def _to_ast(script):
        if isinstance(script, Script):
            return script
        elif isinstance(script, str):
            return RelationsQueries.script_parser.parse(script)
        else:
            raise InvalidScript()

    @classmethod
    def update_term(cls, script, inhibits=None, root=None):
        script_ast = cls._to_ast(script)

        if root:
            cls.remove_script(script, inhibits=inhibits)
            cls.save_script(script, inhibits=inhibits, root=bool(root))
        elif inhibits:
            cls.compute_relations(script,  inhibits=inhibits)

    @classmethod
    def save_script(cls, script, inhibits=None, root=False):
        script_ast = cls._to_ast(script)
        cls.script_db.save_script(script_ast, root=root)

        paradigm_ast = cls._to_ast(cls.script_db.get_script(str(script_ast))['ROOT'])
        cls.compute_relations(paradigm_ast, inhibits=inhibits)

    @classmethod
    def save_multiple_script(cls, list_script):
        scripts = ({
                       'AST': s['AST'],
                   } for s in list_script if not s['ROOT'])

        paradigms = [{
            'AST': s['AST'],
            'INHIBITS': s['INHIBITS']
        } for s in list_script if s['ROOT']]

        bar_p = progressbar.ProgressBar()
        for s in bar_p(paradigms):
            cls.script_db.save_script(s['AST'], root=True)

        bar = progressbar.ProgressBar()
        for s in bar(scripts):
            cls.script_db.save_script(s['AST'], root=False)

        bar_pp = progressbar.ProgressBar(max_value=len(paradigms))
        for i, p in enumerate(paradigms):
            cls.compute_relations(p['AST'], inhibits=p['INHIBITS'])
            bar_pp.update(i + 1)

    @classmethod
    def check_removable(cls, script):
        script_ast = cls._to_ast(script)

        script_entry = cls.script_db.get_script(script_ast)
        if script_entry['ROOT'] == str(script_ast) and len(cls.paradigm(script)) != 1:
            return False
        return True

    @classmethod
    def remove_script(cls, script, inhibits=None):
        script_ast = cls._to_ast(script)

        if not cls.check_removable(script_ast):
            raise CantRemoveNonEmptyRootParadigm()

        script_entry = cls.script_db.get_script(script_ast)
        cls.script_db.remove_script(script_ast)

        if script_entry['ROOT'] != str(script_ast):
            cls.compute_relations(cls._to_ast(script_entry['ROOT']), inhibits=inhibits)

    @classmethod
    def paradigm(cls, script):
        """
        Get all the script in the paradigm argument plus the script argument.
        :param script: the paradigm to get.
        :return: list of entries
        """
        script_ast = cls._to_ast(script)
        return list(cls.script_db.scripts.find(
            {'SINGULAR_SEQUENCES': {'$in': [str(seq) for seq in script_ast.singular_sequences]}}))

    @classmethod
    def compute_relations(cls, paradigm_ast, inhibits=None):
        """
        Compute the relations for a given root paradigm and all the contained scripts.
        :param paradigm_ast: the root paradigm
        :param inhibits: a list of the relation to inhibit
        :return:
        """

        paradigm_entry = cls.script_db.get_script(str(paradigm_ast))
        if paradigm_entry is None or paradigm_entry['ROOT'] != str(paradigm_ast):
            raise NotARootParadigm()

        # Compute the list of script in the paradigm
        scripts_ast = [cls.script_parser.parse(s['_id']) for s in cls.paradigm(paradigm_ast)]

        # erase the RELATIONS field
        cls.script_db.scripts.update(
            {'_id': {'$in': [str(s) for s in scripts_ast]}},
            {'$set': {'RELATIONS': {}}},
            multi=True
        )

        # Compute and save contains and contained (can't be inhibited)
        for s in scripts_ast:
            cls._compute_contained(s)
            cls._compute_contains(s)

        # Compute and save the remarkable siblings
        remarkable_siblings = RemarkableSibling.compute_remarkable_siblings_relations(scripts_ast)

        # Save the twins siblings
        for s in remarkable_siblings[TWIN_SIBLING_RELATION]:
            cls._save_relation(s, TWIN_SIBLING_RELATION,
                               [str(twin) for twin in remarkable_siblings[TWIN_SIBLING_RELATION] if s != twin])

        # Add the other remarkable siblings relations
        for relation_type in (ASSOCIATED_SIBLING_RELATION, CROSSED_SIBLING_RELATION, OPPOSED_SIBLING_RELATION):
            for s in scripts_ast:
                # take all the target where there is a tuple that have s in src.
                cls._save_relation(s, relation_type,
                                   [str(trg) for src, trg in remarkable_siblings[relation_type] if src == s])

        # compute and save the fathers relations
        for s in scripts_ast:
            cls._save_relation(s, FATHER_RELATION, cls._compute_fathers(s))

        # compute and save the children, they need the father to get calculated
        for s in scripts_ast:
            cls._compute_children(str(s))

        for s in scripts_ast:
            cls._inhibit_relations(s, inhibits)

    @classmethod
    def _inhibit_relations(cls, script_ast, inhibits=None):
        if not inhibits:
            return

        unset = {}
        for relation in inhibits:
            unset[relation] = 1

        cls.script_db.scripts.update(
            {'_id': str(script_ast)},
            {'$unset': unset}
        )

    @classmethod
    def relations(cls, script, relation_title=None):
        relations = cls.script_db.scripts.find_one(
            {'_id': script if isinstance(script, str) else str(script)}
        )['RELATIONS']
        if relation_title:
            return relations[relation_title]
        else:
            return relations

    @staticmethod
    def _merge(dic1, dic2):
        if ELEMENTS in dic2:
            if ELEMENTS not in dic1:
                dic1[ELEMENTS] = []

            dic1[ELEMENTS].extend(dic2[ELEMENTS])

        if SUBSTANCE in dic2:
            if SUBSTANCE not in dic1:
                dic1[SUBSTANCE] = {}
                dic1[ATTRIBUTE] = {}
                dic1[MODE] = {}

            RelationsQueries._merge(dic1[SUBSTANCE], dic2[SUBSTANCE])
            RelationsQueries._merge(dic1[ATTRIBUTE], dic2[ATTRIBUTE])
            RelationsQueries._merge(dic1[MODE], dic2[MODE])

    @classmethod
    def _compute_fathers(cls, script_ast, max_depth=-1, _first=True, inhibits=None):
        """
        Compute the father relationship. For a given script, it is all the sub element attribute, mode, substance for a
        given depth.
        :param script_ast:
        :param max_depth:
        :param _first:
        :param inhibits:
        :return:
        {
            SUBSTANCE: {
                # level 1
                ELEMENTS: [substances de arg],
                SUBSTANCE: {...},
                ATTRIBUTE: {...},
                MODE: {...}
            },
            ATTRIBUTE: {...},
            MODE: {...}
        }
        """

        if max_depth == 0 and not _first:
            return {ELEMENTS: [str(script_ast)]}

        if isinstance(script_ast, NullScript):
            return {}

        relations = {
            SUBSTANCE: {},
            ATTRIBUTE: {},
            MODE: {}
        }

        if not _first:
            relations[ELEMENTS] = [str(script_ast)]

        # iteration over the script children (if addition), if Multiplication, just the element
        for sub_s in script_ast if isinstance(script_ast, AdditiveScript) else [script_ast]:
            if len(sub_s.children) != 0:
                # sub_s is a Multiplicative script
                cls._merge(relations[SUBSTANCE], cls._compute_fathers(sub_s.children[0], max_depth - 1, _first=False))
                cls._merge(relations[ATTRIBUTE], cls._compute_fathers(sub_s.children[1], max_depth - 1, _first=False))
                cls._merge(relations[MODE], cls._compute_fathers(sub_s.children[2], max_depth - 1, _first=False))

        return relations

    @classmethod
    def _compute_children(cls, script_str):
        script_entry = cls.script_db.get_script(script_str)
        if CHILD_RELATION in script_entry['RELATIONS']:
            # already computed
            return

        result = {
            SUBSTANCE: {},
            ATTRIBUTE: {},
            MODE: {}
        }

        for rel in (SUBSTANCE, ATTRIBUTE, MODE):
            children = [s['_id'] for s in cls.script_db.scripts.find(
                {'.'.join(['RELATIONS', FATHER_RELATION, rel, ELEMENTS]): script_str})]

            if len(children) != 0:
                for r in children:
                    cls._compute_children(r)

                # get all the children entries of the children
                list_children = [cls.script_db.get_script(r)['RELATIONS'][CHILD_RELATION] for r in children]

                # merge all child dictionary
                for d in list_children:
                    cls._merge(result[rel], d)

                # put the child elemnts
                result[rel][ELEMENTS] = children

        cls._save_relation(script_str, CHILD_RELATION, result)

    @classmethod
    def _save_relation(cls, script, relation_title, relations):
        cls.script_db.scripts.update(
            {'_id': script if isinstance(script, str) else str(script)},
            {'$set': {'RELATIONS.'+relation_title: relations}}
        )

    @classmethod
    def _compute_contained(cls, script_ast):
        """Get all the contains relations for this script"""
        entry = cls.script_db.get_script(str(script_ast))

        result = cls.script_db.scripts.aggregate([
            # select the paradigm
            {'$match': {'$and': [
                {'ROOT': entry['ROOT']},
                {'SINGULAR_SEQUENCES': {
                    '$all': [str(seq) for seq in script_ast.singular_sequences]
                }},
                {'_id': {'$ne': str(script_ast)}},
            ]}},
            {'$project': {'_id': 1}}
        ])
        parser = ScriptParser()
        contained = [parser.parse(e['_id']) for e in result]
        contained.sort()

        cls._save_relation(script_ast, CONTAINED_RELATION, [str(c) for c in contained])

    @classmethod
    def _compute_contains(cls, script_ast):
        """Get all the contained relations for this script"""
        entry = cls.script_db.get_script(str(script_ast))

        result = cls.script_db.scripts.aggregate([
            # select the paradigm
            {'$match': {'$and': [
                {'ROOT': entry['ROOT']},
                {'SINGULAR_SEQUENCES': {'$in': [str(seq) for seq in script_ast.singular_sequences]}},
                {'TYPE': {'$ne': SINGULAR_SEQUENCE_TYPE}},
                {'_id': {'$ne': str(script_ast)}},
            ]}},
            {'$unwind': '$SINGULAR_SEQUENCES'},
            {'$group': {'_id': '$_id', 'SEQUENCE_COUNT': {'$sum': 1}}},
            {'$match': {'SEQUENCE_COUNT': {'$lt': len(script_ast.singular_sequences)}}},
            {'$project': {'_id': 1}}
        ])

        parser = ScriptParser()
        contains = [parser.parse(e['_id']) for e in result]
        contains.sort()

        cls._save_relation(script_ast, CONTAINS_RELATION, [str(c) for c in contains])
