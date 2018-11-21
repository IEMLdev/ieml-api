import os
import subprocess
import unittest

from ieml.constants import DICTIONARY_FOLDER
from ieml.dictionary2.dictionary import Dictionary, FolderWatcherCache


class CacheTestCase(unittest.TestCase):
    def setUp(self):
        self.cache = FolderWatcherCache(DICTIONARY_FOLDER)



    def test_cache(self):
        self.assertTrue(self.cache.is_pruned())
        # d = Dictionary.load(DICTIONARY_FOLDER)
        d = "dasdas"
        self.cache.update(d)
        self.assertFalse(self.cache.is_pruned())

        self._test_f = self.cache._cache_candidates()[0]
        subprocess.Popen("echo '\\n\\n' >> {}".format(self._test_f), shell=True).communicate()
        # os.system("cat '\n\n' >> {}".format(self._test_f))
        # with open(self._test_f, 'a') as fp:
        #     fp.write('\n')
        d = Dictionary.load(DICTIONARY_FOLDER)

        self.assertTrue(self.cache.is_pruned())
        self.cache.update(d)
        self.assertFalse(self.cache.is_pruned())


    def tearDown(self):
        # os.remove(self._test_f)
        os.remove(self.cache.cache_file)

        with open(self._test_f, 'r') as fp:
            r = fp.read().strip() + '\n'

        with open(self._test_f, 'w') as fp:
            fp.write(r)

