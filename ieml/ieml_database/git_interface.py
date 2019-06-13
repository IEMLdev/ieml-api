import hashlib
import os
import logging
from _pygit2 import GIT_CHECKOUT_FORCE, GIT_CHECKOUT_RECREATE_MISSING, GIT_STATUS_WT_NEW, \
    GIT_STATUS_WT_DELETED, GIT_STATUS_WT_MODIFIED, GIT_STATUS_WT_RENAMED

import pygit2
from appdirs import user_cache_dir

from ieml import LIBRARY_VERSION
from ieml.commons import monitor_decorator

logger = logging.getLogger('GitInterface')
logger.setLevel(logging.INFO)

def get_local_cache_dir(origin):
    return os.path.join(user_cache_dir(appname='ieml', appauthor=False, version=LIBRARY_VERSION),
                        hashlib.md5(origin.encode('utf8')).hexdigest())


class git_transaction:
    def __init__(self, db, signature, message):
        self.db = db
        self.signature = signature
        self.message = message

    def __enter__(self):
        self.commit_id = self.db.commit_id

        # ignore files at the root
        if self.db.repo.status() != {}:
            raise ValueError("Try to start a transaction on a not clean working dir state, "
                             "please use db.reset() first.")
        return

    @monitor_decorator("Commit transaction")
    def __exit__(self, type, value, traceback):

        if type is None:
            try:
                status = self.db.repo.status()
                if not status:
                    return

                index = self.db.repo.index
                index.read()

                for f, k in status.items():
                    if k & GIT_STATUS_WT_NEW:
                        index.add(f)
                    elif k & GIT_STATUS_WT_DELETED:
                        index.remove(f)
                    elif k & GIT_STATUS_WT_MODIFIED:
                        index.add(f)
                    elif k & GIT_STATUS_WT_RENAMED:
                        index.add(f)

                index.write()

                tree = index.write_tree()
                oid = self.db.repo.create_commit('refs/heads/{}'.format(self.db.branch),
                                                 self.signature,
                                                 self.signature,
                                                 self.message,
                                                 tree,
                                                 [self.commit_id])

                self.db.commit_id = oid.hex
            except Exception as e:
                logger.error("Error commiting, reset to {}".format(self.commit_id))
                self.db.reset(self.commit_id)
                # TODO : ensure that the reset is perfect
                # even when creating a new file in the folder ? untracked
                raise e
        else:
            self.db.reset(self.commit_id)


class GitInterface:
    def __init__(self,
                 origin,
                 credentials=None,
                 branch='master',
                 commit_id=None,
                 folder=None):

        self.origin = origin
        self.remotes = {'origin': origin}
        self.credentials = credentials
        self.branch = branch
        self.commit_id = commit_id

        if folder:
            self.folder = os.path.abspath(folder)
        else:
            self.folder = get_local_cache_dir(origin)


        # download database
        self.pull(remote='origin')

    def commit(self, signature, message):
        return git_transaction(self, signature, message)

    def reset(self, commit_id=None):
        if commit_id is None:
            commit_id = self.commit_id
        #TODO : test if reset is enough : need to checkout working copy ?
        self.repo.reset(commit_id, pygit2.GIT_RESET_HARD)
        status = self.repo.status()

        # delete new files
        for f, k in status.items():
            if k & GIT_STATUS_WT_NEW:
                os.remove(f)

    @monitor_decorator('pull')
    def pull(self, remote='origin', credentials=None):
        if not os.path.exists(self.folder):
            logger.info("Cloning {} into {}".format(self.remotes['origin'], self.folder))

            callbacks = pygit2.RemoteCallbacks(credentials=credentials if credentials else self.credentials)

            def init_remote(repo, name, url):
                remote = repo.remotes.create(name, url)
                return remote

            repo = pygit2.clone_repository(self.remotes['origin'],
                                           self.folder,
                                           remote=init_remote,
                                           checkout_branch=self.branch,
                                           callbacks=callbacks)
        else:
            repo = pygit2.Repository(self.folder)

        # if remote == 'origin':
        #     # ensure origin is set
        #     self.add_remote('origin', self.remotes['origin'])

        remote_ = repo.remotes[remote]
        remote_.fetch(callbacks=pygit2.RemoteCallbacks(credentials=self.credentials))
        self.commit_id = repo.lookup_reference('refs/heads/{}'.format(self.branch)).target

        # use most recent of remote
        commit_remote = repo.lookup_reference('refs/remotes/{}/{}'.format(remote, self.branch)).target

        merge_result, _ = repo.merge_analysis(commit_remote)

        # Up to date, do nothing
        if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
            logger.info("Merging: repository up-to-date")
            return

        # We can just fastforward
        elif merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
            logger.info("Merging: fast-forward")
            self.commit_id = commit_remote
            repo.checkout_tree(repo.get(self.commit_id))
            master_ref = repo.lookup_reference('refs/heads/{}'.format(self.branch))
            master_ref.set_target(self.commit_id)
            repo.head.set_target(self.commit_id)
        elif merge_result & pygit2.GIT_MERGE_ANALYSIS_NORMAL:
            logger.info("Merging: cherry-pick local branch on remote branch")

            base = repo.merge_base(self.commit_id, commit_remote)

            # rebased_commits : locals commits since base
            rebased_commits = []
            commit = repo.get(self.commit_id)
            while len(commit.parents):
                if base == commit.id:
                    break
                rebased_commits.insert(0, commit)
                commit = commit.parents[0]

            branch = repo.branches.get(self.branch)

            # checkout to pulled branch
            repo.checkout_tree(repo.get(commit_remote), strategy=GIT_CHECKOUT_FORCE | GIT_CHECKOUT_RECREATE_MISSING)
            repo.head.set_target(commit_remote)

            last = commit_remote
            for commit in rebased_commits:
                repo.head.set_target(last)

                repo.cherrypick(commit.id)
                if repo.index.conflicts is None:
                    tree_id = repo.index.write_tree()

                    cherry = repo.get(commit.id)
                    committer = pygit2.Signature('Louis van Beurden', 'louis.vanbeurden@ieml.io')

                    last = repo.create_commit(branch.name, cherry.author, committer,
                                       cherry.message, tree_id, [last])
                    repo.state_cleanup()
                else:
                    raise ValueError("/!\ Merge conflict : can't cherry-pick locals commits on remote branch")

            self.commit_id = last
            repo.head.set_target(last)
        else:
            #TODO handle merge conflicts here
            raise ValueError("Incompatible history, can't merge origin into {}#{} in folder {}".format(self.branch, self.commit_id,self.folder))

    @monitor_decorator('push')
    def push(self, remote='origin', force=False):
        repo = pygit2.Repository(self.folder)
        remote = repo.remotes[remote]
        callbacks = pygit2.RemoteCallbacks(credentials=self.credentials)
        remote.push(['{}refs/heads/{}'.format('+' if force else '', self.branch)],
                    callbacks=callbacks)

    @property
    def repo(self):
        return pygit2.Repository(self.folder)

    def get_version(self):
        return self.branch, self.commit_id

    def set_version(self, branch, commit_id):
        self.branch = branch
        self.commit_id = commit_id
        self.pull()

    def add_remote(self, name, url):
        try:
            r = self.repo.remotes[name]
            if r.url != url:
                raise ValueError("Remote already exists with different url")

        except KeyError:
            self.repo.remotes.create(name, url)
