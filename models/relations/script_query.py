from models.script_relations import ScriptConnector
from models.constants import ROOT_PARADIGM_TYPE
from ieml.parsing.script import ScriptParser
from models.exceptions import NotARootParadigm
from ieml.script import CONTAINED_RELATION, CONTAINS_RELATION, RemarkableSibling, TWIN_SIBLING_RELATION, \
    ASSOCIATED_SIBLING_RELATION, CROSSED_SIBLING_RELATION, OPPOSED_SIBLING_RELATION, ATTRIBUTE, SUBSTANCE, MODE, \
    ELEMENTS, FATHER_RELATION, CHILD_RELATION, AdditiveScript, MultiplicativeScript, NullScript


class RelationsQueries:
    script_db = ScriptConnector()

    @classmethod
    def compute_relations(cls, paradigm):
        paradigm_entry = cls.script_db._get_script(paradigm)
        if paradigm_entry is None or paradigm_entry['ROOT'] == paradigm:
            raise NotARootParadigm()

        parser = ScriptParser()

        #Compute the list of script in the paradigm
        scripts = cls.contained(paradigm)
        scripts_ast = [parser.parse(s) for s in scripts]

        for s in (str(s) for s in scripts_ast):
            cls._save_relation(s, CONTAINS_RELATION, cls.contains(s))
            cls._save_relation(s, CONTAINED_RELATION, cls.contained(s))

        # save the remarkable siblings
        remakable_siblings = RemarkableSibling.compute_remarkable_siblings_relations(scripts_ast)
        # for the twins siblings, just tag the elements in the paradigm
        for s in remakable_siblings[TWIN_SIBLING_RELATION]:
            cls._save_relation(s, TWIN_SIBLING_RELATION, True)

        # Add the other remarkable siblings relations
        for relation_type in (ASSOCIATED_SIBLING_RELATION, CROSSED_SIBLING_RELATION, OPPOSED_SIBLING_RELATION):
            for s in (str(s) for s in scripts_ast):
                # take all the target where there is a tuple that have s in src.
                cls._save_relation(s, relation_type,
                                   [trg for list_tuple in remakable_siblings[relation_type]
                                    for src, trg in list_tuple if src == s])

        # compute and save the fathers


        # compute and save the children

    @classmethod
    def fathers(cls, script_ast, max_depth=-1, _first=True):
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

                _merge(dic1[SUBSTANCE], dic2[SUBSTANCE])
                _merge(dic1[ATTRIBUTE], dic2[ATTRIBUTE])
                _merge(dic1[MODE], dic2[MODE])

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
                _merge(relations[SUBSTANCE], cls.fathers(sub_s.children[0], max_depth - 1, _first=False))
                _merge(relations[ATTRIBUTE], cls.fathers(sub_s.children[1], max_depth - 1, _first=False))
                _merge(relations[MODE], cls.fathers(sub_s.children[2], max_depth - 1, _first=False))

        return relations

    @classmethod
    def _save_relation(cls, script, relation_title, relations):
        cls.script_db.scripts.update(
            {'_id': script},
            {'$set': {'RELATION.'+relation_title: relations}}
        )

    @classmethod
    def contains(cls, script_ast):
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
        return [e['_id'] for e in result]

    @classmethod
    def contained(cls, script_ast):
        """Get all the contained relations for this script"""
        entry = cls.script_db._get_script(str(script_ast))

        result = cls.script_db.scripts.aggregate([
            # select the paradigm
            {'$match': {'$and': [
                {'ROOT': entry['ROOT']},
                {'SINGULAR_SEQUENCES': {
                    '$in': [str(seq) for seq in script_ast.singular_sequences]
                }},
                {'_id': {'$ne': str(script_ast)}},
            ]}},
            {'$unwind': '$SINGULAR_SEQUENCES'},
            {'$group': {'_id': '$_id', 'SEQUENCE_COUNT': {'$sum': 1}}},
            {'$match': {'SEQUENCE_COUNT': {'$lt': len(script_ast.singular_sequences)}}},
            {'$project': {'_id': 1}}
        ])
        return [e['_id'] for e in result]

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

    parser = ScriptParser()
    script = parser.parse("t.M:O:.+wa.-")
    # print(RelationsQueries.contains(script))
    # print(RelationsQueries.contained(script))

    print(RelationsQueries.fathers(script))
