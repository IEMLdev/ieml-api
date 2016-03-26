from ieml import Parser
import logging

logging.getLogger().setLevel(logging.INFO)

data = "[([a.i.-] + [i.i.-]) * ([E:A:T:.]+[E:S:.wa.-]+[E:S:.o.-])]"
test_parser = Parser()

for filename in ["word", "clause", "sentence", "supersentence"]:
    with open("data/example_%s.txt" % filename) as example:
        root = test_parser.parse(example.read())
        print(root)
