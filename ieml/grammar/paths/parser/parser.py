import logging
from functools import lru_cache
import threading

from ply import yacc

from ....exceptions import CannotParse
from .lexer import tokens, get_lexer
from ..paths import Coordinate, AdditivePath, MultiplicativePath, ContextPath
from ....commons import Singleton


class PathParser(metaclass=Singleton):
    tokens = tokens
    lock = threading.Lock()

    def __init__(self):

        # Build the lexer and parser
        self.lexer = get_lexer()
        self.parser = yacc.yacc(module=self, errorlog=logging, start='path',
                                debug=False, optimize=True, picklefile="parser/path_parser.pickle")
        # rename the parsing method (can't name it directly parse with lru_cache due to ply checking)
        self.parse = self.t_parse

    @lru_cache(maxsize=1024)
    def t_parse(self, s):
        """Parses the input string, and returns a reference to the created AST's root"""
        # self.root = None
        # self.path = s
        with self.lock:
            try:
                return self.parser.parse(s, lexer=self.lexer, debug=False)
            except CannotParse as e:
                e.s = s
                raise e

        # if self.root is not None:
        #     if len(self.root.children) == 1:
        #         self.root = self.root.children[0]
        #
        #     return self.root
        # else:
        #     raise CannotParse(s, "Invalid path.")

    def p_path(self, p):
        """path : additive_path"""
        if len(p[1].children) == 1:
            p[0] = p[1].children[0]
        else:
            p[0] = p[1]

    def p_additive_path(self, p):
        """ additive_path : path_sum"""
        p[0] = AdditivePath(p[1])

    def p_path_sum(self, p):
        """ path_sum : ctx_path
                  | path_sum PLUS ctx_path"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_ctx_path(self, p):
        """ ctx_path : ctx_coords"""
        if len(p[1]) == 1:
            p[0] = p[1][0]
        else:
            p[0] = ContextPath(p[1])

    def p_ctx_coords(self, p):
        """ ctx_coords : multiplicative_path
                        | ctx_coords COLON multiplicative_path"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_multiplicative_path(self, p):
        """ multiplicative_path : product"""
        p[0] = MultiplicativePath(p[1])

    def p_product(self, p):
        """ product : additive_path_p
                    | coordinate
                    | product additive_path_p
                    | product coordinate"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]

    def p_additive_path_p(self, p):
        """ additive_path_p : LPAREN additive_path RPAREN"""
        p[0] = p[2]

    def p_coordinate(self, p):
        """ coordinate : COORD_KIND
                        | COORD_KIND COORD_INDEX"""

        if len(p) == 2:
            p[0] = Coordinate(p[1])
        else:
            p[0] = Coordinate(p[1], int(p[2]))

    def p_error(self, p):
        if p:
            msg = "Syntax error at '%s' (%d, %d)" % (p.value, p.lineno, p.lexpos)
        else:
            msg = "Syntax error at EOF"

        raise CannotParse(None, msg)