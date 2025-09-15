from copy import deepcopy
import numpy as np

default_unit = ""


class Data(object):
    """
    This class stores any kind of information from nextnano files (input files, data files).
    This is a template class for datasets like Variables, Coords, InputVariables, etc.

    ...

    Parameters
    ----------
    name : str
        name of the dataset
    value : not defined
        stored value
    unit : str, optional
        unit of the value (default is None)
    metadata : dict, optional
        extra information (default is {})
    label_fmt : method, optional
        formatting label with label_fmt(name, unit) (default is None)
        If it is None, label_fmt = lambda name, unit: f'{name} ({unit})'

    Attributes
    ----------
    name : str
        name of the dataset
    value : not defined
        stored value
    unit : str
        unit of the value (default is None)
    metadata : dict
        extra information (default is {})
    label_fmt : method
        formatting label with label_fmt(name, unit) (default is None)
        If it is None, label_fmt = lambda name, unit: f'{name} ({unit})'
    """

    params = ['name', 'value', 'unit', 'metadata'],

    def __init__(self, name, value, unit=None, metadata={}, label_fmt=None, *args,
                 **kwargs):
        self.name = str(name)
        self.value = np.array(value)
        if unit is None or unit == '':
            unit = default_unit
        self.unit = str(unit)
        if label_fmt is None:
            label_fmt = lambda name, unit: f'{name} ({unit})'
        self.label_fmt = label_fmt
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
        out = f'{cname} - {str(self)}'
        return out

    def __str__(self):
        return f'name: {self.name}'


class Variable(Data):
    """
    This class stores independent variables from data files.

    ...

    Parameters
    ----------
    name : str
        name of the dataset
    value : not defined
        stored value
    unit : str, optional
        unit of the value (default is None)
    metadata : dict, optional
        extra information (default is {})
    label_fmt : method, optional
        formatting label with label_fmt(name, unit) (default is None)
        If it is None, label_fmt = lambda name, unit: f'{name} ({unit})'

    Attributes
    ----------
    name : str
        name of the dataset
    value : not defined
        stored value
    unit : str
        unit of the value (default is None)
    metadata : dict
        extra information (default is {})
    label_fmt : method
        formatting label with label_fmt(name, unit) (default is None)
        If it is None, label_fmt = lambda name, unit: f'{name} ({unit})'


    Methods
    ----------
    get_value()
        return a copy of the value

    """
    params = ['name', 'value', 'unit', 'metadata']

    def __init__(self, name, value, unit=None, metadata={}, **kwargs):
        super().__init__(name, value, unit, metadata, **kwargs)

    def get_value(self):
        value = deepcopy(self.value)
        return value

    def __str__(self):
        return f'name: {self.name} - unit: {self.unit} - shape: {self.value.shape}'


class Coord(Data):
    """
    This class stores the coordinates from data files.

    ...

    Parameters
    ----------
    name : str
        name of the dataset
    value : not defined
        stored value
    dim : int
        dim for the Variable.value
        For example, for a dataset of (100, 2) and a coordinate x of 100 pts, dim = 0
    unit : str, optional
        unit of the value (default is None)
    offset : not defined, optional
        offset to be added to value (default is 0)
    metadata : dict, optional
        extra information (default is {})
    label_fmt : method, optional
        formatting label with label_fmt(name, unit) (default is None)
        If it is None, label_fmt = lambda name, unit: f'{name} ({unit})'

    Attributes
    ----------
    name : str
        name of the dataset
    value : not defined
        stored value
    dim : int
        dim for the Variable.value
        For example, for a dataset of (100, 2) and a coordinate x of 100 pts, dim = 0
    unit : str
        unit of the value (default is None)
    offset : not defined
        offset to be added to value (default is 0)
    metadata : dict
        extra information (default is {})
    label_fmt : method
        formatting label with label_fmt(name, unit) (default is None)
        If it is None, label_fmt = lambda name, unit: f'{name} ({unit})'
    valueo : not defined
        value with offset

    Methods
    ----------
    get_value(use_offset=False)
        return a copy of the value with or without the offset
    """

    params = ['name', 'value', 'unit', 'offset', 'dim', 'metadata']

    def __init__(self, name, value, dim, unit=None, offset=0, metadata={}, **kwargs):
        super().__init__(name, value, unit, metadata, **kwargs)
        self.dim = int(dim)
        self.offset = np.array(offset)
        self.valueo = self.get_value(use_offset=True)

    def get_value(self, use_offset=False):
        value = deepcopy(self.value)
        if use_offset:
            value += self.offset
        return value

    def __str__(self):
        return f'name: {self.name} - unit: {self.unit} - shape: {self.value.shape} - dim: {self.dim}'


class InputVariable(Data):
    """
    Template class for the input variables. For each nextnano product, it will be specified
    the variable character (e.g $ for nextnano++) and the comment character (e.g # for nextnano++).

    ...

    Parameters
    ----------
    name : str
        name of the dataset
    value : not defined
        stored value
    unit : str, optional
        unit of the value (default is '')
    comment : str, optional
        (default is '')
    metadata : dict, optional
        extra information (default is {})
    label_fmt : method, optional
        formatting label with label_fmt(name, unit) (default is None)
        If it is None, label_fmt = lambda name, unit: f'{name} ({unit})'

    Attributes
    ----------
    name : str
        name of the dataset
    value : not defined
        stored value
    unit : str
        unit of the value (default is '')
    comment : str
        (default is '')
    metadata : dict
        extra information (default is {})
    label_fmt : method
        formatting label with label_fmt(name, unit) (default is None)
        If it is None, label_fmt = lambda name, unit: f'{name} ({unit})'
    text : str
        return the raw text for the input file

    Methods
    ----------
    get_value(use)
        return a copy of the value
    """

    params = ['name', 'value', 'unit', 'comment', 'metadata']
    var_char = ''
    com_char = ''

    def __init__(self, name, value, unit='', comment='', metadata={}, **kwargs):
        super().__init__(name, value, unit, metadata, **kwargs)
        self.comment = comment

    def get_value(self):
        value = deepcopy(self.value)
        return value

    @property
    def text(self):
        t = f'{self.var_char}{self.name} = {self.value}'
        if self.comment:
            t = f'{t} {self.com_char} {self.comment}'
        return t

    def __str__(self):
        return self.text
