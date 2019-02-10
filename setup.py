import os
import io
from os import path
from datetime import datetime
from setuptools import setup, find_packages

NAME = 'benten'
VERSION = '0.0.1'
DIR = path.abspath(path.dirname(__file__))
NOW = datetime.utcnow()

if os.path.exists('./VERSION'):
    with io.open('./VERSION', 'r') as f:
        VERSION = f.read().strip()

with open(path.join(DIR, 'Readme.md')) as f:
    long_description = f.read()

setup(
    name=NAME,
    version=VERSION,
    packages=find_packages(),
    platforms=['POSIX', 'MacOS', 'Windows'],
    python_requires='>=3.7.0',
    install_requires=[
        "pyyaml",
        "PySide2",
        "pygraphviz"  # For the "dot" layout algorithm
    ],
    entry_points={
        'console_scripts': [
            'benten = benten.editor.main:main'
        ],
    },

    author='Seven Bridges Genomics Inc.',
    maintainer='Seven Bridges Genomics Inc.',
    maintainer_email='kaushik.ghose@sbgenomics.com',
    author_email='kaushik.ghose@sbgenomics.com',
    description='SBG Python tool to assist hand coding of CWL workflows',
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    license='Copyright (c) {} Seven Bridges Genomics'.format(NOW.year),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: Apache 2.0',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
    ],
    keywords='seven bridges cwl common workflow language'
)