import importlib
import os
import re
import unittest
import models
import sys
import config

def stub_db():
    config.DB_NAME = 'test_db'
    reload_model_package()
    print('switching to test_db.')


def normal_db():
    importlib.reload(config)
    reload_model_package()
    print('resetting to normal db (ieml_db).')


def reload_model_package():
    to_reload = [m for m in sys.modules.keys() if m.partition('.')[0] == 'models']

    # the double loop is for dependencies resolution. it is a nasty hack
    for i in range(len(to_reload)):
        for m in to_reload:
            importlib.reload(sys.modules.get(m))


class ModelTestSuite(unittest.TestSuite):
    def run(self, result, debug=False):
        stub_db()
        super().run(result, debug=False)
        normal_db()


def load_tests(*arg, **kwargs):
    print('Loading model tests...')
    python_files = re.compile('^.+\.py$')
    test_case = [__package__ + '.' + f[:-3] for f in os.listdir('./' + __package__.replace('.', '/'))
                 if python_files.match(f) and f not in ('load_tests.py', '__init__.py') ]
    tests = unittest.TestLoader().loadTestsFromNames(test_case)
    return ModelTestSuite(tests=(tests,))

if __name__ == '__main__':
    print(models.RelationsQueries.relations_db.db)
    stub_db()
    print(models.RelationsQueries.relations_db.db)
    normal_db()
    print(models.RelationsQueries.relations_db.db)


