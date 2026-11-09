import builtins
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from nextnanopy import defaults
from nextnanopy.inputs import InputFileTemplate
from nextnanopy.msb import defaults as msb_defaults
from nextnanopy.msb import inputs as msb_inputs
from nextnanopy.msb import outputs as msb_outputs
from nextnanopy.negf import defaults as negf_defaults
from nextnanopy.negf import inputs as negf_inputs
from nextnanopy.negf import inputs_classic as negf_inputs_classic
from nextnanopy.negf import outputs as negf_outputs
from nextnanopy.nn3 import defaults as nn3_defaults
from nextnanopy.nn3 import inputs as nn3_inputs
from nextnanopy.nn3 import outputs as nn3_outputs
from nextnanopy.nnopti import defaults as nnopti_defaults
from nextnanopy.nnp import defaults as nnp_defaults
from nextnanopy.nnp import inputs as nnp_inputs
from nextnanopy.nnp import outputs as nnp_outputs
from nextnanopy.utils import mycollections

folder_nnp = Path("tests") / "datafiles" / "nextnano++"
folder_nn3 = Path("tests") / "datafiles" / "nextnano3"
folder_negf = Path("tests") / "datafiles" / "nextnano.NEGF"
folder_msb = Path("tests") / "datafiles" / "nextnano.MSB"


class TestDictlist(unittest.TestCase):
    def test_dictlist(self):
        a = mycollections.DictList(a=2, b=3, c=4)
        self.assertEqual(a[0], 2)
        self.assertEqual(a["a"], 2)
        self.assertEqual(a[1], 3)
        self.assertEqual(a["b"], 3)
        self.assertEqual(list(a.keys()), ["a", "b", "c"])
        self.assertEqual(list(a.values()), [2, 3, 4])


class TestFormatting(unittest.TestCase):
    """Each product's is_*_input_text() must recognize its own input and reject the others.

    These used to assert against the is_*_input_file() variants, which took a path and
    reopened the file per call. Those are gone (input_file_type() reads once and delegates
    to input_text_type()), so the same assertions are now made on the text predicates --
    which are the ones input_text_type() actually dispatches on, and which had no direct
    coverage of their own before.
    """

    def test_nn3(self):
        fullpath = folder_nn3 / "example.nn3"
        text = fullpath.read_text()
        self.assertTrue(nn3_defaults.is_nn3_input_text(text))
        self.assertFalse(nnp_defaults.is_nnp_input_text(text))
        self.assertFalse(negf_defaults.is_negf_classic_input_text(text))
        self.assertFalse(negf_defaults.is_negf_input_text(text))
        self.assertFalse(msb_defaults.is_msb_input_text(text))
        self.assertEqual(defaults.input_file_type(fullpath), "nextnano3")
        self.assertEqual(defaults.get_fmt("nextnano3")["var_char"], "%")
        self.assertEqual(defaults.get_fmt("nextnano3")["com_char"], "!")
        self.assertEqual(
            defaults.get_fmt("nextnano3")["input_pattern"], "$end_simulation-dimension"
        )

    def test_nnp(self):
        fullpath = folder_nnp / "example.nnp"
        text = fullpath.read_text()
        self.assertFalse(nn3_defaults.is_nn3_input_text(text))
        self.assertTrue(nnp_defaults.is_nnp_input_text(text))
        self.assertFalse(negf_defaults.is_negf_classic_input_text(text))
        self.assertFalse(negf_defaults.is_negf_input_text(text))
        self.assertFalse(msb_defaults.is_msb_input_text(text))
        self.assertEqual(defaults.input_file_type(fullpath), "nextnano++")
        self.assertEqual(defaults.get_fmt("nextnano++")["var_char"], "$")
        self.assertEqual(defaults.get_fmt("nextnano++")["com_char"], "#")
        self.assertEqual(defaults.get_fmt("nextnano++")["input_pattern"], "global{")

    def test_negf_classic(self):
        fullpath = folder_negf / "example.xml"
        text = fullpath.read_text()
        self.assertFalse(nn3_defaults.is_nn3_input_text(text))
        self.assertFalse(nnp_defaults.is_nnp_input_text(text))
        self.assertFalse(negf_defaults.is_negf_input_text(text))
        self.assertTrue(negf_defaults.is_negf_classic_input_text(text))
        self.assertFalse(msb_defaults.is_msb_input_text(text))
        self.assertEqual(defaults.input_file_type(fullpath), "nextnano.NEGF_classic")
        self.assertEqual(defaults.get_fmt("nextnano.NEGF_classic")["var_char"], "$")
        self.assertEqual(defaults.get_fmt("nextnano.NEGF_classic")["com_char"], "<!--")
        self.assertEqual(defaults.get_fmt("nextnano.NEGF_classic")["input_pattern"], "<Simulation")

    def test_negf(self):
        fullpath = folder_negf / "Minimal_InputFile.negf"
        text = fullpath.read_text()
        self.assertFalse(nn3_defaults.is_nn3_input_text(text))
        self.assertFalse(nnp_defaults.is_nnp_input_text(text))
        self.assertFalse(negf_defaults.is_negf_classic_input_text(text))
        self.assertTrue(negf_defaults.is_negf_input_text(text))
        self.assertFalse(msb_defaults.is_msb_input_text(text))
        self.assertEqual(defaults.input_file_type(fullpath), "nextnano.NEGF")
        self.assertEqual(defaults.get_fmt("nextnano.NEGF")["var_char"], "$")
        self.assertEqual(defaults.get_fmt("nextnano.NEGF")["com_char"], "#")
        self.assertEqual(defaults.get_fmt("nextnano.NEGF")["input_pattern"], "nextnano.NEGF{")

    def test_msb(self):
        # example.msb, not example.xml: the latter is a legacy XML-syntax MSB file which
        # the 'nextnano.MSB{' pattern cannot match (no brace in XML), so it detects as
        # 'not valid'. Test_msb in test_inputs.py only ever loads example.msb too.
        fullpath = folder_msb / "example.msb"
        text = fullpath.read_text()
        self.assertFalse(nn3_defaults.is_nn3_input_text(text))
        self.assertFalse(nnp_defaults.is_nnp_input_text(text))
        self.assertFalse(negf_defaults.is_negf_classic_input_text(text))
        self.assertFalse(negf_defaults.is_negf_input_text(text))
        self.assertTrue(msb_defaults.is_msb_input_text(text))
        self.assertEqual(defaults.input_file_type(fullpath), "nextnano.MSB")
        self.assertEqual(defaults.get_fmt("nextnano.MSB")["var_char"], "$")
        self.assertEqual(defaults.get_fmt("nextnano.MSB")["com_char"], "#")
        self.assertEqual(defaults.get_fmt("nextnano.MSB")["input_pattern"], "nextnano.MSB{")


class TestInputFileType(unittest.TestCase):
    """input_file_type() reads the file once and delegates to input_text_type().

    The two used to be parallel if/elif chains over the same five patterns -- one
    reopening the file per probe, one working on a string. They must agree.
    """

    def test_agrees_with_input_text_type(self):
        for fullpath in [
            folder_nn3 / "example.nn3",
            folder_nnp / "example.nnp",
            folder_negf / "example.xml",
            folder_negf / "Minimal_InputFile.negf",
            folder_msb / "example.msb",
        ]:
            with self.subTest(fullpath=fullpath):
                text = Path(fullpath).read_text()
                self.assertEqual(
                    defaults.input_file_type(fullpath),
                    defaults.input_text_type(text),
                )

    def test_unrecognized_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            fullpath = Path(tmp) / "junk.in"
            fullpath.write_text("this is not a nextnano input file\n")
            self.assertEqual(defaults.input_file_type(fullpath), "not valid")

    def test_reads_the_file_once(self):
        # the whole point of the change: detection is one open(), not one per product.
        # A file matching no product used to be the worst case -- all five probes ran.
        fullpath = folder_nnp / "example.nnp"
        real_open = builtins.open
        opened = []

        def counting_open(file, *args, **kwargs):
            opened.append(file)
            return real_open(file, *args, **kwargs)

        with mock.patch("builtins.open", counting_open):
            product = defaults.input_file_type(fullpath)

        self.assertEqual(product, "nextnano++")
        self.assertEqual(len(opened), 1)


class _Raises:
    """Sentinel: this cell's getter must reject the product with a ValueError.

    Only the exception type is asserted, never the message. The wording is not a contract
    -- each getter phrases it differently today ("There is no InputFile format for ...",
    "... no DataFile format ...", "... no command format ...", "... no formatting defaults
    ...") and a registry should be free to unify it without touching this table.
    """

    def __repr__(self):
        return "RAISES"


RAISES = _Raises()


# The product dispatch matrix: what each of defaults.py's six getters must return for
# each product, or RAISES where it must reject it.
#
# Spelled out longhand against objects imported straight from the product packages, on
# purpose. Deriving the expectations from defaults.py -- the module under test -- would
# make every assertion vacuously true.
#
# Cells are compared with assertIs, not assertEqual. For the classes and functions that is
# the only sensible check; for the fmt/config dicts it additionally pins that the getters
# hand back the product module's own dict rather than a copy, which is what makes mutating
# e.g. nnp_defaults.config_default visible through the getter today.
#
# Note the two NEGF rows: the variants deliberately share their whole output layer and
# config (same objects) while keeping distinct input parsers, commands and fmt. That
# split is spread across four `product == "A" or product == "B"` branches today and is
# the easiest thing for a registry to miswire.
DISPATCH_MATRIX = {
    "nextnano++": {
        "InputFile": nnp_inputs.InputFile,
        "DataFile_loader": nnp_outputs.get_loader,
        "command": nnp_defaults.command_nnp,
        "fmt": nnp_defaults.fmt,
        "config_validator": nnp_defaults.config_validator,
        "config_default": nnp_defaults.config_default,
    },
    "nextnano3": {
        "InputFile": nn3_inputs.InputFile,
        "DataFile_loader": nn3_outputs.get_loader,
        "command": nn3_defaults.command_nn3,
        "fmt": nn3_defaults.fmt,
        "config_validator": nn3_defaults.config_validator,
        "config_default": nn3_defaults.config_default,
    },
    "nextnano.NEGF": {
        "InputFile": negf_inputs.InputFile,
        "DataFile_loader": negf_outputs.get_loader,
        "command": negf_defaults.command_negf,
        "fmt": negf_defaults.fmt,
        "config_validator": negf_defaults.config_validator,
        "config_default": negf_defaults.config_default,
    },
    "nextnano.NEGF_classic": {
        "InputFile": negf_inputs_classic.InputFile,
        "DataFile_loader": negf_outputs.get_loader,  # shared with nextnano.NEGF
        "command": negf_defaults.command_negf_classic,
        "fmt": negf_defaults.fmt_classic,
        "config_validator": negf_defaults.config_validator,  # shared with nextnano.NEGF
        "config_default": negf_defaults.config_default,  # shared with nextnano.NEGF
    },
    "nextnano.MSB": {
        "InputFile": msb_inputs.InputFile,
        "DataFile_loader": msb_outputs.get_loader,
        "command": msb_defaults.command_msb,
        "fmt": msb_defaults.fmt,
        "config_validator": msb_defaults.config_validator,
        "config_default": msb_defaults.config_default,
    },
    # nextnano optimizers is the shape that makes the matrix worth writing down: it is a
    # real product with real config, but it has no input-file format at all, so four of
    # its six cells are rejections and only the config pair resolves.
    "nextnano optimizers": {
        "InputFile": RAISES,
        "DataFile_loader": RAISES,
        "command": RAISES,
        "fmt": RAISES,
        "config_validator": nnopti_defaults.config_validator,
        "config_default": nnopti_defaults.config_default,
    },
}

DISPATCH_GETTERS = {
    "InputFile": defaults.get_InputFile,
    "DataFile_loader": defaults.get_DataFile_loader,
    "command": defaults.get_command,
    "fmt": defaults.get_fmt,
    "config_validator": defaults._get_config_validator,
    "config_default": defaults._get_config_default,
}


class TestProductDispatchMatrix(unittest.TestCase):
    """Pins every (product, getter) cell of defaults.py's dispatch.

    See DISPATCH_MATRIX above for why this exists and how to read it.
    """

    def test_dispatch_matrix(self):
        for product, row in DISPATCH_MATRIX.items():
            for aspect, expected in row.items():
                with self.subTest(product=product, aspect=aspect):
                    getter = DISPATCH_GETTERS[aspect]
                    if expected is RAISES:
                        with self.assertRaises(ValueError):
                            getter(product)
                    else:
                        self.assertIs(getter(product), expected)

    def test_matrix_covers_every_supported_product(self):
        # Fails when a product is added to defaults.products without a matrix row -- which
        # is the moment to check it was wired into all six getters, not just some. That
        # is exactly the drift the registry is meant to make impossible.
        self.assertEqual(set(DISPATCH_MATRIX), set(defaults.products))

    def test_matrix_covers_every_getter(self):
        for product, row in DISPATCH_MATRIX.items():
            with self.subTest(product=product):
                self.assertEqual(set(row), set(DISPATCH_GETTERS))

    def test_unknown_product_is_rejected_by_every_getter(self):
        for aspect, getter in DISPATCH_GETTERS.items():
            with self.subTest(aspect=aspect):
                with self.assertRaises(ValueError):
                    getter("nextnano.DoesNotExist")

    def test_not_valid_sentinel_resolves_an_InputFile_and_nothing_else(self):
        # 'not valid' is a sentinel, not a product: input_text_type() returns it for
        # unrecognized text and get_InputFile() alone accepts it, handing back the
        # product-agnostic template (test_inputs.py::TestNotValidProduct covers the
        # spelling of the sentinel itself; this covers the asymmetry).
        #
        # The asymmetry is a real constraint on the registry: a spec row keyed 'not valid'
        # would satisfy get_InputFile but also leak the sentinel into defaults.products,
        # and from there into ~/.nextnanopy-config as a bogus section.
        self.assertIs(defaults.get_InputFile("not valid"), InputFileTemplate)
        self.assertNotIn("not valid", defaults.products)
        for aspect, getter in DISPATCH_GETTERS.items():
            if aspect == "InputFile":
                continue
            with self.subTest(aspect=aspect):
                with self.assertRaises(ValueError):
                    getter("not valid")


if __name__ == "__main__":
    unittest.main()
