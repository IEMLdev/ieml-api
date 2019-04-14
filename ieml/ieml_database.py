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


# class MyRemoteCallbacks(pygit2.RemoteCallbacks):
#     def credentials(self, url, username_from_url, allowed_types):
#         if allowed_types & pygit2.credentials.GIT_CREDTYPE_USERNAME:
#             return pygit2.Username("git")
#         elif allowed_types & pygit2.credentials.GIT_CREDTYPE_SSH_KEY:
#             return pygit2.Keypair("git", "id_rsa.pub", "id_rsa", "")
#         else:
#             return None

def init_remote(repo, name, url):
    # Create the remote with a mirroring url
    remote = repo.remotes.create(name, url)#, "+refs/*:refs/*")
    # And set the configuration option to true for the push command
    mirror_var = "remote.{}.mirror".format(name)
    repo.config[mirror_var] = True
    # Return the remote, which pygit2 will use to perform the clone
    return remote


class IEMLDatabase:
    def __init__(self, git_address=IEMLDB_DEFAULT_GIT_ADDRESS, branch='master', commit_id=None, folder=None):
        self.git_address = git_address
        self.branch = branch
        self.commit_id = commit_id

        if folder:
            self.folder = os.path.abspath(folder)
        else:
            self.folder = os.path.join(user_cache_dir(appname='ieml', appauthor=False, version=LIBRARY_VERSION),
                                       hashlib.md5("{}/{}".format(git_address, branch).encode('utf8')).hexdigest())

        # download database
        self.update()

    def update(self):
        if not os.path.exists(self.folder):
            repo = pygit2.clone_repository(self.git_address, self.folder, remote=init_remote, checkout_branch=self.branch)
        else:
            repo = pygit2.Repository(self.folder)

        if self.commit_id is None:
            # use most recent of remote
            remote = repo.remotes[0]
            remote.fetch()
            self.commit_id = repo.lookup_reference('refs/remotes/origin/{}'.format(self.branch)).target

        merge_result, _ = repo.merge_analysis(self.commit_id)

        # Up to date, do nothing
        if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
            return

        # We can just fastforward
        elif merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
            repo.checkout_tree(repo.get(self.commit_id))
            master_ref = repo.lookup_reference('refs/heads/{}'.format(self.branch))
            master_ref.set_target(self.commit_id)
            repo.head.set_target(self.commit_id)
        else:
            raise ValueError("Incompatible history, can't merge origin into {}#{} in folder {}".format(self.branch, self.commit_id,
                                                                                                       self.folder))

    def dictionary(self):
        dictionary_path = os.path.join(self.folder, 'dictionary')
        return Dictionary.load(dictionary_path, use_cache=True, cache_folder=self.folder)

    def lexicon(self):
        lexicon_path = os.path.join(self.folder, 'lexicons')
        return Lexicon.load(lexicon_path)

    @property
    def repo(self):
        return pygit2.Repository(self.folder)

    def get_version(self):
        return (self.branch, self.commit_id)

    def set_version(self, branch, commit_id):
        self.branch = branch
        self.commit_id = commit_id
        self.update()


if __name__ == '__main__':
    db = IEMLDatabase()
    v0 = ('master', '650f67dffc616df52d2e3440c2fc4b8cb655cf41')
    v1 = ('master', '58a3bb44f7f33752a84e0dbfdb7ebadc6a7ea8d9')
    db.set_version(*v1)
    assert db.get_version() == v1

    db.set_version(*v0)
    assert db.get_version() == v0

    # db.dictionary()
    # db.lexicon()