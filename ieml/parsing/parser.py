import logging

import ply.yacc as yacc

from helpers.metaclasses import Singleton
from ieml.AST import Word, Morpheme, Clause, SuperClause, Sentence, SuperSentence, Term, Text, HyperText
from ieml.exceptions import CannotParse
from .lexer import get_lexer, get_script_lexer, tokens
from ieml.script import AdditiveScript, MultiplicativeScript, null_element


class ScriptParser(metaclass=Singleton):
    tokens = tokens

    def __init__(self):
        self.root = None

        self.lexer = get_script_lexer()
        self.parser = yacc.yacc(module=self, errorlog=logging, start='term')

    def parse(self, s):
        self.root = None
        self.parser.parse(s)

        if self.root is not None:
            print(self.root)
            self.root.check()
            return self.root
        else:
            raise CannotParse()
    def p_error(self, p):
        print("Error at " + p.lineno + " " + p.value)


    # Rules
    def p_term(self, p):
        """ term : script_lvl_0
                | script_lvl_1
                | script_lvl_2
                | script_lvl_3
                | script_lvl_4
                | script_lvl_5
                | script_lvl_6 """
        self.root = p[1]

    def p_script_lvl_0(self, p):
        """ script_lvl_0 : PRIMITIVE LAYER0_MARK"""
        p[0] = MultiplicativeScript(character=p[1])

    def p_additive_script_lvl_0(self, p):
        """ additive_script_lvl_0 : REMARKABLE_ADDITION
                            | sum_lvl_0"""
        if isinstance(p[1], list):
            p[0] = AdditiveScript(children=p[1])
        else:
            p[0] = AdditiveScript(character=p[1])

    def p_sum_lvl_0(self, p):
        """ sum_lvl_0 : script_lvl_0
                        script_lvl_0 PLUS sum_lvl_0"""
        if len(p) == 3:
            p[0] = [p[1]]
        else:
            p[0].push(p[1])

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
                    | script_lvl_1 PLUS sum_lvl_1"""
        if len(p) == 3:
            p[0] = [p[1]]
        else:
            p[0].push(p[1])

    def p_script_lvl_2(self, p):
        """ script_lvl_2 : sum_lvl_1 LAYER2_MARK"""
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
        if len(p) == 3:
            p[0] = [p[1]]
        else:
            p[0].push(p[1])

    def p_script_lvl_3(self, p):
        """ script_lvl_3 : sum_lvl_2 LAYER3_MARK"""
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
        if len(p) == 3:
            p[0] = [p[1]]
        else:
            p[0].push(p[1])

    def p_script_lvl_4(self, p):
        """ script_lvl_4 : sum_lvl_3 LAYER4_MARK"""
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
        if len(p) == 3:
            p[0] = [p[1]]
        else:
            p[0].push(p[1])

    def p_script_lvl_5(self, p):
        """ script_lvl_5 : sum_lvl_4 LAYER5_MARK"""
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
        if len(p) == 3:
            p[0] = [p[1]]
        else:
            p[0].push(p[1])

    def p_script_lvl_6(self, p):
        """ script_lvl_6: sum_lvl_5 LAYER6_MARK"""
        if len(p) == 3:
            p[0] = MultiplicativeScript(substance=AdditiveScript(p[1]))
        elif len(p) == 4:
            p[0] = MultiplicativeScript(substance=AdditiveScript(p[1]),
                                        attribute=AdditiveScript(p[2]))
        else:
            p[0] = MultiplicativeScript(substance=AdditiveScript(p[1]),
                                        attribute=AdditiveScript(p[2]),
                                        mode=AdditiveScript(p[3]))


class PropositionsParser(metaclass=Singleton):
    """
        Base class for a parser
    """
    tokens = tokens

    def __init__(self):

        # Build the lexer and parser
        self.lexer = get_lexer()
        self.parser = yacc.yacc(module=self, errorlog=logging, start='proposition')

    def parse(self, s):
        """Parses the input string, and returns a reference to the created AST's root"""
        self.root = None
        self.parser.parse(s)

        if self.root is not None:
            self.root.check()
            self.root.order()
            return self.root
        else:
            raise CannotParse()

    # Parsing rules
    def p_ieml_proposition(self, p):
        """proposition : p_term
                        | morpheme
                        | word
                        | clause
                        | sentence
                        | superclause
                        | supersentence"""
        self.root = p[1]

    def p_term(self, p):
        """p_term : LBRACKET TERM RBRACKET"""
        p[0] = Term(p[2])

    def p_proposition_sum(self, p):
        """terms_sum : terms_sum PLUS p_term
                    | p_term
            clauses_sum : clauses_sum PLUS clause
                    | clause
            superclauses_sum : superclauses_sum PLUS superclause
                    | superclause"""
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    def p_morpheme(self, p):
        """morpheme : LPAREN terms_sum RPAREN"""
        p[0] = Morpheme(p[2])

    def p_word(self, p):
        """word : LBRACKET morpheme RBRACKET
                | LBRACKET morpheme TIMES morpheme RBRACKET"""
        if len(p) == 4:
            p[0] = Word(p[2])
        else:
            p[0] = Word(p[2], p[4])

    def p_clause(self, p):
        """clause : LPAREN word TIMES word TIMES word RPAREN"""
        p[0] = Clause(p[2], p[4], p[6])

    def p_sentence(self, p):
        """sentence : LBRACKET clauses_sum RBRACKET"""
        p[0] = Sentence(p[2])

    def p_superclause(self, p):
        """superclause : LPAREN sentence TIMES sentence TIMES sentence RPAREN"""
        p[0] = SuperClause(p[2], p[4], p[6])

    def p_super_sentence(self, p):
        """supersentence : LBRACKET superclauses_sum RBRACKET"""
        p[0] = SuperSentence(p[2])

    def p_error(self, p):
        if p:
            print("Syntax error at '%s' (%d, %d)" % (p.value, p.lineno, p.lexpos))
        else:
            print("Syntax error at EOF")


class USLParser(PropositionsParser):
    """This parser inherits from the basic propositionnal parser, but adds supports for embedded USL's.
    Thus, some parsing rules are modified"""

    def __init__(self):
        # Build the lexer and parser
        self.lexer = get_lexer()
        self.parser = yacc.yacc(module=self, errorlog=logging, start='hypertext')
        self.p_ieml_proposition = None

    def p_hypertext(self, p):
        """hypertext : usl"""
        literal, hypertext = p[1]
        if literal is not None:
            raise CannotParse()

        self.root = hypertext

    def p_word(self, p):
        """word : LBRACKET morpheme RBRACKET
                | LBRACKET morpheme TIMES morpheme RBRACKET
                | LBRACKET morpheme RBRACKET usl_list
                | LBRACKET morpheme TIMES morpheme RBRACKET usl_list
                """
        if len(p) == 4 or len(p) == 5:
            p[0] = Word(p[2])
        else:
            p[0] = Word(p[2], p[4])

        # if there's an USL list (hyperlinks), we're attaching it to the proposition
        if len(p) == 5 or len(p) == 7:
            p[0].add_hyperlink_list(p[len(p) - 1]) # last element is the usl_list

    def p_sentence(self, p):
        """sentence : LBRACKET clauses_sum RBRACKET
                    | LBRACKET clauses_sum RBRACKET usl_list"""
        p[0] = Sentence(p[2])
        if len(p) == 5:
             p[0].add_hyperlink_list(p[4])

    def p_super_sentence(self, p):
        """supersentence : LBRACKET superclauses_sum RBRACKET
                    | LBRACKET superclauses_sum RBRACKET usl_list"""
        p[0] = SuperSentence(p[2])
        if len(p) == 5:
             p[0].add_hyperlink_list(p[4])

    def p_closed_proposition(self, p):
        """closed_proposition : SLASH word SLASH
                            | SLASH sentence SLASH
                            | SLASH supersentence SLASH"""
        p[0] = p[2]

    def p_closed_proposition_list(self, p):
        """closed_proposition_list : closed_proposition_list closed_proposition
                                    | closed_proposition"""
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    def p_usl_list(self, p):
        """usl_list : usl_list usl
                    | usl"""
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    def p_usl(self, p):
        """usl : LITERAL L_CURLY_BRACKET closed_proposition_list R_CURLY_BRACKET
                | L_CURLY_BRACKET closed_proposition_list R_CURLY_BRACKET"""
        if len(p) == 5:
            literal = p[1][1:-1] # scrap out the <>
            p[0] = (literal, HyperText(Text(p[3])))
        else:
            p[0] = (None, HyperText(Text(p[2])))
