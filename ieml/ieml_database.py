import hashlib
import os
# import git
from appdirs import user_cache_dir
from ieml.constants import IEMLDB_DEFAULT_GIT_ADDRESS, LIBRARY_VERSION
import pygit2
# from git import RemoteProgress

# class MyProgressPrinter(RemoteProgress):
#     def update(self, op_code, cur_count, max_count=None, message=''):
#         print(op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "NO MESSAGE")
from ieml.dictionary import Dictionary
from ieml.lexicon import Lexicon


class MyRemoteCallbacks(pygit2.RemoteCallbacks):
    def credentials(self, url, username_from_url, allowed_types):
        if allowed_types & pygit2.credentials.GIT_CREDTYPE_USERNAME:
            return pygit2.Username("git")
        elif allowed_types & pygit2.credentials.GIT_CREDTYPE_SSH_KEY:
            return pygit2.Keypair("git", "id_rsa.pub", "id_rsa", "")
        else:
            return None

def init_remote(repo, name, url):
    # Create the remote with a mirroring url
    remote = repo.remotes.create(name, url)#, "+refs/*:refs/*")
    # And set the configuration option to true for the push command
    mirror_var = "remote.{}.mirror".format(name)
    repo.config[mirror_var] = True
    # Return the remote, which pygit2 will use to perform the clone
    return remote


class IEMLDatabase:
    def __init__(self, git_address=IEMLDB_DEFAULT_GIT_ADDRESS, branch='master', folder=None):
        self.git_address = git_address
        self.branch = branch

        if folder:
            self.folder = os.path.abspath(folder)
        else:
            self.folder = os.path.join(user_cache_dir(appname='ieml', appauthor=False, version=LIBRARY_VERSION),
                                       hashlib.md5("{}/{}".format(git_address, branch).encode('utf8')).hexdigest())

        if not os.path.exists(self.folder) or 'dictionary' not in os.listdir(self.folder):
            # download database
            self.update()

    def update(self):
        if not os.path.exists(self.folder):
            repo = pygit2.clone_repository(self.git_address, self.folder, remote=init_remote, checkout_branch=self.branch)
        else:
            repo = pygit2.Repository(self.folder)

        remote = repo.remotes[0]
        remote.fetch()
        remote_master_id = repo.lookup_reference('refs/remotes/origin/master').target

        merge_result, _ = repo.merge_analysis(remote_master_id)

        # Up to date, do nothing
        if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
            return

        # We can just fastforward
        elif merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
            repo.checkout_tree(repo.get(remote_master_id))
            master_ref = repo.lookup_reference('refs/heads/master')
            master_ref.set_target(remote_master_id)
            repo.head.set_target(remote_master_id)
        else:
            raise ValueError("Incompatible history, can't merge origin into master in {}".format(self.folder))

    def dictionary(self):
        dictionary_path = os.path.join(self.folder, 'dictionary')
        return Dictionary.load(dictionary_path, use_cache=True, cache_folder=self.folder)

    def lexicon(self):
        lexicon_path = os.path.join(self.folder, 'lexicons')
        return Lexicon.load(lexicon_path)


if __name__ == '__main__':
    db = IEMLDatabase()
    db.dictionary()
    db.lexicon()