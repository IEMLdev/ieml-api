import hashlib
import os
import logging
from _pygit2 import GIT_CHECKOUT_FORCE, GIT_CHECKOUT_RECREATE_MISSING, GIT_STATUS_WT_NEW, \
    GIT_STATUS_WT_DELETED, GIT_STATUS_WT_MODIFIED, GIT_STATUS_WT_RENAMED, GitError

import pygit2
from appdirs import user_cache_dir

from ieml.commons import monitor_decorator
from ieml.constants import IEMLDB_DEFAULT_GIT_ADDRESS, LIBRARY_VERSION

logger = logging.getLogger('GitInterface')
logger.setLevel(logging.INFO)

def get_local_cache_dir(origin):
    return os.path.join(user_cache_dir(appname='ieml', appauthor=False, version=LIBRARY_VERSION),
                        hashlib.md5(origin.encode('utf8')).hexdigest())


class MergeConflict(Exception):
    def __init__(self, message, conflicts):
        self.message = message
        self.conflicts = conflicts

    def __repr__(self):
        return self.message

#TODO  normalize repo name with postfix .git

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

                self.db.commit_id = oid
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
                 origin=IEMLDB_DEFAULT_GIT_ADDRESS,
                 credentials=pygit2.Username('git'),
                 branch='master',
                 commit_id=None,
                 folder=None):

        self.origin = origin
        self.remotes = {'origin': origin}
        self.credentials = credentials
        self.branch = branch
        self.commit_id = None

        self.target_commit = commit_id

        if folder:
            self.folder = os.path.abspath(folder)
        else:
            self.folder = get_local_cache_dir(origin)


        # download database
        self.pull(remote='origin')
        if commit_id is not None:
            self.checkout(self.branch, commit_id)

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

        self.commit_id = commit_id

    def checkout(self, branch, commit_id, credentials=None):
        repo = self.get_repo(credentials=credentials)

        master_ref = repo.lookup_reference('refs/heads/{}'.format(branch))
        repo.checkout(master_ref)

        self.repo.reset(commit_id, pygit2.GIT_RESET_HARD)

        # repo.checkout_tree(repo.get(commit_id), strategy=pygit2.GIT_CHECKOUT_FORCE | pygit2.GIT_CHECKOUT_RECREATE_MISSING)
        # master_ref.set_target(commit_id)
        # repo.head.set_target(commit_id)

        self.commit_id = commit_id
        self.branch = branch


    def get_repo(self, credentials=None):
        if not os.path.exists(self.folder):
            logger.info("Cloning {} into {}".format(self.remotes['origin'], self.folder))

            callbacks = pygit2.RemoteCallbacks(credentials=credentials if credentials else self.credentials)

            def init_remote(repo, name, url):
                remote = repo.remotes.create(name, url)
                return remote

            return pygit2.clone_repository(self.remotes['origin'],
                                           self.folder,
                                           remote=init_remote,
                                           checkout_branch=self.branch,
                                           callbacks=callbacks)
        else:
            return pygit2.Repository(self.folder)

    @monitor_decorator('pull')
    def pull(self, remote='origin', credentials=None):
        repo = self.get_repo(credentials=credentials)

        remote_ = repo.remotes[remote]
        try:
            remote_.fetch(callbacks=pygit2.RemoteCallbacks(credentials=self.credentials))
        except GitError as e:
            logger.error(repr(e))
            pass

        current_commit = repo.lookup_reference('refs/heads/{}'.format(self.branch)).target

        if self.target_commit is None or remote != 'origin':
            # use most recent of remote
            commit_target = repo.lookup_reference('refs/remotes/{}/{}'.format(remote, self.branch)).target
        else:
            commit_target = self.target_commit

        merge_result, _ = repo.merge_analysis(commit_target)

        # Up to date, do nothing
        if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
            logger.info("Merging: repository up-to-date")
            self.commit_id = commit_target
            return

        # We can just fastforward
        elif merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
            logger.info("Merging: fast-forward")
            self.checkout(self.branch, commit_target, credentials=credentials)

        elif merge_result & pygit2.GIT_MERGE_ANALYSIS_NORMAL:
            logger.info("Merging: cherry-pick local branch on remote branch")

            base = repo.merge_base(current_commit, commit_target)

            # rebased_commits : locals commits since base
            rebased_commits = []
            commit = repo.get(current_commit)
            while len(commit.parents):
                if base == commit.id:
                    break
                rebased_commits.insert(0, commit)
                commit = commit.parents[0]

            branch = repo.branches.get(self.branch)

            # checkout to pulled branch
            repo.checkout_tree(repo.get(commit_target), strategy=GIT_CHECKOUT_FORCE | GIT_CHECKOUT_RECREATE_MISSING)
            repo.head.set_target(commit_target)

            last = commit_target
            for commit in rebased_commits:
                repo.head.set_target(last)

                repo.cherrypick(commit.id)
                if repo.index.conflicts is None:
                    tree_id = repo.index.write_tree()

                    cherry = repo.get(commit.id)
                    committer = pygit2.Signature('Louis van Beurden', 'lvb@pyth.ai')

                    last = repo.create_commit(branch.name, cherry.author, committer,
                                       cherry.message, tree_id, [last])
                    repo.state_cleanup()
                else:
                    conflicts = self.list_conflict()
                    self.reset()
                    raise MergeConflict(message="can't cherry-pick locals commits on remote branch",
                                        conflicts=conflicts)

                self.commit_id = last
            repo.head.set_target(self.commit_id)
        else:
            #TODO handle merge conflicts here
            raise ValueError("Incompatible history, can't merge origin into {}#{} in folder {}".format(self.branch, commit_target,self.folder))


    def list_conflict(self):
        # ancestor_data = repo.get(ancestor.oid).data.decode('utf8')
        repo = self.get_repo(credentials=self.credentials)
        return []
        #
        # for ancestor, ours, theirs in repo.index.conflicts:
        #     if ancestor:
        #     path = ancestor.path if ancestor is not None else ours.path
        #
        #     ours_data = repo.get(ours.oid).data.decode('utf8')
        #     theirs_data = repo.get(theirs.oid).data.decode('utf8')




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
        return self.branch, str(self.commit_id)

    def set_version(self, branch, commit_id):
        self.checkout(branch, commit_id)
        # self.branch = branch
        # self.commit_id = commit_id
        # self.pull()

    def add_remote(self, name, url):
        try:
            r = self.repo.remotes[name]
            if r.url != url:
                raise ValueError("Remote already exists with different url")

        except KeyError:
            self.repo.remotes.create(name, url)

    def diff(self, commit0, commit1):
        t0 = self.repo.revparse_single(str(commit0))
        t1 = self.repo.revparse_single(str(commit1))

        res = {}
        for patch in self.repo.diff(t0, t1):
            # per file
            #         print(patch.text)
            added = []
            deleted = []

            line = patch.delta.new_file.path

            for h in patch.hunks:
                for l in h.lines:
                    if l.new_lineno == -1:
                        deleted.append(l.content)
                    elif l.old_lineno == -1:
                        added.append(l.content)

            res[line] = {
                'added': added,
                'deleted': deleted
            }

        return res
