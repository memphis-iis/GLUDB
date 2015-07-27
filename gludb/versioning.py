"""versioning.py

GLUDB versioning implementation
"""

import json

import json_delta  # External dependency


# Yes, this could be an enum, but we're supporting Python 2.7
class VersioningTypes(object):
    NONE = "ver:none"
    DELTA_HISTORY = "ver:delta"


# Python 2&3 compatible string testing
def _isstr(s):
    try:
        _basestring = basestring
    except NameError:
        _basestring = str
    return isinstance(s, _basestring)


# If any parameter is a string, parse it as JSON
def _norm_json_params(*args):
    return tuple([
        json.loads(param) if _isstr(param) else param
        for param in args
    ])


def record_diff(old, new):
    """Return a JSON-compatible structure capable turn the `new` record back
    into the `old` record. The parameters must be structures compatible with
    json.dumps *or* strings compatible with json.loads. Note that by design,
    `old == record_patch(new, record_diff(old, new))`"""
    old, new = _norm_json_params(old, new)
    return json_delta.diff(new, old, verbose=False)


def record_patch(rec, diff):
    """Return the JSON-compatible structure that results from applying the
    changes in `diff` to the record `rec`. The parameters must be structures
    compatible with json.dumps *or* strings compatible with json.loads. Note
    that by design, `old == record_patch(new, record_diff(old, new))`"""
    rec, diff = _norm_json_params(rec, diff)
    return json_delta.patch(rec, diff, in_place=False)
