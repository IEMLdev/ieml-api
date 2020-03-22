import logging
import threading
import os
from ply.yacc import yacc

from ieml.constants import PARSER_FOLDER
from ieml.dictionary.script import script
from ieml.exceptions import CannotParse
from ieml.usl.decoration.parser.lexer import tokens, get_lexer
from ieml.usl.decoration.path import UslPath, RolePath, LexemePath, PolymorphemePath, LexemeIndex, GroupIndex
from ieml.usl.syntagmatic_function import SyntagmaticRole


class PathParser:
    tokens = tokens
    lock = threading.Lock()

    def __init__(self):
        # Build the lexer and parser
        self.lexer = get_lexer()
        self.parser = yacc(module=self, errorlog=logging, start='path',
                                  debug=True, debuglog=logging, optimize=False,
                                  picklefile=os.path.join(PARSER_FOLDER, "path_parser.pickle"))

    def parse(self, s):
        with self.lock:
            try:
                return self.parser.parse(s, lexer=self.lexer)
            except ValueError as e:
                raise CannotParse(s, str(e))
            except CannotParse as e:
                e.s = s
                raise e

    def p_path(self, p):
        """path : SEPARATOR
                | SEPARATOR role_path
                | SEPARATOR lexeme_path
                | SEPARATOR polymorpheme_path"""

        if len(p) == 2:
            p[0] = UslPath()
        else:
            p[0] = p[2]

    def p_role_path_list(self, p):
        """role_path_list : role_path_list ROLE
                            | ROLE"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_role_path(self, p):
        """role_path : role_path_list
                     | role_path_list SEPARATOR lexeme_path """
        if len(p) == 2:
            p[0] = RolePath(SyntagmaticRole(p[1]))
        else:
            p[0] = RolePath(SyntagmaticRole(p[1]), child=p[3])

    def p_lexeme_path(self, p):
        """lexeme_path : LEXEME_POSITION
                        | LEXEME_POSITION SEPARATOR polymorpheme_path"""
        lex_index = LexemeIndex[p[1].upper()]
        if len(p) == 2:
            p[0] = LexemePath(lex_index)
        else:
            p[0] = LexemePath(lex_index, child=p[3])

    def p_polymorpheme_path(self, p):
        """polymorpheme_path : POLYMORPHEME_POSITION SEPARATOR MORPHEME"""
        group_idx = GroupIndex[p[1].upper()]
        morpheme = script(p[3])
        p[0] = PolymorphemePath(group_idx, morpheme)


    def p_error(self, p):
        if p:
            msg = "Syntax error at '%s' (%d, %d)" % (p.value, p.lineno, p.lexpos)
        else:
            msg = "Syntax error at EOF"

        raise CannotParse(None, msg)
