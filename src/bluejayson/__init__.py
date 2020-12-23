"""
BlueJayson is a simple Pythonic data definition library to handle very
basic data serializations and validations, and it works with JSON data.
"""
from __future__ import annotations

import json
import os

__all__ = []

this_dir = os.path.dirname(os.path.abspath(__file__))
metadata_file = os.path.join(this_dir, 'package-info.json')

try:
    with open(metadata_file) as fobj:
        metadata = json.load(fobj)
except Exception:  # pragma: no cover
    metadata = {}

__author__ = metadata.get('authoring')
__version__ = metadata.get('version')
__status__ = metadata.get('status')
__license__ = metadata.get('license')
__maintainers__ = metadata.get('maintainers')

# TODO: implements ProductType class with proper constructors and inheritance
# TODO: implements Attribute data descriptor with coerce option
#       (False, True, other coerce functions)
# TODO: implements Attribute data descriptor with default option
