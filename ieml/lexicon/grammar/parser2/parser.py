import logging
import os
import ply.yacc as yacc

from ieml.constants import PARSER_FOLDER
from ieml.dictionary.script import script
from ieml.exceptions import TermNotFoundInDictionary, InvalidIEMLObjectArgument


from ieml.lexicon.syntax import Trait, TraitParadigm, Character, Word
# from ieml.lexicon.grammar import Text, word
# from ieml.lexicon.grammar.fact import Fact
# from ieml.lexicon.grammar.theory import Theory
from ieml.exceptions import CannotParse

from .lexer import get_lexer, tokens
import threading

# def _add(lp1, p2):
#     return lp1[0] + [p2[0]], lp1[1] + p2[1]
#
# def _build(*arg):
#     if len(arg) > 1:
#         _h = []
#         for e in arg[1:]:
#             for h in e[1]:
#                 h[1].insert(0, arg[0])
#                 _h.append(h)
#         return arg[0], _h
#     return arg[0], []
#
#
# def _hyperlink(node, text_list):
#     return node[0], node[1] + [(text, [node[0]]) for text in text_list[0]]


class IEMLParserSingleton(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        # dictionary = args[0] if len(args) > 0 else \
        #     kwargs['dictionary'] if 'dictionary' in kwargs else None

        # if dictionary is None:
        #     dictionary = Dictionary.load()

        # if not isinstance(dictionary, Dictionary):
        #     dictionary = Dictionary.load(dictionary)

        if cls._instance is None:
            # this code is to clean up duplicate class if we reload modules
            cls._instance = super(IEMLParserSingleton, cls).__call__()

        return cls._instance


class IEMLParser():
    tokens = tokens
    lock = threading.Lock()

    def __init__(self):
        # from ieml.dictionary.tools import term

        # self._get_term = partial(term, dictionary=dictionary)

        # Build the lexer and parser
        self.lexer = get_lexer()
        self.parser = yacc.yacc(module=self, errorlog=logging, start='proposition',
                                debug=True, optimize=True,)
                                # picklefile=os.path.join(PARSER_FOLDER, "ieml_parser2.pickle"))
        self._ieml = None

    def parse(self, s):
        """Parses the input string, and returns a reference to the created AST's root"""
        with self.lock:
            try:
                return self.parser.parse(s, lexer=self.lexer)
            except InvalidIEMLObjectArgument as e:
                raise CannotParse(s, str(e))
            except CannotParse as e:
                e.s = s
                raise e


    # Parsing rules
    def p_ieml_proposition(self, p):
        """proposition :  trait
                        | character
                        | word"""
        p[0] = p[1]

    # def p_literal_list(self, p):
    #     """literal_list : literal_list LITERAL
    #                     | LITERAL"""
    #
    #     if len(p) == 3:
    #         p[0] = p[1] + [p[2][1:-1]]
    #     else:
    #         p[0] = [p[1][1:-1]]


    def p_morpheme(self, p):
        """morpheme : MORPHEME"""
                    # | MORPHEME literal_list"""

        morpheme = script(p[1])
        if len(p) == 3:
            logging.error("Literals not supported on script for the moments, and are ignored.")

        p[0] = morpheme


    def p_morpheme_sum(self, p):
        """morpheme_sum : morpheme_sum morpheme
                        | morpheme"""

        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    def p_trait(self, p):
        """trait : morpheme_sum """
        p[0] = Trait(p[1])

    def p_trait_content(self, p):
        """trait_content : LCHEVRON LCHEVRON trait RCHEVRON RCHEVRON"""
        p[0] = p[3]

    def p_trait_function_list(self, p):
        """trait_function_list : trait_function_list LCHEVRON trait RCHEVRON
                                | LCHEVRON trait RCHEVRON """

        if len(p) == 4:
            p[0] = [p[2]]
        else:
            p[0] = p[1] + [p[3]]

    def p_character(self, p):
        """character : LBRACKET trait_content trait_function_list RBRACKET
                     | LBRACKET trait_function_list RBRACKET
                     | LBRACKET trait_content RBRACKET"""
        if len(p) == 4 and isinstance(p[2], list):
            content = None
            functions = p[2]
        elif len(p) == 4:
            content = p[2]
            functions = []
        else:
            content = p[2]
            functions = p[3]

        p[0] = Character(content=content, functions=functions)

    def p_word(self, p):
        """word : LPAREN character TIMES character TIMES character RPAREN"""
        p[0] = Word(substance=p[2], attribute=p[4], mode=p[6])
    #
    # def p_topic(self, p):
    #     """topic : LBRACKET morpheme RBRACKET
    #             | LBRACKET morpheme RBRACKET literal_list
    #             | LBRACKET morpheme TIMES morpheme RBRACKET
    #             | LBRACKET morpheme TIMES morpheme RBRACKET literal_list
    #             | LBRACKET morpheme TIMES morpheme TIMES morpheme RBRACKET
    #             | LBRACKET morpheme TIMES morpheme TIMES morpheme RBRACKET literal_list"""
    #
    #     if len(p) == 4:
    #         p[0] = word(substance=p[2])
    #     elif len(p) == 5:
    #         p[0] = word(substance=p[2], literals=p[4])
    #     elif len(p) == 6:
    #         p[0] = word(substance=p[2], attribute=p[4])
    #     elif len(p) == 7:
    #         p[0] = word(substance=p[2], attribute=p[4], literals=p[6])
    #     elif len(p) == 8:
    #         p[0] = word(substance=p[2], attribute=p[4], mode=p[6])
    #     else:
    #         p[0] = word(substance=p[2], attribute=p[4], mode=p[6], literals=p[8])
    #
    #
    # # def p_decorated(self, p):
    # #     """decorated_word : word
    # #                        | word text_list
    # #         decorated_sentence : sentence
    # #                             | sentence text_list
    # #         decorated_supersentence : supersentence
    # #                                 | supersentence text_list"""
    # #     if len(p) == 2:
    # #         p[0] = p[1]
    # #     else:
    # #         p[0] = _hyperlink(p[1], p[2])
    #
    # def p_clause(self, p):
    #     """clause : LPAREN topic TIMES topic TIMES topic RPAREN"""
    #
    #     # """clause : LPAREN decorated_word TIMES decorated_word TIMES decorated_word RPAREN"""
    #     p[0] = (p[2], p[4], p[6])
    #
    # def p_fact(self, p):
    #     """fact : LBRACKET clauses_sum RBRACKET
    #             | LBRACKET clauses_sum RBRACKET literal_list"""
    #     if len(p) == 4:
    #         p[0] = Fact(p[2])
    #     else:
    #         p[0] = Fact(p[2], literals=p[4])
    #
    # def p_superclause(self, p):
    #     """superclause : LPAREN fact TIMES fact TIMES fact RPAREN"""
    #     # """theory : LPAREN decorated_sentence TIMES decorated_sentence TIMES decorated_sentence RPAREN"""
    #     p[0] = (p[2], p[4], p[6])
    #
    # def p_theory(self, p):
    #     """theory : LBRACKET superclauses_sum RBRACKET
    #               | LBRACKET superclauses_sum RBRACKET literal_list"""
    #     if len(p) == 4:
    #         p[0] = Theory(p[2])
    #     else:
    #         p[0] = Theory(p[2], literals=p[4])
    #
    # def p_closed_proposition(self, p):
    #     """ closed_proposition : topic
    #                            | fact
    #                            | theory"""
    #     p[0] = p[1]
    #
    # def p_closed_proposition_list(self, p):
    #     """ closed_proposition_list :  closed_proposition_list SLASH SLASH closed_proposition
    #                                 | closed_proposition"""
    #     if len(p) == 2:
    #         p[0] = [p[1]]
    #     else:
    #         p[0] = p[1] + [p[4]]
    #
    # def p_text(self, p):
    #     """text : SLASH closed_proposition_list SLASH"""
    #     p[0] = Text(p[2])
    #
    #     # if p[2][1]:
    #     #     raise NotImplementedError("Ieml doesn't support hypertext parsing for the moment.")
    #         # tuple of the hyperlink (end text, path)
    #         # self.hyperlinks += [Hyperlink(p[0][0], e[0], PropositionPath(e[1])) for e in p[2][1]]

    # def p_text_list(self, p):
    #     """text_list : text_list text
    #                 | text"""
    #     if len(p) == 3:
    #         p[0] = _add(p[1], p[2])
    #     else:
    #         p[0] = _add(([], []), p[1])

    def p_error(self, p):
        if p:
            msg = "Syntax error at '%s' (%d, %d)" % (p.value, p.lineno, p.lexpos)
        else:
            msg = "Syntax error at EOF"

        raise CannotParse(None, msg)
