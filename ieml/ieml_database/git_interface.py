import csv
import hashlib
import os
from io import StringIO

import tqdm

from ieml.ieml_database.descriptors import Descriptor, Descriptors

try:
    from pygit2._pygit2 import GIT_CHECKOUT_FORCE, GIT_CHECKOUT_RECREATE_MISSING, GIT_STATUS_WT_NEW, \
        GIT_STATUS_WT_DELETED, GIT_STATUS_WT_MODIFIED, GIT_STATUS_WT_RENAMED, GitError

except ImportError:
    from pygit2 import GIT_CHECKOUT_FORCE, GIT_CHECKOUT_RECREATE_MISSING, GIT_STATUS_WT_NEW, \
        GIT_STATUS_WT_DELETED, GIT_STATUS_WT_MODIFIED, GIT_STATUS_WT_RENAMED, GitError

from sys import stderr

import pygit2
from appdirs import user_cache_dir

from ieml import logger, error
from ieml.commons import monitor_decorator
from ieml.constants import IEMLDB_DEFAULT_GIT_ADDRESS, LIBRARY_VERSION, DEFAULT_COMMITER_SIGNATURE, DESCRIPTORS_CLASS, \
    LANGUAGES


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
    def __init__(self,
                 db,
                 signature,
                 message):

        self.db = db
        self.signature = signature
        self.message = message

    def __enter__(self):
        self.commit_id = self.db.repo.head.target


        # ignore files at the root
        if self.db.status() != {}:
            raise ValueError("Try to start a transaction on a not clean working dir state, "
                             "please use db.reset() first.")

    @monitor_decorator("Commit transaction")
    def __exit__(self, type, value, traceback):
        print("exiting commit context", file=stderr)
        if type is None:
            try:
                status = self.db.status()
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
                oid = self.db.repo.create_commit(self.db.repo.head.name,
                                                 self.signature,
                                                 self.signature,
                                                 self.message,
                                                 tree,
                                                 [self.commit_id])

                # self.db.commit_id = oid
                error("committing db : {}".format(str(oid)))
            except Exception as e:
                error("Error commiting, reset to {}".format(self.commit_id))
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
        """

        :param origin:
        :param credentials:
        :param branch: the branch to checkout
        :param commit_id: the commit to checkout
        :param folder:
        """
        self.origin = origin
        # self.remotes = {'origin': origin}
        self.credentials = credentials

        if folder:
            self.folder = os.path.abspath(folder)
        else:
            self.folder = get_local_cache_dir(origin)

        # clone repository
        _ = self.repo
        # self.checkout(branch, None)

        # update database
        # self.pull(remote='origin')
        self.checkout(branch, commit_id)

    def commit(self, signature, message):
        return git_transaction(self, signature, message)

    def status(self):
        """ignore path starting with '.'"""
        res = {}
        for f, k in self.repo.status().items():
            if not f.startswith('.'):
                res[f] = k
        return res

    def reset(self, commit_id=None):
        """
        Set the current branch HEAD to ref the given commit
        :param commit_id: if set, reset to this commit id, otherwise to the head of the branch
        :return: None
        """
        if commit_id is None:
            logger.info(str(self.repo.head.target))
            commit_id = self.repo.head.target

        self.repo.state_cleanup()

        self.repo.reset(commit_id, pygit2.GIT_RESET_HARD)

        # delete new files
        for f, k in self.status().items():
            if k & GIT_STATUS_WT_NEW:
                os.remove(os.path.join(self.folder, f))


    def checkout(self, branch=None, commit_id=None):
        repo = self.repo

        self.reset()
        if branch is not None:
            master_ref = repo.lookup_reference('refs/heads/{}'.format(branch))
        else:
            master_ref = repo.head

        repo.checkout(master_ref)

        if commit_id is not None:
            self.reset(commit_id)

    @property
    def repo(self):
        if not os.path.exists(self.folder):
            logger.info("Cloning {} into {}".format(self.origin, self.folder))

            callbacks = pygit2.RemoteCallbacks(credentials=self.credentials)

            def init_remote(repo, name, url):
                remote = repo.remotes.create(name, url)
                return remote

            return pygit2.clone_repository(self.origin,
                                           self.folder,
                                           remote=init_remote,
                                           # checkout_branch=self.branch,
                                           callbacks=callbacks)
        else:
            return pygit2.Repository(self.folder)

    @monitor_decorator('pull')
    def pull(self, remote='origin') -> {str: Descriptor}:
        """

        :param remote: the remote to pull from
        :return: the conflicts : a dict that map ieml to the descriptor in conflict. In case of a conflict, the remote version is chosen as current version and the old current is returned by the function.
        """
        repo = self.repo

        remote_ = repo.remotes[remote]
        try:
            remote_.fetch(callbacks=pygit2.RemoteCallbacks(credentials=self.credentials))
        except GitError as e:
            logger.error(repr(e))
            pass

        current_commit = repo.head.target


        # pull not the origin remote
        # if self.target_commit is None or remote != 'origin':
        # use most recent of remote
        commit_target = repo.lookup_reference('refs/remotes/{}/{}'.format(remote, repo.head.shorthand)).target
        # else:
        #     commit_target = self.target_commit

        merge_result, _ = repo.merge_analysis(commit_target)
        conflicts = {}

        # Up to date, do nothing
        if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
            error("Merging: repository up-to-date")
            # self.commit_id = commit_target

        # We can just fastforward
        elif merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
            error("Merging: fast-forward")
            self.checkout(None, commit_target)

        elif merge_result & pygit2.GIT_MERGE_ANALYSIS_NORMAL:
            error("Merging: cherry-pick local branch on remote branch")

            # base = repo.merge_base(current_commit, commit_target)

            # # rebased_commits : locals commits since base
            # rebased_commits = []
            # commit = repo.get(current_commit)
            # while len(commit.parents):
            #     if base == commit.id:
            #         break
            #     rebased_commits.insert(0, commit)
            #     commit = commit.parents[0]

            # branch = repo.branches.get(self.repo.head.shorthand)
            #
            # # checkout to pulled branch
            # repo.checkout_tree(repo.get(commit_target),
            #                    strategy=GIT_CHECKOUT_FORCE | GIT_CHECKOUT_RECREATE_MISSING)
            # repo.head.set_target(commit_target)


            repo.merge(commit_target)

            # we are now in the remote state, we are going to try to add the local commit on top of the remote HEAD
            # until a merge conflict
            # last = commit_target
            # for commit in tqdm.tqdm(rebased_commits, "Cherry picking commits"):
            #     repo.head.set_target(last)
            #     try:
            #         repo.cherrypick(commit.id)
            #     except GitError as e:
            #         # Cherry picking merge commit :
            #         # Usually you cannot cherry-pick a merge because you do not know which side of the merge should
            #         # be considered the mainline. This option specifies the parent number (starting from 1) of the
            #         # mainline and allows cherry-pick to replay the change relative to the specified parent.
            #         # https://stackoverflow.com/questions/9229301/git-cherry-pick-says-38c74d-is-a-merge-but-no-m-option-was-given
            #         pass
            #         # raise e

            if repo.index.conflicts is None:
                tree_id = repo.index.write_tree()

                cherry = repo.get(commit_target)

                last = repo.create_commit('HEAD', cherry.author, DEFAULT_COMMITER_SIGNATURE,
                                   "Merge branch", tree_id, [repo.head.target, commit_target])

            else:
                to_commit = []

                # ancestor : the IndexEntry on the file before the merge, or None if the file is created
                # remote_entry : the IndexEntry of the merged remote file or None if remotely deleted
                # local_entry : the IndexEntry of the local file or None if locally deleted

                # resolve conflicts ...
                for ancestor, local_entry, remote_entry in repo.index.conflicts:
                    old_path = ancestor.path if ancestor is not None else local_entry.path

                    #  None => deleted
                    new_path = remote_entry.path if remote_entry is not None else None

                    if new_path is not None and old_path != new_path:
                        raise ValueError("Renaming not supported")

                    # add local entry as conflicts if a descriptor
                    if old_path.endswith('.desc'):
                        if local_entry is not None:
                            if ancestor is not None and ancestor.path != local_entry.path:
                                raise ValueError("Renaming not supported")

                            # local entry is not deleted
                            res = Descriptors.from_csv_string(repo.get(local_entry.oid).data.decode('utf8'),
                                                              assert_unique_ieml=True)
                            ieml = next(iter(res))
                            conflicts[ieml] = res[ieml]
                        else:
                            # locally deleted
                            assert remote_entry is not None
                            res = Descriptors.from_csv_string(repo.get(remote_entry.oid).data.decode('utf8'),
                                                              assert_unique_ieml=True)
                            ieml = next(iter(res))

                            conflicts[ieml] = {d: {l : [] for l in LANGUAGES} for d in DESCRIPTORS_CLASS}
                    else:
                        print("Ignoring", old_path, "not a descriptor", file=stderr)
                    # repo.index.read()
                    to_commit.append({
                        'old_path': old_path,
                        'new_path': new_path,
                        'data': repo.get(remote_entry.oid).data if remote_entry is not None else None
                    })

                if to_commit != []:
                    for comm in to_commit:
                        data = comm['data']
                        old_path = comm['old_path']
                        new_path = comm['new_path']

                        # accept theirs (ours from git point of view)
                        if data is not None:
                            with open(os.path.join(self.folder, new_path), 'wb') as fp:
                                fp.write(data)

                            repo.index.add(new_path)

                        if new_path is None:
                            del repo.index.conflicts[old_path]
                            os.remove(os.path.join(self.folder, old_path))

                    repo.index.write()

                    tree_id = repo.index.write_tree()
                    last = self.repo.create_commit('HEAD',
                                            DEFAULT_COMMITER_SIGNATURE,
                                            DEFAULT_COMMITER_SIGNATURE,
                                            "Merge {}".format(ieml),
                                            tree_id,
                                            [repo.head.target, commit_target])

                # repo.state_cleanup()

            # repo.head.set_target(last)
        else:
            #TODO handle merge conflicts here
            raise ValueError("Incompatible history, can't merge origin into {}#{} in folder {}".format(self.branch, commit_target,self.folder))

        return conflicts


    @monitor_decorator('push')
    def push(self, remote='origin', force=False):
        repo = pygit2.Repository(self.folder)
        remote = repo.remotes[remote]
        callbacks = pygit2.RemoteCallbacks(credentials=self.credentials)
        remote.push(['{}{}'.format('+' if force else '', self.repo.head.name)],
                    callbacks=callbacks)

    @property
    def current_commit(self):
        return str(self.repo.head.target)

    def get_version(self):
        repo = self.repo
        return repo.head.shorthand, str(repo.head.target)

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

            file_path = patch.delta.new_file.path
            l = None
            for h in patch.hunks:
                for l in h.lines:
                    if l.new_lineno == -1:
                        deleted.append(l.content)
                    elif l.old_lineno == -1:
                        added.append(l.content)
            if l:
                res[file_path] = {
                    'ieml': l.content.split('"')[1],
                    'added': added,
                    'deleted': deleted,
                    'is_new': patch.delta.old_file.mode == 0,
                    'is_removed': patch.delta.new_file.mode == 0,
                }

        return res
