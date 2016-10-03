import logging

import ply.yacc as yacc

from ieml.exceptions import CannotParse
from ieml.ieml_objects.parser.parser import IEMLParser
from ieml.usl.usl import Usl
from ieml.usl.parser.lexer import tokens, get_lexer
from helpers.metaclasses import Singleton


class USLParser(metaclass=Singleton):
    tokens = tokens

    def __init__(self):

        # Build the lexer and parser
        self.lexer = get_lexer()
        self.parser = yacc.yacc(module=self, errorlog=logging, start='usl')

    def parse(self, s):
        """Parses the input string, and returns a reference to the created AST's root"""
        self.root = None
        self.parser.parse(s, lexer=self.lexer)

        if self.root is not None:
            return self.root
        else:
            raise CannotParse(s)

    # Parsing rules
    def p_usl(self, p):
        """ usl : L_CURLY_BRACKET IEML_OBJECT R_CURLY_BRACKET"""
        self.root = Usl(IEMLParser().parse(p[2]))

if __name__ == '__main__':
    print(str(USLParser().parse('{[wa.]}')))
