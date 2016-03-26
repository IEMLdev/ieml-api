from ieml import Parser
import logging

data = "[([a.i.-] + [i.i.-]) * ([E:A:T:.]+[E:S:.wa.-]+[E:S:.o.-])]"
test_parser = Parser()
test_parser.parse(data)
print(test_parser.root)