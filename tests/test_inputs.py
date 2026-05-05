import unittest
import os
import tempfile
from pathlib import Path
from nextnanopy.inputs import InputFile, Sweep


def delete_files(start, directory=Path.cwd(), exceptions=None):
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
        self.assertEqual(file.variables["float"].value, float(0.0))
        self.assertEqual(file.variables["float"].comment, "float number (a.u.)")

        self.assertEqual(file.variables["int"].name, "int")
        self.assertEqual(file.variables["int"].value, int(0))
        self.assertEqual(file.variables["int"].comment, "int number (random = 3)")

        self.assertEqual(file.variables["str"].name, "str")
        self.assertEqual(file.variables["str"].value, '"test"')
        self.assertEqual(
            file.variables["str"].comment, "first comments # second comment"
        )

        self.assertEqual(file.variables["reference"].name, "reference")
        self.assertEqual(file.variables["reference"].value, "$int - 1")

        self.assertEqual(file.variables["NoSpacing"].name, "NoSpacing")
        self.assertEqual(file.variables["NoSpacing"].value, int("7"))
        self.assertEqual(file.variables["NoSpacing"].comment, "this is a comment")
        self.assertEqual(
            file.variables["NoSpacing"].text, "$NoSpacing = 7 # this is a comment"
        )

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
        file.set_variable(
            "float", 1e-5, "some comment", "some unit"
        )  # unit is not visible in nn++

        self.assertEqual(file.variables["float"].name, "float")
        self.assertEqual(file.variables["float"].value, 1e-5)
        self.assertEqual(file.variables["float"].comment, "some comment")
        self.assertEqual(
            file.variables["float"].text, f"$float = {str(1e-5)} # some comment"
        )
        self.assertEqual(file.lines[3], f"$float = {str(1e-5)} # some comment")

        file.set_variable("float", value=1e-7)
        self.assertEqual(file.variables["float"].name, "float")
        self.assertEqual(file.variables["float"].value, 1e-7)
        self.assertEqual(file.variables["float"].comment, "some comment")
        self.assertEqual(
            file.variables["float"].text, f"$float = {str(1e-7)} # some comment"
        )
        self.assertEqual(file.lines[3], f"$float = {str(1e-7)} # some comment")

        file.set_variable("float", comment="new comment")
        self.assertEqual(file.variables["float"].name, "float")
        self.assertEqual(file.variables["float"].value, 1e-7)
        self.assertEqual(file.variables["float"].comment, "new comment")
        self.assertEqual(
            file.variables["float"].text, f"$float = {str(1e-7)} # new comment"
        )
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
        fullpath_example = folder_nnp / "example.in"
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
        self.assertEqual(file.variables["float"].value, float(0.0))
        self.assertEqual(file.variables["float"].comment, "float number (a.u.)")

        self.assertEqual(file.variables["int"].name, "int")
        self.assertEqual(file.variables["int"].value, int(0))
        self.assertEqual(file.variables["int"].comment, "int number (random = 3)")

        self.assertEqual(file.variables["str"].name, "str")
        self.assertEqual(file.variables["str"].value, '"test"')
        self.assertEqual(
            file.variables["str"].comment, "first comments # second comment"
        )

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
        self.assertEqual(
            file.variables["float"].text, f"%float = {str(1e-5)} ! some comment"
        )
        self.assertEqual(file.lines[3], f"%float = {str(1e-5)} ! some comment")

        file.set_variable("float", value=1e-7)
        self.assertEqual(file.variables["float"].name, "float")
        self.assertEqual(file.variables["float"].value, 1e-7)
        self.assertEqual(file.variables["float"].comment, "some comment")
        self.assertEqual(
            file.variables["float"].text, f"%float = {str(1e-7)} ! some comment"
        )
        self.assertEqual(file.lines[3], f"%float = {str(1e-7)} ! some comment")

        file.set_variable("float", comment="new comment")
        self.assertEqual(file.variables["float"].name, "float")
        self.assertEqual(file.variables["float"].value, 1e-7)
        self.assertEqual(file.variables["float"].comment, "new comment")
        self.assertEqual(
            file.variables["float"].text, f"%float = {str(1e-7)} ! new comment"
        )
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
        self.assertRaises(
            FileNotFoundError, file.save, new_file, overwrite=True, automkdir=False
        )
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
        fullpath_example = folder_nn3 / "example.in"
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
        self.assertEqual(file.variables["variable1"].value, float(0.24))
        self.assertEqual(file.variables["variable1"].comment, "Some comment")
        self.assertEqual(file.variables["variable1"].unit, "")

        self.assertEqual(file.variables["variable2"].name, "variable2")
        self.assertEqual(file.variables["variable2"].value, int(0))
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
        self.assertEqual(file.variables["variable1"].value, float(0.137))
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
        self.assertRaises(
            FileNotFoundError, file.save, new_file, overwrite=True, automkdir=False
        )
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


class Test_negf(unittest.TestCase):
    # TODO: implement test for NEGF++ input file
    def test_load(self):
        fullpath = folder_negf / "Minimal_InputFile.negf"

        file = InputFile(fullpath)
        self.assertEqual(file.product, "nextnano.NEGF")

        self.assertEqual(len(file.variables.keys()), 1)
        self.assertEqual(file.variables["alloyComposition"].name, "alloyComposition")
        self.assertAlmostEqual(
            file.variables["alloyComposition"].value, float(0.15), delta=1e-9
        )
        self.assertEqual(
            file.variables["alloyComposition"].comment, "alloy composition"
        )

        fullpath = folder_nnp / "virtual_file.in"
        self.assertRaises(FileNotFoundError, InputFile, fullpath)

    def test_get_variables(self):
        fullpath = folder_negf / "Minimal_InputFile.negf"
        file = InputFile(fullpath)

        self.assertEqual(
            file.variables["alloyComposition"], file.get_variable("alloyComposition")
        )
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
        self.assertEqual(
            file.lines[0], f"$alloyComposition = {str(1e-5)} # some comment"
        )

        file.set_variable("alloyComposition", value=1e-7)
        self.assertEqual(file.variables["alloyComposition"].name, "alloyComposition")
        self.assertEqual(file.variables["alloyComposition"].value, 1e-7)
        self.assertEqual(file.variables["alloyComposition"].comment, "some comment")
        self.assertEqual(
            file.variables["alloyComposition"].text,
            f"$alloyComposition = {str(1e-7)} # some comment",
        )
        self.assertEqual(
            file.lines[0], f"$alloyComposition = {str(1e-7)} # some comment"
        )

        file.set_variable("alloyComposition", comment="new comment")
        self.assertEqual(file.variables["alloyComposition"].name, "alloyComposition")
        self.assertEqual(file.variables["alloyComposition"].value, 1e-7)
        self.assertEqual(file.variables["alloyComposition"].comment, "new comment")
        self.assertEqual(
            file.variables["alloyComposition"].text,
            f"$alloyComposition = {str(1e-7)} # new comment",
        )
        self.assertEqual(
            file.lines[0], f"$alloyComposition = {str(1e-7)} # new comment"
        )

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

        self.assertEqual(
            input_file.variables["Well"].value,
            0.14
        )

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
            Path(created_directory).samefile(
                Path("tests") / "outputs" / "only_variables_sweep"
            )
        )
        self.assertTrue(
            (Path("tests") / "outputs" / "only_variables_sweep").is_dir()
        )

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
            Path(created_directory).samefile(
                Path("tests") / "outputs" / "only_variables_sweep"
            )
        )
        self.assertTrue(
            (Path("tests") / "outputs" / "only_variables_sweep").is_dir()
        )

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

        files_with_names = [
            p.name for p in folder_nnp.iterdir() if "only_variables" in p.name
        ]
        self.assertEqual(len(files_with_names), 5)
        self.assertTrue(
            (folder_nnp / "only_variables__float_2_str_test1_.in").is_file()
        )

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

        files_with_names = [
            file for file in os.listdir(folder_nnp) if "only_variables" in file
        ]
        self.assertEqual(len(files_with_names), 1)
        self.assertFalse(
            (folder_nnp / "only_variables__float_2_str_test1_.in").is_file()
        )


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
            Path(created_directory).samefile(
                Path("tests") / "outputs" / "only_variables_sweep"
            )
        )
        self.assertTrue(
            (Path("tests") / "outputs" / "only_variables_sweep").is_dir()
        )

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

        files_with_names = [
            p.name for p in folder_nn3.iterdir() if "only_variables" in p.name
        ]
        self.assertEqual(len(files_with_names), 5)
        self.assertTrue(
            (folder_nn3 / "only_variables__float_2_str_test1_.in").is_file()
        )

    # TODO test parallel sweeps with and without convergenceCheck
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        sweep_dir = Path("tests") / "outputs" / "only_variables_sweep"
        if sweep_dir.is_dir():
            sweep_dir.rmdir()
        delete_files(
            "only_variables", directory=folder_nnp, exceptions=["only_variables.in"]
        )
        delete_files(
            "only_variables", directory=folder_nn3, exceptions=["only_variables.in"]
        )

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
            combination[0] > 0.2

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


if __name__ == "__main__":
    unittest.main()

    file = folder_nnp / "only_variables.in"
    fi = InputFile(file)
    text = fi.text
