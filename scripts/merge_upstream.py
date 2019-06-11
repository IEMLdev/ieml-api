import shutil, os

import pygit2

from scripts.migrate_versions.migrate_v03Tov04 import GitInterface

if __name__ == '__main__':
    folder = '/tmp/iemldb_test'
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    #
    # # r =
    # # # print(json.dumps(r, indent=True))
    # #
    # # d = Descriptors(db2.get_pandas())
    # # print(d.get_values('wa.', 'en', 'translations'))
    # # db2.remove_key('wa.', 'en', 'translations')
    # # d = Descriptors(db2.get_pandas())
    # # print(d.get_values('wa.', 'en', 'translations'))
    gitdb = GitInterface(origin='ssh://git@github.com/ogrergo/ieml-language.git',
                         credentials=pygit2.Keypair('git', '/home/louis/.ssh/id_rsa.pub', '/home/louis/.ssh/id_rsa', ''),
                         folder=folder)

    gitdb.add_remote('upstream', 'ssh://git@github.com/IEMLdev/ieml-language.git')
    gitdb.pull('upstream')
    # gitdb.push('origin')