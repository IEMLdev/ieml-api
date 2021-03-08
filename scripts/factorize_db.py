import os
import shutil

import pygit2

from ieml.dictionary.script import factorize
from ieml.ieml_database import GitInterface, IEMLDatabase

if __name__ == '__main__':

    folder = '/tmp/migrate_script_iemldb'
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    # os.mkdir(folder)
    git_address = "https://github.com/IEMLdev/ieml-language.git"

    credentials = pygit2.Keypair('ogrergo', '~/.ssh/id_rsa.pub', '~/.ssh/id_rsa', None)
    gitdb = GitInterface(origin=git_address,
                         credentials=credentials,
                         folder=folder)
    gitdb.pull()

    signature = pygit2.Signature("Louis van Beurden", "louis.vanbeurden@gmail.com")

    db = IEMLDatabase(folder=folder, use_cache=False)


    desc = db.get_descriptors()
    struct = db.get_structure()

    to_migrate = {}


    for s in db.get_dictionary().scripts:
        s_f = factorize(s)
        if s_f != s:
            print("Not factorized: {} -> {} ".format(str(s), str(s_f)), end='')
            c = input('[y/n]')
            if c == 'y':
                to_migrate[s] = s_f


    with gitdb.commit(signature, "[Factorize database]"):
        for old, new in to_migrate.items():
            db.remove_structure(old)
            db.remove_descriptor(old)

            for (_, key), values in struct.get_values_partial(old).items():
                for v in values:
                    db.add_structure(new, key, v)

            for (_, lang, d), values in desc.get_values_partial(old).items():
                for v in values:
                    db.add_descriptor(new, lang, d, v)

