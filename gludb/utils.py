"""Central place for misc utilities
"""

import datetime

from uuid import uuid4


def uuid():
    """Return a decent UUID as a string"""
    return uuid4().hex


def now_field():
    """Return a string we use for storing our date time values"""
    return 'UTC:' + datetime.datetime.utcnow().isoformat()
