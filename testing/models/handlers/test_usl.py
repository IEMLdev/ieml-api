import random
import string
import unittest

from _pytest.unittest import UnitTestCase
from handlers import save_usl, get_usl
from ieml.usl.tools import random_usl
from testing.models.stub_db import modelTestCase

rand_string = lambda: ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))

c = modelTestCase('usl')
class TestUslHandler(c):
    def test_save_usl(self):
        _usl = random_usl()
        tags = {'f'}
        fr = rand_string()
        en = rand_string()
        save_usl({
            'ieml': str(_usl),
            'fr': fr,
            'en': en
        })
        self.assertEqual(get_usl({'ieml': str(_usl)}),
                         {'success': True,
                          'ieml': str(_usl),
                          'tags': {'FR': fr, 'EN': en},
                          'keywords': {'FR': [], 'EN': []}}
                         )