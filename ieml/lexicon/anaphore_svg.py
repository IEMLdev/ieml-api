from itertools import combinations

import drawSvg as draw

from ieml import IEMLDatabase
from ieml.dictionary.script import script
from ieml.ieml_database.descriptor import DescriptorSet

"""
_______________
| ieml - trans |
|______________|
|





"""

CELL_HEIGHT=30
MARGIN=10
CELL_WIDTH = 80

CELL_COLOR='gray'

GRAMATICAL_CLASS_2_COLOR = [
    '#fff1bc', # AUX
    '#ffe5d7', # VERB
    '#d9eaff' # NOUN
]

DIFF = 1
ARROW_W = 5
ARROW_H = 8

def draw_arrow(p0, p1, anchors=(MARGIN * 2, 0), size=DIFF, arrow_start=True, arrow_end=True):
    path = draw.Path(stroke_width=1, stroke='black',
                     fill='red', fill_opacity=0.5)

    anchors_x, anchors_y = anchors

    if p0[1] < p1[1]:
        _t = p1
        p1 = p0
        p0 = _t

    if arrow_start:
        p0_c = p0[0] + ARROW_W
    else:
        p0_c = p0[0]

    if arrow_end:
        p1_c = p1[0] + ARROW_W
    else:
        p1_c = p1[0]

    path.M(p0_c, p0[1] - size)

    if arrow_start:
        path.L(p0_c + ARROW_W / 3, p0[1] + ARROW_H / 2)
        path.L(p0[0], p0[1])
        path.L(p0_c + ARROW_W / 3, p0[1] - ARROW_H / 2)

    path.L(p0_c, p0[1] - size)


    path.C(p0[0] + anchors_x - size,
           p0[1] + anchors_y - size,
           p1[0] + anchors_x - size,
           p1[1] + anchors_y + size,
           p1_c,
           p1[1] + size)

    if arrow_end:
        # draw arrow
        path.L(p1[0] + ARROW_W + ARROW_W / 3, p1[1] + ARROW_H / 2)
        path.L(p1[0], p1[1])
        path.L(p1[0] + ARROW_W + ARROW_W / 3, p1[1] - ARROW_H / 2)

    path.L(p1_c, p1[1] - size)

    path.C(p1[0] + anchors_x + size,
           p1[1] + anchors_y - size,
           p0[0] + anchors_x + size,
           p0[1] + anchors_y + size,
           p0[0] + ARROW_W,
           p0[1] + size)

    path.Z()

    return path

def draw_dense(items, desc, origin=(0,0)):
    anchors = []
    group = draw.Group()
    for i, sc in enumerate(items):
        group.append(draw_morpheme(sc, desc, origin=(origin[0], origin[1] + i * (CELL_HEIGHT + MARGIN))))

        anchors.append((origin[0] + MARGIN + CELL_WIDTH,
                        origin[1] + i * (CELL_HEIGHT + MARGIN) + MARGIN + 0.5 * CELL_HEIGHT))

    for p0, p1 in combinations(anchors, 2):
        # d.draw(draw.Arc())
        group.append(draw_arrow(p0, p1))

    return group


def draw_morpheme(script, desc, origin, language='fr',
                  height=CELL_HEIGHT, width=CELL_WIDTH, border=MARGIN):
    trans = desc.get(script, language, 'translations')
    if trans:
        trans = trans[0]
    else:
        trans = '???'

    group = draw.Group()

    group.append(draw.Rectangle(origin[0] + border,
                          origin[1] + border,
                          width,
                          height,
                          fill=GRAMATICAL_CLASS_2_COLOR[script.script_class],
                          stroke="black", stroke_width=1.))

    group.append(draw.Text(str(script),
                     10,
                     origin[0] + border * 1.5,
                     origin[1] + border + 0.6 * height,
                     fill='black'))
    group.append(draw.Text(trans,
                     8,
                     origin[0] + border * 1.5,
                     origin[1] + border + 0.25 * height,
                     fill='black'))

    return group

def draw_trait(trait, desc):
    H=(CELL_HEIGHT + MARGIN) * len(trait) + MARGIN
    W=CELL_WIDTH + MARGIN * 3

    d = draw.Drawing(W, H,
                     origin=(0, 0))

    script_class = max(s.script_class for s in trait)
    core = [s for s in trait if s.script_class == script_class]
    rest = [s for s in trait if s.script_class != script_class]

    d.append(draw_dense(core, desc, origin=(0,0)))

    d.append(draw_dense(rest, desc, origin=(0, len())))

    return d

if __name__ == '__main__':

    desc = IEMLDatabase().descriptors()

    d = draw_trait([script('wa.'),script('S:'), script("wo.")], desc)
    d.setPixelScale(2)
    d.saveSvg('example.svg')