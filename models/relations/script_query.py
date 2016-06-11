from models.script_relations import ScriptConnector
from models.constants import ROOT_PARADIGM_TYPE
from ieml.parsing.script import ScriptParser

class RelationsQueries:
    script_db = ScriptConnector()

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
                # {'_id': {'$ne': entry['ROOT']}}
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

if __name__ == '__main__':

    parser = ScriptParser()
    script = parser.parse("t.M:O:.-")
    # print(RelationsQueries.contains(script))
    print(RelationsQueries.contained(script))
