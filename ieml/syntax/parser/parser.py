import logging
import os
from functools import partial
import ply.yacc as yacc

from ieml.dictionary.terms import Term
from ieml.dictionary.version import DictionaryVersion
from ieml.dictionary.dictionary import Dictionary
from ieml.dictionary.tools import term
from ieml.exceptions import TermNotFoundInDictionary, InvalidIEMLObjectArgument
from ieml.syntax.terms import SyntaxTerm
from ... import parser_folder
from ...exceptions import CannotParse
from ieml.syntax import Word, Morpheme, Clause, SuperClause, Sentence, SuperSentence, Text, Hypertext, Hyperlink, PropositionPath

from .lexer import get_lexer, tokens
import threading

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


class IEMLParserSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        dictionary = args[0] if len(args) > 0 else \
            kwargs['dictionary'] if 'dictionary' in kwargs else None

        if dictionary is None:
            dictionary = Dictionary()

        if not isinstance(dictionary, Dictionary):
            dictionary = Dictionary(dictionary)

        if dictionary.version not in cls._instances:
            # this code is to clean up duplicate class if we reload modules
            cls._instances[dictionary.version] = \
                super(IEMLParserSingleton, cls).__call__(dictionary=dictionary)

        return cls._instances[dictionary.version]


class IEMLParser(metaclass=IEMLParserSingleton):
    tokens = tokens
    lock = threading.Lock()

    def __init__(self, dictionary=None):

        self._get_term = partial(term, dictionary=dictionary)

        # Build the lexer and parser
        self.lexer = get_lexer()
        self.parser = yacc.yacc(module=self, errorlog=logging, start='proposition',
                                debug=False, optimize=True, picklefile=os.path.join(parser_folder, "ieml_parser.pickle"))
        self._ieml = None

    def parse(self, s):
        """Parses the input string, and returns a reference to the created AST's root"""
        # self._ieml = s
        # self.root = None
        # self.hyperlinks = []
        with self.lock:
            try:
                return self.parser.parse(s, lexer=self.lexer)
            except InvalidIEMLObjectArgument as e:
                raise CannotParse(s, str(e))
            except CannotParse as e:
                e.s = s
                raise e

            # if self.root is not None:
        #     if self.hyperlinks:
        #         self.root = Hypertext(self.hyperlinks)
        #
        #     # if isinstance(self.root, Term):
        #     #     self.root = Word(root=Morpheme([self.root]))
        #
        #     return self.root
        # else:
        #     raise CannotParse(s, "Invalid ieml object.")

    # Parsing rules
    def p_ieml_proposition(self, p):
        """proposition : script
                        | term
                        | morpheme
                        | word
                        | clause
                        | sentence
                        | superclause
                        | supersentence
                        | text"""
        if isinstance(p[1], Term):
            # script rule
            p[0] = SyntaxTerm(p[1])
        else:
            p[0] = p[1][0]

    def p_literal_list(self, p):
        """literal_list : literal_list LITERAL
                        | LITERAL"""

        if len(p) == 3:
            p[0] = p[1] + [p[2][1:-1]]
        else:
            p[0] = [p[1][1:-1]]


    def p_script(self, p):
        """script : TERM """
        try:
            p[0] = self._get_term(p[1])
        except TermNotFoundInDictionary as e:
            raise CannotParse(self._ieml, str(e))

    def p_term(self, p):
        """term : LBRACKET script RBRACKET
                | LBRACKET script RBRACKET literal_list"""
        if len(p) == 4:
            p[0] = _build(SyntaxTerm(p[2]))
        else:
            p[0] = _build(SyntaxTerm(p[2], literals=p[4]))


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
            raise NotImplementedError("Ieml doesn't support hypertext parsing for the moment.")
            # tuple of the hyperlink (end text, path)
            # self.hyperlinks += [Hyperlink(p[0][0], e[0], PropositionPath(e[1])) for e in p[2][1]]

    def p_text_list(self, p):
        """text_list : text_list text
                    | text"""
        if len(p) == 3:
            p[0] = _add(p[1], p[2])
        else:
            p[0] = _add(([], []), p[1])

    def p_error(self, p):
        if p:
            msg = "Syntax error at '%s' (%d, %d)" % (p.value, p.lineno, p.lexpos)
        else:
            msg = "Syntax error at EOF"

        raise CannotParse(None, msg)
