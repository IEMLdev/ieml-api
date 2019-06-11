import json
from itertools import product

import pygit2

from ieml.constants import LANGUAGES, INHIBITABLE_RELATIONS
from ieml.dictionary.script import Script, factorize
from ieml.ieml_database.descriptor import DESCRIPTORS_CLASS
from ieml.lexicon.syntax import LexicalItem
from scripts.migrate_versions.migrate_v03Tov04 import _IEMLDatabase


def _check_inhibitions(inhibitions):
    inhibitions = list(inhibitions)
    assert all(i in INHIBITABLE_RELATIONS for i in inhibitions)
    return inhibitions

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

def _check_descriptors(descriptor):
    if descriptor is None:
        descriptor = {}

    for k in LANGUAGES:
        if k not in descriptor:
            descriptor[k] = []

    assert all(isinstance(d, str) for k in LANGUAGES for d in descriptor[k])
    return descriptor


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


class DBTransactions:
    def __init__(self, gitdb, author_name, author_email, cache_folder, use_cache=True):
        self.gitdb = gitdb
        self.signature = pygit2.Signature(author_name, author_email)
        self.cache_folder = cache_folder
        self.use_cache = use_cache

    def create_root_paradigm(self, root, inhibitions, translations, comments):
        db = _IEMLDatabase(folder=self.gitdb.folder, use_cache=self.use_cache, cache_folder=self.cache_folder)

        root = _check_script(root)
        if len(root) == 1:
            raise ValueError("The script is not a paradigm {}, can't use it to define a root paradigm.".format(str(root)))

        translations = _check_descriptors(translations)
        comments = _check_descriptors(comments)

        # if not already exists (no descriptor no structures)
        if db.get_descriptors().get_values_partial(root):
            raise ValueError("Script {} already exists in dictionary".format(root))

        for ss in root.singular_sequences:
            try:
                r = db.get_dictionary().tables.root(ss)
                raise ValueError("Root paradigms {} intersection with script {} ".format(str(r), str(root)))
            except KeyError:
                pass

        with self.gitdb.commit(self.signature, "[dictionary] Create root paradigm {} ({}), create {} singular sequences"
                .format(str(root),
                        " / ".join("{}:{}".format(l, ', '.join(db.get_descriptors().get_values(str(root), l, 'translations'))) for l in LANGUAGES),
                        len(root.singular_sequences)),):

            db.remove_structure(root, 'is_root')
            db.add_structure(root, 'is_root', True)
            for i in _check_inhibitions(inhibitions):
                db.add_structure(root, 'inhibition', i)


            for l in LANGUAGES:
                for v in translations[l]:
                    db.add_descriptor(root, language=l, descriptor='translations', value=v)

                for v in comments[l]:
                    db.add_descriptor(root, language=l, descriptor='comment', value=v)

        # add main tables header
        # main_tables = [tt for tt in root.tables_script if tt != root]

    def add_morpheme_paradigm(self,
                              script: Script,
                              translations,
                              comments):
        db = _IEMLDatabase(folder=self.gitdb.folder, use_cache=self.use_cache, cache_folder=self.cache_folder)
        d = db.get_dictionary()

        script = _check_script(script)
        if len(script) == 1:
            raise ValueError("The script is not a paradigm {}, can't use it to define a paradigm.".format(str(script)))

        if script in d.scripts:
            raise ValueError("Script {} already defined in the dictionary".format(str(script)))

        r_cand = set()
        for ss in script.singular_sequences:
            try:
                r_cand.add(d.tables.root(ss))
            except KeyError:
                raise ValueError("No root paradigms contains this script {}".format(str(script)))

        if len(r_cand) != 1:
            raise ValueError("No root paradigms or too many for script {}".format(str(script)))

        root = next(iter(r_cand))
        descriptors = db.get_descriptors()

        message = "[dictionary] Create paradigm {} ({}) for root paradigm {} ({})"\
            .format(str(script),
                      " / ".join(
                          "{}:{}".format(l, ', '.join(descriptors.get_values(script, l, 'translations'))) for l in LANGUAGES),
                      str(root),
                      " / ".join(
                          "{}:{}".format(l, ', '.join(descriptors.get_values(root, l, 'translations'))) for l in LANGUAGES))

        with self.gitdb.commit(self.signature, message):
            db.remove_structure(script, 'is_root')
            db.add_structure(script, 'is_root', False)

            for l in LANGUAGES:
                for v in translations[l]:
                    db.add_descriptor(script, language=l, descriptor='translations', value=v)

                for v in comments[l]:
                    db.add_descriptor(script, language=l, descriptor='comment', value=v)

    def delete_morpheme_root_paradigm(self,
                                      script: Script, empty_descriptors=True
                                      ):
        db = _IEMLDatabase(folder=self.gitdb.folder, use_cache=self.use_cache, cache_folder=self.cache_folder)
        d = db.get_dictionary()
        descriptors = db.get_descriptors()

        script = _check_script(script)
        if script not in d.tables.roots:
            raise ValueError("Script {} is not a root paradigm".format(str(script)))

        message = "[dictionary] Remove root paradigm {} ({})"\
                          .format(str(script),
                                  " / ".join("{}:{}".format(l, ', '.join(descriptors.get_values(script, l, 'translations'))) for l in
                                             LANGUAGES))

        with self.gitdb.commit(self.signature, message):
            db.remove_structure(script)

            if empty_descriptors:
                for s in list(d.relations.object(script, 'contains')):
                    db.remove_descriptor(s)

    def delete_morpheme_paradigm(self,
                                 script: Script):
        db = _IEMLDatabase(folder=self.gitdb.folder, use_cache=self.use_cache, cache_folder=self.cache_folder)
        d = db.get_dictionary()
        descriptors = db.get_descriptors()

        script = _check_script(script)
        if script in d.scripts and len(script) == 1:
            raise ValueError("Script {} is not a paradigm".format(str(script)))

        root = d.tables.root(script)
        message = "[dictionary] Remove paradigm {} ({})"\
                          .format(str(script),
                                  " / ".join(
                                      "{}:{}".format(l, ', '.join(descriptors.get_values(script, l, 'translations'))) for l in LANGUAGES),
                                  str(root),
                                  " / ".join(
                                      "{}:{}".format(l, ', '.join(descriptors.get_values(root, l, 'translations'))) for l in LANGUAGES))

        with self.gitdb.commit(self.signature, message):
            db.remove_structure(script)
            db.remove_descriptor(script)


    def update_morpheme_paradigm(self,
                                 script_old: Script,
                                 script_new: Script,):
        script_old = _check_script(script_old)
        script_new = _check_script(script_new)

        if script_old == script_new:
            return

        assert len(script_old) != 1 or len(script_new) != 1, "Can't update singular sequences, only paradigms"

        db = _IEMLDatabase(folder=self.gitdb.folder, use_cache=self.use_cache, cache_folder=self.cache_folder)
        d = db.get_dictionary()
        desc = db.get_descriptors()

        assert script_old in d.scripts, "Source script not defined in dictionary"
        assert script_new not in d.scripts, "Target script already defined in dictionary"
        root_old = d.tables.root(script_old)

        message = "[dictionary] Update paradigm IEML from {} to {}"\
                          .format(str(script_old),
                                  str(script_new),
                                  " / ".join(
                                      "{}:{}".format(l, desc.get_values(script_new, l, 'translations')) for l in LANGUAGES))
        ds = db.get_structure()
        is_root = ds.get_values(script_old, 'is_root')
        if is_root and is_root[0][0].lower() == 't':
            # 1st case: root paradigm

            assert script_old in script_new, "Can only update a root paradigm to a bigger version of it"
            # then we can update it to a bigger version of it
            old_structure = ds.get_values_partial(script_old)

            root = True
        else:
            root = False

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

        # transfers translations and structure
        with self.gitdb.commit(self.signature, message):
            if root:
                db.remove_structure(script_old)

                for (_, key), values in old_structure.items():
                    for v in values:
                        db.add_structure(script_new, key, v)

            for (_, l, k), values in desc.get_values_partial(script_old).items():
                for v in values:
                    db.add_descriptor(script_new, l, k, v)

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

    def set_descriptors(self,
                        ieml,
                        descriptor,
                        value):

        db = _IEMLDatabase(folder=self.gitdb.folder, use_cache=self.use_cache, cache_folder=self.cache_folder)

        ieml = _check_ieml(ieml)
        value = _check_descriptors(value)

        desc = db.get_descriptors()
        old_trans = {l: desc.get_values(ieml=ieml, language=l, descriptor=descriptor) for l in LANGUAGES}

        if all(set(value[l]) == set(old_trans[l]) for l in LANGUAGES):
            return

        to_add = {l: [e for e in value[l] if e not in old_trans[l]] for l in LANGUAGES}
        to_remove = {l: [e for e in old_trans[l] if e not in value[l]] for l in LANGUAGES}

        with self.gitdb.commit(self.signature, '[descriptors] Update {} for {} to {}'.format(descriptor,
                                                                                             str(ieml),
                                                                                             json.dumps(value))):
            for l in LANGUAGES:
                for e in to_remove[l]:
                    db.remove_descriptor(ieml, l, descriptor, e)
                for e in to_add[l]:
                    db.add_descriptor(ieml, l, descriptor, e)

    def set_inhibitions(self,
                        ieml,
                        inhibitions):

        db = _IEMLDatabase(folder=self.gitdb.folder, use_cache=self.use_cache, cache_folder=self.cache_folder)

        ieml = _check_ieml(ieml)
        assert db.get_dictionary().tables.root(ieml) == ieml

        inhibitions = _check_inhibitions(inhibitions)

        ds = db.get_structure()
        old_inhib = ds.get_values(ieml, 'inhibition')

        if set(old_inhib) == set(inhibitions):
            return

        to_remove = [e for e in old_inhib if e not in inhibitions]
        to_add = [e for e in inhibitions if e not in old_inhib]

        with self.gitdb.commit(self.signature, '[inhibitions] Update inhibitions for {} to {}'.format(str(ieml),
                                                                                             json.dumps(inhibitions))):
            for e in to_add:
                db.add_structure(ieml, 'inhibition', e)

            for e in to_remove:
                db.remove_structure(ieml, 'inhibition', e)
