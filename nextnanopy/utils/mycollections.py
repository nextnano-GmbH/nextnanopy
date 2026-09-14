from collections import OrderedDict


class DictList(OrderedDict):
    """
    Ordered dictionary whose values are also reachable by position.

    It is a mixture between a dictionary and a list because it allows to
    access the values via keys or integer indexes.
    Common usage::

        d = DictList(a=3, b='t')
        d[0] = 3
        d['a'] = 3

    It has all the methods and attributes from a dictionary like .keys(), .values(), .items()

    Moreover, it supports iterations like a list::

        for value in d:
            print(value)
        >>> 3
        >>> 't'
    
    Notes
    -----
    Two deliberate deviations from normal Mapping semantics:

    1. Iteration yields **values**, not keys. This is the documented behaviour of this class and
       much of nextnanopy relies on it (e.g. ``for var in datafile.variables: var.name``).
       Note that dict/OrderedDict C-level fast paths bypass __iter__, so ``dict(d)``,
       ``d.update(other)``, ``key in d`` and ``**d`` keep their usual key-based behaviour.
       Use .keys() when you need keys.
    2. Integer subscripts are positions, not keys, so integer keys are unreachable via d[...].
       All keys used in nextnanopy are strings (variable/file/folder names).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def _idxs(self):
        return OrderedDict(enumerate(self.keys()))

    def get_indx(self, key):
        for i, _key in enumerate(self.keys()):
            if _key == key:
                return i
        raise KeyError("No such key in the DictList")

    def __getitem__(self, key):
        if isinstance(key, int):
            if key < 0:
                key = len(self) + key
            key = self._idxs[key]
        item = super().__getitem__(key)
        return item

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        cname = self.__class__.__name__
        args = [
            f"(index: {idx} - key: '{key}' - {value})"
            for idx, key, value in zip(self._idxs.keys(), self.keys(), self.values(), strict=True)
        ]
        args = ",\n".join(args)
        return f"{cname}([\n{args}\n])"

    def __iter__(self):
        # Yields values, not keys (see class docstring). Returns a fresh iterator each call so
        # that nested/concurrent loops over the same object do not share iteration state.
        return iter(self.values())
