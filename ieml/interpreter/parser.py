import ply.yacc as yacc
import os
from .lexer import tokens
from ..AST import *

class Parser:
    """
        Base class for a parser
    """
    tokens = tokens

    def __init__(self, **kw):
        self.debug = kw.get('debug', 0)
        self.names = { }
        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[1] + "_" + self.__class__.__name__
        except:
            modname = "parser"+"_"+self.__class__.__name__
        self.debugfile = modname + ".dbg"
        self.tabmodule = modname + "_" + "parsetab"
        #print self.debugfile, self.tabmodule

        # Build the lexer and parser
        yacc.yacc(module=self,
                  debug=self.debug,
                  debugfile=self.debugfile,
                  tabmodule=self.tabmodule)

    def parse(self, s):
        yacc.parse(s)

    # Parsing rules

    def p_ieml_proposition(self, p):
        """proposition : morpheme
                        | word
                        | clause
                        | sentence
                        | superclause
                        | supersentence"""
        self.names[p[1]] = p[3]

    def p_term(self, p):
        """p_term : LBRACKET TERM RBRACKET"""
        p[0] = Term(p[2])

    def p_terms_sum(self, p):
        """terms_sum : terms_sum PLUS p_term
                    | p_term"""
        if len(p) == 4:
            p[0] = p[1] + p[3]
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