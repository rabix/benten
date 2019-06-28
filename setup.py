#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib
from datetime import datetime
from setuptools import setup, find_packages

current_path = pathlib.Path(__file__).parent

name = 'benten'
ver_path = pathlib.Path(current_path, "benten", "version.py")
exec(ver_path.open("r").read())
version = locals()["__version__"]
now = datetime.utcnow()
desc_path = pathlib.Path(current_path, "Readme.md")
long_description = desc_path.open("r").read()

setup(
    name=name,
    version=version,
    packages=find_packages(),
    platforms=['POSIX', 'MacOS', 'Windows'],
    python_requires='>=3.7.0',
    install_requires=[
        "pyyaml",
        "ruamel.yaml",
        "sevenbridges-python"
    ],
    entry_points={
        'console_scripts': [
            'benten-ls = benten.__main__:main'
        ],
    },

    author='Seven Bridges Genomics Inc.',
    maintainer='Seven Bridges Genomics Inc.',
    maintainer_email='kaushik.ghose@sbgenomics.com',
    author_email='kaushik.ghose@sbgenomics.com',
    description='CWL language server developed by Seven Bridges',
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    license='Copyright (c) {} Seven Bridges'.format(now.year),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only'
    ],
    keywords='seven bridges cwl common workflow language'
)
