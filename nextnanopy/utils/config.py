import configparser
import os
from copy import deepcopy
from pathlib import Path


class Config:
    """
    This class stores and manipulates a configuration file.

    The initialization of the class will execute the load method.

    Parameters
    ----------
    fullpath : str
        path to the file. It does not need to exist yet: loading a missing file
        yields an empty configuration which can be filled in and then saved.
        It must not be empty or None, otherwise a ValueError is raised.
    validators : dict
        dict where the keys are the name of the sections and the values
        are another dict.
        In the latter dict, the keys are the name of the options and the values
        are methods to convert the raw information (e.g: int)

    Attributes
    ----------
    fullpath : str
        path to the file
    config : dict
        validated values of each option of each section
    configparser : configparser.ConfigParser object
        ConfigParser object with raw values (str format) of each option of each section
    validators : dict
        dict of validator methods for each section and option (default is {})
    sections : list
        list of the section names

    Raises
    ------
    ValueError
        if fullpath is empty or None.

    Notes
    -----
    A value must not contain a ``%``. One can be read from a file but not written back,
    so `save` raises `ValueError` on it.
    """

    def __init__(self, fullpath, validators=None):
        if not fullpath:
            raise ValueError(
                f"fullpath must be a non-empty path to a configuration file, got {fullpath!r}"
            )
        if validators is None:
            validators = {}
        # Known bug behind the '%' note in the class docstring, left unfixed
        # deliberately: no user has hit it. The default BasicInterpolation rejects a
        # lone '%', so r'C:\Users\%USERNAME%\out' loads fine -- reads come from the
        # parser's raw store -- but save() -> config_to_configparser() assigns through
        # the interpolation and raises ValueError. Real paths do hit it: %USERNAME%,
        # %APPDATA%, an output folder named 50%_doping. The fix is one argument,
        # ConfigParser(interpolation=None); these values are filesystem paths, never
        # templates, so interpolation buys nothing. Apply it if a user ever complains
        # and stop there, nothing else in this class needs to change.
        # Full write-up in .local_dev/decisions_later.md.
        self.configparser = configparser.ConfigParser()
        self.validators = validators
        self.fullpath = fullpath
        self.load()

    def load(self):
        self.read_file()
        self.configparser_to_config()
        self.validate_config()

    def read_file(self):
        self.configparser.read(self.fullpath)

    def configparser_to_config(self):
        self.config = deepcopy(self.configparser._sections)

    def validate_config(self):
        for section in self.sections:
            if section not in self.validators.keys():
                continue
            for option, value in self.config[section].items():
                if option not in self.validators[section].keys():
                    continue
                validated_value = self.validators[section][option](value)
                self.config[section][option] = validated_value

    @property
    def sections(self):
        return self.config.keys()

    def preview(self):
        """Print every section with its options and their values."""
        for sec in self.sections:
            print(f"[{sec}]")
            for key, value in self.config[sec].items():
                print(f"{key} = {value}")
            print("")

    def get_options(self, section):
        """Return the options of a section together with their values.

        Parameters
        ----------
        section : str
            Name of the section, a nextnano product for `.NNConfig`.

        Returns
        -------
        dict
            Value of each option, keyed by option name. The stored mapping itself and
            not a copy, so editing it edits the configuration.

        Raises
        ------
        KeyError
            If there is no such section.
        """
        options = self.config[section]
        return options

    def save(self, fullpath=None):
        """Write the configuration to a file.

        Parameters
        ----------
        fullpath : str or pathlib.Path, default=None
            Where to write. If omitted the current `fullpath` is used; if given it
            becomes the new `fullpath`.

        Raises
        ------
        ValueError
            If any value contains a ``%``. See the class Notes.

        Notes
        -----
        The file is written beside the target and moved into place, so a reader never
        meets a half-written file and a failure part way leaves the previous one intact.
        """
        self.config_to_configparser()
        if fullpath is None:
            fullpath = self.fullpath
        else:
            self.fullpath = fullpath
        target = Path(self.fullpath)
        # Write to a sibling temp file and swap it in: os.replace is atomic, so a
        # concurrent reader never sees a truncated file and a crash mid-write leaves
        # the previous config intact. The temp file must share the target's directory,
        # since os.replace is only atomic within one filesystem.
        tmp = target.with_name(f"{target.name}.{os.getpid()}.tmp")
        try:
            with open(tmp, "w") as file:
                self.configparser.write(file)
            os.replace(tmp, target)
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise

    def config_to_configparser(self):
        for sec in self.sections:
            for key, value in self.config[sec].items():
                self.configparser[sec][key] = str(value)

    def set(self, section, option, value):
        """Change the value of an option.

        Parameters
        ----------
        section : str
            Name of the section, a nextnano product for `.NNConfig`.
        option : str
            Name of the option. One that the section does not already carry is added
            rather than refused, so a misspelling passes unnoticed.
        value : object
            Value to store. The option's validator is applied first, so ``threads``
            is kept as an `int` whatever is handed in.

        Raises
        ------
        KeyError
            If there is no such section.

        Notes
        -----
        The change reaches this process only. `save` writes it to the file.
        """
        if section in self.validators.keys():
            if option in self.validators[section].keys():
                value = self.validators[section][option](value)
        self.config[section][option] = value

    def get(self, section, option):
        """Return the value of an option.

        Parameters
        ----------
        section : str
            Name of the section, a nextnano product for `.NNConfig`.
        option : str
            Name of the option.

        Returns
        -------
        object
            The validated value: ``threads`` comes back as an `int`, the rest as `str`.

        Raises
        ------
        KeyError
            If there is no such section or option.
        """
        return self.config[section][option]

    def add_section(self, section):
        if section not in self.sections:
            self.config[section] = {}
            self.configparser.add_section(section)

    def __repr__(self):
        lines = []
        lines.append(f"{self.__class__.__name__}({self.fullpath})")
        for sec in self.sections:
            lines.append(f"[{sec}]")
            for key, value in self.config[sec].items():
                lines.append(f"{key} = {value}")
        out = "\n".join(lines)
        return out

    def __str__(self):
        return self.__repr__()
