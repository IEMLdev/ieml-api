from ieml.ieml_objects.tools import term


def _nb_relations(term0, term1):
    # print(term0.relations.to(term1, table=False))
    return  5 - len(term0.relations.to(term1, table=False))

def _max_rank(term0, term1):
    rel_table = term0.relations.to(term1, table=True)
    # print(rel_table)
    if 'table_5' in rel_table:
        return 0

    if 'table_4' in rel_table:
        return 1

    if 'table_3' in rel_table:
        return 2

    if 'table_2' in rel_table:
        return 3

    if 'table_1' in rel_table:
        return 4

    return 5


def distance(term0, term1):
    if term0 == term1:
        return 0,0

    if term0.script.paradigm or term1.script.paradigm:
        raise ValueError("Not implemented for paradigms")

    return _nb_relations(term0, term1), _max_rank(term0, term1)

    print(term0.relations.to(term1))
    print(term1.relations.to(term0))


if __name__ == '__main__':
    print(distance(term("E:U:.k.-"), term("E:U:.m.-")))
    print(distance(term("y."), term("j.")))
    print(distance(term("y."), term("g.")))

    root = term("M:M:.o.-M:M:.o.-E:.-+s.u.-'")
    ss = [term(s) for s in root.script.singular_sequences]

    print(ss[34].translation['fr'])
    print([t.translation['fr'] for t in sorted(ss, key=lambda t1: distance(ss[34], t1))])
