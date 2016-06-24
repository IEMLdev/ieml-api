import logging

import ply.yacc as yacc

from helpers.metaclasses import Singleton
from ieml.exceptions import CannotParse
from .lexer import get_script_lexer, tokens
from ieml.script import AdditiveScript, MultiplicativeScript
from functools import lru_cache


class ScriptParser(metaclass=Singleton):
    tokens = tokens

    def __init__(self):
        self.root = None

        self.lexer = get_script_lexer()
        self.parser = yacc.yacc(module=self, errorlog=logging, start='term', debug=False)

        # rename the parsing method (can't name it directly parse with lru_cache due to ply checking)
        self.parse = self.t_parse

    @lru_cache()
    def t_parse(self, s):
        self.root = None
        self.parser.parse(s)

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
        """ script_lvl_0 : PRIMITIVE LAYER0_MARK"""
        p[0] = MultiplicativeScript(character=p[1])

    def p_additive_script_lvl_0(self, p):
        """ additive_script_lvl_0 : REMARKABLE_ADDITION LAYER0_MARK
                                 | sum_lvl_0"""
        if isinstance(p[1], list):
            p[0] = AdditiveScript(children=p[1])
        else:
            p[0] = AdditiveScript(character=p[1])

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

    def p_script_lvl_2(self, p):
        """ script_lvl_2 : sum_lvl_1 LAYER2_MARK
                        | sum_lvl_1 sum_lvl_1 LAYER2_MARK
                        | sum_lvl_1 sum_lvl_1 sum_lvl_1 LAYER2_MARK"""
        if len(p) == 3:
            p[0] = MultiplicativeScript(substance=AdditiveScript(p[1]))
        elif len(p) == 4:
            p[0] = MultiplicativeScript(substance=AdditiveScript(p[1]),
                                        attribute=AdditiveScript(p[2]))
        else:
            p[0] = MultiplicativeScript(substance=AdditiveScript(p[1]),
                                        attribute=AdditiveScript(p[2]),
                                        mode=AdditiveScript(p[3]))
    def p_sum_lvl_2(self, p):
        """ sum_lvl_2 : script_lvl_2
                    | script_lvl_2 PLUS sum_lvl_2"""
        if len(p) == 4:
            p[3].append(p[1])
            p[0] = p[3]
        else:
            p[0] = [p[1]]

    def p_additive_script_lvl_2(self, p):
        """ additive_script_lvl_2 : sum_lvl_2 """
        p[0] = AdditiveScript(children=p[1])

    def p_script_lvl_3(self, p):
        """ script_lvl_3 : sum_lvl_2 LAYER3_MARK
                        | sum_lvl_2 sum_lvl_2 LAYER3_MARK
                        | sum_lvl_2 sum_lvl_2 sum_lvl_2 LAYER3_MARK"""
        if len(p) == 3:
            p[0] = MultiplicativeScript(substance=AdditiveScript(p[1]))
        elif len(p) == 4:
            p[0] = MultiplicativeScript(substance=AdditiveScript(p[1]),
                                        attribute=AdditiveScript(p[2]))
        else:
            p[0] = MultiplicativeScript(substance=AdditiveScript(p[1]),
                                        attribute=AdditiveScript(p[2]),
                                        mode=AdditiveScript(p[3]))

    def p_sum_lvl_3(self, p):
        """ sum_lvl_3 : script_lvl_3
                    | script_lvl_3 PLUS sum_lvl_3"""
        if len(p) == 4:
            p[3].append(p[1])
            p[0] = p[3]
        else:
            p[0] = [p[1]]

    def p_additive_script_lvl_3(self, p):
        """ additive_script_lvl_3 : sum_lvl_3 """
        p[0] = AdditiveScript(children=p[1])

    def p_script_lvl_4(self, p):
        """ script_lvl_4 : sum_lvl_3 LAYER4_MARK
                        | sum_lvl_3 sum_lvl_3 LAYER4_MARK
                        | sum_lvl_3 sum_lvl_3 sum_lvl_3 LAYER4_MARK"""
        if len(p) == 3:
            p[0] = MultiplicativeScript(substance=AdditiveScript(p[1]))
        elif len(p) == 4:
            p[0] = MultiplicativeScript(substance=AdditiveScript(p[1]),
                                        attribute=AdditiveScript(p[2]))
        else:
            p[0] = MultiplicativeScript(substance=AdditiveScript(p[1]),
                                        attribute=AdditiveScript(p[2]),
                                        mode=AdditiveScript(p[3]))

    def p_sum_lvl_4(self, p):
        """ sum_lvl_4 : script_lvl_4
                    | script_lvl_4 PLUS sum_lvl_4"""
        if len(p) == 4:
            p[3].append(p[1])
            p[0] = p[3]
        else:
            p[0] = [p[1]]

    def p_additive_script_lvl_4(self, p):
        """ additive_script_lvl_4 : sum_lvl_4 """
        p[0] = AdditiveScript(children=p[1])

    def p_script_lvl_5(self, p):
        """ script_lvl_5 : sum_lvl_4 LAYER5_MARK
                        | sum_lvl_4 sum_lvl_4 LAYER5_MARK
                        | sum_lvl_4 sum_lvl_4 sum_lvl_4 LAYER5_MARK"""
        if len(p) == 3:
            p[0] = MultiplicativeScript(substance=AdditiveScript(p[1]))
        elif len(p) == 4:
            p[0] = MultiplicativeScript(substance=AdditiveScript(p[1]),
                                        attribute=AdditiveScript(p[2]))
        else:
            p[0] = MultiplicativeScript(substance=AdditiveScript(p[1]),
                                        attribute=AdditiveScript(p[2]),
                                        mode=AdditiveScript(p[3]))

    def p_sum_lvl_5(self, p):
        """ sum_lvl_5 : script_lvl_5
                    | script_lvl_5 PLUS sum_lvl_5"""
        if len(p) == 4:
            p[3].append(p[1])
            p[0] = p[3]
        else:
            p[0] = [p[1]]

    def p_additive_script_lvl_5(self, p):
        """ additive_script_lvl_5 : sum_lvl_5 """
        p[0] = AdditiveScript(children=p[1])

    def p_script_lvl_6(self, p):
        """ script_lvl_6 : sum_lvl_5 LAYER6_MARK
                        | sum_lvl_5 sum_lvl_5 LAYER6_MARK
                        | sum_lvl_5 sum_lvl_5 sum_lvl_5 LAYER6_MARK"""
        if len(p) == 3:
            p[0] = MultiplicativeScript(substance=AdditiveScript(p[1]))
        elif len(p) == 4:
            p[0] = MultiplicativeScript(substance=AdditiveScript(p[1]),
                                        attribute=AdditiveScript(p[2]))
        else:
            p[0] = MultiplicativeScript(substance=AdditiveScript(p[1]),
                                        attribute=AdditiveScript(p[2]),
                                        mode=AdditiveScript(p[3]))

    def p_sum_lvl_6(self, p):
        """ sum_lvl_6 : script_lvl_6
                    | script_lvl_6 PLUS sum_lvl_6"""
        if len(p) == 4:
            p[3].append(p[1])
            p[0] = p[3]
        else:
            p[0] = [p[1]]

    def p_additive_script_lvl_6(self, p):
        """ additive_script_lvl_6 : sum_lvl_6 """
        p[0] = AdditiveScript(children=p[1])
