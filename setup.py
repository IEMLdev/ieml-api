from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()


setup(name='ieml',
      version='1.0.0',
      description='Python implementation of the artificial natural language IEML',
      long_description=readme(),
      classifiers=[
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Programming Language :: Python :: 3.5',
            'Topic :: Text Processing :: Linguistic',
            'Topic :: Text Processing :: Indexing'
      ],
      keywords='ieml semantic-representation syntax semantic-relations semantic-distance',
      url='https://github.com/IEMLdev/ieml',
      author='Louis van Beurden',
      author_email='louis.vanbeurden@gmail.com',
      license='GPLv3',
      packages=find_packages(exclude=['scripts', '*.test']),
      install_requires=[
            'numpy',
            'bidict',
            'ply',
            'cached-property',
            'tqdm'
      ],
      test_suite='nose2.collector.collector',
      tests_require=['nose2'],

      include_package_data=True,
      zip_safe=False)