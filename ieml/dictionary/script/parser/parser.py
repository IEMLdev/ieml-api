import logging
import types
from functools import lru_cache
import os
import ply.yacc as yacc
from sly import Parser
from sly.yacc import YaccProduction

from ieml.exceptions import InvalidScript, CannotParse
from ieml.dictionary.script import AdditiveScript, MultiplicativeScript, NullScript
from ieml.constants import REMARKABLE_ADDITION, PARSER_FOLDER
from ieml.commons import Singleton
from .lexer import ScriptLexer

import threading


#  TODO : make into a singleton
class ScriptParser(Parser):
    tokens = ScriptLexer.tokens
    lexer = ScriptLexer()

    # ply have an internal state , then we forbid two thread try to parse a string simultaneously
    lock = threading.Lock()

    def __init__(self):
        self.t_add_rules()

    @lru_cache(maxsize=10000)
    def parse_script(self, s: str):
        with self.lock:
            try:
                return self.parse(self.lexer.tokenize(s))
            except InvalidScript as e:
                raise CannotParse(s, str(e))

    def error(self, p: YaccProduction):
        # TODO: refactor
        if p:
            msg = "Syntax error at '%s' (%d, %d)" % (p.value, p.lineno, p.lexpos)
        else:
            msg = "Syntax error at EOF"

        raise InvalidScript(msg)

    @_("script_lvl_0",
       "additive_script_lvl_0",
       "script_lvl_1",
       "additive_script_lvl_1",
       "script_lvl_2",
       "additive_script_lvl_2",
       "script_lvl_3",
       "additive_script_lvl_3",
       "script_lvl_4",
       "additive_script_lvl_4",
       "script_lvl_5",
       "additive_script_lvl_5",
       "script_lvl_6",
       "additive_script_lvl_6 ")
    def term(self, p):
        return p[1]

    @_("PRIMITIVE LAYER0_MARK")
    def script_lvl_0(self, p: YaccProduction):
        if p.PRIMITIVE == 'E':
            return NullScript(layer=0)
        else:
           return MultiplicativeScript(character=p.PRIMITIVE)

    @_("REMARKABLE_ADDITION LAYER0_MARK")
    def script_lvl_0(self, p: YaccProduction):
        return AdditiveScript(character=p.REMARKABLE_ADDITION)

    @_("sum_lvl_0")
    def additive_script_lvl_0(self, p: YaccProduction):
        return AdditiveScript(children=p[1])
    
    @_("script_lvl_0",
       "sum_lvl_0 PLUS script_lvl_0")
    def sum_lvl_0(self, p: YaccProduction):
        if len(p) == 3:
            p[0].append(p[2])
            return p[3]
        else:
            return [p[1]]

    @_("additive_script_lvl_0 LAYER1_MARK",
       "additive_script_lvl_0 additive_script_lvl_0 LAYER1_MARK",
       "additive_script_lvl_0 additive_script_lvl_0 additive_script_lvl_0 LAYER1_MARK")
    def script_lvl_1(self, p: YaccProduction):
        if len(p) == 2:
            return MultiplicativeScript(substance=p[0])
        elif len(p) == 3:
            return MultiplicativeScript(substance=p[0],
                                        attribute=p[1])
        else:
            return MultiplicativeScript(substance=p[0],
                                        attribute=p[1],
                                        mode=p[2])

    @_("REMARKABLE_MULTIPLICATION LAYER1_MARK")
    def script_lvl_1(self, p: YaccProduction):
        return MultiplicativeScript(character=p.REMARKABLE_MULTIPLICATION)

    # TODO use parser state and a generic rule to parse sums and levels
    def sum_lvl_1(self, p):
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
            function.__name__ = 'p_sum_lvl_%d' % layer
            function.__doc__ = """sum_lvl_%d : script_lvl_%d
                                            | script_lvl_%d PLUS sum_lvl_%d""" % ((layer,) * 4)
            result.append(function)

            # additive parser rule
            function = types.FunctionType(_additive.__code__, _additive.__globals__)
            function.__name__ = 'p_additive_script_lvl_%d' % layer
            function.__doc__ = "additive_script_lvl_%d : sum_lvl_%d " % ((layer,) * 2)
            result.append(function)

            function = types.FunctionType(_script.__code__, _script.__globals__)
            function.__name__ = 'p_script_lvl_%d' % layer
            function.__doc__ = """script_lvl_%d : sum_lvl_%d LAYER%d_MARK
                                    | sum_lvl_%d sum_lvl_%d LAYER%d_MARK
                                    | sum_lvl_%d sum_lvl_%d sum_lvl_%d LAYER%d_MARK """ % (
                    (layer, layer - 1, layer) +
                    (layer - 1,) * 2 + (layer,) +
                    (layer - 1,) * 3 + (layer,))

            result.append(function)

            return result

        for i in range(2, 7):
            for f in rule_layer(i):
                setattr(self.__class__, f.__name__, f)
