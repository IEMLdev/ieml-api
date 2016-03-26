from ieml import Parser
import logging

logging.getLogger().setLevel(logging.DEBUG)

data = "[([a.i.-] + [i.i.-]) * ([E:A:T:.]+[E:S:.wa.-]+[E:S:.o.-])]"
test_parser = Parser()

with open("data/example_word.txt") as example:
    test_parser.parse(example.read())
    print(test_parser.root)

with open("data/example_clause.txt") as example:
    test_parser.parse(example.read())
    print(test_parser.root)

with open("data/example_sentence.txt") as example:
    root = test_parser.parse(example.read())
    print(root)

with open("data/example_supersentence.txt") as example:
    root = test_parser.parse(example.read())
    print(root)