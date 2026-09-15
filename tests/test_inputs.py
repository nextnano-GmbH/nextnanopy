import builtins
import inspect
import os
import tempfile
import unittest
import unittest.mock
from pathlib import Path

import nextnanopy
from nextnanopy import defaults
from nextnanopy.inputs import InputFile, InputFileTemplate, Sweep
from nextnanopy.nnp.inputs import Parser


def delete_files(start, directory=None, exceptions=None):
    if directory is None:
        directory = Path.cwd()
    for fpath in Path(directory).iterdir():
        if fpath.name.startswith(start):
            if exceptions:
                if fpath.name in exceptions:
                    continue
                else:
                    fpath.unlink()
            else:
                fpath.unlink()


folder_nnp = Path("tests") / "datafiles" / "nextnano++"
folder_nn3 = Path("tests") / "datafiles" / "nextnano3"
folder_negf = Path("tests") / "datafiles" / "nextnano.NEGF"
folder_msb = Path("tests") / "datafiles" / "nextnano.MSB"


class Test_nnp(unittest.TestCase):
    def test_load(self):
        fullpath = folder_nnp / "only_variables.in"

        file = InputFile(fullpath)
        self.assertEqual(file.product, "nextnano++")

        self.assertEqual(len(file.variables.keys()), 7)
        self.assertEqual(file.variables["float"].name, "float")
        self.assertEqual(file.variables["float"].value, 0.0)
        self.assertEqual(file.variables["float"].comment, "float number (a.u.)")

        self.assertEqual(file.variables["int"].name, "int")
        self.assertEqual(file.variables["int"].value, 0)
        self.assertEqual(file.variables["int"].comment, "int number (random = 3)")

        self.assertEqual(file.variables["str"].name, "str")
        self.assertEqual(file.variables["str"].value, '"test"')
        self.assertEqual(file.variables["str"].comment, "first comments # second comment")

        self.assertEqual(file.variables["reference"].name, "reference")
        self.assertEqual(file.variables["reference"].value, "$int - 1")

        self.assertEqual(file.variables["NoSpacing"].name, "NoSpacing")
        self.assertEqual(file.variables["NoSpacing"].value, int("7"))
        self.assertEqual(file.variables["NoSpacing"].comment, "this is a comment")
        self.assertEqual(file.variables["NoSpacing"].text, "$NoSpacing = 7 # this is a comment")

        self.assertEqual(file.variables["MAYUS"].name, "MAYUS")
        self.assertEqual(file.variables["MAYUS"].value, "TEXT")
        self.assertEqual(file.variables["MAYUS"].comment, "")
        self.assertEqual(file.variables["MAYUS"].text, "$MAYUS = TEXT")

        fullpath = folder_nnp / "virtual_file.in"
        self.assertRaises(FileNotFoundError, InputFile, fullpath)

    def test_get_variables(self):
        fullpath = folder_nn3 / "only_variables.in"
        file = InputFile(fullpath)

        self.assertEqual(file.variables["float"], file.get_variable("float"))
        self.assertRaises(KeyError, file.get_variable, name="new_variable")

    def test_set_variables(self):
        fullpath = folder_nnp / "only_variables.in"
        file = InputFile(fullpath)
        file.set_variable("float", 1e-5, "some comment", "some unit")  # unit is not visible in nn++

        self.assertEqual(file.variables["float"].name, "float")
        self.assertEqual(file.variables["float"].value, 1e-5)
        self.assertEqual(file.variables["float"].comment, "some comment")
        self.assertEqual(file.variables["float"].text, f"$float = {str(1e-5)} # some comment")
        self.assertEqual(file.lines[3], f"$float = {str(1e-5)} # some comment")

        file.set_variable("float", value=1e-7)
        self.assertEqual(file.variables["float"].name, "float")
        self.assertEqual(file.variables["float"].value, 1e-7)
        self.assertEqual(file.variables["float"].comment, "some comment")
        self.assertEqual(file.variables["float"].text, f"$float = {str(1e-7)} # some comment")
        self.assertEqual(file.lines[3], f"$float = {str(1e-7)} # some comment")

        file.set_variable("float", comment="new comment")
        self.assertEqual(file.variables["float"].name, "float")
        self.assertEqual(file.variables["float"].value, 1e-7)
        self.assertEqual(file.variables["float"].comment, "new comment")
        self.assertEqual(file.variables["float"].text, f"$float = {str(1e-7)} # new comment")
        self.assertEqual(file.lines[3], f"$float = {str(1e-7)} # new comment")

        file.set_variable("float", value=0)
        self.assertEqual(file.variables["float"].value, 0)
        file.set_variable("float", value="0")
        self.assertEqual(file.variables["float"].value, "0")
        self.assertRaises(KeyError, file.set_variable, name="new_variable")
        self.assertRaises(KeyError, file.set_variable, name="new_variable")

    def test_fullpath(self):
        fullpath = folder_nnp / "only_variables.in"
        file = InputFile(fullpath)

        self.assertEqual(Path(file.fullpath), fullpath)
        self.assertEqual(
            Path(file.save(file.fullpath, overwrite=False)),
            folder_nnp / "only_variables_0.in",
        )
        Path(file.fullpath).unlink()

    def test_config(self):
        fullpath = folder_nnp / "only_variables.in"
        file = InputFile(fullpath)
        from nextnanopy import config

        for key, value in config.config["nextnano++"].items():
            self.assertEqual(file.default_command_args[key], value)

    def test_text(self):
        fullpath_onlyvar = folder_nnp / "only_variables.in"
        fullpath_example = folder_nnp / "example.nnp"
        file = InputFile(fullpath_onlyvar)
        text = file.text

        new_file = InputFile(fullpath_example)
        new_file.text = text
        self.assertEqual(new_file.product, "nextnano++")
        self.assertEqual(new_file.text, text)
        self.assertEqual(new_file.lines, file.lines)
        self.assertEqual(new_file.variables["MAYUS"].name, "MAYUS")
        self.assertEqual(new_file.variables["MAYUS"].value, "TEXT")
        self.assertEqual(new_file.variables["MAYUS"].comment, "")
        self.assertEqual(new_file.variables["MAYUS"].text, "$MAYUS = TEXT")
        self.assertEqual(
            Path(new_file.save(file.fullpath, overwrite=False)),
            folder_nnp / "only_variables_0.in",
        )
        Path(new_file.fullpath).unlink()

    def test_set_and_save(self):
        fullpath = folder_nnp / "only_variables.in"
        file = InputFile(fullpath)
        file.set_variable(name="float", value=0.4)
        self.assertAlmostEqual(file.variables["float"].value, 0.4)

        self.addCleanup((folder_nnp / "only_variables_0.in").unlink)
        file.save()
        self.assertTrue((folder_nnp / "only_variables_0.in").is_file())

    def test_save_temp(self):
        # The saved filename is deliberately not asserted here. _get_temp_dir hands out one
        # directory per class for the whole process, so an earlier temp save of the same file
        # (Sweep.save_sweep does one) is still sitting in it and pushes this save onto an
        # index - which index depends on test order. test_save_to_another_folder covers the
        # "free name keeps its name" contract in a directory this test owns.
        fullpath = folder_nnp / "only_variables.in"
        file = InputFile(fullpath)
        file.save(temp=True)
        self.assertTrue(Path(file.fullpath).is_file())
        try:
            self.assertTrue(Path(file.fullpath).is_file())
            # Check that the file is in the system temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()
            file_dir = Path(file.fullpath).resolve().parent
            self.assertTrue(str(file_dir).startswith(str(temp_dir)))
        finally:
            if Path(file.fullpath).exists():
                Path(file.fullpath).unlink()

    def test_save_to_another_folder(self):
        file = InputFile(folder_nnp / "only_variables.in")
        with tempfile.TemporaryDirectory() as target:
            target = Path(target)

            # the name is free in the target folder, so it is kept as-is
            first = Path(file.save(target / "only_variables.in"))
            self.assertEqual(first.name, "only_variables.in")
            self.assertTrue(first.is_file())
            self.assertEqual([p.name for p in target.iterdir()], ["only_variables.in"])

            # only once the name is taken does an index appear
            second = Path(file.save(target / "only_variables.in"))
            self.assertEqual(second.name, "only_variables_0.in")
            self.assertTrue(second.is_file())

            # the source file in the original folder was left alone
            self.assertFalse((folder_nnp / "only_variables_0.in").exists())

    def test_same_dir_saving(self):
        current_directory = Path.cwd()
        self.addCleanup(os.chdir, current_directory)

        os.chdir(folder_nnp)

        path = "only_variables.in"
        file = InputFile(path)
        file.set_variable(name="float", value=0.3333)
        self.assertAlmostEqual(file.variables["float"].value, 0.3333)
        self.addCleanup(
            delete_files,
            "only_variables",
            directory=".",
            exceptions=["only_variables.in"],
        )
        file.save()
        self.assertTrue(Path("only_variables_0.in").is_file())

    ###content tests

    def test_content_get(self):
        fullpath = folder_nnp / "only_variables.in"
        file = InputFile(fullpath, parse=True)

        self.assertIsNotNone(file.content)
        self.assertEqual(file.content[0], "$float = 0.0 ")
        self.assertEqual(file.content[-1].name, "global")

    def test_content_set(self):
        fullpath = folder_nnp / "only_variables.in"
        file = InputFile(fullpath, parse=True)

        file.content[0] = "$DUMMY = 1"
        self.assertEqual(file.content[0], "$DUMMY = 1")
        file.content["_entry_0"] = "DUMMY LINE"
        self.assertEqual(file.content[0], "DUMMY LINE")

    def test_content_roundtrip_does_not_duplicate_statements(self):
        """A block written on one line must not leak its body into the enclosing blocks.

        Compare against the *original* text, not against a second parse: re-parsing the
        duplicated output is idempotent, so a parse-twice-and-compare check passes even
        when the tree is corrupt.
        """
        fullpath = folder_nnp / "example.nnp"
        file = InputFile(fullpath, parse=True)
        rendered = str(file.content)

        for statement in ["pos =", "spacing =", 'name = "GaAs"', "num_ev =", "alloy_x ="]:
            self.assertEqual(
                rendered.count(statement),
                file.raw_text.count(statement),
                f"{statement!r} was duplicated by the parser",
            )

    def test_content_roundtrip_preserves_block_nesting(self):
        parser = Parser()
        parser.parse("global{ sub{ a = 1 } }", mode="str")

        outer = parser.result.content[0]
        inner = outer.content[0]
        self.assertEqual(len(parser.result.content), 1)  # nothing leaked to the root
        self.assertEqual(len(outer.content), 1)  # nothing leaked into global{}
        self.assertEqual(inner.content, ["a = 1 "])

    def test_non_parseable_parse_true_raises(self):
        fullpath = folder_nnp / "example_non_parseable.nnp"
        with self.assertRaises(ValueError):
            InputFile(fullpath, parse=True)

    def test_non_parseable_parse_false_ok(self):
        fullpath = folder_nnp / "example_non_parseable.nnp"
        file = InputFile(fullpath, parse=False)
        self.assertIsNone(file.content)
        self.assertEqual(len(file.variables), 8)
        self.assertAlmostEqual(file.variables["BIAS"].value, 0.0)
        self.assertAlmostEqual(file.variables["ALLOY"].value, 0.3)


class Test_nn3(unittest.TestCase):
    def test_load(self):
        fullpath = folder_nn3 / "only_variables.in"

        file = InputFile(fullpath)
        self.assertEqual(file.product, "nextnano3")

        self.assertEqual(len(file.variables.keys()), 7)
        self.assertEqual(file.variables["float"].name, "float")
        self.assertEqual(file.variables["float"].value, 0.0)
        self.assertEqual(file.variables["float"].comment, "float number (a.u.)")

        self.assertEqual(file.variables["int"].name, "int")
        self.assertEqual(file.variables["int"].value, 0)
        self.assertEqual(file.variables["int"].comment, "int number (random = 3)")

        self.assertEqual(file.variables["str"].name, "str")
        self.assertEqual(file.variables["str"].value, '"test"')
        self.assertEqual(file.variables["str"].comment, "first comments # second comment")

        self.assertEqual(file.variables["reference"].name, "reference")
        self.assertEqual(file.variables["reference"].value, "$int - 1")

        self.assertEqual(file.variables["NoSpacing"].name, "NoSpacing")
        self.assertEqual(file.variables["NoSpacing"].value, int("7"))
        self.assertEqual(file.variables["NoSpacing"].comment, "this is a comment")

        self.assertEqual(file.variables["MAYUS"].name, "MAYUS")
        self.assertEqual(file.variables["MAYUS"].value, "TEXT")
        self.assertEqual(file.variables["MAYUS"].comment, "")

        fullpath = folder_nn3 / "virtual_file.in"
        self.assertRaises(FileNotFoundError, InputFile, fullpath)

    def test_get_variables(self):
        fullpath = folder_nn3 / "only_variables.in"
        file = InputFile(fullpath)

        self.assertEqual(file.variables["float"], file.get_variable("float"))
        self.assertRaises(KeyError, file.get_variable, name="new_variable")

    def test_set_variables(self):
        fullpath = folder_nn3 / "only_variables.in"
        file = InputFile(fullpath)
        file.set_variable("float", 1e-5, "some comment")

        self.assertEqual(file.variables["float"].name, "float")
        self.assertEqual(file.variables["float"].value, 1e-5)
        self.assertEqual(file.variables["float"].comment, "some comment")
        self.assertEqual(file.variables["float"].text, f"%float = {str(1e-5)} ! some comment")
        self.assertEqual(file.lines[3], f"%float = {str(1e-5)} ! some comment")

        file.set_variable("float", value=1e-7)
        self.assertEqual(file.variables["float"].name, "float")
        self.assertEqual(file.variables["float"].value, 1e-7)
        self.assertEqual(file.variables["float"].comment, "some comment")
        self.assertEqual(file.variables["float"].text, f"%float = {str(1e-7)} ! some comment")
        self.assertEqual(file.lines[3], f"%float = {str(1e-7)} ! some comment")

        file.set_variable("float", comment="new comment")
        self.assertEqual(file.variables["float"].name, "float")
        self.assertEqual(file.variables["float"].value, 1e-7)
        self.assertEqual(file.variables["float"].comment, "new comment")
        self.assertEqual(file.variables["float"].text, f"%float = {str(1e-7)} ! new comment")
        self.assertEqual(file.lines[3], f"%float = {str(1e-7)} ! new comment")

        file.set_variable("float", value=0)
        self.assertEqual(file.variables["float"].value, 0)
        file.set_variable("float", value="0")
        self.assertEqual(file.variables["float"].value, "0")
        self.assertRaises(KeyError, file.set_variable, name="new_variable")

    def test_fullpath(self):
        fullpath = folder_nn3 / "only_variables.in"
        file = InputFile(fullpath)

        self.assertEqual(Path(file.fullpath), fullpath)
        self.assertEqual(
            Path(file.save(file.fullpath, overwrite=False)),
            folder_nn3 / "only_variables_0.in",
        )
        Path(file.fullpath).unlink()

    def test_config(self):
        fullpath = folder_nn3 / "only_variables.in"
        file = InputFile(fullpath)
        from nextnanopy import config

        for key, value in config.config["nextnano3"].items():
            self.assertEqual(file.default_command_args[key], value)

    def test_save(self):
        fullpath = folder_nn3 / "only_variables.in"
        file = InputFile(fullpath)
        new_folder = folder_nn3 / "temp"
        new_file = new_folder / "example_copy.in"
        self.assertRaises(FileNotFoundError, file.save, new_file, overwrite=True, automkdir=False)
        self.assertEqual(Path(file.save(new_file, overwrite=True, automkdir=True)), new_file)
        Path(file.fullpath).unlink()
        new_folder.rmdir()

    def test_save_temp(self):
        fullpath = folder_nn3 / "only_variables.in"
        file = InputFile(fullpath)
        file.save(temp=True)
        self.assertTrue(Path(file.fullpath).is_file())
        try:
            self.assertTrue(Path(file.fullpath).is_file())
            # Check that the file is in the system temp directory
            temp_dir = Path(tempfile.gettempdir()).resolve()
            file_dir = Path(file.fullpath).resolve().parent
            self.assertTrue(str(file_dir).startswith(str(temp_dir)))
        finally:
            if Path(file.fullpath).exists():
                Path(file.fullpath).unlink()

    def test_text(self):
        fullpath_onlyvar = folder_nn3 / "only_variables.in"
        fullpath_example = folder_nn3 / "example.nn3"
        file = InputFile(fullpath_onlyvar)
        text = file.text

        new_file = InputFile(fullpath_example)
        new_file.text = text

        self.assertEqual(new_file.product, "nextnano3")
        self.assertEqual(new_file.text, text)
        self.assertEqual(new_file.lines, file.lines)
        self.assertEqual(new_file.variables["MAYUS"].name, "MAYUS")
        self.assertEqual(new_file.variables["MAYUS"].value, "TEXT")
        self.assertEqual(new_file.variables["MAYUS"].comment, "")
        self.assertEqual(new_file.variables["MAYUS"].text, "%MAYUS = TEXT")
        self.assertEqual(
            Path(new_file.save(file.fullpath, overwrite=False)),
            folder_nn3 / "only_variables_0.in",
        )
        Path(new_file.fullpath).unlink()

    def test_set_and_save(self):
        fullpath = folder_nn3 / "only_variables.in"
        file = InputFile(fullpath)
        file.set_variable(name="float", value=0.4)
        self.assertAlmostEqual(file.variables["float"].value, 0.4)

        self.addCleanup((folder_nn3 / "only_variables_0.in").unlink)
        file.save()
        self.assertTrue((folder_nn3 / "only_variables_0.in").is_file())

    def test_same_dir(self):
        current_directory = Path.cwd()
        self.addCleanup(os.chdir, current_directory)

        os.chdir(folder_nn3)

        path = "only_variables.in"
        file = InputFile(path)
        file.set_variable(name="float", value=0.3333)
        self.assertAlmostEqual(file.variables["float"].value, 0.3333)
        self.addCleanup(
            delete_files,
            "only_variables",
            directory=".",
            exceptions=["only_variables.in"],
        )
        file.save()
        self.assertTrue(Path("only_variables_0.in").is_file())

    def test_content(self):
        fullpath = folder_nn3 / "only_variables.in"
        file = InputFile(fullpath)

        self.assertIsNone(file.content)


class Test_negf_classic(unittest.TestCase):
    def test_load(self):
        fullpath = folder_negf / "example.xml"
        file = InputFile(fullpath)

        self.assertEqual(file.product, "nextnano.NEGF_classic")

        self.assertEqual(len(file.variables.keys()), 4)

        self.assertEqual(file.variables["variable1"].name, "variable1")
        self.assertEqual(file.variables["variable1"].value, 0.24)
        self.assertEqual(file.variables["variable1"].comment, "Some comment")
        self.assertEqual(file.variables["variable1"].unit, "")

        self.assertEqual(file.variables["variable2"].name, "variable2")
        self.assertEqual(file.variables["variable2"].value, 0)
        self.assertEqual(file.variables["variable2"].comment, "Another comment")
        self.assertEqual(file.variables["variable2"].unit, "meV")

        self.assertEqual(file.variables["text_var"].name, "text_var")
        self.assertEqual(file.variables["text_var"].value, "some text")

        self.assertEqual(file.variables["ref_var"].value, "$(1-variable1)")

        fullpath = folder_negf / "virtual_file.xml"
        self.assertRaises(FileNotFoundError, InputFile, fullpath)

    def test_get_variables(self):
        fullpath = folder_negf / "example.xml"
        file = InputFile(fullpath)

        self.assertEqual(file.variables["variable1"], file.get_variable("variable1"))

        self.assertRaises(KeyError, file.get_variable, name="new_variable")

    def test_set_variables(self):
        fullpath = folder_negf / "example.xml"
        file = InputFile(fullpath)

        file.set_variable("variable1", 0.137, "test comment", "test unit^2")
        self.assertEqual(file.variables["variable1"].value, 0.137)
        self.assertEqual(file.variables["variable1"].comment, "test comment")
        self.assertEqual(file.variables["variable1"].unit, "test unit^2")

        file.set_variable("text_var", "string variable test")
        self.assertEqual(file.variables["text_var"].value, "string variable test")

        file.set_variable("ref_var", "$variable1 - 0.1")
        self.assertEqual(file.variables["ref_var"].value, "$variable1 - 0.1")

        self.assertRaises(KeyError, file.set_variable, name="new_variable")

    def test_fullpath(self):
        fullpath = folder_negf / "example.xml"
        file = InputFile(fullpath)

        self.assertEqual(Path(file.fullpath), fullpath)
        self.assertEqual(
            Path(file.save(file.fullpath, overwrite=False)),
            folder_negf / "example_0.xml",
        )
        Path(file.fullpath).unlink()

    def test_config(self):
        fullpath = folder_negf / "example.xml"
        file = InputFile(fullpath)
        from nextnanopy import config

        for key, value in config.config["nextnano.NEGF_classic"].items():
            self.assertEqual(file.default_command_args[key], value)

    def test_save(self):
        fullpath = folder_negf / "example.xml"
        file = InputFile(fullpath)

        new_folder = folder_negf / "temp"
        new_file = new_folder / "example_copy.in"
        self.assertRaises(FileNotFoundError, file.save, new_file, overwrite=True, automkdir=False)
        self.assertEqual(Path(file.save(new_file, overwrite=True, automkdir=True)), new_file)
        Path(file.fullpath).unlink()
        new_folder.rmdir()

    def test_set_and_save(self):
        fullpath = folder_negf / "example.xml"
        file = InputFile(fullpath)
        file.set_variable(name="variable1", value=0.4)
        self.assertAlmostEqual(file.variables["variable1"].value, 0.4)

        self.addCleanup((folder_negf / "example_0.xml").unlink)
        file.save()
        self.assertTrue((folder_negf / "example_0.xml").is_file())

    def test_content(self):
        fullpath = folder_negf / "example.xml"
        file = InputFile(fullpath)

        self.assertIsNone(file.content)


class Test_negf_classic_variables_section(unittest.TestCase):
    """A <Variables> section must be read and written back correctly whether it
    is populated, present but empty, or absent altogether.

    These three shapes are the contract. The empty section is the interesting
    one: it exists but has no children, so any check that conflates "has
    children" with "was found" collapses it into the absent case.
    """

    def write_input(self, variables_section):
        text = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            "<Simulation>\n"
            f"{variables_section}"
            "</Simulation>\n"
        )
        fullpath = Path(tempfile.mkdtemp()) / "input.xml"
        fullpath.write_text(text)
        return fullpath

    def test_populated_variables_section(self):
        fullpath = self.write_input(
            "  <Variables>\n"
            '    <Constant><Name Comment="first">$alpha</Name>'
            '<Value Unit="nm">3.5</Value></Constant>\n'
            '    <Constant><Name Comment="second">$beta</Name>'
            '<Value Unit="meV">42</Value></Constant>\n'
            "  </Variables>\n"
        )
        file = InputFile(fullpath)

        self.assertEqual(len(file.variables.keys()), 2)
        self.assertEqual(file.variables["alpha"].value, 3.5)
        self.assertEqual(file.variables["alpha"].unit, "nm")
        self.assertEqual(file.variables["alpha"].comment, "first")
        self.assertEqual(file.variables["beta"].value, 42)

        # Edits must survive the round trip back out to XML.
        file.set_variable("alpha", value=7.5, unit="um", comment="edited")
        rendered = "\n".join(file.lines)
        self.assertIn('<Value Unit="um">7.5</Value>', rendered)
        self.assertIn('Comment="edited"', rendered)

    def test_empty_variables_section(self):
        fullpath = self.write_input("  <Variables></Variables>\n")
        file = InputFile(fullpath)

        # Present but childless: no variables, and the section is not dropped.
        self.assertEqual(len(file.variables.keys()), 0)
        self.assertIn("<Variables", "\n".join(file.lines))

    def test_missing_variables_section(self):
        fullpath = self.write_input("")
        file = InputFile(fullpath)

        self.assertEqual(len(file.variables.keys()), 0)
        self.assertNotIn("<Variables", "\n".join(file.lines))


class Test_negf(unittest.TestCase):
    # TODO: implement test for NEGF++ input file
    def test_load(self):
        fullpath = folder_negf / "Minimal_InputFile.negf"

        file = InputFile(fullpath)
        self.assertEqual(file.product, "nextnano.NEGF")

        self.assertEqual(len(file.variables.keys()), 1)
        self.assertEqual(file.variables["alloyComposition"].name, "alloyComposition")
        self.assertAlmostEqual(file.variables["alloyComposition"].value, 0.15, delta=1e-9)
        self.assertEqual(file.variables["alloyComposition"].comment, "alloy composition")

        fullpath = folder_nnp / "virtual_file.in"
        self.assertRaises(FileNotFoundError, InputFile, fullpath)

    def test_get_variables(self):
        fullpath = folder_negf / "Minimal_InputFile.negf"
        file = InputFile(fullpath)

        self.assertEqual(file.variables["alloyComposition"], file.get_variable("alloyComposition"))
        self.assertRaises(KeyError, file.get_variable, name="new_variable")

    def test_set_variables(self):
        fullpath = folder_negf / "Minimal_InputFile.negf"
        file = InputFile(fullpath)
        file.set_variable(
            "alloyComposition", 1e-5, "some comment", "some unit"
        )  # unit is not visible in nn++

        self.assertEqual(file.variables["alloyComposition"].name, "alloyComposition")
        self.assertEqual(file.variables["alloyComposition"].value, 1e-5)
        self.assertEqual(file.variables["alloyComposition"].comment, "some comment")
        self.assertEqual(
            file.variables["alloyComposition"].text,
            f"$alloyComposition = {str(1e-5)} # some comment",
        )
        self.assertEqual(file.lines[0], f"$alloyComposition = {str(1e-5)} # some comment")

        file.set_variable("alloyComposition", value=1e-7)
        self.assertEqual(file.variables["alloyComposition"].name, "alloyComposition")
        self.assertEqual(file.variables["alloyComposition"].value, 1e-7)
        self.assertEqual(file.variables["alloyComposition"].comment, "some comment")
        self.assertEqual(
            file.variables["alloyComposition"].text,
            f"$alloyComposition = {str(1e-7)} # some comment",
        )
        self.assertEqual(file.lines[0], f"$alloyComposition = {str(1e-7)} # some comment")

        file.set_variable("alloyComposition", comment="new comment")
        self.assertEqual(file.variables["alloyComposition"].name, "alloyComposition")
        self.assertEqual(file.variables["alloyComposition"].value, 1e-7)
        self.assertEqual(file.variables["alloyComposition"].comment, "new comment")
        self.assertEqual(
            file.variables["alloyComposition"].text,
            f"$alloyComposition = {str(1e-7)} # new comment",
        )
        self.assertEqual(file.lines[0], f"$alloyComposition = {str(1e-7)} # new comment")

        file.set_variable("alloyComposition", value=0)
        self.assertEqual(file.variables["alloyComposition"].value, 0)

        self.assertRaises(KeyError, file.set_variable, name="new_variable")
        self.assertRaises(KeyError, file.set_variable, name="new_variable")

    def test_fullpath(self):
        fullpath = folder_negf / "Minimal_InputFile.negf"
        file = InputFile(fullpath)

        self.assertEqual(Path(file.fullpath), fullpath)
        self.assertEqual(
            Path(file.save(file.fullpath, overwrite=False)),
            folder_negf / "Minimal_InputFile_0.negf",
        )
        Path(file.fullpath).unlink()

    def test_config(self):
        fullpath = folder_negf / "Minimal_InputFile.negf"
        file = InputFile(fullpath)
        from nextnanopy import config

        for key, value in config.config["nextnano.NEGF"].items():
            self.assertEqual(file.default_command_args[key], value)

    def test_set_and_save(self):
        fullpath = folder_negf / "Minimal_InputFile.negf"
        file = InputFile(fullpath)
        file.set_variable(name="alloyComposition", value=0.4)
        self.assertAlmostEqual(file.variables["alloyComposition"].value, 0.4)

        self.addCleanup((folder_negf / "Minimal_InputFile_0.negf").unlink)
        file.save()
        self.assertTrue((folder_negf / "Minimal_InputFile_0.negf").is_file())

    def test_same_dir_saving(self):
        current_directory = Path.cwd()
        self.addCleanup(os.chdir, current_directory)

        os.chdir(folder_negf)

        path = "Minimal_InputFile.negf"
        file = InputFile(path)
        file.set_variable(name="alloyComposition", value=0.3333)
        self.assertAlmostEqual(file.variables["alloyComposition"].value, 0.3333)
        self.addCleanup(
            delete_files,
            "Minimal_InputFile",
            directory=".",
            exceptions=["Minimal_InputFile.negf"],
        )
        file.save()
        self.assertTrue(Path("Minimal_InputFile_0.negf").is_file())


class Test_msb(unittest.TestCase):
    def test_load(self):
        fullpath = folder_msb / "example.msb"

        input_file = InputFile(fullpath)
        print(input_file)
        print(input_file.text)
        print(type(input_file))
        self.assertEqual(input_file.product, "nextnano.MSB")
        self.assertEqual(len(input_file.variables.keys()), 1)

        fullpath = folder_msb / "virtual_file.msb"
        self.assertRaises(FileNotFoundError, InputFile, fullpath)

    def get_variables(self):
        fullpath = folder_msb / "example.msb"
        input_file = InputFile(fullpath)

        self.assertEqual(
            input_file.variables["Well"],
            input_file.get_variable("Well"),
        )
        self.assertRaises(KeyError, input_file.get_variable, name="new_variable")

        self.assertEqual(input_file.variables["Well"].value, 0.14)

    def test_set_variable(self):
        fullpath = folder_msb / "example.msb"
        input_file = InputFile(fullpath)

        input_file.set_variable("Well", 0.2, "Updated well width", "nm")
        self.assertEqual(input_file.variables["Well"].value, 0.2)
        self.assertEqual(input_file.variables["Well"].comment, "Updated well width")
        self.assertEqual(input_file.variables["Well"].unit, "nm")

    def test_set_and_save(self):
        fullpath = folder_msb / "example.msb"
        input_file = InputFile(fullpath)

        input_file.set_variable(name="Well", value=0.25)
        self.assertAlmostEqual(input_file.variables["Well"].value, 0.25)
        self.addCleanup((folder_msb / "example_0.msb").unlink)
        input_file.save()
        self.assertTrue((folder_msb / "example_0.msb").is_file())
        input_file_1 = InputFile(folder_msb / "example_0.msb")
        self.assertAlmostEqual(input_file_1.variables["Well"].value, 0.25)


class TestInputFile(unittest.TestCase):
    def test_access_by_index(self):
        fullpath = folder_nnp / "only_variables.in"
        file = InputFile(fullpath)
        for key, value in file.variables.items():
            self.assertEqual(file[key], value)

    def test_for_loop(self):
        fullpath = folder_nnp / "only_variables.in"
        file = InputFile(fullpath)
        for i, fi in enumerate(file):
            self.assertEqual(file.variables[i], fi)

    def test_fullpath(self):
        fullpath = folder_nnp / "only_variables.in"
        file = InputFile(fullpath)
        self.assertEqual(Path(file.fullpath), fullpath)
        self.assertEqual(file.filename, "only_variables.in")
        self.assertEqual(file.filename_only, "only_variables")
        self.assertEqual(Path(file.folder_input), folder_nnp)
        self.assertEqual(file.execute_info, {})

        file.filename = "new_name.in"
        self.assertEqual(file.filename, "new_name.in")
        self.assertEqual(file.filename_only, "new_name")
        self.assertEqual(Path(file.fullpath), folder_nnp / "new_name.in")
        self.assertEqual(Path(file.folder_input), folder_nnp)

        file.filename_only = "another_filename"
        self.assertEqual(file.filename, "another_filename.in")
        self.assertEqual(file.filename_only, "another_filename")
        self.assertEqual(Path(file.fullpath), folder_nnp / "another_filename.in")
        self.assertEqual(Path(file.folder_input), folder_nnp)

        npath = Path("new") / "folder"
        file.folder_input = npath
        self.assertEqual(file.filename, "another_filename.in")
        self.assertEqual(file.filename_only, "another_filename")
        self.assertEqual(Path(file.fullpath), npath / "another_filename.in")
        self.assertEqual(Path(file.folder_input), npath)

        npath = Path("random") / "path"
        file.execute_info["outputdirectory"] = npath
        self.assertEqual(Path(file.folder_output), npath)


class TestNotValidProduct(unittest.TestCase):
    """The 'not valid' sentinel must be spelled the same everywhere.

    InputFileTemplate.validate() used to write 'Not valid' (capital N) while the
    __init__ default, both detectors (defaults.input_text_type / input_file_type) and
    the dispatch branch in defaults.get_InputFile all use lowercase 'not valid'. The
    mismatch made get_InputFile's 'not valid' -> InputFileTemplate branch unreachable,
    so loading any non-nextnano file raised `ValueError: Not valid is not valid`.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.fullpath = Path(self._tmp.name) / "junk.in"
        self.fullpath.write_text("this is not a nextnano input file\n")

    def tearDown(self):
        self._tmp.cleanup()

    def test_sentinel_is_lowercase_everywhere(self):
        # the sentinel the detectors emit, the dispatcher accepts, and validate() writes
        # must all be the same string.
        self.assertEqual(defaults.input_text_type("not a nextnano file"), "not valid")
        self.assertEqual(defaults.input_file_type(self.fullpath), "not valid")
        self.assertIs(defaults.get_InputFile("not valid"), InputFileTemplate)

        template = InputFileTemplate(self.fullpath)
        self.assertEqual(template.product, "not valid")

    def test_validate_keeps_the_lowercase_sentinel(self):
        # validate() is what rewrote the sentinel. Reach it directly: a fresh template
        # whose product is anything unrecognized must come out as lowercase 'not valid'.
        template = InputFileTemplate()
        template.product = "something unrecognized"
        template.validate()
        self.assertEqual(template.product, "not valid")

    def test_unrecognized_file_loads_as_template(self):
        # the user-visible consequence: this used to raise
        # `ValueError: Not valid is not valid` out of InputFile.__new__.
        file = InputFile(self.fullpath)
        self.assertIsInstance(file, InputFileTemplate)
        self.assertEqual(file.product, "not valid")
        self.assertEqual(len(file.variables), 0)


class TestInputFileDispatch(unittest.TestCase):
    """InputFile.__new__ detects the product, dispatches to the class for it, and
    does both while reading each of the input file and the config exactly once.
    """

    def _counting_open(self, counter):
        real_open = builtins.open

        def counted(*args, **kwargs):
            counter.append(args[0] if args else kwargs.get("file"))
            return real_open(*args, **kwargs)

        return counted

    def test_reads_the_input_file_once(self):
        fullpath = folder_nnp / "only_variables.in"
        opened = []
        with unittest.mock.patch.object(builtins, "open", self._counting_open(opened)):
            InputFile(fullpath)
        reads = [p for p in opened if Path(p) == fullpath]
        # __new__ reads the text to detect the product and hands it to the class it
        # picks, so the load does not go back to disk for the same bytes.
        self.assertEqual(len(reads), 1)

    def test_does_not_read_the_config_file(self):
        # The file's config is a copy of the process-wide NNConfig, which is built once
        # per process and cached, so once it exists a construction must not go back to
        # disk for the config at all - neither for the returned object nor for product
        # detection. This used to be 'builds the config exactly once', back when every
        # input file re-read ~/.nextnanopy-config for itself.
        fullpath = folder_nnp / "only_variables.in"
        defaults.get_config()  # prime the cache; the first use is what may read a file
        reads = []
        real_read_file = defaults.NNConfig.read_file

        def counted(self):
            reads.append(self.fullpath)
            return real_read_file(self)

        with unittest.mock.patch.object(defaults.NNConfig, "read_file", counted):
            file = InputFile(fullpath)

        self.assertEqual(reads, [])
        # and it is a copy, so it still carries the values
        self.assertEqual(file.default_command_args, defaults.get_config().config["nextnano++"])

    def test_dispatches_on_product(self):
        # every product must reach its own InputFile class.
        cases = [
            (folder_nnp / "only_variables.in", "nextnano++"),
            (folder_nnp / "example.nnp", "nextnano++"),
            (folder_nn3 / "only_variables.in", "nextnano3"),
            (folder_nn3 / "example.nn3", "nextnano3"),
            (
                Path("tests") / "datafiles" / "nextnano.NEGF" / "example.xml",
                "nextnano.NEGF_classic",
            ),
            (Path("tests") / "datafiles" / "nextnano.MSB" / "example.msb", "nextnano.MSB"),
        ]
        for fullpath, product in cases:
            with self.subTest(fullpath=fullpath):
                file = InputFile(fullpath)
                self.assertEqual(file.product, product)
                self.assertIsInstance(file, defaults.get_InputFile(product))

    def test_no_fullpath_gives_a_bare_template(self):
        # with no path there is no text to detect from: InputFile() is an empty
        # InputFileTemplate carrying the 'not valid' sentinel. __new__ must not open None.
        file = InputFile()
        self.assertIsInstance(file, InputFileTemplate)
        self.assertEqual(file.product, "not valid")
        self.assertIsNone(file.fullpath)

    def test_parse_passes_through_positionally(self):
        # __new__ used to swallow a *args it never forwarded, so the third positional --
        # `parse` in InputFileTemplate.__init__ -- was silently dropped: InputFile(p, None,
        # True) returned an unparsed file with .content None and raised nothing.
        fullpath = folder_nnp / "example.nnp"
        file = InputFile(fullpath, None, True)
        self.assertTrue(file.parse)
        self.assertIsNotNone(file.content)

    def test_parse_passes_through_by_keyword(self):
        # the same parameter by its other spelling; this half always worked (it rode
        # **kwargs, which __new__ did forward), so it pins that the rewrite kept it.
        fullpath = folder_nnp / "example.nnp"
        file = InputFile(fullpath, parse=True)
        self.assertTrue(file.parse)
        self.assertIsNotNone(file.content)

    def test_unknown_keyword_is_rejected(self):
        # __new__ spells InputFileTemplate.__init__'s parameters out instead of taking
        # **kwargs, so a name that is not one of them must fail loudly, at __new__.
        with self.assertRaises(TypeError):
            InputFile(folder_nnp / "example.nnp", bogus=1)

    def test_text_builds_from_a_string_without_reading_disk(self):
        # InputFile(text=...) used to be a silent no-op: __init__ only called load() when
        # fullpath was not None, so the text was dropped and an empty template came back.
        # It must now detect the product from the text and parse it, opening no file.
        fullpath = folder_nnp / "only_variables.in"
        text = fullpath.read_text()
        opened = []
        with unittest.mock.patch.object(builtins, "open", self._counting_open(opened)):
            file = InputFile(text=text)
        self.assertIsInstance(file, defaults.get_InputFile("nextnano++"))
        self.assertEqual(file.product, "nextnano++")
        self.assertIsNone(file.fullpath)
        # the config may be read; the input file must not be -- there is no path to read.
        self.assertEqual([p for p in opened if "only_variables" in str(p)], [])
        # the point of the feature: same bytes in, same file out as loading from disk.
        from_disk = InputFile(fullpath)
        self.assertEqual(list(file.variables.keys()), list(from_disk.variables.keys()))
        self.assertEqual(
            [v.value for v in file.variables.values()],
            [v.value for v in from_disk.variables.values()],
        )

    def test_text_with_fullpath_names_the_file_without_reading_it(self):
        # `fullpath` is the name to save back to; `text` is the contents. This used to
        # raise `TypeError: got multiple values for keyword argument 'text'`, because
        # __new__ spliced its own text= into a **kwargs that already carried the caller's.
        fullpath = folder_nnp / "only_variables.in"
        text = (folder_nn3 / "only_variables.in").read_text()
        opened = []
        with unittest.mock.patch.object(builtins, "open", self._counting_open(opened)):
            file = InputFile(fullpath, text=text)
        # the text decides the product, not the (nnp) path it is named after.
        self.assertEqual(file.product, "nextnano3")
        self.assertEqual(Path(file.fullpath), fullpath)
        self.assertEqual([p for p in opened if Path(p) == fullpath], [])

    def test_text_that_matches_no_product_gives_a_template(self):
        # same contract as an unrecognized file on disk, reached through text=.
        file = InputFile(text="this is not a nextnano input file\n")
        self.assertIsInstance(file, InputFileTemplate)
        self.assertEqual(file.product, "not valid")
        self.assertEqual(len(file.variables), 0)

    def test_cannot_be_subclassed(self):
        # __new__ ignores cls and builds the class it detects, so a subclass used to come
        # back as a plain product InputFile: no MyInput instance, no my_helper, no error.
        # Defining the subclass is allowed; constructing one is what must raise.
        class MyInput(InputFile):
            def my_helper(self):
                return "hello"

        with self.assertRaises(TypeError) as ctx:
            MyInput(folder_nnp / "example.nnp")
        self.assertIn("InputFileTemplate", str(ctx.exception))

    def test_subclassing_the_product_class_still_works(self):
        # the escape hatch the TypeError points at must actually work.
        class MyNnpInput(defaults.get_InputFile("nextnano++")):
            def my_helper(self):
                return "hello"

        file = MyNnpInput(folder_nnp / "example.nnp")
        self.assertIsInstance(file, MyNnpInput)
        self.assertEqual(file.my_helper(), "hello")
        self.assertEqual(file.product, "nextnano++")


class TestConfigAtCreation(unittest.TestCase):
    """`InputFile(..., configpath=...)` chooses the config file the object runs on.

    The config is bound once, at construction: __init__ builds an NNConfig from
    `configpath` (or from the default path when it is None) and every later read of
    .default_command_args - which is what execute() turns into command line arguments -
    goes through that object. So `configpath` is the supported way to run one file
    against a config that is not the user's ~/.nextnanopy-config.
    """

    def write_config(self, **nnp_options):
        """Write a config file to a temp folder and return its path.

        NNConfig writes the full set of defaults out when the file does not exist yet,
        so what lands on disk is a complete config with these options overridden.
        """
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        fullpath = Path(folder.name) / "custom.nnconfig"
        config = defaults.NNConfig(fullpath)
        for option, value in nnp_options.items():
            config.set("nextnano++", option, value)
        config.save()
        return fullpath

    def fake_default_config_path(self):
        """Redirect the default config path at a temp folder for the current test.

        Two module globals have to move, and both are restored afterwards. NNConfig
        reads config_default_path when it is called, so patching it keeps the
        'configpath is None' tests off the developer's real ~/.nextnanopy-config - but
        get_config() builds at most one NNConfig per process, so a cache primed by an
        earlier test would hand back a config built from the real path and ignore the
        redirect entirely.
        """
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        fullpath = Path(folder.name) / ".nextnanopy-config"
        for attribute, value in [("config_default_path", fullpath), ("_config", None)]:
            patch = unittest.mock.patch.object(defaults, attribute, value)
            patch.start()
            self.addCleanup(patch.stop)
        return fullpath

    def test_configpath_is_used_instead_of_the_default(self):
        configpath = self.write_config(outputdirectory=r"C:\custom\out", threads=7)

        file = InputFile(folder_nnp / "only_variables.in", configpath=configpath)

        self.assertEqual(Path(file.configpath), configpath)
        self.assertEqual(Path(file.config.fullpath), configpath)
        self.assertNotEqual(Path(file.configpath), defaults.config_default_path)
        # the values the file will run on come from that file, not from the default one
        self.assertEqual(file.default_command_args["outputdirectory"], r"C:\custom\out")
        # and they are validated on the way in like any other config: threads is the
        # int 7, not the string configparser read back off disk.
        self.assertEqual(file.default_command_args["threads"], 7)

    def test_configpath_is_the_second_positional_parameter(self):
        # __new__ spells InputFileTemplate.__init__'s parameters out and forwards them
        # positionally, so the second positional must still be configpath.
        configpath = self.write_config(threads=7)

        file = InputFile(folder_nnp / "only_variables.in", configpath)

        self.assertEqual(Path(file.configpath), configpath)
        self.assertEqual(file.default_command_args["threads"], 7)

    def test_configpath_applies_when_building_from_text(self):
        # the config is independent of where the input came from: no file on disk, but
        # the object still runs on the config it was given.
        configpath = self.write_config(threads=7)
        text = (folder_nnp / "only_variables.in").read_text()

        file = InputFile(text=text, configpath=configpath)

        self.assertEqual(file.product, "nextnano++")
        self.assertEqual(Path(file.configpath), configpath)
        self.assertEqual(file.default_command_args["threads"], 7)

    def test_each_file_gets_its_own_config(self):
        # two files, two configs: neither the objects nor their values are shared, so
        # setting one file's config cannot reach the other.
        first_path = self.write_config(threads=7)
        second_path = self.write_config(threads=3)

        first = InputFile(folder_nnp / "only_variables.in", configpath=first_path)
        second = InputFile(folder_nnp / "only_variables.in", configpath=second_path)

        self.assertIsNot(first.config, second.config)
        self.assertEqual(first.default_command_args["threads"], 7)
        self.assertEqual(second.default_command_args["threads"], 3)

    def test_configpath_none_uses_the_default_config_file(self):
        fake_default = self.fake_default_config_path()

        file = InputFile(folder_nnp / "only_variables.in")

        self.assertEqual(Path(file.configpath), fake_default)

    def test_configpath_that_does_not_exist_yet_is_created_with_the_defaults(self):
        # NNConfig bootstraps a missing file rather than failing, so a fresh configpath
        # is a usable one: the file comes up on the defaults and the config now exists.
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        configpath = Path(folder.name) / "not_written_yet.nnconfig"

        file = InputFile(folder_nnp / "only_variables.in", configpath=configpath)

        self.assertTrue(configpath.is_file())
        self.assertEqual(Path(file.configpath), configpath)
        self.assertEqual(
            file.default_command_args["threads"],
            defaults.PRODUCTS["nextnano++"].config_default["threads"],
        )

    def test_empty_configpath_raises(self):
        # None means 'use the default path'; an empty path is a caller bug, and must
        # not be silently read as the default.
        with self.assertRaises(ValueError):
            InputFile(folder_nnp / "only_variables.in", configpath="")


class TestConfigFromTheGlobalConfig(unittest.TestCase):
    """`nn.config.set(...)` before `InputFile(...)` reaches the new file.

    Configure the process-wide config in the script, then build the input files and run
    them - the workflow templates/config_nextnano.py teaches. No `save()` is needed for
    it: an input file built with no configpath copies `nn.config` as it stands, so a
    `set()` alone carries. Saving is for other processes.

    A copy, not the object itself, which is what the last two tests are for. The two
    halves of 'bound at construction' - a new file sees the change, an existing one
    does not - only both hold if the file took a snapshot; sharing the global object
    would break the second, and re-reading the file from disk (as this did before)
    breaks the first.
    """

    SENTINEL = r"C:\sentinel\never-a-real-outputdirectory"

    def global_config(self):
        """The real process-wide config, restored after the test.

        Mutating it in memory is safe - save() is never called here, so the user's
        ~/.nextnanopy-config is only ever read - but it outlives the test, hence the
        cleanup: Test_nnp.test_config asserts a file agrees with this same object.
        """
        config = nextnanopy.get_config()
        original = config.get("nextnano++", "outputdirectory")
        self.addCleanup(config.set, "nextnano++", "outputdirectory", original)
        return config

    def test_set_on_the_global_config_reaches_a_new_input_file(self):
        config = self.global_config()
        config.set("nextnano++", "outputdirectory", self.SENTINEL)

        file = InputFile(folder_nnp / "only_variables.in")

        self.assertEqual(
            file.default_command_args["outputdirectory"],
            self.SENTINEL,
            "the value set on nn.config did not reach a file built after it, so"
            " execute() would run this file on a stale outputdirectory",
        )

    def test_set_on_the_global_config_reaches_the_files_a_sweep_creates(self):
        # A sweep builds input files of its own, and they must agree with the sweep's
        # own prototype: they used to be handed the resolved .configpath, which made
        # them read the config file from disk and miss this.
        self.addCleanup(
            delete_files,
            "only_variables",
            directory=folder_nnp,
            exceptions=["only_variables.in"],
        )
        config = self.global_config()
        config.set("nextnano++", "outputdirectory", self.SENTINEL)

        sweep = Sweep({"float": [1, 2]}, folder_nnp / "only_variables.in")
        sweep.save_sweep()

        self.assertEqual(sweep.config.get("nextnano++", "outputdirectory"), self.SENTINEL)
        self.assertEqual(len(sweep.input_files), 2)
        for input_file in sweep.input_files:
            self.assertEqual(input_file.default_command_args["outputdirectory"], self.SENTINEL)

    def test_the_config_is_bound_at_construction(self):
        # The design, stated in one test: a file takes the config as it stands when it
        # is built. Changing nn.config afterwards does not reach back into files that
        # already exist - it applies to the next one built.
        config = self.global_config()
        before = InputFile(folder_nnp / "only_variables.in")

        config.set("nextnano++", "outputdirectory", self.SENTINEL)
        after = InputFile(folder_nnp / "only_variables.in")

        self.assertEqual(after.default_command_args["outputdirectory"], self.SENTINEL)
        self.assertNotEqual(before.default_command_args["outputdirectory"], self.SENTINEL)

    def test_a_files_config_is_its_own_copy(self):
        # Why a copy rather than the shared global object: editing one file's config
        # must not reach nn.config, nor any other input file.
        config = self.global_config()
        file = InputFile(folder_nnp / "only_variables.in")
        original = config.get("nextnano++", "outputdirectory")

        file.config.set("nextnano++", "outputdirectory", self.SENTINEL)
        other = InputFile(folder_nnp / "only_variables.in")

        self.assertIsNot(file.config, config)
        self.assertEqual(config.get("nextnano++", "outputdirectory"), original)
        self.assertEqual(other.default_command_args["outputdirectory"], original)

    def test_explicit_configpath_still_wins_over_the_global_config(self):
        # An explicit configpath stays authoritative: it names a config file to read,
        # and the global config must not leak into it.
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        configpath = Path(folder.name) / "explicit.nnconfig"
        explicit = defaults.NNConfig(configpath)
        explicit.set("nextnano++", "outputdirectory", r"C:\explicit\out")
        explicit.save()

        config = self.global_config()
        config.set("nextnano++", "outputdirectory", self.SENTINEL)

        file = InputFile(folder_nnp / "only_variables.in", configpath=configpath)

        self.assertEqual(file.default_command_args["outputdirectory"], r"C:\explicit\out")


class TestSweep(unittest.TestCase):
    def test_init(self):
        self.assertRaises(TypeError, Sweep)
        sweep = Sweep({})
        self.assertEqual(sweep.fullpath, None)
        self.assertEqual(sweep.var_sweep, {})
        self.assertRaises(ValueError, Sweep, {"Name": "some_name"})

    def test_nnp_init(self):
        fullpath = folder_nnp / "only_variables.in"
        self.assertRaises(ValueError, Sweep, {"Name": "some_name"}, fullpath)

        sweep = Sweep({}, fullpath)
        self.assertEqual(Path(sweep.fullpath), fullpath)
        self.assertEqual(sweep.var_sweep, {})
        self.assertFalse(sweep.input_files)
        self.assertFalse(sweep.sweep_output_directory)

        self.assertRaises(ValueError, Sweep, {"float": 1})
        self.assertRaises(TypeError, Sweep, {"float": 1}, fullpath)

        sweep = Sweep({"float": [1, 2, 5]}, fullpath)
        self.assertEqual(Path(sweep.fullpath), fullpath)
        self.assertEqual(sweep.var_sweep["float"], [1, 2, 5])

        self.addCleanup(
            delete_files,
            "only_variables",
            directory=folder_nnp,
            exceptions=["only_variables.in"],
        )

    def test_nnp_mkdir(self):
        fullpath = folder_nnp / "only_variables.in"
        sweep = Sweep({}, fullpath=fullpath)
        sweep.config.set("nextnano++", "outputdirectory", r"tests//outputs")
        created_directory = sweep.mk_dir(overwrite=True)
        self.assertTrue(
            Path(created_directory).samefile(Path("tests") / "outputs" / "only_variables_sweep")
        )
        self.assertTrue((Path("tests") / "outputs" / "only_variables_sweep").is_dir())

        self.addCleanup((Path("tests") / "outputs" / "only_variables_sweep").rmdir)
        self.addCleanup(
            delete_files,
            "only_variables",
            directory=folder_nnp,
            exceptions=["only_variables.in"],
        )

    def test_nnp_mkdir_specify(self):
        fullpath = folder_nnp / "only_variables.in"
        sweep = Sweep({}, fullpath=fullpath)
        created_directory = sweep.mk_dir(overwrite=True, output_directory=r"tests//outputs")
        self.assertTrue(
            Path(created_directory).samefile(Path("tests") / "outputs" / "only_variables_sweep")
        )
        self.assertTrue((Path("tests") / "outputs" / "only_variables_sweep").is_dir())

        self.addCleanup((Path("tests") / "outputs" / "only_variables_sweep").rmdir)
        self.addCleanup(
            delete_files,
            "only_variables",
            directory=folder_nnp,
            exceptions=["only_variables.in"],
        )

    def test_nnp_save(self):
        self.addCleanup(
            delete_files,
            "only_variables",
            directory=folder_nnp,
            exceptions=["only_variables.in"],
        )
        fullpath = folder_nnp / "only_variables.in"
        sweep = Sweep({"float": [1, 2], "str": ["test1", "test2"]}, fullpath)
        sweep.save_sweep()

        files_with_names = [p.name for p in folder_nnp.iterdir() if "only_variables" in p.name]
        self.assertEqual(len(files_with_names), 5)
        self.assertTrue((folder_nnp / "only_variables__float_2_str_test1_.in").is_file())

    def test_nnp_save_temp(self):
        self.addCleanup(
            delete_files,
            "only_variables",
            directory=folder_nnp,
            exceptions=["only_variables.in"],
        )

        fullpath = folder_nnp / "only_variables.in"
        sweep = Sweep({"float": [1, 2], "str": ["test1", "test2"]}, fullpath)
        sweep.save_sweep(temp=True)

        files_with_names = [file for file in os.listdir(folder_nnp) if "only_variables" in file]
        self.assertEqual(len(files_with_names), 1)
        self.assertFalse((folder_nnp / "only_variables__float_2_str_test1_.in").is_file())

    # nn3 section
    def test_nn3_init(self):
        fullpath = folder_nn3 / "only_variables.in"
        self.assertRaises(ValueError, Sweep, {"Name": "some_name"}, fullpath)

        sweep = Sweep({}, fullpath)
        self.assertEqual(Path(sweep.fullpath), fullpath)
        self.assertEqual(sweep.var_sweep, {})
        self.assertFalse(sweep.input_files)
        self.assertFalse(sweep.sweep_output_directory)

        self.assertRaises(ValueError, Sweep, {"float": 1})
        self.assertRaises(TypeError, Sweep, {"float": 1}, fullpath)

        sweep = Sweep({"float": [1, 2, 5]}, fullpath)
        self.assertEqual(Path(sweep.fullpath), fullpath)
        self.assertEqual(sweep.var_sweep["float"], [1, 2, 5])

        self.addCleanup(
            delete_files,
            "only_variables",
            directory=folder_nn3,
            exceptions=["only_variables.in"],
        )

    def test_nn3_mkdir(self):
        fullpath = folder_nn3 / "only_variables.in"
        sweep = Sweep({}, fullpath=fullpath)
        sweep.config.set("nextnano3", "outputdirectory", r"tests//outputs")
        created_directory = sweep.mk_dir(overwrite=True)
        self.assertTrue(
            Path(created_directory).samefile(Path("tests") / "outputs" / "only_variables_sweep")
        )
        self.assertTrue((Path("tests") / "outputs" / "only_variables_sweep").is_dir())

        self.addCleanup((Path("tests") / "outputs" / "only_variables_sweep").rmdir)
        self.addCleanup(
            delete_files,
            "only_variables",
            directory=folder_nn3,
            exceptions=["only_variables.in"],
        )

    def test_nn3_save(self):
        self.addCleanup(
            delete_files,
            "only_variables",
            directory=folder_nn3,
            exceptions=["only_variables.in"],
        )
        fullpath = folder_nn3 / "only_variables.in"
        sweep = Sweep({"float": [1, 2], "str": ["test1", "test2"]}, fullpath)
        sweep.save_sweep()

        files_with_names = [p.name for p in folder_nn3.iterdir() if "only_variables" in p.name]
        self.assertEqual(len(files_with_names), 5)
        self.assertTrue((folder_nn3 / "only_variables__float_2_str_test1_.in").is_file())

    # --- 2.13: Sweep composes an InputFile instead of inheriting one ---

    def test_composes_single_input_file(self):
        # The prototype must be parsed exactly once. The old design built a
        # throwaway InputFile *and* re-parsed via the base-class __init__, so
        # the input file was read multiple times before the sweep did anything.
        fullpath = folder_nnp / "only_variables.in"
        real_load_raw = InputFileTemplate.load_raw
        calls = []

        def counting_load_raw(self, *args, **kwargs):
            calls.append(self.fullpath)
            return real_load_raw(self, *args, **kwargs)

        with unittest.mock.patch.object(InputFileTemplate, "load_raw", counting_load_raw):
            sweep = Sweep({"float": [1, 2, 5]}, fullpath)

        prototype_reads = [c for c in calls if Path(c) == fullpath]
        self.assertEqual(len(prototype_reads), 1)
        # InputFile.__new__ returns the product-specific subclass (nnp/nn3/...),
        # which inherits from InputFileTemplate, not the base InputFile itself.
        self.assertIsInstance(sweep.input_file, InputFileTemplate)
        # Variables are validated against the real, parsed prototype.
        self.assertIn("float", sweep.input_file.variables.keys())

    def test_does_not_expose_input_file_api(self):
        # A Sweep is-a-sweep, not an input file: the inherited, nonsensical
        # surface must be gone so a future accidental re-inheritance fails here.
        fullpath = folder_nnp / "only_variables.in"
        sweep = Sweep({}, fullpath)
        self.assertNotIsInstance(sweep, InputFileTemplate)
        for attr in ("check_convergence", "set_variable", "get_variable", "load"):
            self.assertFalse(hasattr(sweep, attr), f"Sweep should not expose {attr!r}")
        # The forwarded, still-needed members remain available.
        self.assertEqual(Path(sweep.fullpath), fullpath)
        self.assertEqual(sweep.product, sweep.input_file.product)
        self.assertIs(sweep.config, sweep.input_file.config)

    def test_execute_and_save_mirror_the_sweep_methods(self):
        # `execute`/`save` exist, but as sweep-level mirrors of
        # execute_sweep/save_sweep - NOT the old inherited input-file methods.
        fullpath = folder_nnp / "only_variables.in"
        sweep = Sweep({}, fullpath)
        with unittest.mock.patch.object(Sweep, "save_sweep") as mock_save:
            sweep.save("a", b=1)
            mock_save.assert_called_once_with("a", b=1)
        with unittest.mock.patch.object(Sweep, "execute_sweep") as mock_execute:
            sweep.execute("a", b=1)
            mock_execute.assert_called_once_with("a", b=1)

    # TODO test parallel sweeps with and without convergenceCheck
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        sweep_dir = Path("tests") / "outputs" / "only_variables_sweep"
        if sweep_dir.is_dir():
            sweep_dir.rmdir()
        delete_files("only_variables", directory=folder_nnp, exceptions=["only_variables.in"])
        delete_files("only_variables", directory=folder_nn3, exceptions=["only_variables.in"])

    def test_conditional_sweep(self):
        self.addCleanup(
            delete_files,
            "only_variables",
            directory=folder_nnp,
            exceptions=["only_variables.in"],
        )

        def condition(combination):
            return combination[0] > 0.2

        fullpath = folder_nnp / "only_variables.in"
        sweep = Sweep(
            {"float": [0.1, 0.2, 0.3, 0.4, 0.5]},
            fullpath,
        )

        sweep.save_sweep(variables_comb_screen_fn=condition)

        self.assertEqual(len(sweep.input_files), 3)

        for combination in sweep.sweep_infodict.values():
            combination = list(combination.values())
            assert combination[0] > 0.2

    def test_conditional_sweep_multivar(self):
        self.addCleanup(
            delete_files,
            "only_variables",
            directory=folder_nnp,
            exceptions=["only_variables.in"],
        )

        def condition(combination):
            return combination[1] > combination[0]

        fullpath = folder_nnp / "only_variables.in"
        sweep = Sweep(
            {"float": [0.5, 1.5, 2.5], "int": [1, 2, 3]},
            fullpath,
        )
        sweep.save_sweep(variables_comb_screen_fn=condition)

        self.assertEqual(len(sweep.input_files), 6)

        for combination in sweep.sweep_infodict.values():
            combination = list(combination.values())
            self.assertTrue(combination[1] > combination[0])


class Test_check_convergence_pause_tty(unittest.TestCase):
    """check_convergence(mode='pause') must never block on input() without a TTY.

    Headless runs (CI, cluster jobs, the ExecutionQueue worker thread) have no
    usable stdin; 'pause' must degrade to 'terminate' there instead of hanging.
    """

    NOT_CONVERGED = "Maximum number of iterations exceeded\n"

    def make_file(self, log_text):
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)
        log = Path(tmpdir.name) / "sim.log"
        log.write_text(log_text)
        file = InputFile(folder_nnp / "only_variables.in")
        file.execute_info = {"logfile": str(log)}
        return file

    def test_pause_without_tty_terminates_instead_of_prompting(self):
        file = self.make_file(self.NOT_CONVERGED)
        stdin = unittest.mock.Mock()
        stdin.isatty.return_value = False
        prompt = unittest.mock.Mock(side_effect=AssertionError("input() called without a TTY"))
        with (
            unittest.mock.patch("sys.stdin", stdin),
            unittest.mock.patch("builtins.input", prompt),
        ):
            with self.assertRaises(RuntimeError):
                file.check_convergence(mode="pause")
        prompt.assert_not_called()

    def test_pause_with_stdin_none_terminates(self):
        # sys.stdin is None under pythonw / some embedded interpreters
        file = self.make_file(self.NOT_CONVERGED)
        with unittest.mock.patch("sys.stdin", None):
            with self.assertRaises(RuntimeError):
                file.check_convergence(mode="pause")

    def test_pause_with_tty_still_prompts(self):
        file = self.make_file(self.NOT_CONVERGED)
        stdin = unittest.mock.Mock()
        stdin.isatty.return_value = True
        with (
            unittest.mock.patch("sys.stdin", stdin),
            unittest.mock.patch("builtins.input", return_value="y") as prompt,
        ):
            self.assertIsNone(file.check_convergence(mode="pause"))
        prompt.assert_called()

        with (
            unittest.mock.patch("sys.stdin", stdin),
            unittest.mock.patch("builtins.input", return_value="n"),
        ):
            with self.assertRaises(RuntimeError):
                file.check_convergence(mode="pause")

    def test_converged_log_never_prompts(self):
        file = self.make_file("everything fine\n")
        prompt = unittest.mock.Mock(side_effect=AssertionError("input() called for converged log"))
        with unittest.mock.patch("builtins.input", prompt):
            self.assertIsNone(file.check_convergence(mode="pause"))


class TestExecuteOutputDirectoryParams(unittest.TestCase):
    """`overwrite` and `create_subdirectory` are execute() parameters, not command args.

    Where the output goes is nextnanopy's own business, so both are named parameters
    of InputFile.execute() rather than members of **kwargs: **kwargs is the set of
    arguments handed to the simulator as they are, and it is also where a misspelled
    keyword would disappear without a word. They are not configuration options
    either - the config file holds command line arguments (plus the outputdirectory
    they are resolved against), so nothing there needs to know about them.

    commands.execute() is patched out here: what it does with the two values is
    covered by TestExecuteOutputDirectory in test_commands.py, so these tests only
    check that they arrive.
    """

    def setUp(self):
        patch = unittest.mock.patch("nextnanopy.inputs.cmd_execute", return_value={})
        self.cmd_execute = patch.start()
        self.addCleanup(patch.stop)

    def passed_to_commands(self):
        _args, kwargs = self.cmd_execute.call_args
        return kwargs

    def test_both_are_named_parameters_of_execute(self):
        parameters = inspect.signature(InputFile.execute).parameters
        self.assertEqual(parameters["overwrite"].default, False)
        self.assertEqual(parameters["create_subdirectory"].default, True)

    def test_the_defaults_are_a_subdirectory_per_file_that_no_run_writes_over(self):
        # overwrite=False like .save() and Sweep.execute_sweep(); the always-reuse
        # behaviour of earlier versions is now overwrite=True.
        InputFile(folder_nnp / "only_variables.in").execute()

        passed = self.passed_to_commands()
        self.assertEqual(passed["overwrite"], False)
        self.assertEqual(passed["create_subdirectory"], True)

    def test_values_are_forwarded(self):
        InputFile(folder_nnp / "only_variables.in").execute(
            overwrite=True, create_subdirectory=False
        )

        passed = self.passed_to_commands()
        self.assertEqual(passed["overwrite"], True)
        self.assertEqual(passed["create_subdirectory"], False)

    def test_neither_is_a_config_option(self):
        # .default_command_args is the config section verbatim, and every entry in it
        # becomes a command line argument, so these two must stay out of it.
        file = InputFile(folder_nnp / "only_variables.in")

        self.assertNotIn("overwrite", file.default_command_args)
        self.assertNotIn("create_subdirectory", file.default_command_args)


class TestTempSaveKeepsTheWorkingDirectory(unittest.TestCase):
    """A file saved with temp=True still runs where the user keeps it.

    execute() runs the simulator in the folder of the input file, so a temp copy
    would otherwise run in the temporary folder: a different place on every run,
    gone at interpreter exit, and nowhere near the files an input file may refer
    to relatively. save(temp=True) therefore records the folder it came from in
    .wdir, which execute() uses as its default.

    commands.execute() is patched out; what it does with the value is covered by
    TestExecuteWorkingDirectory in test_commands.py.
    """

    def setUp(self):
        patch = unittest.mock.patch("nextnanopy.inputs.cmd_execute", return_value={})
        self.cmd_execute = patch.start()
        self.addCleanup(patch.stop)
        self.origin = (folder_nnp).resolve()

    def passed_wdir(self):
        return self.cmd_execute.call_args.kwargs["wdir"]

    def input_file(self):
        return InputFile(folder_nnp / "only_variables.in")

    def test_a_plain_file_has_none_and_follows_itself(self):
        # None is what tells commands.execute() to use the input file's own folder
        file = self.input_file()

        self.assertIsNone(file.wdir)
        file.execute()
        self.assertIsNone(self.passed_wdir())

    def test_a_temp_save_records_the_folder_it_came_from(self):
        file = self.input_file()

        file.save(temp=True, overwrite=True)

        self.assertEqual(Path(file.wdir), self.origin)
        # the file itself did move
        self.assertNotEqual(Path(file.fullpath).parent, self.origin)
        file.execute()
        self.assertEqual(Path(self.passed_wdir()), self.origin)

    def test_a_second_temp_save_keeps_the_original_folder(self):
        # by then fullpath is in the temporary folder, which is not where it came from
        file = self.input_file()

        file.save(temp=True, overwrite=True)
        file.save(temp=True, overwrite=True)

        self.assertEqual(Path(file.wdir), self.origin)

    def test_an_explicit_wdir_wins(self):
        file = self.input_file()
        file.save(temp=True, overwrite=True)

        file.execute(wdir=folder_nn3)

        self.assertEqual(self.passed_wdir(), folder_nn3)

    def test_a_caller_set_wdir_survives_a_temp_save(self):
        file = self.input_file()
        file.wdir = folder_nn3

        file.save(temp=True, overwrite=True)

        self.assertEqual(file.wdir, folder_nn3)

    def test_a_swept_file_runs_where_the_swept_input_file_is(self):
        sweep = Sweep({"float": [1, 2]}, folder_nnp / "only_variables.in")

        sweep.save_sweep(temp=True)

        self.assertEqual(len(sweep.input_files), 2)
        for file in sweep.input_files:
            # written into the temporary folder, but pointed back at the original one
            self.assertNotEqual(Path(file.fullpath).parent, self.origin)
            self.assertEqual(Path(file.wdir), self.origin)

    def test_a_sweep_without_temp_leaves_it_alone(self):
        sweep = Sweep({"float": [1, 2]}, folder_nnp / "only_variables.in")
        self.addCleanup(delete_files, "only_variables__", folder_nnp)

        sweep.save_sweep()

        for file in sweep.input_files:
            self.assertIsNone(file.wdir)


class TestSweepForwardsOverwrite(unittest.TestCase):
    """execute_sweep(overwrite=...) reaches the individual simulations.

    It already decides whether the sweep folder is reused or created fresh; the
    same answer has to reach each input file underneath, otherwise a sweep run with
    overwrite=False still clobbers per-file output whenever the folder it writes into
    is one an earlier run already used (separate_sweep_dir=False, or a reused sweep
    folder). The per-file subdirectory itself is never switched off for a sweep: it
    is the only thing keeping the sweep points apart.
    """

    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.outputdirectory = Path(folder.name)

        # InputFileTemplate, not InputFile: the sweep's files are product classes,
        # which are siblings of InputFile and inherit execute() from the template.
        # autospec=True so the file being executed is recorded with the call.
        patch = unittest.mock.patch.object(
            InputFileTemplate, "execute", autospec=True, side_effect=self.fake_execute
        )
        self.execute = patch.start()
        self.addCleanup(patch.stop)

    def fake_execute(self, input_file, **kwargs):
        """Stand in for InputFile.execute() without running anything.

        The real one stores the output directory in .execute_info, which
        execute_sweep() reads back through .folder_output once every file is done.
        """
        input_file.execute_info = self.output_info(input_file)
        return input_file.execute_info

    def output_info(self, input_file):
        return {"outputdirectory": self.outputdirectory / input_file.filename_only}

    def make_sweep(self):
        sweep = Sweep({"float": [1, 2]}, folder_nnp / "only_variables.in")
        # temp=True keeps the generated input files out of the test data folder
        sweep.save_sweep(temp=True)
        return sweep

    def test_each_input_file_gets_the_sweep_overwrite_value(self):
        sweep = self.make_sweep()

        sweep.execute_sweep(overwrite=False, outputdirectory=self.outputdirectory)

        self.assertEqual(self.execute.call_count, 2)
        for call in self.execute.call_args_list:
            self.assertEqual(call.kwargs["overwrite"], False)
            self.assertEqual(call.kwargs.get("create_subdirectory", True), True)

    def test_overwrite_true_is_forwarded_too(self):
        sweep = self.make_sweep()

        sweep.execute_sweep(overwrite=True, outputdirectory=self.outputdirectory)

        self.assertEqual(self.execute.call_count, 2)
        for call in self.execute.call_args_list:
            self.assertEqual(call.kwargs["overwrite"], True)

    def test_the_parallel_branch_forwards_it_as_well(self):
        # parallel_limit > 1 runs the files through an ExecutionQueue, which passes
        # the kwargs it was built with to every InputFile.execute() it starts.
        sweep = self.make_sweep()
        for input_file in sweep.input_files:
            # the queue is mocked away, so nothing sets this along the way
            input_file.execute_info = self.output_info(input_file)

        with unittest.mock.patch("nextnanopy.inputs.ExecutionQueue") as queue:
            sweep.execute_sweep(
                overwrite=False, parallel_limit=2, outputdirectory=self.outputdirectory
            )

        self.assertEqual(queue.call_args.kwargs["overwrite"], False)


if __name__ == "__main__":
    unittest.main()

    file = folder_nnp / "only_variables.in"
    fi = InputFile(file)
    text = fi.text
