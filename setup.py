from codecs import open
from os import path

# Always prefer setuptools over distutils
from setuptools import setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
# Note that we are using README.rst - it is generated from README.md in
# build.sh
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='gludb',
    version='0.1.5',
    description='A simple database wrapper',
    long_description=long_description,
    url='https://github.com/memphis-iis/GLUDB',
    author='University of Memphis Institute for Intelligent Systems',
    author_email='cnkelly@memphis.edu',
    license='Apache Version 2.0',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',

        'Topic :: Database',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Archiving :: Backup',

        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords='database versioning backup'
             'sqlite dynamodb cloud datastore mongodb',

    packages=['gludb', 'gludb.backends'],

    install_requires=[
        "json_delta>=1.1.3",
    ],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': [],
        'test': ['coverage', 'nose', 'tornado'],
        'dynamodb': ['boto'],
        'gcd': ['googledatastore'],
        'mongodb': ['pymongo'],
        'backups': ['boto'],
    },

    package_data={},
    data_files=[],
    entry_points={},
)
