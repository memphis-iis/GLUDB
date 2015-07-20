"""versioning.py

GLUDB versioning implementation
"""


# Yes, this could be an enum, but we're supporting Python 2.7
class VersioningTypes(object):
    NONE = "ver:none"
    LOGGED_ONLY = "ver:logged"
    DELTA_HISTORY = "ver:delta"
