#!/usr/bin/env python3
# Setting up python packaging

import io
import os
import sys
from shutil import rmtree

from setuptools import Command, setup, find_packages

# Obtain metadata information about the package from the source file itself
this_dir = os.path.dirname(os.path.abspath(__file__))
about_ns = {}
with open(os.path.join(this_dir, "bluejayson", "__metadata__.py")) as f:
    exec(f.read(), about_ns)

# Basic package information
NAME = "BlueJayson"
DESCRIPTION = ("BlueJayson is a simple Pythonic data definition library to manage "
               "very basic data validations and serializations to and from JSON.")
URL = "https://github.com/abhabongse/bluejayson"
LICENSE = about_ns['__license__']
AUTHOR = about_ns['__author__']
EMAIL = about_ns['__email__']
VERSION = about_ns['__version__']
REQUIRES_PYTHON = ">=3.6.0,<4"
KEYWORDS = "schema data-definition json"

# What packages are required for this module to be executed?
REQUIRED = []

# What packages are optional?
EXTRAS = {}

# Obtain long description of the project from README.md file
try:
    with io.open(os.path.join(this_dir, "README.md"), encoding='utf-8') as f:
        LONG_DESCRIPTION = '\n' + f.read()
except FileNotFoundError:
    LONG_DESCRIPTION = DESCRIPTION


# Upload package to PyPI using Twine
class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(this_dir, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(VERSION))
        os.system('git push --tags')

        sys.exit()


# Run the package setup
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    keywords=KEYWORDS,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license=LICENSE,
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries",
    ],
    cmdclass={
        'upload': UploadCommand,
    },
)
