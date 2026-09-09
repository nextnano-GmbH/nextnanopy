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

    Methods
    -------
    preview()
        print the text of the file.
    load()
        load the file located at .fullpath
    save(fullpath=None)
        save the current configuration into a file. (default is None)
        If it is None, it will use the current .fullpath
    get_options(section)
        get the list of option names of a given section
    config_to_configparser()
        copy the information in .config to .configparser
    set(section, option, value)
        change the value of a given option of a section in .config
        it applies the validator if there is any
    get(section, option)
        return the value of a given option of a section in .config
    add_section(section)
        create a new section in the configuration

    Raises
    ------
    ValueError
        if fullpath is empty or None.

    Notes
    -----
    Known bug: a value containing a '%' can be loaded but never saved. Reads go through
    the parser's raw store, so the '%' survives, but save() -> config_to_configparser()
    assigns through configparser's default BasicInterpolation, which rejects a lone '%'::

        config.set('nextnano++', 'outputdirectory', r'C:\\Users\\%USERNAME%\\out')
        config.save()   # ValueError: invalid interpolation syntax ... at position 9

    This bites real paths (%USERNAME%, %APPDATA%, an output folder named 50%_doping).
    The fix is one argument -- build the parser as ConfigParser(interpolation=None); the
    values here are filesystem paths, never templates, so interpolation buys nothing.
    Left unfixed deliberately: no user has hit it. Apply the one argument if one ever
    does, and stop there -- nothing else in this class needs to change.
    See .local_dev/decisions_later.md for the full write-up.
    """

    def __init__(self, fullpath, validators=None):
        if not fullpath:
            raise ValueError(
                f"fullpath must be a non-empty path to a configuration file, got {fullpath!r}"
            )
        if validators is None:
            validators = {}
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
        for sec in self.sections:
            print(f"[{sec}]")
            for key, value in self.config[sec].items():
                print(f"{key} = {value}")
            print("")

    def get_options(self, section):
        options = self.config[section]
        return options

    def save(self, fullpath=None):
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
        if section in self.validators.keys():
            if option in self.validators[section].keys():
                value = self.validators[section][option](value)
        self.config[section][option] = value

    def get(self, section, option):
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
