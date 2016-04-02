from ieml import PropositionsParser
import logging

logging.getLogger().setLevel(logging.INFO)

test_parser = PropositionsParser()

for filename in ["word", "clause", "sentence", "supersentence"]:
    with open("data/example_%s.txt" % filename) as example:
        root = test_parser.parse(example.read())
        print(root)
