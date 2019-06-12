import argparse
import functools
import glob
import hashlib
import logging
import operator
import shutil
import traceback
from _pygit2 import GIT_RESET_HARD, GIT_CHECKOUT_FORCE, GIT_CHECKOUT_RECREATE_MISSING, GIT_STATUS_WT_NEW, \
    GIT_STATUS_WT_DELETED, GIT_STATUS_WT_MODIFIED, GIT_STATUS_WT_RENAMED
from collections import defaultdict

import pandas
from functools import reduce

import pygit2
import time
import tqdm
from appdirs import user_cache_dir

from ieml import IEMLDatabase, LIBRARY_VERSION
import os
import json
from hashlib import sha224
import subprocess

from ieml.commons import FolderWatcherCache
from ieml.constants import LANGUAGES, INHIBITABLE_RELATIONS, STRUCTURE_KEYS
from ieml.dictionary import Dictionary
from ieml.dictionary.dictionary import Dictionary2
from ieml.dictionary.script import Script, NullScript, MultiplicativeScript, AdditiveScript, script
from ieml.ieml_database.descriptor import DESCRIPTORS_CLASS
from ieml.ieml_database.ieml_database import monitor_decorator
from ieml.lexicon.grammar.parser2 import IEMLParser
from ieml.lexicon.syntax import PolyMorpheme, Word


def get_local_cache_dir(origin):
    return os.path.join(user_cache_dir(appname='ieml', appauthor=False, version=LIBRARY_VERSION),
                        hashlib.md5(origin.encode('utf8')).hexdigest())

logger = logging.getLogger('GitInterface')
logger.setLevel(logging.INFO)


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


def _normalize_key(ieml, key, value, parse_ieml=False, partial=False, structure=False):
    if not (partial or (ieml and key and (structure or value))):
        raise ValueError("IEML and Key can't be null")

    if ieml:
        ieml = str(ieml)
        if parse_ieml:
            parsed = IEMLParser().parse(str(ieml))
            if ieml != str(parsed):
                raise ValueError("IEML is not normalized: {}".format(ieml))

            # if len(parsed) == 1 and structure:
            #     raise ValueError("Only paradigms can have a structure: {}".format(ieml))

    if structure:
        if key:
            key = str(key)
            if key not in STRUCTURE_KEYS:
                raise ValueError("Unsupported structure key: '{}'".format(str(key)))

        if value:
            if key and key == 'inhibition':
                value = str(value)
                if value not in INHIBITABLE_RELATIONS:
                    raise ValueError("Unsupported inhibition: {}".format(value))

            if key and key in ['is_root', 'is_ignored']:
                value = json.loads(str(value).lower())
                if not isinstance(value, bool):
                    raise ValueError("is_root or is_ignored field only accept boolean, not {}".format(value))
                value = str(value)
    else:
        if key:
            key = str(key)
            if key not in LANGUAGES:
                raise ValueError("Unsupported language: '{}'".format(str(key)))

        if value:
            value = str(value)
            if value not in DESCRIPTORS_CLASS:
                raise ValueError("Unsupported descriptor: '{}'".format(str(value)))

    return ieml, key, value


def _normalize_value(value):
    if not isinstance(value, str):
        raise ValueError("Expected a string, not a {}".format(value.__class__.__name__))

    # TODO normalize accent encoding
    return value.strip()


def _normalize_inhibitions(inhibitions):
    return inhibitions


class Descriptors:
    def __init__(self, df):
        assert list(df.columns) == ['ieml', 'language', 'descriptor', 'value']
        self.df = df.set_index(['ieml', 'language', 'descriptor']).sort_index()

    # @monitor_decorator('get_values')
    def get_values(self, ieml, language, descriptor):
        ieml, language, descriptor = _normalize_key(ieml, language, descriptor,
                                                    parse_ieml=False, partial=False)
        try:
            return self.df.loc(axis=0)[(ieml, language, descriptor)].to_dict('list')['value']
        except KeyError:
            return []

    # @monitor_decorator('get_values_partial')
    def get_values_partial(self, ieml, language=None, descriptor=None):
        ieml, language, descriptor = _normalize_key(ieml, language, descriptor,
                                                    parse_ieml=False, partial=True)

        key = {'ieml': ieml, 'language': language, 'descriptor': descriptor}
        key = reduce(operator.and_,
                     [self.df.index.get_level_values(k) == v for k, v in key.items() if v is not None],
                     True)

        res = defaultdict(list)
        for k, (v,) in self.df[key].iterrows():
            res[k].append(v)

        return dict(res)


class Structure:
    def __init__(self, df):
        assert list(df.columns) == ['ieml', 'key', 'value']
        self.df = df.set_index(['ieml', 'key']).sort_index()

    @monitor_decorator('get_structure_values')
    def get_values(self, ieml, key):
        ieml, key, _ = _normalize_key(ieml, key, None, parse_ieml=False, partial=False, structure=True)

        try:
            return self.df.loc(axis=0)[(ieml, key)].to_dict('list')['value']
        except KeyError:
            return []

    @monitor_decorator('get_values_partial')
    def get_values_partial(self, ieml, key=None):
        ieml, key, _ = _normalize_key(ieml, key, None, parse_ieml=False, partial=True, structure=True)

        key = {'ieml': ieml, 'key': key}
        key = reduce(operator.and_,
                     [self.df.index.get_level_values(k) == v for k, v in key.items() if v is not None],
                     True)

        res = defaultdict(list)
        for k, (v,) in self.df[key].iterrows():
            res[k].append(v)

        return dict(res)

def cache_results_watch_files(path, name):
    def decorator(f):
        def wrapper(*args, **kwargs):
            use_cache = args[0].use_cache
            self = args[0]
            cache_folder = self.cache_folder
            db_path = self.folder

            files = [ff for ff in glob.glob(os.path.join(db_path, path), recursive=True)]

            if use_cache:
                cache = FolderWatcherCache(files, cache_folder=cache_folder, name=name)
                if not cache.is_pruned():
                    logger.info("read_{}.cache: Reading cache at {}".format(name, cache.cache_file))
                    try:
                        instance = cache.get()
                    except Exception as e:
                        # cache.prune()
                        # raise e
                        instance = None
                else:
                    logger.info("read_{}.cache: Pruned cache at {}".format(name, cache_folder))
                    instance = None

                if instance:
                    return instance

            instance = f(*args, **kwargs)

            if use_cache and cache_folder:
                cache = FolderWatcherCache(files, cache_folder=cache_folder, name=name)

                logger.info("read_{}.cache: Updating cache at {}".format(name, cache.cache_file))
                cache.update(instance)

            return instance

        functools.wraps(wrapper)

        return wrapper

    return decorator


class _IEMLDatabase:
    CLASS_TO_FOLDER={
        NullScript: ('morpheme', 0),
        AdditiveScript: ('morpheme', 0),
        MultiplicativeScript: ('morpheme', 0),
        PolyMorpheme: ('polymorpheme', 5),
        Word: ('word', 10)
    }

    MAX_IEML_NAME_SIZE = 100
    HASH_SIZE = 10

    def __init__(self, folder,
                 cache_folder=None,
                 use_cache=True):
        self.folder = folder

        self.use_cache = use_cache
        self.cache_folder = cache_folder
        if self.use_cache:
            if cache_folder is None:
                self.cache_folder = self.folder
        else:
            self.cache_folder = None

    def filename_of(self, ieml):
        l = str(ieml)
        if len(l) > self.MAX_IEML_NAME_SIZE:
            l = "{}|{}".format(l[:self.MAX_IEML_NAME_SIZE - self.HASH_SIZE - 1],
                               sha224(l.encode('utf8')).hexdigest()[:self.HASH_SIZE])
        return l

    def path_of(self, ieml, descriptor=True, mkdir=False):
        if isinstance(ieml, str):
            ieml = IEMLParser().parse(ieml)

        if descriptor:
            ext = '.desc'
        else:
            ext = '.ieml'

        class_folder, prefix_sixe = self.CLASS_TO_FOLDER[ieml.__class__]

        filename = self.filename_of(ieml)
        prefix = filename[:prefix_sixe]

        p = os.path.join(self.folder, class_folder,
                         'singular' if len(ieml) == 1 else 'paradigm', prefix)
        if mkdir:
            os.makedirs(p, exist_ok=True)

        return os.path.join(p, filename + ext)

    @monitor_decorator("list paradigms")
    def list(self, type, paradigm=True, parse=False):
        p = os.path.join(self.folder, type, 'paradigm' if paradigm else 'singular')
        p1 = subprocess.Popen("find -path *.desc -print0".split(), stdout=subprocess.PIPE, cwd=p)
        p2 = subprocess.Popen("xargs -0 cat".split(), stdin=p1.stdout, stdout=subprocess.PIPE, cwd=p)
        p3 = subprocess.Popen(["cut", "-f2", '-d', '"'], stdin=p2.stdout, stdout=subprocess.PIPE, cwd=p)
        p4 = subprocess.Popen(["uniq"], stdin=p3.stdout, stdout=subprocess.PIPE, cwd=p)

        res = [s.strip().decode('utf8') for s in p4.stdout.readlines() if s.strip()]

        if parse:
            parser = IEMLParser()
            return [parser.parse(s) for s in res]

        return res

    @monitor_decorator("Get descriptors")
    def get_descriptors(self):
        p1 = subprocess.Popen("find -path *.desc -print0".split(), stdout=subprocess.PIPE, cwd=self.folder)
        p2 = subprocess.Popen("xargs -0 cat".split(), stdin=p1.stdout, stdout=subprocess.PIPE, cwd=self.folder)
        r = pandas.read_csv(p2.stdout, sep=' ', header=None)
        r.columns=['ieml', 'language', 'descriptor', 'value']
        return Descriptors(r)

    @monitor_decorator("Get structure")
    def get_structure(self):
        p1 = subprocess.Popen("find -path *.ieml -print0".split(), stdout=subprocess.PIPE, cwd=self.folder)
        p2 = subprocess.Popen("xargs -0 cat".split(), stdin=p1.stdout, stdout=subprocess.PIPE, cwd=self.folder)
        r = pandas.read_csv(p2.stdout, sep=' ', header=None)
        r.columns = ['ieml', 'key', 'value']
        return Structure(r)

    @monitor_decorator("Get dictionary")
    @cache_results_watch_files("morpheme/*/*.ieml", 'dictionary')
    def get_dictionary(self):
        return Dictionary2(self.list('morpheme', paradigm=True), self.get_structure())

    def add_descriptor(self, ieml, language, descriptor, value):
        ieml, language, descriptor = _normalize_key(ieml, language, descriptor,
                                                         parse_ieml=True, partial=False)
        value = _normalize_value(value)
        if not value:
            return

        with open(self.path_of(ieml, mkdir=True), 'a', encoding='utf8') as fp:
            fp.write('"{}" {} {} "{}"\n'.format(
                str(ieml),
                language,
                descriptor,
                self.escape_value(value)))

    @monitor_decorator('remove_key')
    def remove_descriptor(self, ieml, language=None, descriptor=None, value=None):
        ieml, language, descriptor = _normalize_key(ieml, language, descriptor,
                                                         parse_ieml=True, partial=True)

        if not os.path.isfile(self.path_of(ieml, mkdir=True)):
            return

        if descriptor is None and language is None and value is None:
            os.remove(self.path_of(ieml, mkdir=True))
            return

        if descriptor is None or language is None:
            if language is None:
                for l in LANGUAGES:
                    self.remove_descriptor(ieml, l, descriptor)
            else:
                for d in DESCRIPTORS_CLASS:
                    self.remove_descriptor(ieml, language, d)
            return

        if value:
            value = _normalize_value(value)


        with open(self.path_of(ieml, mkdir=True), "r", encoding='utf8') as f:
            lines = [l for l in f.readlines()
                     if not l.startswith('"{}" {} {} '.format(str(ieml), language, descriptor) + \
                                        ('"{}"'.format(self.escape_value(value)) if value else ''))]
        with open(self.path_of(ieml), "w", encoding='utf8') as f:
            f.writelines(lines)

    def add_structure(self, ieml, key, value):
        ieml, key, value = _normalize_key(ieml, key, value, parse_ieml=True, partial=False, structure=True)

        with open(self.path_of(ieml, descriptor=False, mkdir=True), 'a', encoding='utf8') as fp:
            fp.write('"{}" {} "{}"\n'.format(str(ieml), key, value))

    def remove_structure(self, ieml, key=None, value=None):
        ieml, key, value = _normalize_key(ieml, key, value, parse_ieml=True, partial=True, structure=True)

        if not os.path.isfile(self.path_of(ieml, descriptor=False, mkdir=True)):
            return

        if key is None:
            os.remove(self.path_of(ieml, descriptor=False, mkdir=True))
            return

        with open(self.path_of(ieml, descriptor=False, mkdir=True), "r", encoding='utf8') as f:
            lines = [l for l in f.readlines()
                     if not l.startswith('"{}" {} '.format(str(ieml), key) + \
                                        ('"{}"'.format(value) if value else ''))]

        with open(self.path_of(ieml, descriptor=False), "w", encoding='utf8') as f:
            f.writelines(lines)

    def escape_value(self, v):
        return v.replace('"', '""').replace('\n', '\\n')


def migrate(database, out_folder):
    descriptors = database.descriptors()
    dictionary = database.dictionary_structure()
    # 'root', 'paradigms', 'inhibitions'

    shutil.rmtree(out_folder + '/descriptors')
    shutil.rmtree(out_folder + '/structure')
    # os.rmdir(out_folder)

    # os.mkdir(out_folder)

    db2 = _IEMLDatabase(out_folder)
    # db2.get_csv()

    if not os.path.isdir(out_folder):
        os.mkdir(out_folder)

    for ieml, (paradigms, inhibitions) in tqdm.tqdm(dictionary.structure.iterrows(), 'migrating structure'):
        l = IEMLParser().parse(ieml, factorize_script=True)

        db2.add_structure(str(l), 'is_root', True)
        for i in inhibitions:
            db2.add_structure(str(l), 'inhibition', i)

    all_db = defaultdict(lambda : defaultdict(dict))

    for (ieml, lang, desc), (v) in descriptors:
        all_db[ieml][(lang,desc)] = v.values[0]

    for ieml, dd in tqdm.tqdm(all_db.items(), 'migrating descriptors'):
        l = IEMLParser().parse(ieml, factorize_script=True)

        path = db2.path_of(l)

        os.makedirs('/'.join(path.split('/')[:-1]), exist_ok=True)


        with open(path, 'w') as fp:
            for (lang, desc), v in dd.items():
                for vv in v:
                    fp.write('"{}" {} {} "{}"\n'.format(str(l), lang, desc, db2.escape_value(vv)))


            # fp.write(json.dumps({'ieml': str(l), **dd}, indent=True))

def ignore_body_parts(gitdb, db):
    root = script("f.o.-f.o.-',n.i.-f.i.-',M:O:.-O:.-',_+f.o.-f.o.-'E:.-U:.S:+B:T:.-l.-',E:.-U:.M:T:.-l.-'E:.-A:.M:T:.-l.-',_")

    to_ignore = []
    for ss in db.list('morpheme', paradigm=False, parse=True):
        if ss in root:
            to_ignore.append(ss)

    for p in db.list('morpheme', paradigm=True, parse=True):
        if set(root.singular_sequences).issuperset(p.singular_sequences):
            to_ignore.append(p)
    print(len(to_ignore))
    with gitdb.commit(pygit2.Signature("Louis van Beurden", 'louis.vanbeurden@gmail.com'), "[Ignore] ignore body part root paradigm"):
        for s in to_ignore:
            db.add_structure(s, 'is_ignored', True)




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('author_name', type=str)
    parser.add_argument('author_email', type=str)

    parser.add_argument('--folder', type=str)

    args = parser.parse_args()

    # folder = args.folder

    #
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

    # gitdb = GitInterface(origin='https://github.com/ogrergo/ieml-language.git',
    #                      credentials=pygit2.Username('git'),
    #                      folder=folder)

    db = IEMLDatabase(git_address='ssh://git@github.com/ogrergo/ieml-language.git',
                      db_folder=folder,
                      credentials=pygit2.Keypair('git', '/home/louis/.ssh/id_rsa.pub', '/home/louis/.ssh/id_rsa', ''),)
    #
    # d = Descriptors(db2.get_pandas())
    # # print(d.get_values('wa.', 'fr', 'translations'))
    # # db2.remove_key('wa.', 'fr', 'translations', 'agir')
    # # d = Descriptors(db2.get_pandas())
    # # print(d.get_values('wa.', 'fr', 'translations'))
    #
    # # v = d.get_values_partial(None, 'fr', None)
    #
    # # v = d.get_values_partial(None, 'fr', None)
    # # print(v)

    signature = pygit2.Signature(args.author_name, args.author_email)

    with gitdb.commit(signature, '[Migration] migrate from 0.3 to 0.4'):
        migrate(db, folder)

        with open(os.path.join(folder, 'version'), 'w') as fp:
            fp.write('0.4')
    # # #
    db2 = _IEMLDatabase(gitdb.folder)


    # # # #
    with gitdb.commit(signature, '[Descriptor] add missing translations for hands and feet'):
        root = script("f.o.-f.o.-',n.i.-f.i.-',x.-O:.-',_M:.-',_;+f.o.-f.o.-',n.i.-f.i.-',x.-O:.-',_E:F:.-',_;", factorize=True)
        assert str(root) == "f.o.-f.o.-',n.i.-f.i.-',x.-O:.-',_M:.+E:F:.-',_;"
        p0 =   script("f.o.-f.o.-',n.i.-f.i.-',x.-A:.-',_M:.+E:F:.-',_;")
        p1 =   script("f.o.-f.o.-',n.i.-f.i.-',x.-U:.-',_M:.+E:F:.-',_;")

        db2.add_descriptor(root, 'fr', 'translations', 'parties des mains et des pieds')
        db2.add_descriptor(root, 'en', 'translations', 'parts of hands and feet')

        db2.add_descriptor(p0, 'fr', 'translations', 'parties des pieds')
        db2.add_descriptor(p0, 'en', 'translations', 'parts of feet')

        db2.add_descriptor(p1, 'fr', 'translations', 'parties des mains')
        db2.add_descriptor(p1, 'en', 'translations', 'parts of hands')

    # ignore_body_parts(gitdb, db2)

    with gitdb.commit(signature, '[Descriptor] remove old descriptors'):
        sc = script('F:.n.-')
        db2.remove_descriptor(sc, 'fr', 'translations')
        db2.remove_descriptor(sc, 'en', 'translations')
    desc = db2.get_descriptors()
    with gitdb.commit(signature, '[Descriptor] remove Nan values'):
        for key, v in list(desc.df[desc.df.value.isna()].iterrows()):
            db2.remove_descriptor(*key, "")
            print(key, "remove")

    with gitdb.commit(signature, '[Gitignore] ignore cache'):
        with open(os.path.join(gitdb.folder, '.gitignore'), 'w') as fp:
            fp.write(".dictionary-cache.*\n")

    with gitdb.commit(signature, "[Migration] add '.ieml' file for non-root paradigms"):
        d = db2.get_dictionary()
        for s in d.scripts:
            if len(s) != 1 and s not in d.tables.roots:
                db2.add_structure(s, 'is_root', False)

    gitdb.push('origin')
    # # print(db.get_structure().df)
    # # print(len(db.list('morpheme', paradigm=True)))
    # # print(len(db.list('morpheme', paradigm=False)))
    # # print(len(db.list('polymorpheme', paradigm=False)))
    # # from pympler import asizeof
    #
    # # print(asizeof.asizeof(db2.get_dictionary()))
