import ply.yacc as yacc

from helpers import Singleton
from ..AST import *
from .lexer import get_lexer, tokens
import logging

class Parser(metaclass=Singleton):
    """
        Base class for a parser
    """
    tokens = tokens

    def __init__(self):

        # Build the lexer and parser
        self.lexer = get_lexer()
        self.parser = yacc.yacc(module=self, errorlog=logging)

    def parse(self, s):
        """Parses the input string, and returns a reference to the created AST's root"""
        yacc.parse(s)
        return self.root

    # Parsing rules
    def p_ieml_proposition(self, p):
        """proposition : p_term
                        | morpheme
                        | word
                        | clause
                        | sentence"""
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
        """sentence : LBRACKET superclauses_sum RBRACKET"""
        p[0] = SuperSentence(p[2])

    def p_error(self, p):
        if p:
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")
