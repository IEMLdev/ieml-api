import functools
import hashlib
import json
import os
import traceback
from itertools import product
from time import time
from typing import List, Dict

from appdirs import user_cache_dir

from ieml.commons import FolderWatcherCache
from ieml.constants import IEMLDB_DEFAULT_GIT_ADDRESS, LIBRARY_VERSION, LANGUAGES, INHIBITABLE_RELATIONS
import pygit2
import logging

from ieml.dictionary import Dictionary
from ieml.dictionary.script import Script, factorize
from ieml.ieml_database.descriptor import DescriptorSet, DESCRIPTORS_CLASS
from ieml.ieml_database.dictionary_structure import DictionaryStructure
# from ieml.ieml_database.versions import IEMLDatabaseIO_factory
# from ieml.ieml_database.versions.ieml_database_io import ScriptDescription
from ieml.ieml_database.lexicon.lexicon_descriptor import LexiconDescriptorSet
from ieml.ieml_database.lexicon.lexicon_structure import LexiconStructure
from ieml.lexicon import Lexicon
from ieml.lexicon.syntax import LexicalItem

logger = logging.getLogger("IEMLDatabase")

Inhibitions = List[str]
Translations = Comments = Dict[str, List[str]]

def monitor_decorator(name):
    def decorator(f):
        def wrapper(*args, **kwargs):
            before = time()
            res = f(*args, **kwargs)
            print(name, time() - before)
            return res

        functools.wraps(wrapper)
        return wrapper

    return decorator



def init_remote(repo, name, url):
    remote = repo.remotes.create(name, url)
    mirror_var = "remote.{}.mirror".format(name)
    repo.config[mirror_var] = True
    return remote


def _check_script(script):
    assert isinstance(script, Script)
    assert factorize(script) == script
    return script

def _check_lexical_item(ieml):
    assert isinstance(ieml, LexicalItem)
    return ieml


def _check_ieml(ieml):
    if isinstance(ieml, Script):
        return _check_script(ieml)
    elif isinstance(ieml, LexicalItem):
        return _check_lexical_item(ieml)
    else:
        assert False, "Invalid ieml {}".format(ieml)


def _check_inhibitions(inhibitions):
    inhibitions = list(inhibitions)
    assert all(i in INHIBITABLE_RELATIONS for i in inhibitions)
    return inhibitions

def _check_multi_descriptors(descriptor):
    if descriptor is None:
        descriptor = {}

    for k in LANGUAGES:
        if k not in descriptor:
            descriptor[k] = {}

        for d in DESCRIPTORS_CLASS:
            if d not in descriptor[k]:
                descriptor[k][d] = []

    assert all(l in LANGUAGES for l in descriptor)
    assert all(k in DESCRIPTORS_CLASS and isinstance(descriptor[l][k], list) and
               all(isinstance(v, str) for v in descriptor[l][k])
               for l in descriptor for k in descriptor[l])
    return descriptor


def _check_descriptors(descriptor):
    if descriptor is None:
        descriptor = {}

    for k in LANGUAGES:
        if k not in descriptor:
            descriptor[k] = []

    assert all(isinstance(d, str) for k in LANGUAGES for d in descriptor[k])
    return descriptor


def cache_results_watch_files(_files, name):
    def decorator(f):
        def wrapper(*args, **kwargs):
            use_cache = args[0].use_cache
            self = args[0]
            cache_folder = self.cache_folder
            db_path = self.folder

            files = [os.path.join(db_path, ff) for ff in _files]

            if use_cache:
                cache = FolderWatcherCache(files, cache_folder=cache_folder, name=name)
                if not cache.is_pruned():
                    logger.info("read_{}.cache: Reading cache at {}".format(name, cache.cache_file))
                    try:
                        instance = cache.get()
                    except Exception:
                        # cache.prune()
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


class IEMLDatabase:
    # descriptor_dictionary_file = 'dictionary/descriptors'
    structure_dictionary_file = 'structure/dictionary'
    descriptors_folder = 'descriptors'
    structure_lexicon_folder = 'structure/lexicons'


    def __init__(self,
                 git_address=IEMLDB_DEFAULT_GIT_ADDRESS,
                 credentials=None,
                 branch='master',
                 commit_id=None,
                 db_folder=None,
                 cache_folder=None,
                 use_cache=True):

        self.git_address = git_address
        self.credentials = credentials
        self.branch = branch
        self.commit_id = commit_id


        if db_folder:
            self.folder = os.path.abspath(db_folder)
        else:
            self.folder = os.path.join(user_cache_dir(appname='ieml', appauthor=False, version=LIBRARY_VERSION),
                                       hashlib.md5("{}/{}".format(git_address, branch).encode('utf8')).hexdigest())

        self.use_cache = use_cache
        self.cache_folder = cache_folder
        if self.use_cache:
            if cache_folder is None:
                self.cache_folder = self.folder
        else:
            self.cache_folder = None

        # download database
        self.update()

    @monitor_decorator("Save DB")
    def save_changes(self, author_name, author_mail, message,
                     to_add=(), to_remove=(), check_coherency=True,
                     push_username=None,
                     push_password=None):
        """
        Files are already modified on disk
        :param author_name:
        :param author_mail:
        :param message:
        :param to_add:
        :param to_remove:
        :return:
        """

        if check_coherency:
            try:
                self.dictionary()
            except ValueError as e:
                # roll back
                self.repo.reset(self.commit_id, pygit2.GIT_RESET_HARD)
                raise e

        self.update()
        old_commit = self.commit_id
        try:

            self.commit_files(author_name=author_name,
                              author_mail=author_mail,
                              message=message,
                              to_add=to_add,
                              to_remove=to_remove)
            self.update()

            if push_password is not None and push_username is not None:
                self.push(push_username, push_password)

        except Exception as e:
            traceback.print_exc()
            self.reset(old_commit)
            raise e

        for f in to_remove:
            os.remove(os.path.join(self.folder, f))

    def commit_files(self,
                     author_name,
                     author_mail,
                     message,
                     to_add=(),
                     to_remove=()):
        if not to_add and not to_remove:
            return

        repo = pygit2.Repository(self.folder)

        index = repo.index

        # index.read()
        for f in to_add:
            index.add(f)
        #
        for f in to_remove:
            index.remove(f)
        index.write()

        tree = index.write_tree()

        author = pygit2.Signature(author_name, author_mail)

        oid = repo.create_commit('refs/heads/{}'.format(self.branch),
                                 author,
                                 author,
                                 message,
                                 tree,
                                 [repo.head.peel().hex])

        self.commit_id = oid.hex

    def reset(self, commit_id):
        repo = pygit2.Repository(self.folder)
        repo.reset(commit_id, pygit2.GIT_RESET_HARD)

    def update(self, remote_name='origin'):
        if not os.path.exists(self.folder):
            callbacks = pygit2.RemoteCallbacks(credentials=self.credentials)
            repo = pygit2.clone_repository(self.git_address, self.folder, remote=init_remote, checkout_branch=self.branch, callbacks=callbacks)
        else:
            repo = pygit2.Repository(self.folder)

        if self.commit_id is None:
            # use most recent of remote
            remote = [r for r in repo.remotes if r.name == remote_name][0]
            remote.fetch(callbacks=pygit2.RemoteCallbacks(credentials=self.credentials))
            self.commit_id = repo.lookup_reference('refs/remotes/origin/{}'.format(self.branch)).target
            # self.commit_id = repo.lookup_reference('refs/heads/{}'.format(self.branch)).target

        # try:
        merge_result, _ = repo.merge_analysis(self.commit_id)
        # except TypeError as e:
        #     raise e

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

    def push(self, github_username=None, github_password=None,
                   public_key=None, private_key=None,
             remote='origin'):
        repo = pygit2.Repository(self.folder)

        if github_username is not None and github_password is not None:
            credentials = pygit2.UserPass(github_username, github_password)
        else:
            credentials = self.credentials

        remote = repo.remotes[remote]
        callbacks = pygit2.RemoteCallbacks(credentials=credentials)
        remote.push(['refs/heads/{}'.format(self.branch)], callbacks=callbacks)


    # def descriptors(self):
    #     desc = DescriptorSet.from_folder(os.path.join(self.folder, IEMLDatabase.descriptor_dictionary_file))
    #     return desc

    def dictionary_structure(self):
        return DictionaryStructure.from_file(os.path.join(self.folder, IEMLDatabase.structure_dictionary_file))

    @monitor_decorator("Build dictionary")
    @cache_results_watch_files([structure_dictionary_file], 'dictionary_structure')
    def dictionary(self, use_cache=True):
        return Dictionary(self.dictionary_structure())

    # def lexicon(self):
    #     lexicon_path = os.path.join(self.folder, 'lexicon')
    #     return Lexicon.load(lexicon_path)
    @monitor_decorator("Build descriptors")
    def descriptors(self):
        return LexiconDescriptorSet.from_folder(self.folder)

    def lexicon_structure(self, domains):
        assert 'descriptors' not in domains
        return LexiconStructure.from_folder(os.path.join(self.folder, self.structure_lexicon_folder), domains)

    @monitor_decorator("Build Lexicon")
    def lexicon(self, domains):
        if domains == 'all':
            domains = [f for f in os.listdir(os.path.join(self.folder, self.structure_lexicon_folder)) if f != 'descriptors']
        return Lexicon(self.lexicon_structure(domains), dictionary=self.dictionary(), descriptors=self.descriptors())

    @property
    def repo(self):
        return pygit2.Repository(self.folder)

    def get_version(self):
        return self.branch, self.commit_id

    def set_version(self, branch, commit_id):
        self.branch = branch
        self.commit_id = commit_id
        self.update()

    @monitor_decorator("create_morpheme_root_paradigm")
    def create_morpheme_root_paradigm(self,
                                      script: Script,
                                      author_name: str,
                                      author_mail: str,
                                      inhibitions: Inhibitions = (),
                                      push_username=None,
                                      push_password=None):

        inhibitions = _check_inhibitions(inhibitions)
        script = _check_script(script)

        ds = self.dictionary_structure()
        d = self.dictionary()

        try:
            ds.get(script)
            raise ValueError("Script {} already exists in dictionary".format(script))
        except KeyError:
            pass

        for ss in script.singular_sequences:
            try:
                r = d.tables.root(ss)
                raise ValueError("Root paradigms {} intersection with script {} ".format(str(r), str(script)))
            except KeyError:
                pass

        main_tables = [tt for tt in script.tables_script if tt != script]

        ds.set_value(script, main_tables, inhibitions)

        file = os.path.join(self.folder, 'structure/dictionary')
        ds.write_to_file(file)

        descriptors = self.descriptors()

        self.save_changes(author_name, author_mail,
                          "[dictionary] Create root paradigm {} ({}), create {} singular sequences and {} "
                          "paradigms.".format(str(script),
                                              " / ".join("{}:{}".format(l, descriptors.get(str(script), l, 'translations')) for l in LANGUAGES),
                                              len(script.singular_sequences),
                                              len(main_tables)),
                          to_add=[IEMLDatabase.structure_dictionary_file],
                          push_username=push_username,
                          push_password=push_password)

    @monitor_decorator("add_morpheme_paradigm")
    def add_morpheme_paradigm(self,
                              script: Script,
                              author_name: str,
                              author_mail: str,
                              push_username=None,
                              push_password=None):
        d = self.dictionary()

        r_cand = set()
        for ss in script.singular_sequences:
            try:
                r_cand.add(d.tables.root(ss))
            except KeyError:
                raise ValueError("No root paradigms contains this script {}".format(str(script)))

        assert len(r_cand) == 1, "No root paradigms or too many for script {}".format(str(script))

        root = next(iter(r_cand))

        script = _check_script(script)
        assert script not in d.scripts, "Script {} already defined in the dictionary".format(str(script))

        ds = self.dictionary_structure()
        para, inhib = ds.get(root)
        para = sorted(set(para) | {str(script)})
        ds.set_value(root, para, inhib)

        file = os.path.join(self.folder, 'structure/dictionary')
        ds.write_to_file(file)

        descriptors = self.descriptors()

        self.save_changes(author_name, author_mail,
                          "[dictionary] Create paradigm {} ({}) for root paradigm {} ({})"
                          .format(str(script),
                                  " / ".join("{}:{}".format(l,descriptors.get(script,l,'translations')) for l in LANGUAGES),
                                  str(root),
                                  " / ".join("{}:{}".format(l, descriptors.get(root,l,'translations')) for l in LANGUAGES)),
                          to_add=[IEMLDatabase.structure_dictionary_file],
                          push_username=push_username,
                          push_password=push_password)

    @monitor_decorator("delete_morpheme_root_paradigm")
    def delete_morpheme_root_paradigm(self,
                                      script: Script,
                                      author_name: str,
                                      author_mail: str,
                                      push_username=None,
                                      push_password=None):
        script = _check_script(script)
        d = self.dictionary()
        assert script in d.tables.roots

        ds = self.dictionary_structure()
        try:
            _ = ds.get(script)
        except KeyError as e:
            return
            # raise e

        ds.structure.drop([str(script)], inplace=True)

        file = os.path.join(self.folder, 'structure/dictionary')
        ds.write_to_file(file)

        descriptors = self.descriptors()

        self.save_changes(author_name, author_mail,
                          "[dictionary] Remove root paradigm {} ({})"
                          .format(str(script),
                                  " / ".join("{}:{}".format(l, descriptors.get(script, l, 'translations')) for l in LANGUAGES)),
                          to_add=[IEMLDatabase.structure_dictionary_file],
                          push_username=push_username,
                          push_password=push_password)


    @monitor_decorator("delete_morpheme_paradigm")
    def delete_morpheme_paradigm(self,
                                 script: Script,
                                 author_name: str,
                                 author_mail: str,
                                 push_username=None,
                                 push_password=None):
        d = self.dictionary()
        # files, root = self._do_delete_paradigm(script)

        script = _check_script(script)
        assert script in d.scripts and len(script) != 1

        root = d.tables.root(script)

        ds = self.dictionary_structure()
        paradigms, inhibitions = ds.get(root)
        # assert script in root_def.paradigms

        paradigms = sorted(set(paradigms) - {str(script)})
        ds.set_value(root, paradigms, inhibitions)

        file = os.path.join(self.folder, 'structure/dictionary')

        ds.write_to_file(file)

        # files = self.iemldb_io.delete_morpheme_root_paradigm(self.folder,
        #                                                      get_root_script_description(d,script))
        descriptors = self.descriptors()

        self.save_changes(author_name, author_mail,
                          "[dictionary] Remove paradigm {} ({}) from root paradigm {} ({})"
                          .format(str(script),
                                  " / ".join("{}:{}".format(l,descriptors.get(script, l, 'translations')) for l in LANGUAGES),
                                  str(root),
                                  " / ".join("{}:{}".format(l, descriptors.get(root, l ,'translations')) for l in LANGUAGES)),
                          to_add=[IEMLDatabase.structure_dictionary_file],
                          push_username=push_username,
                          push_password=push_password)

    # @monitor_decorator("Set morpheme translations")
    # def set_morpheme_translation(self,
    #                              script: Script,
    #                              translations: Translations,
    #                              author_name: str,
    #                              author_mail: str,
    #                              push_username=None,
    #                              push_password=None):
    #
    #     script = _check_script(script)
    #
    #     translation = _check_descriptors(translations)
    #
    #     desc = self.descriptors()
    #
    #     if all(translation[l] == desc.get(script, l, 'translations') for l in LANGUAGES):
    #         return
    #
    #     old_trans = {l: desc.get(script=script, language=l, descriptor='translations') for l in LANGUAGES}
    #
    #     for l in LANGUAGES:
    #         desc.set_value(script, descriptor='translations', language=l, values=translations[l])
    #
    #     desc.write_to_file(os.path.join(self.folder, desc.file[0]))
    #
    #     self.save_changes(author_name, author_mail,
    #                       "[dictionary] Update translation for {} ({}) to ({})"
    #                       .format(str(script),
    #                               " / ".join("{}:{}".format(l,old_trans[l]) for l in LANGUAGES),
    #                               " / ".join("{}:{}".format(l,translation[l]) for l in LANGUAGES)),
    #                       to_add=[IEMLDatabase.descriptor_dictionary_file],
    #                       check_coherency=False,
    #                       push_username=push_username,
    #                       push_password=push_password)
    #
    # @monitor_decorator("set_morpheme_comments")
    # def set_morpheme_comments(self, script: Script,
    #                                 comments: Comments,
    #                                 author_name: str,
    #                                 author_mail: str,
    #                                 push_username=None,
    #                                 push_password=None):
    #
    #     script = _check_script(script)
    #
    #     comments = _check_descriptors(comments)
    #     desc = self.descriptors()
    #
    #     if all(comments[l] == desc.get(script, l, 'comments') for l in LANGUAGES):
    #         return
    #
    #     old_com = {l: desc.get(script=script, language=l, descriptor='comments') for l in LANGUAGES}
    #
    #     for l in LANGUAGES:
    #         desc.set_value(script, descriptor='comments', language=l, values=comments[l])
    #
    #     desc.write_to_file(os.path.join(self.folder, desc.file[0]))
    #
    #     self.save_changes(author_name, author_mail,
    #                       "[dictionary] Update comments for {} ({}) to ({})"
    #                       .format(str(script),
    #                               " / ".join("{}:{}".format(l,old_com[l]) for l in LANGUAGES),
    #                               " / ".join("{}:{}".format(l,comments[l]) for l in LANGUAGES)),
    #                       to_add=[IEMLDatabase.descriptor_dictionary_file],
    #                       push_username=push_username,
    #                       push_password=push_password)

    @monitor_decorator("set_root_morpheme_inhibitions")
    def set_root_morpheme_inhibitions(self,
                                      script: Script,
                                      inhibitions: Inhibitions,
                                      author_name: str,
                                      author_mail: str,
                                      push_username=None,
                                      push_password=None):
        d = self.dictionary()
        script = _check_script(script)
        inhibitions = _check_inhibitions(inhibitions)

        assert d.tables.root(script) == script

        ds = self.dictionary_structure()
        para, _inhib_old = ds.get(script)

        if _inhib_old == inhibitions:
            return

        ds.set_value(script, para, inhibitions)

        ds.write_to_file(os.path.join(self.folder, ds.file[0]))
        self.save_changes(author_name, author_mail,
                          "[dictionary] Update comments for {} [{}] to [{}]"
                          .format(str(script),
                                  ', '.join(_inhib_old),
                                  ', '.join(inhibitions)),
                          to_add=[IEMLDatabase.structure_dictionary_file],
                          push_username=push_username,
                          push_password=push_password)



    @monitor_decorator("update_morpheme_paradigm")
    def update_morpheme_paradigm(self,
                                 script_old: Script,
                                 script_new: Script,
                                 author_name: str,
                                 author_mail: str,
                                 push_username=None,
                                 push_password=None):
        script_old = _check_script(script_old)
        script_new = _check_script(script_new)

        if script_old == script_new:
            return

        assert len(script_old) != 1 or len(script_new) != 1, "Can't update singular sequences, only paradigms"

        d = self.dictionary()

        assert script_old in d.scripts, "Source script not defined in dictionary"
        assert script_new not in d.scripts, "Target script already defined in dictionary"
        root_old = d.tables.root(script_old)
        # root_new = d.tables.root(script_new)

        ds = self.dictionary_structure()
        try:
            # 1st case: root paradigm
            para, inhib = ds.get(script_old)
            root_new = root_old
            # then we can update it to a bigger version of it
            assert script_old in script_new, "Can only update a root paradigm to a bigger version of it"

            ds.structure.drop([str(script_old)], inplace=True)
            ds.set_value(script_new, para, inhib)
        except KeyError:
            # 2nd case paradigm
            root_new_cand = set()
            for ss in script_new.singular_sequences:
                root_new_cand.add(d.tables.root(ss))
            assert len(root_new_cand) == 1, "No root paradigms or too many for script {}".format(str(script_new))
            root_new = next(iter(root_new_cand))

            para_old, inhib_old = ds.get(root_old)
            assert str(script_old) in para_old

            if root_old == root_new:
                para_old = sorted(set(para_old) - {str(script_old)} | {str(script_new)})
                ds.set_value(root_old, para_old, inhib_old)
            else:
                para_old = sorted(set(para_old) - {str(script_old)})
                ds.set_value(root_old, para_old, inhib_old)

                para_new, inhib_new = ds.get(root_new)
                para_new = sorted(set(para_new) | {str(script_new)})
                ds.set_value(root_new, para_new, inhib_new)

        desc = self.descriptors()
        # transfers translations
        for l, k in product(LANGUAGES, DESCRIPTORS_CLASS):
            desc.set_value(script=script_new,
                           language=l,
                           descriptor=k,
                           values=desc.get(script=script_old,
                                           language=l,
                                           descriptor=k))

        ds_file = os.path.join(self.folder, ds.file[0])
        ds.write_to_file(ds_file)

        desc_file = os.path.join(self.folder, desc.file[0])
        desc.write_to_file(desc_file)

        self.save_changes(author_name, author_mail,
                          "[dictionary] Update paradigm IEML from {} to {} ({}),"
                          " from root paradigm {} ({}) to {} ({})"
                          .format(str(script_old),
                                  str(script_new),
                                  " / ".join("{}:{}".format(l,desc.get(script_new, l, 'translations')) for l in LANGUAGES),
                                  str(root_old),
                                  " / ".join("{}:{}".format(l, desc.get(root_old, l, 'translations')) for l in LANGUAGES),
                                  str(root_new),
                                  " / ".join("{}:{}".format(l, desc.get(root_new, l, 'translations')) for l in LANGUAGES)),
                          to_add=[IEMLDatabase.structure_dictionary_file, IEMLDatabase.descriptor_dictionary_file],
                          push_username=push_username,
                          push_password=push_password)


    @monitor_decorator("create_lexical_paradigm")
    def create_lexical_paradigm(self,
                                lexeme,
                                domain,
                                author_name: str,
                                author_mail: str,
                                 push_username=None,
                                 push_password=None):

        assert isinstance(lexeme, LexicalItem) and len(lexeme) != 1

        lex = self.lexicon_structure('all')
        lex.add_paradigm(paradigm=lexeme, domain=domain)

        lex.write_to_folder(self.folder)

        self.save_changes(author_name, author_mail,
                          "[lexicon] Create paradigm {}"
                          .format(str(lexeme)),

                          to_add=[self.structure_lexicon_folder + '/' + domain],
                          push_username=push_username,
                          push_password=push_password)

    def set_translation(self,
                        ieml,
                        translations: Translations,
                        author_name: str,
                        author_mail: str,
                        push_username=None,
                        push_password=None):

        ieml = _check_ieml(ieml)

        translation = _check_descriptors(translations)

        desc = self.descriptors()

        if all(translation[l] == desc.get(ieml, l, 'translations') for l in LANGUAGES):
            return

        old_trans = {l: desc.get(ieml=ieml, language=l, descriptor='translations') for l in LANGUAGES}

        for l in LANGUAGES:
            desc.set_value(ieml, descriptor='translations', language=l, values=translations[l])

        desc.write_to_folder(self.folder)

        self.save_changes(author_name, author_mail,
                          "[descriptors] Update translation for {} ({}) to ({})"
                          .format(str(ieml),
                                  " / ".join("{}:{}".format(l,old_trans[l]) for l in LANGUAGES),
                                  " / ".join("{}:{}".format(l,translation[l]) for l in LANGUAGES)),
                          to_add=desc.get_files(),
                          check_coherency=False,
                          push_username=push_username,
                          push_password=push_password)


    def set_comments(self,
                     ieml,
                     comments: Comments,
                     author_name: str,
                     author_mail: str,
                     push_username=None,
                     push_password=None):

        ieml = _check_ieml(ieml)

        comments = _check_descriptors(comments)

        desc = self.descriptors()

        if all(comments[l] == desc.get(ieml, l, 'comments') for l in LANGUAGES):
            return

        old_trans = {l: desc.get(ieml=ieml, language=l, descriptor='comments') for l in LANGUAGES}

        for l in LANGUAGES:
            desc.set_value(ieml, descriptor='comments', language=l, values=comments[l])

        desc.write_to_folder(self.folder)

        self.save_changes(author_name, author_mail,
                          "[descriptors] Update comments for {} ({}) to ({})"
                          .format(str(ieml),
                                  " / ".join("{}:{}".format(l,old_trans[l]) for l in LANGUAGES),
                                  " / ".join("{}:{}".format(l,comments[l]) for l in LANGUAGES)),
                          to_add=desc.get_files(),
                          check_coherency=False,
                          push_username=push_username,
                          push_password=push_password)



    def set_descriptors(self,
                         ieml,
                         descriptors,
                         author_name: str,
                         author_mail: str,
                         push_username=None,
                         push_password=None):

        ieml = _check_ieml(ieml)

        descriptors = _check_multi_descriptors(descriptors)

        desc = self.descriptors()

        if all(descriptors[l][d] == desc.get(ieml, l, d) for l in LANGUAGES for d in DESCRIPTORS_CLASS):
            return

        # old_trans = {l: desc.get(ieml=ieml, language=l, descriptor='comments') for l in LANGUAGES}
        for d in DESCRIPTORS_CLASS:
            for l in LANGUAGES:
                desc.set_value(ieml, descriptor=d, language=l, values=descriptors[l][d])

        desc.write_to_folder(self.folder)

        self.save_changes(author_name, author_mail,
                          "[descriptors] Update descriptors for {} to {}"
                          .format(str(ieml), json.dumps(descriptors)),
                          to_add=desc.get_files(),
                          check_coherency=False,
                          push_username=push_username,
                          push_password=push_password)