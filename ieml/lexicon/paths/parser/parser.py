from functools import lru_cache

from sly.yacc import YaccProduction

from .lexer import PathLexer
from ..paths import Coordinate, AdditivePath, MultiplicativePath, ContextPath
from ....commons import BaseIEMLParser
from ....exceptions import CannotParse


class PathParser(BaseIEMLParser):
    tokens = PathLexer.tokens
    lexer = PathLexer()

    @lru_cache(maxsize=1024)
    def parse(self, s: str):
        """Parses the input string, and returns a reference to the created AST's root"""
        with self.lock:
            try:
                return super().parse(self.lexer.tokenize(s))
            except CannotParse as e:
                e.s = s
                raise e

    @_("additive_path")
    def p_path(self, p: YaccProduction):
        if len(p.additive_path.children) == 1:
            return p.additive_path.children[0]
        else:
            return p.additive_path

    @_("path_sum")
    def additive_path(self, p: YaccProduction):
        return AdditivePath(p.path_sum)

    @_("path_sum PLUS ctx_path",
       "ctx_path")
    def path_sum(self, p: YaccProduction):
        if len(p) == 3:
            p.path_sum.append(p.ctx_path)
            return p.path_sum
        else:
            return [p.ctx_path]

    @_("ctx_coords")
    def ctx_path(self, p: YaccProduction):
        if len(p.ctx_coords) == 1:
            return p.ctx_coords[0]
        else:
            return ContextPath(p.ctx_coords)

    @_("ctx_coords COLON multiplicative_path",
       "multiplicative_path")
    def ctx_coords(self, p):
        if len(p) == 3:
            p.ctx_coords.append(p.multiplicative_path)
            return p.ctx_coords
        else:
            return [p.multiplicative_path]

    @_("product")
    def multiplicative_path(self, p: YaccProduction):
        return MultiplicativePath(p.product)

    @_("additive_path_p",
       "coordinate",
       "product additive_path_p",
       "product coordinate")
    def product(self, p: YaccProduction):
        if len(p) == 2:
            p[0].append(p[1])
            return p[0]
        else:
            return [p[0]]

    @_("LPAREN additive_path RPAREN")
    def additive_path_p(self, p: YaccProduction):
        return p.additive_path

    @_("COORD_KIND")
    def coordinate(self, p: YaccProduction):
        return Coordinate(p.COORD_KIND)

    @_("COORD_KIND COORD_INDEX")
    def coordinate(self, p: YaccProduction):
        return Coordinate(p.COORD_KIND, int(p.COORD_INDEX))