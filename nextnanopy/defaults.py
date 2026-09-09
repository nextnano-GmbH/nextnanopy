import warnings
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from nextnanopy.inputs import InputFileTemplate
from nextnanopy.msb import defaults as _msb
from nextnanopy.msb import inputs as _msb_inputs
from nextnanopy.msb import outputs as _msb_outputs
from nextnanopy.negf import defaults as _negf
from nextnanopy.negf import inputs as _negf_inputs
from nextnanopy.negf import inputs_classic as _negf_inputs_classic
from nextnanopy.negf import outputs as _negf_outputs
from nextnanopy.nn3 import defaults as _nn3
from nextnanopy.nn3 import inputs as _nn3_inputs
from nextnanopy.nn3 import outputs as _nn3_outputs
from nextnanopy.nnevo import defaults as _nnevo
from nextnanopy.nnp import defaults as _nnp
from nextnanopy.nnp import inputs as _nnp_inputs
from nextnanopy.nnp import outputs as _nnp_outputs
from nextnanopy.utils.config import Config

config_default_path = Path.home() / ".nextnanopy-config"

# Sentinel product for text that matches no nextnano syntax. Deliberately not a PRODUCTS
# key: it must stay out of `products`, or it would gain a section in ~/.nextnanopy-config.
# Only get_InputFile() accepts it, returning the product-agnostic template.
NOT_VALID = "not valid"


@dataclass(frozen=True)
class ProductSpec:
    """
    Everything nextnanopy knows about one nextnano product.

    A product need not support every part of the package. nextnanoevo has configuration
    but no input-file format at all, so its fmt/command/detect/InputFile/get_loader are
    None and the matching getters reject it. ``None`` therefore means "this product has no
    such thing", and the getters turn that into the ValueError they always raised.
    """

    name: str
    # Every product has configuration, including those with no input-file format.
    config_default: dict
    config_validator: dict
    # Input-file support: either all of these are set, or all are None.
    fmt: dict | None = None
    command: Callable | None = None
    detect: Callable[[str], bool] | None = None
    InputFile: type | None = None
    get_loader: Callable | None = None


# The one place a product is defined. Adding a product is one entry here; previously it
# meant editing `products` plus six parallel if/elif chains, where missing one left that
# single aspect raising "is not valid" at runtime.
#
# Order carries two meanings, neither of which currently constrains it. `products` is
# derived from it, so it is the order sections are written to a *fresh* config file
# (existing files are never reordered) -- cosmetic. And input_text_type() returns the
# first spec whose `detect` matches, so of two products that both recognize a file, the
# earlier one wins. No shipped input file matches more than one product's pattern, so
# today no order is more correct than another; this one is kept for historical continuity.
# That could change: NEGF and MSB input files use nnp brace syntax, and the patterns are
# plain substring checks, so a NEGF file that ever grows a `global{` block would be
# detected as nextnano++ from here.

PRODUCTS: dict[str, ProductSpec] = {
    "nextnano++": ProductSpec(
        name="nextnano++",
        config_default=_nnp.config_default,
        config_validator=_nnp.config_validator,
        fmt=_nnp.fmt,
        command=_nnp.command_nnp,
        detect=_nnp.is_nnp_input_text,
        InputFile=_nnp_inputs.InputFile,
        get_loader=_nnp_outputs.get_loader,
    ),
    "nextnano3": ProductSpec(
        name="nextnano3",
        config_default=_nn3.config_default,
        config_validator=_nn3.config_validator,
        fmt=_nn3.fmt,
        command=_nn3.command_nn3,
        detect=_nn3.is_nn3_input_text,
        InputFile=_nn3_inputs.InputFile,
        get_loader=_nn3_outputs.get_loader,
    ),
    # The two NEGF variants share their whole output layer and configuration, and differ
    # only in input syntax: classic is XML, modern is nnp-style braces.
    "nextnano.NEGF": ProductSpec(
        name="nextnano.NEGF",
        config_default=_negf.config_default,
        config_validator=_negf.config_validator,
        fmt=_negf.fmt,
        command=_negf.command_negf,
        detect=_negf.is_negf_input_text,
        InputFile=_negf_inputs.InputFile,
        get_loader=_negf_outputs.get_loader,
    ),
    "nextnano.NEGF_classic": ProductSpec(
        name="nextnano.NEGF_classic",
        config_default=_negf.config_default,
        config_validator=_negf.config_validator,
        fmt=_negf.fmt_classic,
        command=_negf.command_negf_classic,
        detect=_negf.is_negf_classic_input_text,
        InputFile=_negf_inputs_classic.InputFile,
        get_loader=_negf_outputs.get_loader,
    ),
    "nextnano.MSB": ProductSpec(
        name="nextnano.MSB",
        config_default=_msb.config_default,
        config_validator=_msb.config_validator,
        fmt=_msb.fmt,
        command=_msb.command_msb,
        detect=_msb.is_msb_input_text,
        InputFile=_msb_inputs.InputFile,
        get_loader=_msb_outputs.get_loader,
    ),
    # Configuration only: nextnanoevo has no input-file format, so it is not detectable
    # and has no fmt, command, InputFile or loader.
    "nextnanoevo": ProductSpec(
        name="nextnanoevo",
        config_default=_nnevo.config_default,
        config_validator=_nnevo.config_validator,
    ),
}

products = list(PRODUCTS)


def _spec(product):
    try:
        return PRODUCTS[product]
    except KeyError:
        raise ValueError(f"{product} is not valid") from None


def get_InputFile(product):
    # NOT_VALID is a sentinel rather than a spec, so it is handled before the lookup.
    # InputFileTemplate is imported at module level like the product classes; that works
    # only as long as nextnanopy.inputs never reads an attribute off this module while
    # its own body runs (it imports `defaults` for use inside methods, which is fine).
    if product == NOT_VALID:
        return InputFileTemplate
    spec = _spec(product)
    if spec.InputFile is None:
        raise ValueError(f"There is no InputFile format for {product}")
    return spec.InputFile


def get_DataFile_loader(product):
    """Return the product's get_loader(extension, filename_only) function."""
    spec = _spec(product)
    if spec.get_loader is None:
        raise ValueError(f"There is no DataFile format for {product}")
    return spec.get_loader


def get_command(product):
    spec = _spec(product)
    if spec.command is None:
        raise ValueError(f"There is no command format for {product}")
    return spec.command


def get_fmt(product):
    spec = _spec(product)
    if spec.fmt is None:
        raise ValueError(f"There is no formatting defaults for {product}")
    return spec.fmt


def input_file_type(fullpath):
    with open(fullpath) as f:
        text = f.read()
    return input_text_type(text)


def input_text_type(text):
    for spec in PRODUCTS.values():
        if spec.detect is not None and spec.detect(text):
            return spec.name
    return NOT_VALID


def get_config_validators():
    config_validator = {product: _get_config_validator(product) for product in products}
    return config_validator


def get_config_defaults():
    config_defaults = {product: _get_config_default(product) for product in products}
    return config_defaults


def _get_config_validator(product):
    return _spec(product).config_validator


def _get_config_default(product):
    return _spec(product).config_default


class NNConfig(Config):
    def __init__(self, fullpath=None):
        self.default_fullpath = config_default_path
        validators = get_config_validators()
        self.defaults = get_config_defaults()
        if fullpath is None:
            fullpath = self.default_fullpath
        super().__init__(fullpath, validators)
        if not Path(fullpath).is_file():
            self.reset()
        elif not self._complete:
            # TODO add tests for these behaviour
            # ensures smooth transition to additional product: NEGF++
            self.update_with_defaults()
            self.save()

        unsupported_products = self.get_unsupported_products()
        if unsupported_products:
            # stacklevel=1: fires at import time; the warning is about the config file's
            # contents, not any call site, so no caller frame is actionable.
            warnings.warn(
                f"Unsupported products in config file: {unsupported_products} will be ignored. To not see this message, please remove unsupported products from the config file: {self.fullpath}. "
                "Note: nextnano.NEGF++ was renamed to nextnano.NEGF, nextnano.NEGF was renamed to nextnano.NEGF_classic. Please check the documentation for more details.",
                stacklevel=1,
            )

    def to_default(self):
        for section in self.defaults.keys():
            if section not in self.sections:
                self.add_section(section)
            for option, value in self.defaults[section].items():
                self.set(section, option, value)

    def reset(self):
        self.to_default()
        self.save()

    @property
    def _complete(self):
        return self.check_complete()

    def check_complete(self):
        for section in self.defaults.keys():
            if section not in self.sections:
                return False
        return True

    def get_unsupported_products(self):
        unsupported_products = []
        for section in self.sections:
            if section not in self.defaults.keys():
                unsupported_products.append(section)
        return unsupported_products

    def update_with_defaults(self):
        for section in self.defaults.keys():
            if section not in self.sections:
                self.add_section(section)
                for option, value in self.defaults[section].items():
                    self.set(section, option, value)


_config = None


def get_config():
    """
    Return the process-wide NNConfig, building it on first use.

    Constructing an NNConfig reads ~/.nextnanopy-config, and creates it if it is
    missing, so it is deliberately not done at import time: importing the package
    must not touch the user's home directory. ``nextnanopy.config`` resolves here via
    the module __getattr__ in nextnanopy/__init__.py, so the config is built on first
    access instead.

    This is the configuration new input files start from: with no ``configpath``,
    InputFileTemplate.__init__ takes a copy of it. It lives here rather than in
    nextnanopy/__init__.py, where it used to, because nextnanopy.inputs has to reach
    it and cannot import the package root -- the package root imports nextnanopy.inputs.
    """
    global _config
    if _config is None:
        _config = NNConfig()
    return _config
