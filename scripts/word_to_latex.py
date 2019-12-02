import subprocess
import tempfile
from itertools import zip_longest
import os
from pylatex import Document, Package
from pylatex.utils import dumps_list

from ieml.constants import LANGUAGES
from ieml.dictionary.script import Script
from ieml.ieml_database import IEMLDatabase, GitInterface
from ieml.ieml_database.ieml_database import Descriptors
from ieml.usl import Word
from ieml.usl.constants import *
from ieml.usl.lexeme import Lexeme
from ieml.usl.syntagmatic_function import SyntagmaticRole, ProcessSyntagmaticFunction, \
    DependantQualitySyntagmaticFunction, IndependantQualitySyntagmaticFunction
from ieml.usl.usl import usl



NAMES_TO_ADDRESS = {
    ONE_ACTANT_PROCESS: 'process',
    TWO_ACTANTS_PROCESS: 'process',
    THREE_ACTANTS_PROCESS: 'process',

    INITIATOR_SCRIPT: 'initiator',
    INTERACTANT_SCRIPT: 'interactant',
    RECIPIENT_SCRIPT: 'recipient',

    TIME_SCRIPT: 'time',
    LOCATION_SCRIPT: 'location',
    MANNER_SCRIPT: 'manner',
    INTENTION_SCRIPT: 'intention',
    CAUSE_SCRIPT: 'cause',

    INDEPENDANT_QUALITY: 'quality',
    DEPENDANT_QUALITY: 'actant',

    JUNCTION_AND: 'and',
    JUNCTION_OR: 'or (inclusive)',
    JUNCTION_XOR: 'or (exclusive)',

    JUNCTION_COMPARISON_ANCHOR: 'comparison reference',

    JUNCTION_COMPARISON_RELATIVE_AS_GOOD_AS: 'as good as',
    JUNCTION_COMPARISON_RELATIVE_AS_MUCH_AS: 'as much as',
    JUNCTION_COMPARISON_RELATIVE_BETTER_THAN: 'better than',
    JUNCTION_COMPARISON_RELATIVE_LESS_THAN: 'less than',
    JUNCTION_COMPARISON_RELATIVE_WORSE_THAN: 'worse than',
    JUNCTION_COMPARISON_RELATIVE_MORE_THAN: 'more than',

    JUNCTION_COMPARISON_ABSOLUTE_THE_BEST_OF: "the best of",
    JUNCTION_COMPARISON_ABSOLUTE_AVERGAGE_QUALITY_OF: "average quality of",
    JUNCTION_COMPARISON_ABSOLUTE_NORMAL_QUANTITY_OF: "normal quantity of",
    JUNCTION_COMPARISON_ABSOLUTE_THE_LEAST_OF: "the least of",
    JUNCTION_COMPARISON_ABSOLUTE_THE_MOST_OF: "the most of",
    JUNCTION_COMPARISON_ABSOLUTE_THE_WORST_OF: "the worst of",

    JUNCTION_ANTINOMIC_ANCHOR: "certainly...",
    JUNCTION_ANTINOMIC_BUT_LINK: "but",
    JUNCTION_ANTINOMIC_EXCEPT_LINK: "except",
    JUNCTION_ANTINOMIC_ALTOUGH_LINK: "altough",
    JUNCTION_ANTINOMIC_ON_THE_OTHER_HAND_LINK: "on the other hand",
    JUNCTION_ANTINOMIC_CONTRARIWISE_LINK: "contrariwise",

    JUNCTION_CAUSAL_ANCHOR: "causal anchor",
    JUNCTION_CAUSAL_CAUSE_TO_EFFECT_LINK: "cause to effect",
    JUNCTION_CAUSAL_EFFECT_TO_CAUSE_LINK: "effect to cause",
    JUNCTION_CAUSAL_A_FORTIORI_LINK: "a fortiori",

    **{j: "*{}".format(i+1) for i, j in enumerate(JUNCTION_INDEX)}

    # JUNCTION_EXPLICATION_ANCHOR: "",
    # JUNCTION_EXPLICATION_BEST_LINK: "",
}

def _render_role(role: List[Script], language: LANGUAGES):
    if len(role) == 1:
        return NAMES_TO_ADDRESS[role[0]]
    else:
        return _render_role(role[1:], language) + ' of ' + NAMES_TO_ADDRESS[role[0]]


COLORS = {
    'motor': ('c9e9f6', 'c9e9f6'),
    'process': ('fdc3bc', 'fdc3bc'),
    'location': ('d2f8d2', 'd2f8d2'),
    'manner': ('ffe69a', 'ffe69a'),
}


def color_from_role(role: List[Script], is_main: bool):
    _r = role[0]
    if _r in ADDRESS_PROCESS_VALENCE_SCRIPTS:
        res = COLORS['process']
    elif _r in ADDRESS_ACTANTS_MOTOR_SCRIPTS:
        res = COLORS['motor']
    elif _r in {LOCATION_SCRIPT, TIME_SCRIPT}:
        res = COLORS['location']
    elif _r in {MANNER_SCRIPT, INTENTION_SCRIPT, CAUSE_SCRIPT}:
        res = COLORS['manner']
    else:
        res = COLORS['motor']

    return res[1 if is_main else 0]

LINE_TEMPLATE = "\\cellcolor[HTML]{{{color}}}{lexeme} &\\cellcolor[HTML]{{{color}}}{role} &\\cellcolor[HTML]{{{color}}}{flexion} &\\cellcolor[HTML]{{{color}}}{content}\\\\\n"

def _serialize_role(_role: List[Script], _lexeme: Lexeme, descriptors: Descriptors, language: LANGUAGES, color: str):
    flexion = _lexeme.pm_flexion.constant
    content = _lexeme.pm_content.constant

    res = ''

    for lex, r, fl, ctt in zip_longest([_lexeme], [_role], flexion, content):
        if lex is None:
            lexeme = ''
        else:
            lexeme = "\\textbf{{{}}}".format(', '.join(descriptors.get_values(lex, language, 'translations')))

        if r is None:
            role = ''
        else:
            role = "\\textbf{{{}}}".format(_render_role(r, language))

        if fl is None:
            flexion = ''
        else:
            flexion = "\\textbf{{{}}}".format(', '.join(descriptors.get_values(fl, language, 'translations')))

        if ctt is None:
            content = ''
        else:
            content = "\\textbf{{{}}}".format(', '.join(descriptors.get_values(ctt, language, 'translations')))

        res += LINE_TEMPLATE.format(**{
            'lexeme': lexeme,
            'role': role if r is not None else '',
            'flexion': flexion if fl and not fl.empty else '',
            'content': content if ctt and not ctt.empty else '',
            'color': color
        })

        res += LINE_TEMPLATE.format(**{
            'lexeme': '',
            'role': ' '.join(map(str, r)) if r is not None else '',
            'flexion': str(fl) if fl and not fl.empty else '',
            'content': str(ctt) if ctt and not ctt.empty else '',
            'color': color
        })

    return res

def word_to_latex(w: Word, descriptors: Descriptors, language: LANGUAGES):
    prefix = ()
    if w.syntagmatic_fun.__class__ == ProcessSyntagmaticFunction:
        pass
    elif w.syntagmatic_fun.__class__ == DependantQualitySyntagmaticFunction:
        prefix = (DEPENDANT_QUALITY,)
    elif w.syntagmatic_fun.__class__ == IndependantQualitySyntagmaticFunction:
        prefix = (INDEPENDANT_QUALITY,)

    res = """
\\begin{figure}
\\centering

\\begin{tabular}{|llll|}
\\hline
lexeme & role & flexion & content \\\\
\\hline
"""


    for role, lex in sorted(w.syntagmatic_fun.actors.items(), key=lambda e: e[0]):
        color = color_from_role(prefix + role.constant, prefix + role.constant == w.role.constant)
        res += _serialize_role(prefix + role.constant, lex.actor, descriptors, language, color)
        res += '\\hline\n'

    res += """
\\end{{tabular}}
\\caption{{{caption}}}
\\label{{fig:word_ieml}}
\\end{{figure}}
""".format(caption="\\textbf{{{trans}}} \\small{{{ieml}}}".format(**{
        'trans':', '.join(descriptors.get_values(w, language, 'translations')),
        'ieml': str(w)
    }))

    # print(res)
    return res

def compile_latex(latex_str):
    old_cwd = os.getcwd()

    with tempfile.TemporaryDirectory() as tempdir:
        path = os.path.join(tempdir, 'output')
        doc = Document(path, data=[dumps_list([latex_str], escape=False)], geometry_options='landscape')

        doc.packages.append(Package('xcolor', ['dvipsnames','table']))
        try:
            doc.generate_pdf(clean_tex=False)
            doc.generate_tex()
        except subprocess.CalledProcessError:
            os.chdir(old_cwd)  # because pylatex change it but doesnt restore it
            return b''

        with open(path + '.pdf', 'rb') as fp:
            return fp.read()


def rendex_latex_word(w: Word, descriptors: Descriptors, language: LANGUAGES):
    return compile_latex(word_to_latex(w, descriptors, language))




if __name__ == "__main__":

    gitdb = GitInterface()
    db = IEMLDatabase(gitdb.folder)

    ieml = "[E:T:. (E:.b.wa.- E:.-wa.-t.o.-' E:.-'we.-S:.-'t.o.-',)(e.) > E:.n.- (E:.wo.- E:S:.-d.u.-') > E:.d.- (E:.wo.- E:S:.-d.u.-')(m.-S:.U:.-') > ! E:.n.- E:U:. ()]"

    w = usl(ieml)
    res = rendex_latex_word(w, db.get_descriptors(), 'en')

    with open("output.pdf", 'wb') as fp:
        fp.write(res)
