import progressbar
from models.exceptions import DBException
from models.script_relations import ScriptConnector
from models.relations import RelationsQueries
from ieml.parsing import ScriptParser

def load_old_db(all=True):
    db = ScriptConnector()

    parser = ScriptParser()

    # root paradigm
    roots = db.terms.find({'PARADIGM': "1"})
    count_root = roots.count()
    roots_ast = [parser.parse(r['IEML']) for r in roots]
    if all:

        print("\tLoad the roots paradigms, %d entries." % count_root, flush=True)
        # Empty the db
        db.scripts.remove({})

        bar_root = progressbar.ProgressBar(max_value=count_root)
        for i, root in enumerate(roots_ast):
            bar_root.update(i + 1)
            try:
                db.save_script(root, root=True)
            except DBException as e:
                print('\nException ' + e.__class__.__name__ + ' for script ' + root['IEML'])

        # paradigm and singular sequences
        paradigms = db.terms.find({'PARADIGM': "0"})
        count = paradigms.count()

        print("\n\n\tLoad the paradigms and singular sequences, %d entries." % count, flush=True)
        bar_elem = progressbar.ProgressBar(max_value=count)

        error = {}
        for i, paradigm in enumerate(paradigms):
            bar_elem.update(i + 1)
            try:
                db.save_script(paradigm['IEML'])
            except DBException as e:
                if e.__class__.__name__ not in error:
                    error[e.__class__.__name__] = []
                error[e.__class__.__name__].append(paradigm['IEML'])

        if len(error) != 0:
            print('\nErrors : ')
            for e in error:
                print(' %s:'%e)
                for elem in error[e]:
                    print('\t -> %s'%elem)

    # The relations
    print('\n\n\tComputing the relations, for the %s roots paradigms.'%count_root, flush=True)

    bar_rel = progressbar.ProgressBar(max_value=count_root)

    for i, t in enumerate(roots_ast):
        RelationsQueries.compute_relations(t)
        bar_rel.update(i + 1)

    print('\n\nDone.', flush=True)

if __name__ == '__main__':
    load_old_db(all=True)
