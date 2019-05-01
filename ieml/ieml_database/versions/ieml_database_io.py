from ieml.dictionary.script import Script
from ieml.ieml_database.db_interface import IEMLDBInterface
from ...commons import FolderWatcherCache
from ...dictionary import Dictionary

import logging
logger = logging.getLogger("IEMLDatabaseIO")
logger.setLevel(logging.INFO)

from typing import Dict, List

import os

ScriptDescription = Dict
RootScriptDescription = Dict

class IEMLDatabaseIOMeta(type):
    versions_map = {}

    def __new__(cls, name, bases, dct):
        klass = type.__new__(cls, name, bases, dct)

        if klass.version:
            cls.versions_map[klass.version] = klass
        return klass


class IEMLDatabaseIO(metaclass=IEMLDatabaseIOMeta):
    version = None

    # @staticmethod
    # def from_version(version):
    #     return IEMLDatabaseIO.__class__.

    @staticmethod
    def _get_dictionary_files(db_folder):
        raise NotImplementedError

    @staticmethod
    def _get_descriptors_files(db_folder):
        raise NotImplementedError

    @classmethod
    def _get_cache_descriptors(cls, db_folder, cache_folder):
        cache = FolderWatcherCache(cls._get_descriptors_files(db_folder), cache_folder=cache_folder, name="descriptor")
        if not cache.is_pruned():
            logger.info("read_descriptor.cache: Reading cache at {}".format(cache.cache_file))

            # print("Dictionary.load: Reading cache at {}".format(cache.cache_file), file=sys.stderr)
            try:
                return cache.get()
            except Exception:
                # cache.prune()
                pass

        logger.info("read_descriptor.cache: Pruned cache at {}".format(cache_folder))
        return None

    @classmethod
    def _get_cache_dictionary(cls, db_folder, cache_folder):
        cache = FolderWatcherCache(cls._get_dictionary_files(db_folder), cache_folder=cache_folder, name="dictionary")
        if not cache.is_pruned():
            logger.info("read_dictionary.cache: Reading cache at {}".format(cache.cache_file))

            # print("Dictionary.load: Reading cache at {}".format(cache.cache_file), file=sys.stderr)
            try:
                return cache.get()
            except Exception:
                # cache.prune()
                pass

        logger.info("read_dictionary.cache: Pruned cache at {}".format(cache_folder))
        return None


    @classmethod
    def _save_cache_descriptors(cls, db_folder, cache_folder, descriptor):
        cache = FolderWatcherCache(cls._get_dictionary_files(db_folder), cache_folder=cache_folder, name='descriptor')

        logger.info("read_descriptor.cache: Updating cache at {}".format(cache.cache_file))
        cache.update(descriptor)

    @classmethod
    def _save_cache_dictionary(cls, db_folder, cache_folder, dictionary):
        cache = FolderWatcherCache(cls._get_dictionary_files(db_folder), cache_folder=cache_folder, name='dictionary')

        logger.info("read_dictionary.cache: Updating cache at {}".format(cache.cache_file))
        cache.update(dictionary)

    @staticmethod
    def _do_read_descriptors(dic_folder):
        raise NotImplementedError

    @staticmethod
    def _do_read_dictionary(dic_folder):
        raise NotImplementedError

    @staticmethod
    def _do_read_lexicon(folder):
        raise NotImplementedError

    @staticmethod
    def _do_save_dictionary(db_folder, dictionary: Dictionary):
        raise NotImplementedError

    @classmethod
    def _check_folder(cls, folder):
        files = os.listdir(folder)
        assert 'dictionary' in files and os.path.isdir(os.path.join(folder, 'dictionary'))
        assert 'lexicons' in files and os.path.isdir(os.path.join(folder, 'lexicons'))
        assert 'version' in files

        with open(os.path.join(folder, 'version')) as fp:
            version = fp.read().strip()
            assert version == cls.version, "IEML Database version unsupported {} at {}".format(version, folder)

    @classmethod
    def read_descriptors(cls, db_folder, cache_folder=None):
        cls._check_folder(db_folder)

        if cache_folder:
            dictionary = cls._get_cache_descriptors(db_folder, cache_folder)
            if dictionary:
                return dictionary

        logger.info("read_descriptors: Reading descriptors at {}".format(db_folder))
        descriptors = cls._do_read_descriptors(db_folder)
        logger.info("read_descriptors: Read {} languages, {} translations and {} comments"
                    .format(len(descriptors.translations),
                            sum(map(len, descriptors.translations.values())),
                            sum(map(len, descriptors.comments.values()))))

        if cache_folder:
            cls._save_cache_descriptors(db_folder, cache_folder, descriptors)

        return descriptors


    @classmethod
    def read_dictionary(cls, db_folder, cache_folder=None):
        cls._check_folder(db_folder)

        if cache_folder:
            dictionary = cls._get_cache_dictionary(db_folder, cache_folder)
            if dictionary:
                return dictionary

        logger.info("read_dictionary: Reading dictionary at {}".format(db_folder))
        scripts, roots, inhibitions = cls._do_read_dictionary(db_folder)

        # n_p = sum(1 if s.cardinal != 1 else 0 for s in scripts) - len(roots)
        # n_ss = len(scripts) - n_p - len(roots)
        logger.info("read_dictionary: Read {} root paradigms".format(len(roots)))

        dictionary = Dictionary(scripts=scripts,
                                 # translations=translations,
                                 root_paradigms=roots,
                                 inhibitions=inhibitions,)
                                 # comments=comments)
        if cache_folder:
            cls._save_cache_dictionary(db_folder, cache_folder, dictionary)

        return dictionary

    @classmethod
    def read_lexicon(cls, folder):
        cls._check_folder(folder)
        return cls._do_read_lexicon(os.path.join(folder, 'lexicon'))

    @classmethod
    def write_morpheme_root_paradigm(cls,
                                     db_folder:str,
                                     root_description: RootScriptDescription,
                                     ss_description: List[ScriptDescription],
                                     p_description: List[ScriptDescription]):

        raise NotImplementedError

    @classmethod
    def delete_morpheme_root_paradigm(cls, db_folder:str, root_description: RootScriptDescription):
        raise NotImplementedError

    @classmethod
    def update_morpheme_translation(cls, db_folder:str, root:RootScriptDescription, script: ScriptDescription):
        raise NotImplementedError


    @classmethod
    def update_morpheme_comments(cls, db_folder:str, root:RootScriptDescription, script: ScriptDescription):
        raise NotImplementedError


def IEMLDatabaseIO_factory(db_folder) -> IEMLDatabaseIO:
    with open(os.path.join(db_folder, 'version')) as fp:
        version = fp.read().strip()

    try:
        return IEMLDatabaseIOMeta.versions_map[version]
    except KeyError:
        err = "IEMLDatabaseIOFactory: Unsupported IEMLDb version {} at {}".format(version, db_folder)
        logger.error(err)
        raise ValueError(err)