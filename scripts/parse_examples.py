from tqdm import tqdm

from ieml.usl import check_word

FILE = '../ieml/test/words_example_corrected_translated2.txt'
OUTFILE = '../ieml/test/words_example_corrected_translated3.txt'
with open(FILE) as fp:
    lines = fp.readlines()

import re
from ieml.usl.usl import usl

spliter = re.compile(r'^(\[.*\])\s*#\s*(.*)$')


def process_line(l):
    match = spliter.match(l)
    ieml, trans_fr = match.groups()
    ieml = ieml.replace('X', 'wa.')

    print(ieml, trans_fr)

    try:
        u = usl(ieml)
    except Exception as e:
        # print(e.args[0])
        raise

    check_word(u)
    return str(u), trans_fr


with open(OUTFILE, 'w') as fp:
    for l in tqdm(lines):
        if l.startswith('//'):
            continue
        fp.write("{} # {}\n".format(*process_line(l)))



