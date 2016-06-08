"""Iris sample data."""

import os


def _get_path():
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sample_data')


__version__ = '1.0.0-dev'

path = _get_path()
