from ieml.ieml_objects.tools import RandomPoolIEMLObjectGenerator
from models.intlekt.edition.glossary import GlossaryConnector
from testing.models.stub_db import ModelTestCase


class TestModel(ModelTestCase):
    connectors = ('glossary',)

    def test_new(self):
        id = self.glossary.add_glossary("test")
        self.assertEqual(id, self.glossary.get(name='test')['id'])

        self.assertTrue(self.glossary.remove_glossary(id=id))

    def test_add_terms(self):
        id = self.glossary.add_glossary("test")

        terms = [str(RandomPoolIEMLObjectGenerator().term()) for _ in range(10)]

        self.assertTrue(self.glossary.add_terms(terms, id))

        g = self.glossary.get(id=id)
        self.assertSetEqual(set(g['terms']), set(map(str, terms)))

        self.assertTrue(self.glossary.remove_terms(terms, id))

    def test_all_glossaries(self):
        names = ["test%d"%i for i in range(10)]
        ids = [self.glossary.add_glossary(n) for n in names]

        glossaries = self.glossary.all_glossaries()

        self.assertTrue(all(g['nb_terms'] == 0 for g in glossaries))
        self.assertSetEqual(set(names), set(g['name'] for g in glossaries))
        self.assertSetEqual(set(ids), set(g['id'] for g in glossaries))


    def test_double_add(self):
        self.glossary.drop()
        self.glossary.add_glossary('test')
        with self.assertRaises(ValueError):
            self.glossary.add_glossary('test')
