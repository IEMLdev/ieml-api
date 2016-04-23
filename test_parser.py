from ieml import PropositionsParser, USLParser
import logging

logging.getLogger().setLevel(logging.INFO)

test_parser = PropositionsParser()

for filename in ["word", "clause", "sentence", "supersentence"]:
    with open("data/example_%s.txt" % filename) as example:
        root = test_parser.parse(example.read())
        print(root)


usl_parser = USLParser()
for filename in ["usl"]:
    with open("data/example_%s.txt" % filename) as example:
        root = usl_parser.parse(example.read())
        root2 = usl_parser.parse(str(root))
        print(root)
        print(root2)
        for k in root.hyperlinks_table.keys():
            print(k)
        assert(str(root) == str(root2))
