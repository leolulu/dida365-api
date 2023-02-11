from collections import defaultdict


def groupby_func(iter, key_func):
    d = defaultdict(list)
    for i in iter:
        value = key_func(i)
        d[value].append(i)
    return d
