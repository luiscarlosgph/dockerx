__version__='0.6.0'

import sys

if sys.version_info < (3, 9):
    error_msg = '[ERROR] The dockerx package requires at least Python 3.9.'
    raise RuntimeError(error_msg)

from .dl import *
