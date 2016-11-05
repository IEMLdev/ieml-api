import logging
from collections import defaultdict

import progressbar

from ieml.script import CONTAINED_RELATION, CONTAINS_RELATION, RemarkableSibling, TWIN_SIBLING_RELATION, \
    ASSOCIATED_SIBLING_RELATION, CROSSED_SIBLING_RELATION, OPPOSED_SIBLING_RELATION, ATTRIBUTE, SUBSTANCE, MODE, \
    ELEMENTS, FATHER_RELATION, CHILD_RELATION, AdditiveScript, NullScript, Script, SCRIPT_RELATIONS
from ieml.script.constants import ROOT_RELATION
from ieml.script.parser import ScriptParser
from ieml.script.tables import get_table_rank
from models.constants import RELATION_COMPUTING, SCRIPT_INSERTION, SCRIPT_DELETION
from models.exceptions import NotARootParadigm, CantRemoveNonEmptyRootParadigm, InvalidRelationTitle, \
    InvalidRelationCollectionState
from models.relations.relations import RelationsConnector, safe_execution


class RelationsQueries:
    @classmethod
    def rank(cls, script):
        entry = RelationsConnector().get_script(script)
        if 'RANK' not in entry:
            raise InvalidRelationCollectionState()
        return entry['RANK']

    @classmethod
    @safe_execution(SCRIPT_INSERTION)
    def save_script(cls, script, root=False, recompute_relations=True, verbose=False):
        """
        Save a parser in the relation collection.
        :param script: the parser to save (str or Script instance)
        :param root: if the associated term is a root paradigm.
        :param inhibition: the list of roots paradigms with their inhibitions.
        :param recompute_relations: if we must recompute the relations
        :return: None
        """
        script_ast = cls._to_ast(script)
        RelationsConnector().save_script(script_ast, root=root)

        if recompute_relations:
            paradigm_ast = cls._to_ast(RelationsConnector().get_script(str(script_ast))['ROOT'])

            cls.compute_relations(
                roots_paradigms=[paradigm_ast],
                globals=True,
                inhibitions=True,
                verbose=verbose)

    @classmethod
    @safe_execution(SCRIPT_INSERTION)
    def save_multiple_script(cls, list_script, recompute_relations=True, verbose=False):
        """
        Save multiple parser in a single transaction. This method doesn't compute the relation multiple times, improving
        the computational speed than multiple call of save_script.
        :param list_script: the list of parser, must be a list with the given pattern :
        [ {
            'AST': Script (the instance of Script for this parser),
            'ROOT': bool (if the parser is a root paradigm)
            } for each parser to save, ...
        ]
        :param inhibition: list of root paradigm with theirs inhibitions.
        :return:
        """
        non_roots = [s['AST'] for s in list_script if not s['ROOT']]
        roots = [s['AST'] for s in list_script if s['ROOT']]

        # save the roots first
        for s in roots:
            RelationsConnector().save_script(s, root=True)

        # save the content of each paradigm
        for s in non_roots:
            RelationsConnector().save_script(s, root=False)

        if recompute_relations:
            # we get all the root paradigm impacted by the modification
            roots_paradigms = set(cls._to_ast(root) for root in cls.root_paradigms(non_roots)).union(set(roots))

            # then compute the relations in each paradigms
            cls.compute_relations(
                roots_paradigms=roots_paradigms,
                globals=True,
                inhibitions=True,
                verbose=verbose)

    @classmethod
    def check_removable(cls, script):
        """
        Check that parser is removable, if the parser is not a non-empty root paradigm.
        :param script: the parser to check if removable.
        :return: None
        """
        script_ast = cls._to_ast(script)

        script_entry = RelationsConnector().get_script(script_ast)
        if script_entry['ROOT'] == str(script_ast) and len(cls.paradigm(script)) != 1:
            return False
        return True

    @classmethod
    @safe_execution(SCRIPT_DELETION)
    def remove_script(cls, script, recompute_relations=True, verbose=False):
        """
        Remove a parser in the relation collection. Recompute the relation to keep the coherence of the collection.
        :param script: the parser to remove.
        :param inhibition: list of root paradigm with their inhibition, must be specified if recompute_relation is true
        :param recompute_relations: optinonal, if set recompute the relation after the removing.
        :return: None
        """
        script_ast = cls._to_ast(script)

        # Defensive check
        if not cls.check_removable(script_ast):
            raise CantRemoveNonEmptyRootParadigm(script_ast)

        # Remove the parser
        script_entry = RelationsConnector().get_script(script_ast)
        RelationsConnector().remove_script(script_ast)

        if recompute_relations:
            roots = None
            # If we remove a element of a paradigm (not the root paradigm), recompute the relation inside the paradigm
            if script_entry['ROOT'] != str(script_ast):
                roots = [cls._to_ast(script_entry['ROOT'])]

            cls.compute_relations(
                roots_paradigms=roots,
                globals=True,
                inhibitions=True,
                verbose=verbose)

    @classmethod
    def root_paradigms(cls, script_list=None):
        """
        Get a list of all the root paradigm saved in the database.
        :param script_list: optional, a set of parser to get the subset of root paradigms.
        :return: a list of the ieml of root paradigms.
        """
        pipeline = []
        if script_list:
            pipeline.append({'$match': {'_id': [s if isinstance(s, str) else str(s) for s in script_list]}})
        pipeline.append({'$group': {'_id': '$ROOT'}})

        return [root['_id'] for root in RelationsConnector().relations.aggregate(pipeline)]

    @classmethod
    def paradigm(cls, script):
        """
        Get all the parser in the paradigm argument plus the parser argument.
        :param script: the paradigm to get.
        :return: list of entries
        """
        script_ast = cls._to_ast(script)
        return list(RelationsConnector().relations.find(
            {'SINGULAR_SEQUENCES': {'$in': [str(seq) for seq in script_ast.singular_sequences]}}))

    @classmethod
    @safe_execution(RELATION_COMPUTING)
    def compute_relations(cls, roots_paradigms=None, globals=True, inhibitions=True, verbose=False):
        """
        Compute the relations collection. Use a lock to forbid another computation to occur in the same time. If
        this function try to access the collection while another computation is running, it will rise a
        CollectionAlreadyLocked exception.

        There is three stages of relations computation, the three positional arguments root_paradigms, inhibitions
        and globals are responsible of each stages.

        This operation is polynomial on the number of parser impacted in this collection for the two first stages. All
        the scripts in each of the paradigms in roots_paradigms for the local stage, and all the scripts of the collection
        for the global stage. It is linear for the inhibition stage given the size of elements in all the paradigms to
        inhibit. To display a progressbar of the processing, set verbose to True.

        :param roots_paradigms: The list of the root paradigms to compute the local relations (contains, contained,
            rank, siblings), if None (default), no local computation is performed. Should be Script type or str.
        :param globals: If the globals relations should be computed (father, children).
        :param inhibitions: If True (default), will perfom the inhibition of the relation. Need to be performed after each
        computation to ensure collection coherence.
        :param verbose: if True, print progressbar to display the progress of the computation.
        :return:
        """
        if roots_paradigms:
            for p in roots_paradigms:
                cls._compute_local_relations(cls._to_ast(p), verbose=verbose)

        if globals:
            cls._compute_global_relations(verbose=verbose)

        if inhibitions:
            cls._do_inhibition(cls._inhibitions(), verbose=verbose)


    @classmethod
    def relations(cls, script, relation_title=None, pack_ancestor=False, max_depth_father=-1, max_depth_child=-1):
        """
        Relation getter, get the relations for the argument parser. If relation_title is specified, return the relation
        with the given name. For the relation_title that can be specified, see the list in constant of ieml.
        :param script: the parser to get the relation from. (str or Script instance)
        :param relation_title: optional, the name of a particular relation to see.
        :param pack_ancestor: pack the ancestors relations.
        :param max_depth_father: the max depth we fetch the ancestors.
        :param max_depth_child: the max depth we fetch the descendant.
        :return: a dict of all relations or a specific relation.
        """
        relations_db_entry = RelationsConnector().relations.find_one(
            {'_id': script if isinstance(script, str) else str(script)}
        )

        relations = relations_db_entry['RELATIONS']
        if relation_title:

            if relation_title == ROOT_RELATION:
                return relations_db_entry["ROOT"]
            elif relation_title in (FATHER_RELATION, CHILD_RELATION):
                return cls._format_relations((relation_title,), pack_ancestor=pack_ancestor,
                                             max_depth_father=max_depth_father, max_depth_child=max_depth_child)
            else:
                try:
                    return relations[relation_title] # we only return the selected relation
                except KeyError:
                    return []
        else:
            result = cls._format_relations(relations, pack_ancestor=pack_ancestor,
                                           max_depth_father=max_depth_father, max_depth_child=max_depth_child)
            result["ROOT"] = relations_db_entry["ROOT"]
            return result # we output all relations PLUS the root paradigm property

    @classmethod
    def _compute_local_relations(cls, paradigm_ast, verbose=False):
        """
        Compute the relations for a given root paradigm and all the contained scripts.
        :param paradigm_ast: the root paradigm
        :param verbose: text progressbar
        :return: None
        """

        paradigm_entry = RelationsConnector().get_script(str(paradigm_ast))

        if paradigm_entry['ROOT'] != str(paradigm_ast):
            raise NotARootParadigm(paradigm_ast)

        # Compute the list of parser in the paradigm
        scripts_ast = [cls._to_ast(s['_id']) for s in cls.paradigm(paradigm_ast)]

        # erase the RELATIONS field
        RelationsConnector().relations.update(
            {'_id': {'$in': [str(s) for s in scripts_ast]}},
            {'$set': {'RELATIONS': {}}},
            multi=True
        )
        if verbose:
            logging.info('Computing local relations for paradigm %s...' % str(paradigm_ast))

        # Compute and save contains and contained (can't be inhibited)
        cls._compute_containing_relations(scripts_ast)

        cls._compute_tables_rank(scripts_ast)

        # Compute and save the remarkable siblings
        remarkable_siblings = RemarkableSibling.compute_remarkable_siblings_relations(scripts_ast, regex=False)

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
    def _compute_global_relations(cls, verbose=False):
        """
        Compute all global relations in the relation db. The global relations are inter-paradigms relations (father and
        children). Must be call after each modification of the relations collection.
        :return: None
        """
        scripts = [cls._to_ast(s['_id']) for s in RelationsConnector().relations.find({})]

        RelationsConnector().relations.update(
            {},
            {'$unset': {'RELATIONS' + '.' + CHILD_RELATION: 1, 'RELATIONS' + '.' + FATHER_RELATION: 1}})

        if verbose:
            logging.info('Computing global relations...')

        bar = cls._get_progressbar(verbose)
        # compute and save the fathers relations
        for s in bar(scripts):
            cls._save_relation(s, FATHER_RELATION, cls._compute_fathers(s))

        bar = cls._get_progressbar(verbose)
        # compute and save the children, they need the father to get calculated
        for s in bar(scripts):
            cls._compute_children(str(s))

    @classmethod
    def _do_inhibition(cls, inhibition, verbose=False):
        """
        Remove the relations for each parser that are inhibited in the inhibition list in argument.
        :param inhibition: a list of couple (parser <str>, inbition list <list of str>)
        :return: None
        """
        bar = cls._get_progressbar(verbose)
        for s, i in bar(inhibition):
            cls._inhibit_relations(str(s), i)

    @staticmethod
    def _format_relations(relations, pack_ancestor=False, max_depth_father=-1, max_depth_child=-1):
        result = defaultdict(lambda: list())

        def _accumulation(current_path, dic, max_depth=-1):
            if max_depth == 0:
                return

            for key in dic:
                if pack_ancestor:
                    if key == ELEMENTS:
                        result[current_path] = list(set(result[current_path]).union(dic[ELEMENTS]))
                    else:
                        _accumulation(current_path, dic[key], max_depth=max_depth-1)
                else:
                    if key == ELEMENTS:
                        result[current_path] = dic[ELEMENTS]
                    else:
                        _accumulation(current_path + '.' + key, dic[key], max_depth=max_depth-1)

        for r in relations:
            if r in (FATHER_RELATION, CHILD_RELATION):
                for i in (MODE, ATTRIBUTE, SUBSTANCE):
                    if i not in relations[r]:
                        relations[r][i] = []
                    else:
                        _accumulation(r + '.' + i, relations[r][i],
                                      max_depth=(max_depth_father if r == FATHER_RELATION else max_depth_child))
            else:
                # list type
                result[r] = relations[r]

        return result

    @staticmethod
    def _merge(dic1, dic2, inverse_key=None):
        """
        Merge two dict in the model of father children relationship
        :param dic1: the dict to merge in.
        :param dic2: the dict to add in dic1.
        :param inverse_key: the key to put at the end of the first dic
        :return: None
        """
        # first merge the current level of dict
        # ELEMENTS present implies that the dict has another level of recursion
        for key in dic2:
            if key == ELEMENTS:
                # data copy
                if inverse_key:
                    if inverse_key not in dic1:
                        dic1[inverse_key] = {}

                    if ELEMENTS not in dic1[inverse_key]:
                        dic1[inverse_key][ELEMENTS] = dic2[ELEMENTS]
                    else:
                        dic1[inverse_key][ELEMENTS] = list(set(dic1[inverse_key][ELEMENTS]).union(dic2[ELEMENTS]))
                else:
                    if ELEMENTS not in dic1:
                        dic1[ELEMENTS] = dic2[ELEMENTS]
                    else:
                        dic1[ELEMENTS] = list(set(dic1[ELEMENTS]).union(dic2[ELEMENTS]))
            else:
                # dict recursion
                if key not in dic1:
                    dic1[key] = {}

                RelationsQueries._merge(dic1[key], dic2[key], inverse_key=inverse_key)

    @classmethod
    def _compute_tables_rank(cls, scripts_ast):
        for s in scripts_ast:
            if s.paradigm:
                RelationsConnector().relations.update({'_id': str(s)},
                                                  {'$set': {'RANK': get_table_rank(s)}})

    @classmethod
    def _compute_fathers(cls, script_ast):
        """
        Compute the father relationship. For a given parser, it is all the sub element attribute, mode, substance for a
        given depth.
        :param script_ast: the parser to calculate the relations to.
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
        #
        # if not _first:
        #     return {ELEMENTS: [str(script_ast)]}

        if isinstance(script_ast, NullScript):
            return {}

        relations = {}

        for sub_s in script_ast if isinstance(script_ast, AdditiveScript) else [script_ast]:
            if len(sub_s.children) == 0 or isinstance(sub_s, NullScript):
                continue

            for i, e in enumerate((SUBSTANCE, ATTRIBUTE, MODE)):
                if isinstance(sub_s.children[i], NullScript):
                    continue

                if e not in relations:
                    relations[e] = {}

                if RelationsConnector().exists(sub_s.children[i]):
                    if ELEMENTS not in relations[e]:
                        relations[e][ELEMENTS] = []

                    r = set(relations[e][ELEMENTS])
                    r.add(str(sub_s.children[i]))
                    relations[e][ELEMENTS] = list(r)

                cls._merge(relations[e], cls._compute_fathers(sub_s.children[i]))

                if not relations[e]:
                    del relations[e]

        return relations

    @classmethod
    def _compute_children(cls, script_str):
        """
        Compute the children relations and save it. The relations collection must have already calculated the father
        relationship, otherwise the children relations will be invalid.
        :param script_str: the parser to calculate the relation to.
        :return: None
        """
        script_entry = RelationsConnector().get_script(script_str)
        if CHILD_RELATION in script_entry['RELATIONS']:
            # already computed
            return

        result = {}

        # we check in all the father relations to get the childrens
        for rel in (SUBSTANCE, ATTRIBUTE, MODE):
            children = [s['_id'] for s in RelationsConnector().relations.find(
                {'.'.join(['RELATIONS', FATHER_RELATION, rel, ELEMENTS]): script_str})]

            if len(children) != 0:
                # Compute the children of the parent, to aggregate the grand-child
                for r in children:
                    cls._compute_children(r)

                # get all the children entries of the children
                list_children = [RelationsConnector().get_script(r)['RELATIONS'][CHILD_RELATION] for r in children]

                # merge all child dictionary
                for d in list_children:
                    cls._merge(result, d, inverse_key=rel)

                # save the child elements
                if rel not in result:
                    result[rel] = {}

                result[rel][ELEMENTS] = children

        cls._save_relation(script_str, CHILD_RELATION, result)

    @classmethod
    def _save_relation(cls, script, relation_title, relations):
        """
        Save the given relations in the collection.
        :param script: the parser which we had the relation
        :param relation_title: the relation title
        :param relations: the relation value
        :return: None
        """
        if relation_title not in SCRIPT_RELATIONS:
            raise InvalidRelationTitle(relation_title)

        RelationsConnector().relations.update(
            {'_id': script if isinstance(script, str) else str(script)},
            {'$set': {'RELATIONS.'+relation_title: relations}}
        )

    @classmethod
    def _compute_containing_relations(cls, scripts_ast):
        """
        Compute all the contained relations for this parser and save the resulting relations.
        :param scripts_ast: the parser ast to compute contained relations.
        :return: None
        """
        contains = {}

        for s in scripts_ast:
            entry = RelationsConnector().get_script(str(s))

            result = RelationsConnector().relations.aggregate([
                # select the paradigm
                {'$match': {'$and': [
                    {'ROOT': entry['ROOT']},
                    {'SINGULAR_SEQUENCES': {
                        '$all': [str(seq) for seq in s.singular_sequences]
                    }},
                    {'_id': {'$ne': str(s)}},
                ]}},
                {'$project': {'_id': 1}}
            ])

            contained = [cls._to_ast(e['_id']) for e in result]
            contained.sort()

            cls._save_relation(s, CONTAINED_RELATION, [str(c) for c in contained])
            s_str = str(s)
            for c in contained:
                if c not in contains:
                    contains[c] = []
                contains[c].append(s_str)

        for src in contains:
            cls._save_relation(src, CONTAINS_RELATION, contains[src])

    @staticmethod
    def _to_ast(script):
        if isinstance(script, Script):
            return script
        elif isinstance(script, str):
            return ScriptParser().parse(script)
        else:
            raise ValueError(script)

    @classmethod
    def _inhibit_relations(cls, script_str, inhibits=None):
        """
        Inhibit a parser relation given the inhibit dict.
        :param script_str: the parser to inhibit.
        :param inhibits: the dict of relation to inhibit.
        :return: None
        """
        if not inhibits:
            return

        unset = {}
        for relation in inhibits:
            unset['RELATIONS.' + relation] = 1

        RelationsConnector().relations.update(
            {'ROOT': script_str},
            {'$unset': unset},
            multi=True
        )

    @staticmethod
    def _get_progressbar(verbose):
        def empty_bar(it):
            yield from it

        if verbose:
            return progressbar.ProgressBar()
        else:
            return empty_bar

    @staticmethod
    def _inhibitions():
        from models.terms.terms import TermsConnector
        return TermsConnector().get_inhibitions()