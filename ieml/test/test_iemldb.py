import unittest

from ieml import IEMLDatabase
from ieml.constants import LANGUAGES
from ieml.dictionary.script import script
import shutil, os

class IEMLDBTest(unittest.TestCase):
    DB_FOLDER='test_dbfolder'
    def setUp(self):
        if os.path.isdir(self.DB_FOLDER):
            shutil.rmtree(self.DB_FOLDER)
        self.db = IEMLDatabase(db_folder=self.DB_FOLDER)

    def test_factorised(self):
        dic = self.db.dictionary()


        _scripts = set(map(lambda s: script(s, factorize=True),map(lambda s: script(s, factorize=True), dic.scripts)))

        for s in dic.scripts:
            assert s in _scripts, str(s)

        for r in dic.tables.roots:
            assert r in _scripts, str(r)


    def test_change_versions(self):
        db = IEMLDatabase()
        v0 = ('master', '650f67dffc616df52d2e3440c2fc4b8cb655cf41')
        v1 = ('master', '58a3bb44f7f33752a84e0dbfdb7ebadc6a7ea8d9')
        db.set_version(*v1)
        self.assertEqual(db.get_version(), v1)

        db.set_version(*v0)
        self.assertEqual(db.get_version(), v0)

    def test_edition(self):
        sc = script('O:O:O:.')
        translations = {'fr': ['test-fr', 'second descripteur'],'en':['test-en', 'second descriptor']}
        comments = {'fr': ['fr-c'], 'en': ['en-c']}
        inhibitions = ['father_substance', 'crossed']
        author_mail = 'test@test.st'
        author_name = 'testor'

        version0 = self.db.get_version()

        self.db.create_morpheme_root_paradigm(script=sc,
                                         # translations=translations,
                                         # comments=comments,
                                         inhibitions=inhibitions,
                                         author_mail=author_mail,
                                         author_name=author_name)


        self.db.set_morpheme_translation(script=sc,
                                         translations=translations,
                                         # comments=comments,
                                         # inhibitions=inhibitions,
                                         author_mail=author_mail,
                                         author_name=author_name)

        self.db.set_morpheme_comments(script=sc,
                                         # translations=translations,
                                         comments=comments,
                                         # inhibitions=inhibitions,
                                         author_mail=author_mail,
                                         author_name=author_name)

        version1 = self.db.get_version()
        assert version0 != version1

        d = self.db.dictionary()
        assert sc in d.scripts
        assert sc in d.tables.roots
        for ss in sc.singular_sequences:
            assert ss in d.scripts
            assert d.tables.root(ss) == sc

        t0 = script('O:O:U:.')
        t1 = script('O:O:A:.')

        assert t0 in d.scripts
        assert d.tables.root(t0) == sc

        assert t1 in d.scripts
        assert d.tables.root(t1) == sc

        assert dict(zip(d.translations[sc]._fields, d.translations[sc])) == translations
        assert dict(zip(d.comments[sc]._fields, d.comments[sc])) == comments

        with self.assertRaises(ValueError):
            self.db.create_morpheme_root_paradigm(script=sc,
                                                 # translations=translations,
                                                 # comments=comments,
                                                 inhibitions=inhibitions,
                                                 author_mail=author_mail,
                                                 author_name=author_name)


        v = self.db.get_version()
        assert v == version1

        with self.assertRaises(ValueError):
            self.db.add_morpheme_paradigm(sc,
                                          # translations=translations,
                                          author_mail=author_mail,
                                          author_name=author_name)

        v = self.db.get_version()
        assert v == version1

        trans = lambda i, e: {l: str(p) + ' ' + str(i) + l for l in LANGUAGES}
        # add paradigms
        para = [script('O:A:A:.'), script('O:A:U:.')]
        para_m = [script('O:U:A:.'), script('O:U:U:.')]


        for i, p in enumerate(para):
            self.db.add_morpheme_paradigm(p,
                                          # translations=trans(i, p),
                                          author_mail=author_mail,
                                          author_name=author_name)
            self.db.set_morpheme_translation(script=p, translations=trans(i, p),
                                             author_mail=author_mail,
                                             author_name=author_name)
        version0 = self.db.get_version()
        assert version1 != version0
        d = self.db.dictionary()

        for i, p in enumerate(para):
            assert p in d.scripts
            assert trans(i, p) == dict(zip(d.translations[p]._fields, d.translations[p]))
            assert d.tables.root(p) == sc

        trans2 = lambda i, e: {l: str(p) + ' 2 ' + str(i) + l for l in LANGUAGES}
        for i, p in enumerate(para):
            self.db.set_morpheme_translation(p,
                                                translations=trans2(i, p),
                                            author_mail=author_mail,
                                            author_name=author_name)

        version1 = self.db.get_version()
        assert version1 != version0
        d = self.db.dictionary()

        for i, p in enumerate(para):
            assert p in d.scripts
            assert trans2(i, p) == dict(zip(d.translations[p]._fields, d.translations[p]))
            assert d.tables.root(p) == sc

        for p0, p1 in zip(para, para_m):
            self.db.update_morpheme_paradigm(p0,
                                        p1,
                                        author_name=author_name,
                                        author_mail=author_mail)

        version0 = self.db.get_version()
        assert version1 != version0
        d = self.db.dictionary()

        for i, (p0, p1) in enumerate(zip(para, para_m)):
            assert p0 not in d.scripts
            assert p1 in d.scripts
            # assert trans2(i, p0) == dict(zip(d.translations[p1]._fields, d.translations[p1]))

        for p in para_m:
            self.db.delete_morpheme_paradigm(p,
                                             author_mail=author_mail,
                                             author_name=author_name)

        version1 = self.db.get_version()
        assert version1 != version0
        d = self.db.dictionary()


        for p in para:
            assert p not in d.scripts




if __name__ == '__main__':
    unittest.main()
