from ieml.parsing.script import ScriptParser
from ieml.script import CONTAINED_RELATION, CONTAINS_RELATION, RemarkableSibling, TWIN_SIBLING_RELATION, \
    ASSOCIATED_SIBLING_RELATION, CROSSED_SIBLING_RELATION, OPPOSED_SIBLING_RELATION, ATTRIBUTE, SUBSTANCE, MODE, \
    ELEMENTS, FATHER_RELATION, CHILD_RELATION, AdditiveScript, NullScript, Script, SCRIPT_RELATIONS
from models.constants import SINGULAR_SEQUENCE_TYPE
from models.exceptions import NotARootParadigm, InvalidScript, CantRemoveNonEmptyRootParadigm, InvalidRelationTitle
from models.relations.relations import RelationsConnector
import progressbar


class RelationsQueries:
    relations_db = RelationsConnector()
    script_parser = ScriptParser()

    @classmethod
    def update_script(cls, script, inhibition, root=None):
        """
        Update the term in the term and relation collection.
        :param script: the script to update.
        :param inhibition: the inhibitions
        :param root: optional, the new rootness value of this paradigm.
        :return: None
        """

        if root is not None:
            cls.remove_script(script, inhibition)
            cls.save_script(script, inhibition, root=bool(root))
        elif inhibition:
            cls.compute_relations(script)
            cls.compute_global_relations()
            cls.do_inhibition(inhibition)

    @classmethod
    def save_script(cls, script, inhibition, root=False):
        """
        Save a script in the relation collection.
        :param script: the script to save (str or Script instance)
        :param root: if the associated term is a root paradigm.
        :param inhibition: the list of root paradigm with their inhibitions.
        :return: None
        """
        script_ast = cls._to_ast(script)
        cls.relations_db.save_script(script_ast, root=root)

        paradigm_ast = cls._to_ast(cls.relations_db.get_script(str(script_ast))['ROOT'])
        cls.compute_relations(paradigm_ast)
        cls.compute_global_relations()
        cls.do_inhibition(inhibition)

    @classmethod
    def save_multiple_script(cls, list_script, inhibition):
        """
        Save multiple script in a single transaction. This method doesn't compute the relation multiple times, improving
        the computational speed than multiple call of save_script.
        :param list_script: the list of script, must be a list with the given pattern :
        [ {
            'AST': Script (the instance of Script for this script),
            'ROOT': bool (if the script is a root paradigm)
            } for each script to save, ...
        ]
        :param inhibition: list of root paradigm with theirs inhibitions.
        :return:
        """
        non_roots = [s['AST'] for s in list_script if not s['ROOT']]
        roots = [s['AST'] for s in list_script if s['ROOT']]

        # save the roots first
        bar_p = progressbar.ProgressBar()
        for s in bar_p(roots):
            cls.relations_db.save_script(s, root=True)

        # save the content of each paradigm
        bar = progressbar.ProgressBar()
        for s in bar(non_roots):
            cls.relations_db.save_script(s, root=False)

        # we get all the root paradigm impacted by the modification
        roots_paradigms = set(cls._to_ast(root) for root in cls.root_paradigms(non_roots)).union(set(roots))

        # then compute the relations in each paradigms
        bar_pp = progressbar.ProgressBar(max_value=len(roots))
        for p in bar_pp(roots_paradigms):
            cls.compute_relations(cls._to_ast(p))

        cls.compute_global_relations()
        cls.do_inhibition(inhibition)

    @classmethod
    def check_removable(cls, script):
        """
        Check that script is removable, if the script is not a non-empty root paradigm.
        :param script: the script to check if removable.
        :return: None
        """
        script_ast = cls._to_ast(script)

        script_entry = cls.relations_db.get_script(script_ast)
        if script_entry['ROOT'] == str(script_ast) and len(cls.paradigm(script)) != 1:
            return False
        return True

    @classmethod
    def remove_script(cls, script, inhibition):
        """
        Remove a script in the relation collection. Recompute the relation to keep the coherence of the collection.
        :param script: the script to remove.
        :param inhibition: list of root paradigm with their inhibition
        :return: None
        """
        script_ast = cls._to_ast(script)

        # Defensive check
        if not cls.check_removable(script_ast):
            raise CantRemoveNonEmptyRootParadigm()

        # Remove the script
        script_entry = cls.relations_db.get_script(script_ast)
        cls.relations_db.remove_script(script_ast)

        # If we remove a element of a paradigm (not the root paradigm), recompute the relation inside the paradigm
        if script_entry['ROOT'] != str(script_ast):
            cls.compute_relations(cls._to_ast(script_entry['ROOT']))

        # Recompute the global relations
        cls.compute_global_relations()

        # Unset inhibited relations
        cls.do_inhibition(inhibition)

    @classmethod
    def root_paradigms(cls, script_list=None):
        """
        Get a list of all the root paradigm saved in the database.
        :param script_list: optional, a set of script to get the subset of root paradigms.
        :return: a list of the ieml of root paradigms.
        """
        pipeline = []
        if script_list:
            pipeline.append({'$match': {'_id': [s if isinstance(s, str) else str(s) for s in script_list]}})
        pipeline.append({'$group': {'_id': '$ROOT'}})

        return [root['_id'] for root in cls.relations_db.relations.aggregate(pipeline)]

    @classmethod
    def paradigm(cls, script):
        """
        Get all the script in the paradigm argument plus the script argument.
        :param script: the paradigm to get.
        :return: list of entries
        """
        script_ast = cls._to_ast(script)
        return list(cls.relations_db.relations.find(
            {'SINGULAR_SEQUENCES': {'$in': [str(seq) for seq in script_ast.singular_sequences]}}))

    @classmethod
    def compute_relations(cls, paradigm_ast):
        """
        Compute the relations for a given root paradigm and all the contained scripts.
        :param paradigm_ast: the root paradigm
        :return: None
        """

        paradigm_entry = cls.relations_db.get_script(str(paradigm_ast))
        if paradigm_entry is None or paradigm_entry['ROOT'] != str(paradigm_ast):
            raise NotARootParadigm()

        # Compute the list of script in the paradigm
        scripts_ast = [cls.script_parser.parse(s['_id']) for s in cls.paradigm(paradigm_ast)]

        # erase the RELATIONS field
        cls.relations_db.relations.update(
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

    @classmethod
    def compute_global_relations(cls):
        """
        Compute all global relations in the relation db. The global relations are inter-paradigms relations (father and
        children). Must be call after each modification of the relations collection.
        :return: None
        """
        scripts = [cls.script_parser.parse(s['_id']) for s in cls.relations_db.relations.find({})]

        cls.relations_db.relations.update(
            {},
            {'$unset': {'RELATIONS' + '.' + CHILD_RELATION: 1, 'RELATIONS' + '.' + FATHER_RELATION: 1}})

        father_bar = progressbar.ProgressBar()
        # compute and save the fathers relations
        for s in father_bar(scripts):
            cls._save_relation(s, FATHER_RELATION, cls._compute_fathers(s))

        children_bar = progressbar.ProgressBar()
        # compute and save the children, they need the father to get calculated
        for s in children_bar(scripts):
            cls._compute_children(str(s))

    @classmethod
    def do_inhibition(cls, inhibition):
        """
        Remove the relations for each script that are inhibited in the inhibition list in argument.
        :param inhibition: a list of couple (script <str>, inbition list <list of str>)
        :return: None
        """

        inhibit_bar = progressbar.ProgressBar()
        for s, i in inhibit_bar(inhibition):
            cls._inhibit_relations(s, i)

    @staticmethod
    def _format_relations(relations):
        result = {}

        def _accumulation(current_path, dic):
            if ELEMENTS in dic:
                result[current_path] = dic[ELEMENTS]
                for i in (MODE, ATTRIBUTE, SUBSTANCE):
                    _accumulation(current_path + '.' + i, dic[i])

        for r in relations:
            if r in [FATHER_RELATION, CHILD_RELATION]:
                for i in (MODE, ATTRIBUTE, SUBSTANCE):
                    _accumulation(r + '.' + i, relations[r][i])
            else:
                # list type
                result[r] = relations[r]

        return result

    @classmethod
    def relations(cls, script, relation_title=None):
        """
        Relation getter, get the relations for the argument script. If relation_title is specified, return the relation
        with the given name. For the relation_title that can be specified, see the list in constant of ieml.
        :param script: the script to get the relation from. (str or Script instance)
        :param relation_title: optional, the name of a particular relation to see.
        :return: a dict of all relations or a specific relation.
        """
        relations = cls.relations_db.relations.find_one(
            {'_id': script if isinstance(script, str) else str(script)}
        )['RELATIONS']
        if relation_title:
            return relations[relation_title]
        else:
            return cls._format_relations(relations)

    @staticmethod
    def _merge(dic1, dic2):
        """
        Merge two dict in the model of father children relationship
        :param dic1: the dict to merge in.
        :param dic2: the dict to add in dic1.
        :return: None
        """
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
        :param script_ast: the script to calculate the relations to.
        :param max_depth: the max depth of the relation.
        :param _first: internal use.
        :return: the relation entry in the form of :
        {
            SUBSTANCE: {
                # level 1
                ELEMENTS: [substances de arg],
                SUBSTANCE: {...},
                ATTRIBUTE: {...},
                MODE: {...}
            },
            ATTRIBUTE: {...},
            MODE: {} if no element (MODE.ELEMENTS = []) otherwise same as the model of substance.
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
        """
        Compute the children relations and save it. The relations collection must have already calculated the father
        relationship, otherwise the children relations will be invalid.
        :param script_str: the script to calculate the relation to.
        :return: None
        """
        script_entry = cls.relations_db.get_script(script_str)
        if CHILD_RELATION in script_entry['RELATIONS']:
            # already computed
            return

        result = {
            SUBSTANCE: {},
            ATTRIBUTE: {},
            MODE: {}
        }

        # we check in all the father relations to get the childrens
        for rel in (SUBSTANCE, ATTRIBUTE, MODE):
            children = [s['_id'] for s in cls.relations_db.relations.find(
                {'.'.join(['RELATIONS', FATHER_RELATION, rel, ELEMENTS]): script_str})]

            if len(children) != 0:
                # Compute the children of the parent, to aggregate the grand-child
                for r in children:
                    cls._compute_children(r)

                # get all the children entries of the children
                list_children = [cls.relations_db.get_script(r)['RELATIONS'][CHILD_RELATION] for r in children]

                # merge all child dictionary
                for d in list_children:
                    cls._merge(result[rel], d)

                # save the child elements
                result[rel][ELEMENTS] = children

        cls._save_relation(script_str, CHILD_RELATION, result)

    @classmethod
    def _save_relation(cls, script, relation_title, relations):
        """
        Save the given relations in the collection.
        :param script: the script which we had the relation
        :param relation_title: the relation title
        :param relations: the relation value
        :return: None
        """
        if relation_title not in SCRIPT_RELATIONS:
            raise InvalidRelationTitle()

        cls.relations_db.relations.update(
            {'_id': script if isinstance(script, str) else str(script)},
            {'$set': {'RELATIONS.'+relation_title: relations}}
        )

    @classmethod
    def _compute_contained(cls, script_ast):
        """
        Compute all the contained relations for this script and save the resulting relations.
        :param script_ast: the script ast to compute contained relations.
        :return: None
        """
        entry = cls.relations_db.get_script(str(script_ast))

        result = cls.relations_db.relations.aggregate([
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

        contained = [cls.script_parser.parse(e['_id']) for e in result]
        contained.sort()

        cls._save_relation(script_ast, CONTAINED_RELATION, [str(c) for c in contained])

    @classmethod
    def _compute_contains(cls, script_ast):
        """
        Compute all the contains relations for this script and save the resulting relations.
        :param script_ast: the script ast to compute contains relations.
        :return: None
        """
        entry = cls.relations_db.get_script(str(script_ast))

        result = cls.relations_db.relations.aggregate([
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

        contains = [cls.script_parser.parse(e['_id']) for e in result]
        contains.sort()

        cls._save_relation(script_ast, CONTAINS_RELATION, [str(c) for c in contains])

    @staticmethod
    def _to_ast(script):
        if isinstance(script, Script):
            return script
        elif isinstance(script, str):
            return RelationsQueries.script_parser.parse(script)
        else:
            raise InvalidScript()

    @classmethod
    def _inhibit_relations(cls, script_str, inhibits=None):
        """
        Inhibit a script relation given the inhibit dict.
        :param script_str: the script to inhibit.
        :param inhibits: the dict of relation to inhibit.
        :return: None
        """
        if not inhibits:
            return

        unset = {}
        for relation in inhibits:
            unset[relation] = 1

        cls.relations_db.relations.update(
            {'ROOT': script_str},
            {'$unset': unset}
        )
