import logging

import ply.yacc as yacc

from ieml.AST import *
from .lexer import get_lexer, tokens

class PropositionsParser(metaclass=Singleton):
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
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")


class USLParser(PropositionsParser):
    """This parser inherits from the basic propositionnal parser, but adds supports for embedded USL's.
    Thus, some parsing rules are modified"""

    # Parsing rules
    def p_ieml_proposition(self, p):
        """proposition : p_term
                        | morpheme
                        | word
                        | clause
                        | sentence
                        | superclause
                        | supersentence"""
        p[0] = p[1]

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
            p[0].add_hyperlink(p[-1]) # last element is the usl_list

    def p_sentence(self, p):
        """sentence : LBRACKET clauses_sum RBRACKET
                    | LBRACKET clauses_sum RBRACKET usl_list"""
        p[0] = Sentence(p[2])
        if len(p) == 5:
             p[0].add_hyperlink(p[4])

    def p_super_sentence(self, p):
        """sentence : LBRACKET superclauses_sum RBRACKET
                    | LBRACKET superclauses_sum RBRACKET usl_list"""
        p[0] = SuperSentence(p[2])
        if len(p) == 5:
             p[0].add_hyperlink(p[4])

    def p_closed_proposition(self, p):
        """closed_proposition : SLASH word SLASH
                            | SLASH sentence SLASH
                            | SLASH super SLASH"""
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
        """usl : L_CURLY_BRACKET closed_proposition_list R_CURLY_BRACKET"""
        p[0] = USL(p[2])

    def p_hypertext(self, p):
        """hypertext : usl"""
        self.root = p[1]