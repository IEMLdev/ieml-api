import ply.yacc as yacc
import ply.lex as lex
from ..AST import *
from .lexer import get_lexer, tokens
import logging

class Parser:
    """
        Base class for a parser
    """
    tokens = tokens

    def __init__(self):

        # Build the lexer and parser
        self.lexer = get_lexer()
        self.parser = yacc.yacc(module=self, errorlog=logging)

    def parse(self, s):
        yacc.parse(s)

    # Parsing rules

    def p_ieml_proposition(self, p):
        """proposition : morpheme
                        | word
                        """
        self.root = p[1]

    def p_term(self, p):
        """p_term : LBRACKET TERM RBRACKET"""
        p[0] = Term(p[2])

    def p_terms_sum(self, p):
        """terms_sum : terms_sum PLUS p_term
                    | p_term"""
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

    def p_error(self, p):
        if p:
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")

if __name__ == '__main__':
    calc = Parser()
    calc.parse()