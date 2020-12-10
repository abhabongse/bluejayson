#!/usr/bin/env python3
import io
import json
from glob import glob
from os.path import basename, dirname, join, splitext

from setuptools import find_packages, setup


def read(*names, **kwargs):
    with io.open(join(dirname(__file__), *names),
                 encoding=kwargs.get('encoding', 'utf8')) as fh:
        return fh.read()


_METADATA = json.loads(read(join('src', 'bluejayson', 'meta.json')))

setup(
    name='bluejayson',
    version=_METADATA['version'],
    license=_METADATA['license'],
    description=_METADATA['description'],
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    author=_METADATA['author'],
    author_email=_METADATA['email'],
    url='https://github.com/abhabongse/bluejayson',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # Complete classifier list:
        # http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Utilities',
        'Typing :: Typed',
    ],
    project_urls={
        'Documentation': 'https://bluejayson.readthedocs.io/',
        'Changelog': 'https://github.com/abhabongse/bluejayson/blob/main/CHANGELOG.md',
        'Issue Tracker': 'https://github.com/abhabongse/bluejayson/issues',
    },
    keywords=[],
    python_requires='>=3.7',
    install_requires=[
        'typing-extensions>=3.7.4',
    ],
)
