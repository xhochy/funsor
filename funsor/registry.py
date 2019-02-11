from __future__ import absolute_import, division, print_function

import inspect
import itertools
from collections import defaultdict


class UnaryRegistry(object):
    """
    Dynamic table for dispatch on a single type and a key (typically ops).
    """
    def __init__(self):
        self._registry = defaultdict(dict)
        self._cache = {}

    def register(self, key, cls):
        """
        Creates a decorator dispatching on given class and key.
        """

        def decorator(fn):
            self._registry[key][cls] = fn
            self._cache.clear()
            return fn

        return decorator

    def __call__(self, key, x, *args, **kwargs):
        """
        Dispatches and calls registered implementation if found,
        raises ``NotImplementedError`` otherwise.
        """
        try:
            fn = self._cache[key, type(x)]
        except KeyError:
            fn = self._dispatch(key, type(x))
            self._cache[key, type(x)] = fn
        if fn is NotImplemented:
            raise NotImplementedError
        return fn(x, *args, **kwargs)

    def _dispatch(self, key, cls):
        registry = self._registry[key]
        if not registry:
            return NotImplemented
        for match in inspect.getmro(cls):
            if match in registry:
                return registry[match]
        return NotImplemented


class BinaryRegistry(object):
    """
    Dynamic table for dispatch on two types and a key (typically ops).
    """
    def __init__(self):
        self._registry = defaultdict(dict)
        self._cache = {}

    def register(self, key, cls1, cls2):
        """
        Creates a decorator dispatching on given class and key.
        """
        def decorator(fn):
            self._registry[key][cls1, cls2] = fn
            self._cache.clear()
            return fn

        return decorator

    def __call__(self, key, x, y, *args, **kwargs):
        """
        Dispatches and calls registered implementation if found,
        raises ``NotImplementedError`` otherwise.
        """
        try:
            fn = self._cache[key, type(x), type(y)]
        except KeyError:
            fn = self._dispatch(key, type(x), type(y))
            self._cache[key, type(x), type(y)] = fn
        if fn is NotImplemented:
            raise NotImplementedError
        return fn(x, y, *args, **kwargs)

    def _dispatch(self, key, cls1, cls2):
        registry = self._registry[key]
        if not registry:
            return NotImplemented
        ranks1 = {s: i for i, s in enumerate(inspect.getmro(cls1))}
        ranks2 = {s: i for i, s in enumerate(inspect.getmro(cls2))}
        matches = [match for match in itertools.product(ranks1, ranks2)
                   if match in registry]
        if not matches:
            return NotImplemented
        match1 = min(matches, key=lambda m: (ranks1[m[0]], ranks2[m[1]]))
        match2 = min(matches, key=lambda m: (ranks2[m[1]], ranks1[m[0]]))
        if match1 is not match2:
            raise ValueError('Ambiguous dispatch, please register {}'.format(
                (match1[0], match2[1]) + key))
        return registry[match1]


__all__ = [
    'BinaryRegistry',
    'UnaryRegistry',
]
