import logging
import types

import ply.yacc as yacc

from helpers.metaclasses import Singleton
from ieml.exceptions import CannotParse
from ieml.script.script import NullScript
from .lexer import get_script_lexer, tokens
from ieml.script import AdditiveScript, MultiplicativeScript
from functools import lru_cache


class ScriptParser(metaclass=Singleton):
    tokens = tokens

    def __init__(self):
        self.root = None
        self.t_add_rules()

        self.lexer = get_script_lexer()
        self.parser = yacc.yacc(module=self, errorlog=logging, start='term', debug=False)
        # rename the parsing method (can't name it directly parse with lru_cache due to ply checking)
        self.parse = self.t_parse

    @lru_cache()
    def t_parse(self, s):
        self.root = None
        self.parser.parse(s, lexer=self.lexer)

        if self.root is not None:
            self.root.check()

            return self.root
        else:
            raise CannotParse()

    def p_error(self, p):
        if p:
            print("Syntax error at '%s' (%d, %d)" % (p.value, p.lineno, p.lexpos))
        else:
            print("Syntax error at EOF")

    # Rules
    def p_term(self, p):
        """ term : script_lvl_0
                | additive_script_lvl_0
                | script_lvl_1
                | additive_script_lvl_1
                | script_lvl_2
                | additive_script_lvl_2
                | script_lvl_3
                | additive_script_lvl_3
                | script_lvl_4
                | additive_script_lvl_4
                | script_lvl_5
                | additive_script_lvl_5
                | script_lvl_6
                | additive_script_lvl_6 """
        self.root = p[1]

    def p_script_lvl_0(self, p):
        """ script_lvl_0 : PRIMITIVE LAYER0_MARK
                            | REMARKABLE_ADDITION LAYER0_MARK"""
        if p[1] == 'E':
            p[0] = NullScript(layer=0)
        elif p[1] in 'OMFI':
            p[0] = AdditiveScript(character=p[1])
        else:
            p[0] = MultiplicativeScript(character=p[1])


    def p_additive_script_lvl_0(self, p):
        """ additive_script_lvl_0 : sum_lvl_0"""
        p[0] = AdditiveScript(children=p[1])

    def p_sum_lvl_0(self, p):
        """ sum_lvl_0 : script_lvl_0
                    | script_lvl_0 PLUS sum_lvl_0"""
        if len(p) == 4:
            p[3].append(p[1])
            p[0] = p[3]
        else:
            p[0] = [p[1]]

    def p_script_lvl_1(self, p):
        """ script_lvl_1 : additive_script_lvl_0 LAYER1_MARK
                        | additive_script_lvl_0 additive_script_lvl_0 LAYER1_MARK
                        | additive_script_lvl_0 additive_script_lvl_0 additive_script_lvl_0 LAYER1_MARK
                        | REMARKABLE_MULTIPLICATION LAYER1_MARK"""
        if isinstance(p[1], AdditiveScript):
            if len(p) == 3:
                p[0] = MultiplicativeScript(substance=p[1])
            elif len(p) == 4:
                p[0] = MultiplicativeScript(substance=p[1],
                                            attribute=p[2])
            else:
                p[0] = MultiplicativeScript(substance=p[1],
                                            attribute=p[2],
                                            mode=p[3])
        else:
            p[0] = MultiplicativeScript(character=p[1])

    def p_sum_lvl_1(self, p):
        """ sum_lvl_1 : script_lvl_1
                    |  script_lvl_1 PLUS sum_lvl_1"""
        if len(p) == 4:
            p[3].append(p[1])
            p[0] = p[3]
        else:
            p[0] = [p[1]]

    def p_additive_script_lvl_1(self, p):
        """ additive_script_lvl_1 : sum_lvl_1 """
        p[0] = AdditiveScript(children=p[1])

    def t_add_rules(self):
        def rule_layer(layer):
            def _sum(self, p):
                if len(p) == 4:
                    p[3].append(p[1])
                    p[0] = p[3]
                else:
                    p[0] = [p[1]]

            def _additive(self, p):
                p[0] = AdditiveScript(children=p[1])

            def _script(self, p):
                if len(p) == 3:
                    p[0] = MultiplicativeScript(substance=AdditiveScript(p[1]))
                elif len(p) == 4:
                    p[0] = MultiplicativeScript(substance=AdditiveScript(p[1]),
                                                attribute=AdditiveScript(p[2]))
                else:
                    p[0] = MultiplicativeScript(substance=AdditiveScript(p[1]),
                                                attribute=AdditiveScript(p[2]),
                                                mode=AdditiveScript(p[3]))

            result = []
            # sum rule
            function = types.FunctionType(_sum.__code__, _sum.__globals__)
            function.__name__ = 'p_sum_lvl_%d'%layer
            function.__doc__ = """sum_lvl_%d : script_lvl_%d
                                            | script_lvl_%d PLUS sum_lvl_%d"""%((layer,)*4)
            result.append(function)

            # additive script rule
            function = types.FunctionType(_additive.__code__, _additive.__globals__)
            function.__name__ = 'p_additive_script_lvl_%d'%layer
            function.__doc__ = "additive_script_lvl_%d : sum_lvl_%d "%((layer,)*2)
            result.append(function)

            function = types.FunctionType(_script.__code__, _script.__globals__)
            function.__name__ = 'p_script_lvl_%d'%layer
            function.__doc__ = """script_lvl_%d : sum_lvl_%d LAYER%d_MARK
                                    | sum_lvl_%d sum_lvl_%d LAYER%d_MARK
                                    | sum_lvl_%d sum_lvl_%d sum_lvl_%d LAYER%d_MARK """%(
                (layer, layer - 1, layer) +
                (layer-1,)*2 + (layer,) +
                (layer-1,)*3 + (layer,))

            result.append(function)

            return result

        for i in range(2, 7):
            for f in rule_layer(i):
                setattr(self.__class__, f.__name__, f)