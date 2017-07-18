import logging
import os
import ply.yacc as yacc

from ... import parser_folder
from ...metaclasses import Singleton
from ...exceptions import CannotParse
from .. import Word, Morpheme, Clause, SuperClause, Sentence, SuperSentence, Text, Hypertext, Hyperlink, PropositionPath
from ...dictionary import Dictionary

from .lexer import get_lexer, tokens


def _add(lp1, p2):
    return lp1[0] + [p2[0]], lp1[1] + p2[1]


def _build(*arg):
    if len(arg) > 1:
        _h = []
        for e in arg[1:]:
            for h in e[1]:
                h[1].insert(0, arg[0])
                _h.append(h)
        return arg[0], _h
    return arg[0], []


def _hyperlink(node, text_list):
    return node[0], node[1] + [(text, [node[0]]) for text in text_list[0]]


class IEMLParser(metaclass=Singleton):
    tokens = tokens

    def __init__(self):

        # Build the lexer and parser
        self.lexer = get_lexer()
        self.parser = yacc.yacc(module=self, errorlog=logging, start='proposition',
                                debug=False, optimize=True, picklefile=os.path.join(parser_folder, "ieml_parser.pickle"))
        self._ieml = None

    def parse(self, s):
        """Parses the input string, and returns a reference to the created AST's root"""
        self._ieml = s
        self.root = None
        self.hyperlinks = []
        self.parser.parse(s, lexer=self.lexer)

        if self.root is not None:
            if self.hyperlinks:
                self.root = Hypertext(self.hyperlinks)
            return self.root
        else:
            raise CannotParse(s)

    # Parsing rules
    def p_ieml_proposition(self, p):
        """proposition : term
                        | morpheme
                        | word
                        | clause
                        | sentence
                        | superclause
                        | supersentence
                        | text"""
        self.root = p[1][0]

    def p_literal_list(self, p):
        """literal_list : literal_list LITERAL
                        | LITERAL"""

        if len(p) == 3:
            p[0] = p[1] + [p[2][1:-1]]
        else:
            p[0] = [p[1][1:-1]]


    def p_term(self, p):
        """term : LBRACKET TERM RBRACKET"""
        p[0] = _build(Dictionary().terms[p[2]])

    def p_proposition_sum(self, p):
        """terms_sum : terms_sum PLUS term
                    | term
            clauses_sum : clauses_sum PLUS clause
                    | clause
            superclauses_sum : superclauses_sum PLUS superclause
                    | superclause
            closed_proposition_list : closed_proposition_list closed_proposition
                                    | closed_proposition"""
        if len(p) == 4:
            p[0] = _add(p[1], p[3])
        elif len(p) == 3:
            p[0] = _add(p[1], p[2])
        else:
            p[0] = _add(([], []), p[1])

    def p_morpheme(self, p):
        """morpheme : LPAREN terms_sum RPAREN"""
        p[0] = _build(Morpheme(p[2][0]), p[2])

    def p_word(self, p):
        """word : LBRACKET morpheme RBRACKET
                | LBRACKET morpheme RBRACKET literal_list
                | LBRACKET morpheme TIMES morpheme RBRACKET
                | LBRACKET morpheme TIMES morpheme RBRACKET literal_list"""

        if len(p) == 4:
            p[0] = _build(Word(root=p[2][0]), p[2])
        elif len(p) == 5:
            p[0] = _build(Word(root=p[2][0], literals=p[4]), p[2])
        elif len(p) == 6:
            p[0] = _build(Word(root=p[2][0], flexing=p[4][0]), p[2], p[4])
        else:
            p[0] = _build(Word(root=p[2][0], flexing=p[4][0], literals=p[6]), p[2], p[4])

    def p_decorated(self, p):
        """decorated_word : word
                           | word text_list
            decorated_sentence : sentence
                                | sentence text_list
            decorated_supersentence : supersentence
                                    | supersentence text_list"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = _hyperlink(p[1], p[2])

    def p_clause(self, p):
        """clause : LPAREN decorated_word TIMES decorated_word TIMES decorated_word RPAREN"""
        p[0] = _build(Clause(substance=p[2][0], attribute=p[4][0], mode=p[6][0]), p[2], p[4], p[6])

    def p_sentence(self, p):
        """sentence : LBRACKET clauses_sum RBRACKET
                    | LBRACKET clauses_sum RBRACKET literal_list"""
        if len(p) == 4:
            p[0] = _build(Sentence(p[2][0]), p[2])
        else:
            p[0] = _build(Sentence(p[2][0], literals=p[4]), p[2])

    def p_superclause(self, p):
        """superclause : LPAREN decorated_sentence TIMES decorated_sentence TIMES decorated_sentence RPAREN"""
        p[0] = _build(SuperClause(substance=p[2][0], attribute=p[4][0], mode=p[6][0]), p[2], p[4], p[6])

    def p_super_sentence(self, p):
        """supersentence : LBRACKET superclauses_sum RBRACKET
                         | LBRACKET superclauses_sum RBRACKET literal_list"""
        if len(p) == 4:
            p[0] = _build(SuperSentence(p[2][0]), p[2])
        else:
            p[0] = _build(SuperSentence(p[2][0], literals=p[4]), p[2])

    def p_closed_proposition(self, p):
        """ closed_proposition : SLASH decorated_word SLASH
                               | SLASH decorated_sentence SLASH
                               | SLASH decorated_supersentence SLASH"""
        p[0] = p[2]

    def p_text(self, p):
        """text : L_CURLY_BRACKET closed_proposition_list R_CURLY_BRACKET"""
        p[0] = _build(Text(p[2][0]))

        if p[2][1]:
            # tuple of the hyperlink (end text, path)
            self.hyperlinks += [Hyperlink(p[0][0], e[0], PropositionPath(e[1])) for e in p[2][1]]

    def p_text_list(self, p):
        """text_list : text_list text
                    | text"""
        if len(p) == 3:
            p[0] = _add(p[1], p[2])
        else:
            p[0] = _add(([], []), p[1])

    def p_error(self, p):
        if p:
            print("Syntax error at '%s' (%d, %d)" % (p.value, p.lineno, p.lexpos))
        else:
            print("Syntax error at EOF")

        raise CannotParse(self._ieml)

if __name__ == '__main__':
    print(str(IEMLParser().parse('[wa.]')))
