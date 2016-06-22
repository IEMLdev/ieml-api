from .script import AdditiveScript, MultiplicativeScript, REMARKABLE_MULTIPLICATION_SCRIPT, Script
from .constants import LAYER_MARKS, REMARKABLE_ADDITION, PRIMITVES, OPPOSED_SIBLING_RELATION, \
    ASSOCIATED_SIBLING_RELATION, CROSSED_SIBLING_RELATION, TWIN_SIBLING_RELATION, MAX_LAYER
from ieml.exceptions import NoRemarkableSiblingForAdditiveScript
import re


class RemarkableSibling:

    @classmethod
    def compute_remarkable_siblings_relations(cls, script_ast_list, regex=True):
        """
        Compute the list of relation for remarkable siblings.
        For the relation associated, opposed and crossed, the list take the form of the tuple: (script_src, script_dest).
        For a tuple (a, b) the symetric (b, a) for a relation is always present in the relation's list.
        For the relation twin, the list is all the script that are in relation together.
        :param script_ast_list: the list of script. must all be in the same layer (paradigm)
        :param regex: optional, if true, use the regex algorithm, otherwise, use the ast based algorithm.
        :return:
        """
        relations = {
            # lists of couple (a, b) if a in relation with b
            OPPOSED_SIBLING_RELATION: [],
            ASSOCIATED_SIBLING_RELATION: [],
            CROSSED_SIBLING_RELATION: [],
            # list of all script that are in relation
            TWIN_SIBLING_RELATION: []
        }

        if len(script_ast_list) == 0:
            return relations

        if regex:
            for i, s_src in enumerate(script_ast_list):
                try:
                    opposed = cls.opposed_sibling_regex(s_src)
                except NoRemarkableSiblingForAdditiveScript:
                    opposed = None
                try:
                    associated = cls.associated_sibling_regex(s_src)
                except NoRemarkableSiblingForAdditiveScript:
                    associated = None
                try:
                    cross = cls.cross_sibling_regex(s_src)
                except NoRemarkableSiblingForAdditiveScript:
                    cross = None

                for s_trg in script_ast_list[i:]:
                    if opposed and opposed.match(str(s_trg)):
                        relations[OPPOSED_SIBLING_RELATION].append((s_src, s_trg))
                        # symetrical
                        relations[OPPOSED_SIBLING_RELATION].append((s_trg, s_src))

                    if associated and associated.match(str(s_trg)):
                        relations[ASSOCIATED_SIBLING_RELATION].append((s_src, s_trg))
                        # symetrical
                        relations[ASSOCIATED_SIBLING_RELATION].append((s_trg, s_src))

                    if cross and cross.match(str(s_trg)):
                        relations[CROSSED_SIBLING_RELATION].append((s_src, s_trg))
                        # symetrical
                        relations[CROSSED_SIBLING_RELATION].append((s_trg, s_src))

            # level -> twin regex map
            twin_regex = {}
            for i in range(MAX_LAYER):
                twin_regex[i] = cls.twin_siblings_regex(i)

            for s in script_ast_list:
                if twin_regex[s.layer].match(str(s)):
                    relations[TWIN_SIBLING_RELATION].append(s)
        else:
            # AST based method
            for i, s_src in enumerate(script_ast_list):
                for s_trg in script_ast_list[i:]:
                    if cls.opposed_siblings(s_src, s_trg):
                        relations[OPPOSED_SIBLING_RELATION].append((s_src, s_trg))
                        # symetrical
                        relations[OPPOSED_SIBLING_RELATION].append((s_trg, s_src))

                    if cls.associated_siblings(s_src, s_trg):
                        relations[ASSOCIATED_SIBLING_RELATION].append((s_src, s_trg))
                        # symetrical
                        relations[ASSOCIATED_SIBLING_RELATION].append((s_trg, s_src))

                    if cls.cross_siblings(s_src, s_trg):
                        relations[CROSSED_SIBLING_RELATION].append((s_src, s_trg))
                        # symetrical
                        relations[CROSSED_SIBLING_RELATION].append((s_trg, s_src))

            for s in script_ast_list:
                if cls.twin_siblings(s):
                    relations[TWIN_SIBLING_RELATION].append(s)

        return relations

    @classmethod
    def opposed_sibling_regex(cls, script_ast):
        if isinstance(script_ast, MultiplicativeScript) and script_ast.layer > 0:
            return re.compile(''.join([
                '^',
                cls._opposed_sibling_string(script_ast),
                '$'
            ]))

        raise NoRemarkableSiblingForAdditiveScript()

    @classmethod
    def _opposed_sibling_string(cls, script_ast):
        if isinstance(script_ast, MultiplicativeScript) and script_ast.layer > 0:
            substance = script_ast.children[0]
            attribute = script_ast.children[1]

            return ''.join([
                re.escape(str(attribute)), # substance
                re.escape(str(substance)), # attribute
                cls._regex_layer(attribute.layer, optional=True), # mode
                re.escape(LAYER_MARKS[script_ast.layer])
            ])

    @classmethod
    def associated_sibling_regex(cls, script_ast):
        if isinstance(script_ast, MultiplicativeScript) and script_ast.layer > 0:
            substance = script_ast.children[0]
            attribute = script_ast.children[1]
            mode = script_ast.children[2]

            return re.compile(''.join([
                '^',
                re.escape(str(attribute)),
                re.escape(str(substance)),
                '(?!',
                re.escape(str(mode) + LAYER_MARKS[script_ast.layer]),
                '$)',
                cls._regex_layer(attribute.layer, optional=True),
                re.escape(LAYER_MARKS[script_ast.layer]),
                '$'
            ]))

        raise NoRemarkableSiblingForAdditiveScript()

    @classmethod
    def twin_siblings_regex(cls, layer):
        return re.compile(''.join([
            '^(?P<substance>', # substance
            cls._regex_layer(layer - 1),
            ')(?P=substance)', # attribute == substance
            cls._regex_layer(layer - 1, optional=True),      # mode
            re.escape(LAYER_MARKS[layer]),
            '$'
        ]))

    @classmethod
    def cross_sibling_regex(cls, script_ast):
        if isinstance(script_ast, MultiplicativeScript) and script_ast.layer > 1 and \
                isinstance(script_ast.children[0], MultiplicativeScript) \
           and isinstance(script_ast.children[1], MultiplicativeScript):

            substance = script_ast.children[0]
            attribute = script_ast.children[1]

            return re.compile(''.join([
                '^',
                cls._opposed_sibling_string(substance),
                cls._opposed_sibling_string(attribute),
                cls._regex_layer(substance.layer, optional=True),
                re.escape(LAYER_MARKS[script_ast.layer]),
                '$'
            ]))

    @classmethod
    def _regex_layer(cls, layer, optional=False):
        primitives = [r'+'] + list(REMARKABLE_ADDITION) + list(PRIMITVES)
        if layer > 0:
            primitives += list(REMARKABLE_MULTIPLICATION_SCRIPT)

        primitives += LAYER_MARKS[:layer]

        return '(?:[' + re.escape(''.join(primitives)) + ']+' + re.escape(LAYER_MARKS[layer]) + ')' + \
               ('*' if optional else '')

    @classmethod
    def opposed_siblings(cls, script1, script2):
        if not isinstance(script1, MultiplicativeScript) or not isinstance(script2, MultiplicativeScript):
            return False

        if script1.layer == 0 or script2.layer == 0:
            return False

        return script1.children[0] == script2.children[1] and \
            script1.children[1] == script2.children[0]

    @classmethod
    def associated_siblings(cls, script1, script2):
        if not isinstance(script1, MultiplicativeScript) or not isinstance(script2, MultiplicativeScript):
            return False

        if script1.layer == 0 or script2.layer == 0:
            return False

        return script1.children[0] == script2.children[0] and \
            script1.children[1] == script2.children[1] and \
            script1.children[2] != script2.children[2]

    @classmethod
    def twin_siblings(cls, script):
        if not isinstance(script, MultiplicativeScript):
            return False

        if script.layer == 0:
            return False

        return script.children[0] == script.children[1]

    @classmethod
    def cross_siblings(cls, script1, script2):
        if not isinstance(script1, MultiplicativeScript) or not isinstance(script2, MultiplicativeScript):
            return False

        if script1.layer < 2 or script2.layer < 2:
            return False

        return cls.opposed_siblings(script1.children[0], script2.children[1]) and \
            cls.opposed_siblings(script1.children[1], script2.children[0])
