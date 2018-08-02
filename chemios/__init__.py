# -*- coding: utf-8 -*-

"""Top-level package for Chemios Temperature Controllers."""

__author__ = """Chemios"""
__email__ = 'hello@chemios.io'
__version__ = '0.1.0'

from ._constants import StatusCodes  # noqa: F401
from ._units import units

# Set default logging handler to avoid "No handler found" warnings.
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
