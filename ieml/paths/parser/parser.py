import logging

from ply import yacc

from helpers.metaclasses import Singleton
from ieml.exceptions import CannotParse
from ieml.paths.constants import KIND_TO_RANK
from ieml.paths.parser.lexer import tokens, get_lexer
from ieml.paths.paths import Coordinate, Path, AdditivePath, MultiplicativePath, ContextPath


def _coord(kind, index=None):
    if kind in KIND_TO_RANK:
        return Coordinate(kind, index=index)
    else:
        #sentence or ss type need context to determine
        return {
            'type': 'c',
            'args': {'kind': kind, 'index': index}
        }


def _plus(children):
    if any(isinstance(c, Path) for c in children):
        rank = [c for c in children if isinstance(c, Path)][0].rank
        return AdditivePath([_resolve(c, rank) for c in children])
    else:
        return {
            'type': '+',
            'args': children
        }


def _mul(rank_list):
    rank = None
    for i, l in enumerate(rank_list):
        if any(isinstance(c, Path) for c in l):
            rank = [c for c in l if isinstance(c, Path)][0].rank + i
            break

    if not rank and len(rank_list) > 1:
        # we have only tree element
        if len(rank_list) > 2:
            raise ValueError('Too many tree structures')

        # supersentence
        rank = 3

    if rank:
        return MultiplicativePath([_resolve(c, rank - offset) for offset, l in enumerate(rank_list) for c in l])
    else:
        return {
            'type': '*',
            'args': rank_list
        }


def _resolve(e, rank):
    if isinstance(e, Path):
        if e.rank != rank:
            raise ValueError('Rank not matching, invalid synthax')
        return e

    if e['type'] == 'c':
        return Coordinate(**{**e['args'], 'rank': rank})

    if e['type'] == '+':
        return AdditivePath([_resolve(c, rank) for c in e['args']])

    if e['type'] == '*':
        return MultiplicativePath([_resolve(c, rank - offset) for offset, l in enumerate(e['args']) for c in l])

    raise ValueError('Invalid argument')


class PathParser(metaclass=Singleton):
    tokens = tokens

    def __init__(self):

        # Build the lexer and parser
        self.lexer = get_lexer()
        self.parser = yacc.yacc(module=self, errorlog=logging, start='path', debug=True)

    def parse(self, s):
        """Parses the input string, and returns a reference to the created AST's root"""
        self.root = None
        self.parser.parse(s, lexer=self.lexer, debug=False)

        if self.root is not None:
            if not isinstance(self.root, Path):
                self.root = _resolve(self.root, 2)

            if len(self.root.children) == 1:
                self.root = self.root.children[0]

            return self.root
        else:
            raise CannotParse(s)

    def p_path(self, p):
        """path : additive_path"""
        self.root = p[1]

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
            print("Syntax error at '%s' (%d, %d)" % (p.value, p.lineno, p.lexpos))
        else:
            print("Syntax error at EOF")