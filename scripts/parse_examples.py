from tqdm import tqdm

FILE = '/home/louis/code/ieml/ieml-project/ieml/ieml/test/words_example.txt'
OUTFILE = '/home/louis/code/ieml/ieml-project/ieml/ieml/test/words_example_corrected.txt'
with open(FILE) as fp:
    lines = fp.readlines()

import re
from ieml.usl.usl import usl

spliter = re.compile(r'^(\[.*\])\s*#\s*(.*)$')


def process_line(l):
    match = spliter.match(l)
    ieml, trans_fr = match.groups()
    print(ieml, trans_fr)

    try:
        u = usl(ieml)
    except Exception as e:
        # print(e.args[0])
        raise

    return str(u), trans_fr


with open(OUTFILE, 'w') as fp:
    for l in tqdm(lines):
        fp.write("{} # {}".format(*process_line(l)))



