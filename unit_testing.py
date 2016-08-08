import unittest
# logging.getLogger().setLevel(logging.ERROR)

if __name__ == "__main__":
    # loader = unittest.TestLoader()
    # suite = loader.discover('testing')
    # unittest.TextTestRunner().run(suite)
    suite = unittest.TestLoader().discover('testing', top_level_dir='.')
    unittest.TextTestRunner(verbosity=2).run(suite)
