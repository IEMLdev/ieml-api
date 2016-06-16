from models.script_relations import ScriptConnector
from models.constants import ROOT_PARADIGM_TYPE, SINGULAR_SEQUENCE_TYPE
from ieml.parsing.script import ScriptParser
from models.exceptions import NotARootParadigm
from ieml.script import CONTAINED_RELATION, CONTAINS_RELATION, RemarkableSibling, TWIN_SIBLING_RELATION, \
    ASSOCIATED_SIBLING_RELATION, CROSSED_SIBLING_RELATION, OPPOSED_SIBLING_RELATION, ATTRIBUTE, SUBSTANCE, MODE, \
    ELEMENTS, FATHER_RELATION, CHILD_RELATION, AdditiveScript, MultiplicativeScript, NullScript, MAX_LAYER


class RelationsQueries:
    script_db = ScriptConnector()

    @classmethod
    def compute_relations(cls, paradigm_ast):
        paradigm_entry = cls.script_db._get_script(str(paradigm_ast))
        if paradigm_entry is None or paradigm_entry['ROOT'] != str(paradigm_ast):
            raise NotARootParadigm()

        parser = ScriptParser()

        #Compute the list of script in the paradigm
        cls._compute_contains(paradigm_ast)

        scripts = cls.relation(str(paradigm_ast), CONTAINS_RELATION)
        scripts_ast = [parser.parse(s) for s in scripts]
        scripts_ast.extend(paradigm_ast.singular_sequences)
        scripts_ast.append(paradigm_ast)

        for s in scripts_ast:
            cls._compute_contained(s)
            cls._compute_contains(s)

        # save the remarkable siblings
        remakable_siblings = RemarkableSibling.compute_remarkable_siblings_relations(scripts_ast)
        # for the twins siblings, just tag the elements in the paradigm
        for s in remakable_siblings[TWIN_SIBLING_RELATION]:
            cls._save_relation(s, TWIN_SIBLING_RELATION, [str(twin) for twin in remakable_siblings[TWIN_SIBLING_RELATION] if s != twin])

        # Add the other remarkable siblings relations
        for relation_type in (ASSOCIATED_SIBLING_RELATION, CROSSED_SIBLING_RELATION, OPPOSED_SIBLING_RELATION):
            for s in scripts_ast:
                # take all the target where there is a tuple that have s in src.
                cls._save_relation(s, relation_type,
                                   [str(trg) for src, trg in remakable_siblings[relation_type] if src == s])

        # compute and save the fathers
        for s in scripts_ast:
            cls._save_relation(s, FATHER_RELATION, cls._compute_fathers(s))

        # compute and save the children, they need the father to get calculated
        for s in scripts_ast:
            cls._compute_children(str(s))

    @classmethod
    def relation(cls, script, relation_title=None):
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
    def _compute_fathers(cls, script_ast, max_depth=-1, _first=True):
        """
        Compute the father relationship. For a given script, it is all the sub element attribute, mode, substance for a
        given depth.
        :param script_ast:
        :param max_depth:
        :param _first:
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
    def _compute_children(cls, script_str, max_depth=-1):
        script_entry = cls.script_db._get_script(script_str)
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
                list_children = [cls.script_db._get_script(r)['RELATIONS'][CHILD_RELATION] for r in children]

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
        entry = cls.script_db._get_script(str(script_ast))

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
        entry = cls.script_db._get_script(str(script_ast))

        result = cls.script_db.scripts.aggregate([
            # select the paradigm
            {'$match': {'$and': [
                {'ROOT': entry['ROOT']},
                {'SINGULAR_SEQUENCES':
                    {'$in': [str(seq) for seq in script_ast.singular_sequences]}
                },
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

    @classmethod
    def _invalid_relations_paradigm(cls, paradigm_ieml):
        paradigm = cls.script_db._get_script(paradigm_ieml)

        # check if root paradigm
        if paradigm['ROOT'] != paradigm_ieml:
            raise NotARootParadigm()

        contained = cls.contained(paradigm_ieml)
        cls.script_db.scripts.update(
            {'_id': {'$in': contained}},
            {'$set': {'RELATIONS': {}}}
        )

if __name__ == '__main__':
    # _parser = ScriptParser()
    # RelationsQueries.script_db.scripts.update({}, {'$unset': {'RELATIONS.CHILD_RELATION': 1}},
    #                                           {'multi': True, 'upsert': False})

    terms = [t['IEML'] for t in RelationsQueries.script_db.terms.find({})]
    for t in terms:
        # RelationsQueries.script_db.terms.update(
        #     {'IEML': t},
        #     {'$set': {'IEML': str(_parser.parse(t))}}
        # )
        RelationsQueries._compute_children(t)
    #
    # _parser = ScriptParser()
    # script = _parser.parse("t.M:O:.+wa.-")
    # # print(RelationsQueries.contains(script))
    # # print(RelationsQueries.contained(script))
    #
    # print(RelationsQueries.fathers(script))
