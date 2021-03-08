import json
import tqdm

from ieml import error
from ieml.ieml_database import IEMLDatabase
from ieml.constants import INHIBITABLE_RELATIONS, LANGUAGES, DESCRIPTORS_CLASS
from ieml.dictionary.script import Script, factorize
from ieml.usl import USL


def append_idx_to_dict(d, idx):
    return {k: [vv + str(idx) for vv in v] for k, v in d.items()}

def _check_inhibitions(inhibitions):
    inhibitions = list(inhibitions)
    assert all(i in INHIBITABLE_RELATIONS for i in inhibitions)
    return inhibitions

def _check_script(script):
    assert isinstance(script, Script)
    assert factorize(script) == script
    return script


def _check_lexical_item(ieml):
    assert isinstance(ieml, USL)
    return ieml

def _check_ieml(ieml):
    if isinstance(ieml, Script):
        return _check_script(ieml)
    elif isinstance(ieml, USL):
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
    def __init__(self, gitdb, signature, cache_folder=None, use_cache=True):
        self.gitdb = gitdb
        self.signature = signature
        self.cache_folder = cache_folder
        self.use_cache = use_cache

    def create_root_paradigm(self, root, inhibitions, translations, comments):
        db = IEMLDatabase(folder=self.gitdb.folder, use_cache=self.use_cache, cache_folder=self.cache_folder)

        root = _check_script(root)
        if len(root) == 1:
            raise ValueError("The script is not a paradigm {}, can't use it to define a root paradigm.".format(str(root)))

        translations = _check_descriptors(translations)
        comments = _check_descriptors(comments)

        # if not already exists (no descriptor no structures)
        if db.get_descriptors().get_values_partial(root):
            raise ValueError("Script {} already exists in dictionary".format(root))

        dictionary = db.get_dictionary()
        for ss in root.singular_sequences:
            if dictionary.tables.root(ss) is not None:
                raise ValueError("Root paradigms {} intersection with script {} ".format(str(r), str(root)))

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
                    db.add_descriptor(root, language=l, descriptor='comments', value=v)

        # add main tables header
        for i, t in enumerate([tt for tt in root.tables_script if tt != root]):
            self.add_morpheme_paradigm(t,
                                       translations=append_idx_to_dict(translations, i),
                                       comments=append_idx_to_dict(comments, i))
        # main_tables = [tt for tt in root.tables_script if tt != root]

    def add_morpheme_paradigm(self,
                              script: Script,
                              translations,
                              comments):
        db = IEMLDatabase(folder=self.gitdb.folder, use_cache=self.use_cache, cache_folder=self.cache_folder)
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
            db.remove_descriptor(script)
            db.remove_structure(script)

            db.add_structure(script, 'is_root', False)

            for l in LANGUAGES:
                for v in translations[l]:
                    db.add_descriptor(script, language=l, descriptor='translations', value=v)

                for v in comments[l]:
                    db.add_descriptor(script, language=l, descriptor='comments', value=v)

    def delete_morpheme_root_paradigm(self,
                                      script: Script, empty_descriptors=True
                                      ):
        db = IEMLDatabase(folder=self.gitdb.folder, use_cache=self.use_cache, cache_folder=self.cache_folder)
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
        db = IEMLDatabase(folder=self.gitdb.folder, use_cache=self.use_cache, cache_folder=self.cache_folder)
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

        db = IEMLDatabase(folder=self.gitdb.folder, use_cache=self.use_cache, cache_folder=self.cache_folder)
        d = db.get_dictionary()
        desc = db.get_descriptors()
        ds = db.get_structure()

        assert script_old in d.scripts, "Source script not defined in dictionary"
        assert script_new not in d.scripts, "Target script already defined in dictionary"
        root_old = d.tables.root(script_old)
        is_root = ds.get_values(script_old, 'is_root')
        is_root = is_root and is_root[0][0].lower() == 't'


        root_new_cand = set()
        for ss in script_new.singular_sequences:
            try:
                root_new_cand.add(d.tables.root(ss))
            except KeyError:
                if not is_root:
                    raise ValueError("A non root paradigm is defined over singular sequences that are in no paradigms")

        assert len(root_new_cand) == 1, "No root paradigms or too many for script {}".format(str(script_new))
        root_new = next(iter(root_new_cand))

        message = "[dictionary] Update paradigm IEML from {} to {}"\
                          .format(str(script_old),
                                  str(script_new),
                                  " / ".join(
                                      "{}:{}".format(l, desc.get_values(script_new, l, 'translations')) for l in LANGUAGES))

        if is_root:
            # 1st case: root paradigm

            assert script_old in script_new, "Can only update a root paradigm to a bigger version of it"


            # then we can update it to a bigger version of it
            old_structure = ds.get_values_partial(script_old)

        # transfers translations and structure
        with self.gitdb.commit(self.signature, message):

            if is_root:
                db.remove_structure(script_old)
                db.add_structure(script_old, 'is_root', 'False')

                for (_, key), values in old_structure.items():
                    for v in values:
                        db.add_structure(script_new, key, v)
            else:
                db.remove_structure(script_old)
                db.add_structure(script_new, 'is_root', 'False')

            db.remove_descriptor(script_old)

            for (_, l, k), values in desc.get_values_partial(script_old).items():
                for v in values:
                    db.add_descriptor(script_new, l, k, v)
                    if is_root:
                        db.add_descriptor(script_old, l, k, '(translation migrated to {}) '.format(str(script_new)) + v)

    def set_descriptors(self,
                        ieml,
                        descriptor,
                        value):

        db = IEMLDatabase(folder=self.gitdb.folder, use_cache=self.use_cache, cache_folder=self.cache_folder)

        ieml = _check_ieml(ieml)
        value = _check_descriptors(value)

        desc = db.get_descriptors()
        old_trans = {l: desc.get_values(ieml=ieml, language=l, descriptor=descriptor) for l in LANGUAGES}

        if all(sorted(value[l]) == sorted(old_trans[l]) for l in LANGUAGES):
            error("No update needed, db already contains {}:{} for {}".format(descriptor, json.dumps(value), str(ieml)))
            return False

        # test if after modification there is still at least a descriptor
        if all(not (desc.get_values(ieml=ieml, language=l, descriptor=d) if d != descriptor else value[l])
               for l in LANGUAGES for d in DESCRIPTORS_CLASS):
            error('[descriptors] Remove {}'.format(str(ieml)))
            with self.gitdb.commit(self.signature, '[descriptors] Remove {}'.format(str(ieml))):
                db.remove_descriptor(ieml)
            return True
        # to_add = {l: [e for e in value[l] if e not in old_trans[l]] for l in LANGUAGES}
        # to_remove = {l: [e for e in old_trans[l] if e not in value[l]] for l in LANGUAGES}

        with self.gitdb.commit(self.signature, '[descriptors] Update {} for {} to {}'.format(descriptor,
                                                                                             str(ieml),
                                                                                             json.dumps(value))):
            db.remove_descriptor(ieml, None, descriptor)

            for l in LANGUAGES:
                for e in value[l]:
                    db.add_descriptor(ieml, l, descriptor, e)

            return True

    def set_inhibitions(self,
                        ieml,
                        inhibitions):

        db = IEMLDatabase(folder=self.gitdb.folder, use_cache=self.use_cache, cache_folder=self.cache_folder)

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


    def update_all_ieml(self, f, message: str):
        db = IEMLDatabase(folder=self.gitdb.folder, use_cache=self.use_cache, cache_folder=self.cache_folder)
        desc = db.get_descriptors()

        with self.gitdb.commit(self.signature, '[IEML migration] Update all ieml in db: {}'.format(message)):

            for old_ieml in tqdm.tqdm(db.list(parse=True), "Migrate all usls"):
                new_ieml = f(old_ieml)

                value = desc.get_values_partial(old_ieml)

                db.remove_descriptor(old_ieml, None, None)

                for l in LANGUAGES:
                    for d in value[l]:
                        for e in value[l][e]:
                            db.add_descriptor(new_ieml, l, d, e)