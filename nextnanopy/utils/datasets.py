from copy import deepcopy

import numpy as np

default_unit = ""


def default_label_fmt(name, unit):
    return f"{name} ({unit})"


class Data:
    """Base class for the datasets nextnanopy reads out of nextnano files: `.Variable`
    and `.Coord` from data files, `.InputVariable` from input files.

    Named value with a unit, a label and free-form metadata.

    Parameters
    ----------
    name : str
        Name of the dataset.
    value : not defined
        Stored value.
    unit : str, default=None
        Unit of the value.
    metadata : dict, default=None
        Extra information.
    label_fmt : callable, default=None
        Called as ``label_fmt(name, unit)`` to build `label`.
        If not defined, the two are joined as ``'{name} ({unit})'``.

    Attributes
    ----------
    name : str
        Name of the dataset.
    value : not defined
        Stored value.
    unit : str
        Unit of the value.
    metadata : dict
        Extra information. Empty unless the loader filled it in.
    label : str
        Name and unit rendered by `label_fmt`, ready to use as an axis label.
        Read-only.
    label_fmt : callable
        Called as ``label_fmt(name, unit)`` to build `label`. If omitted,
        the two are joined as ``'{name} ({unit})'``.
    """

    params = ["name", "value", "unit", "metadata"]

    def __init__(self, name, value, unit=None, metadata=None, label_fmt=None, *args, **kwargs):
        self.name = str(name)
        self.value = np.array(value)
        if unit is None or unit == "":
            unit = default_unit
        self.unit = str(unit)
        if label_fmt is None:
            label_fmt = default_label_fmt
        self.label_fmt = label_fmt
        if metadata is None:
            metadata = {}
        self.metadata = metadata

    def parameters(self):
        dict_ = {}
        for param in self.params:
            value = getattr(self, param)
            dict_[param] = value
        dict_ = deepcopy(dict_)
        return dict_

    @property
    def label(self):
        return self.label_fmt(self.name, self.unit)

    def __repr__(self):
        cname = self.__class__.__name__
        out = f"{cname} - {str(self)}"
        return out

    def __str__(self):
        return f"name: {self.name}"


class Variable(Data):
    """Dependent variable read from a nextnano data file.

    Holds the quantity itself; the axes it is sampled on are `.Coord` objects.

    Parameters
    ----------
    name : str
        Name of the dataset.
    value : array_like
        Stored value.
    unit : str, default=None
        Unit of the value.
    metadata : dict, default=None
        Extra information.
    label_fmt : callable, default=None
        Called as ``label_fmt(name, unit)`` to build `label`.
        If not defined, the two are joined as ``'{name} ({unit})'``.

    Attributes
    ----------
    name : str
        Name of the dataset.
    value : numpy.ndarray
        Stored value.
    unit : str
        Unit of the value.
    metadata : dict
        Extra information. Empty unless the loader filled it in.
    label : str
        Name and unit rendered by `label_fmt`, ready to use as an axis label.
        Read-only.
    label_fmt : callable
        Called as ``label_fmt(name, unit)`` to build `label`. If omitted,
        the two are joined as ``'{name} ({unit})'``.
    """

    params = ["name", "value", "unit", "metadata"]

    def __init__(self, name, value, unit=None, metadata=None, **kwargs):
        if metadata is None:
            metadata = {}
        super().__init__(name, value, unit, metadata, **kwargs)

    def get_value(self):
        "Return a copy of the value."
        value = deepcopy(self.value)
        return value

    def __str__(self):
        return f"name: {self.name} - unit: {self.unit} - shape: {self.value.shape}"


class Coord(Data):
    """Independent variable read from a nextnano data file.

    Holds one axis of the dataset; the quantities sampled on it are `.Variable` objects.

    Parameters
    ----------
    name : str
        Name of the dataset.
    value : array_like
        Stored value.
    dim : int
        Index of the axis this coordinate spans in the shape of the data it belongs to.
        For a dataset of shape ``(100, 2)``, a coordinate of 100 points has ``dim = 0``.
    unit : str, default=None
        Unit of the value.
    offset : array_like, default=0
        Shift added to `value` when the offset is requested.
    metadata : dict, default=None
        Extra information.
    label_fmt : callable, default=None
        Called as ``label_fmt(name, unit)`` to build `label`.
        If not defined, the two are joined as ``'{name} ({unit})'``.

    Attributes
    ----------
    name : str
        Name of the dataset.
    value : numpy.ndarray
        Stored value.
    dim : int
        Index of the axis this coordinate spans in the shape of the data it belongs to.
        For a dataset of shape ``(100, 2)``, a coordinate of 100 points has ``dim = 0``.
    unit : str
        Unit of the value.
    offset : numpy.ndarray
        Shift added to `value` when the offset is requested.
    metadata : dict
        Extra information. Empty unless the loader filled it in.
    label : str
        Name and unit rendered by `label_fmt`, ready to use as an axis label.
        Read-only.
    label_fmt : callable
        Called as ``label_fmt(name, unit)`` to build `label`. If omitted,
        the two are joined as ``'{name} ({unit})'``.
    valueo : numpy.ndarray
        `value` shifted by `offset`. Computed once at construction, so it does not
        follow later changes to either.
    """

    params = ["name", "value", "unit", "offset", "dim", "metadata"]

    def __init__(self, name, value, dim, unit=None, offset=0, metadata=None, **kwargs):
        if metadata is None:
            metadata = {}
        super().__init__(name, value, unit, metadata, **kwargs)
        self.dim = int(dim)
        self.offset = np.array(offset)
        self.valueo = self.get_value(use_offset=True)

    def get_value(self, use_offset=False):
        """Return a copy of the value, with or without the offset.

        Parameters
        ----------
        use_offset : bool, default=False
            Whether to add `offset` to the returned copy.

        Returns
        -------
        numpy.ndarray
            A copy, so changing it does not change `value`.
        """
        value = deepcopy(self.value)
        if use_offset:
            value += self.offset
        return value

    def __str__(self):
        return (
            f"name: {self.name} - unit: {self.unit} - shape: {self.value.shape} - dim: {self.dim}"
        )


class InputVariable(Data):
    """Variable defined in a nextnano input file.

    Base class for the per-product variants, which set `var_char` and `com_char` to
    the characters that product marks variables and comments with -- ``$`` and ``#``
    for nextnano++.

    Parameters
    ----------
    name : str
        Name of the dataset.
    value : not defined
        Stored value.
    unit : str, default=''
        Unit of the value.
    comment : str, default=''
        Comment written after the value on the same line of the input file.
    metadata : dict, default=None
        Extra information.
    label_fmt : callable, default=None
        Called as ``label_fmt(name, unit)`` to build `label`.
        If not defined, the two are joined as ``'{name} ({unit})'``.

    Attributes
    ----------
    name : str
        Name of the dataset.
    value : numpy.ndarray or object
        Stored value. Converted with `numpy.array` at construction; assigning to it,
        as `InputFile.set_variable` does, stores the object unchanged.
    unit : str
        Unit of the value.
    comment : str
        Comment written after the value on the same line of the input file.
    metadata : dict
        Extra information. Carries ``line_idx``, the line the variable was read from,
        for every variable parsed out of a file.
    label : str
        Name and unit rendered by `label_fmt`, ready to use as an axis label.
        Read-only.
    label_fmt : callable
        Called as ``label_fmt(name, unit)`` to build `label`. If omitted,
        the two are joined as ``'{name} ({unit})'``.
    text : str
        The variable as one line of input-file syntax, ``$name = value # comment``,
        with the characters of the product. Read-only.
    """

    params = ["name", "value", "unit", "comment", "metadata"]
    var_char = ""
    com_char = ""

    def __init__(self, name, value, unit="", comment="", metadata=None, **kwargs):
        if metadata is None:
            metadata = {}
        super().__init__(name, value, unit, metadata, **kwargs)
        self.comment = comment

    def get_value(self):
        """Return a copy of the value."""
        value = deepcopy(self.value)
        return value

    @property
    def text(self):
        t = f"{self.var_char}{self.name} = {self.value}"
        if self.comment:
            t = f"{t} {self.com_char} {self.comment}"
        return t

    def __str__(self):
        return self.text
