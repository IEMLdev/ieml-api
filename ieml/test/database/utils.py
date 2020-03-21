from ieml.ieml_database import GitInterface
import os
import shutil

def init_repo(folders):
    if all(os.path.isdir(folder) for folder in folders):
        commit_id= '7f3a0b96aba5cf299ecc4e2985ec49f9bb7559ba'

    else:
        commit_id = None
        for folder in folders:
            if os.path.isdir(folder):
                shutil.rmtree(folder)

        folder = '/tmp/iemldb_test/tmp'
        if os.path.isdir(folder):
            shutil.rmtree(folder)

        print("Cloning IEML db : ", folder)
        GitInterface(folder=folder)

    gitdbs = []
    for f in folders:

        if not commit_id:
            print("Copying IEML db: ", f)

            shutil.copytree(folder, f)
            git = GitInterface(folder=f)
        else:
            git = GitInterface(folder=f)
            git.reset(commit_id)

        gitdbs.append(git)

    if not commit_id:
        shutil.rmtree('/tmp/iemldb_test/tmp')

    return gitdbs
