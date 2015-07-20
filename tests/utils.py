"""Some simple utilities for testing
"""

import json


def compare_data_objects(obj1, obj2):
    def get_dict(o):
        d = json.loads(o.to_data())
        for k in [k for k, _ in d.items() if k.startswith('_')]:
            del d[k]
        return d
    return get_dict(obj1) == get_dict(obj2)
