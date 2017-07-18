import logging
import os
import ply.yacc as yacc

from ieml import parser_folder
from ieml.exceptions import CannotParse
from ieml.syntax.parser import IEMLParser
from ieml.usl.parser.lexer import tokens, get_lexer
from ieml.usl import Usl
from ieml.metaclasses import Singleton


class USLParser(metaclass=Singleton):
    tokens = tokens

    def __init__(self):

        # Build the lexer and parser
        self.lexer = get_lexer()
        self.parser = yacc.yacc(module=self, errorlog=logging, start='usl',
                                debug=False, optimize=True, picklefile=os.path.join(parser_folder, "usl_parser.pickle"))

    def parse(self, s):
        """Parses the input string, and returns a reference to the created AST's root"""
        self.usl = s
        self.root = None
        self.parser.parse(s, lexer=self.lexer)

        if self.root is not None:
            return self.root
        else:
            raise CannotParse(s)

    # Parsing rules
    def p_usl(self, p):
        """ usl : IEML_OBJECT """
        self.root = Usl(IEMLParser().parse(p[1]))

    def p_error(self, p):
        if p:
            print("Syntax error at '%s' (%d, %d)" % (p.value, p.lineno, p.lexpos))
        else:
            print("Syntax error at EOF")

        raise CannotParse(self.usl)

if __name__ == '__main__':
    print(str(USLParser().parse('{[wa.]}')))
