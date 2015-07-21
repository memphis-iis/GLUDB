"""Some simple utilities for testing
"""

import json


def compare_data_objects(obj1, obj2):
    def get_dict(o):
        d = json.loads(o.to_data())
        for k in [k for k, _ in d.items() if k.startswith('_')]:
            del d[k]
        return d

    d1, d2 = get_dict(obj1), get_dict(obj2)
    eq = (d1 == d2)

    if not eq:
        print('Objects not equal')
        print(d1)
        print(d2)

    return eq
