import os
import shutil

import pygit2

from ieml.exceptions import CannotParse
from ieml.usl import Word
from ieml.usl.parser import USLParser
from ieml.usl.usl import usl
from ieml.dictionary.script import factorize, Script
from ieml.ieml_database import GitInterface, IEMLDatabase
from ieml.usl.word import simplify_word

# This module remove unnormalized USL and save theirs normalized versions

if __name__ == '__main__':

    folder = '/tmp/migrate_script_iemldb'
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    # os.mkdir(folder)
    git_address = "https://github.com/plevyieml/ieml-language.git"

    credentials = pygit2.Keypair('git', '~/.ssh/id_rsa.pub', '~/.ssh/id_rsa', None)
    gitdb = GitInterface(origin=git_address,
                         credentials=credentials,
                         folder=folder)
    #
    # gitdb.pull()

    signature = pygit2.Signature("Louis van Beurden", "louis.vanbeurden@gmail.com")

    db = IEMLDatabase(folder=folder, use_cache=False)



    desc = db.get_descriptors()
    struct = db.get_structure()

    to_migrate = {}
    to_remove = []

    parser = USLParser(dictionary=db.get_dictionary())

    all_db = db.list()
    # assert "[E:.b.E:B:.- E:S:. ()(a.T:.-) > ! E:.l.- ()(d.i.-l.i.-')]" in all_db
    for s in all_db:
        to_pass = True

        try:
            _s = parser.parse(s)
        except CannotParse as e:
            print(str(e))
            print("\t", str(s))
            to_pass = False
        else:
            if isinstance(_s, Word):
                try:
                    _s = simplify_word(_s)
                except Exception:
                    pass
                # usl(str(_s))

            if str(_s) != s:
                print("Not normalized \n\t({}){}{} != \n\t({}){}{}".format(str(_s) in all_db, '[NO !]' if '!' not in str(_s) else '',
                                                                           str(_s), str(s) in all_db, '[NO !]' if '!' not in str(s) else '', str(s)))
                to_pass = False

                # if str(_s) not in all_db and str(s) in all_db:
                to_migrate[s] = _s

            try:
                if not isinstance(_s, Script):
                    _s.check()
            except Exception as e:
                print(str(e))
                print("\t", str(s))
                to_pass = False



        # while not to_pass:
        #     c = input('\t[r]emove/[u]pdate/[p]ass')
        #     if c == 'u':
        #         to_migrate[s] = _s
        #         to_pass = True
        #     elif c == 'r':
        #         to_remove.append(s)
        #         to_pass = True
        #     elif c == 'p':
        #         to_pass = True

    with gitdb.commit(signature, "[Filter database - Normalize DB]"):
        for old, new in to_migrate.items():
            to_remove.append(old)

            for (_, key), values in struct.get_values_partial(old).items():
                for v in values:
                    db.add_structure(new, key, v)

            for (_, lang, d), values in desc.get_values_partial(old).items():
                for v in values:
                    db.add_descriptor(new, lang, d, v)

        for old in to_remove:
            db.remove_structure(old, normalize=False)
            db.remove_descriptor(old, normalize=False)

