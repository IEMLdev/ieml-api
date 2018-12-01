import os
import subprocess
import unittest

from ieml.constants import DICTIONARY_FOLDER
from ieml.dictionary2.dictionary import Dictionary, FolderWatcherCache


class CacheTestCase(unittest.TestCase):
    def setUp(self):
        self.cache = FolderWatcherCache(DICTIONARY_FOLDER)

    def test_cache(self):
        Dictionary.load(DICTIONARY_FOLDER)
        self.assertFalse(self.cache.is_pruned())

        self._test_f = os.path.join(self.cache.folder, os.listdir(self.cache.folder)[0])
        subprocess.Popen("echo '\\n\\n' >> {}".format(self._test_f), shell=True).communicate()
        self.assertTrue(self.cache.is_pruned())

        # d = Dictionary.load(DICTIONARY_FOLDER)
        Dictionary.load(DICTIONARY_FOLDER)
        self.assertFalse(self.cache.is_pruned())

        with open(self._test_f, 'r') as fp:
            r = fp.read().strip() + '\n'

        with open(self._test_f, 'w') as fp:
            fp.write(r)

        self.assertTrue(self.cache.is_pruned())
        Dictionary.load(DICTIONARY_FOLDER)
        self.assertFalse(self.cache.is_pruned())

