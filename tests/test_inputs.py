import unittest
import os
from nextnanopy.inputs import InputFile, Sweep


def delete_files(start, directory=os.getcwd(), exceptions=None):
    for fname in os.listdir(directory):
        if fname.startswith(start):
            if exceptions:
                if fname in exceptions:
                    continue
                else:
                    os.remove(os.path.join(directory, fname))
            else:
                os.remove(os.path.join(directory, fname))


folder_nnp = os.path.join("tests", "datafiles", "nextnano++")
folder_nn3 = os.path.join("tests", "datafiles", "nextnano3")
folder_negf = os.path.join("tests", "datafiles", "nextnano.NEGF")


class Test_nnp(unittest.TestCase):
    def test_load(self):
        fullpath = os.path.join(folder_nnp, "only_variables.in")

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

        fullpath = os.path.join(folder_nnp, "virtual_file.in")
        self.assertRaises(FileNotFoundError, InputFile, fullpath)

    def test_get_variables(self):
        fullpath = os.path.join(folder_nn3, "only_variables.in")
        file = InputFile(fullpath)

        self.assertEqual(file.variables["float"], file.get_variable("float"))
        self.assertRaises(KeyError, file.get_variable, name="new_variable")

    def test_set_variables(self):
        fullpath = os.path.join(folder_nnp, "only_variables.in")
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
        fullpath = os.path.join(folder_nnp, "only_variables.in")
        file = InputFile(fullpath)

        self.assertEqual(file.fullpath, fullpath)
        self.assertEqual(
            file.save(file.fullpath, overwrite=False),
            os.path.join(folder_nnp, "only_variables_0.in"),
        )
        os.remove(file.fullpath)

    def test_config(self):
        fullpath = os.path.join(folder_nnp, "only_variables.in")
        file = InputFile(fullpath)
        from nextnanopy import config

        for key, value in config.config["nextnano++"].items():
            self.assertEqual(file.default_command_args[key], value)

    def test_text(self):
        fullpath_onlyvar = os.path.join(folder_nnp, "only_variables.in")
        fullpath_example = os.path.join(folder_nnp, "example.in")
        file = InputFile(fullpath_onlyvar)
        text = file.text

        new_file = InputFile(fullpath_example)
        # new_file = InputFile()
        # self.assertEqual(new_file.product, 'not valid')
        # self.assertEqual(new_file.fullpath, None)
        # self.assertEqual(new_file.text, '')
        # self.assertEqual(new_file.raw_lines, [])

        new_file.text = text
        self.assertEqual(new_file.product, "nextnano++")
        # self.assertEqual(new_file.fullpath, None)
        self.assertEqual(new_file.text, text)
        self.assertEqual(new_file.lines, file.lines)
        self.assertEqual(new_file.variables["MAYUS"].name, "MAYUS")
        self.assertEqual(new_file.variables["MAYUS"].value, "TEXT")
        self.assertEqual(new_file.variables["MAYUS"].comment, "")
        self.assertEqual(new_file.variables["MAYUS"].text, "$MAYUS = TEXT")
        # self.assertRaises(ValueError, new_file.save)
        self.assertEqual(
            new_file.save(file.fullpath, overwrite=False),
            os.path.join(folder_nnp, "only_variables_0.in"),
        )
        os.remove(new_file.fullpath)

    def test_set_and_save(self):
        fullpath = os.path.join(folder_nnp, "only_variables.in")
        file = InputFile(fullpath)
        file.set_variable(name="float", value=0.4)
        self.assertAlmostEqual(file.variables["float"].value, 0.4)

        self.addCleanup(os.remove, os.path.join(folder_nnp, "only_variables_0.in"))
        file.save()
        self.assertTrue(os.path.isfile(os.path.join(folder_nnp, "only_variables_0.in")))

    def test_same_dir_saving(self):
        current_directory = os.getcwd()
        self.addCleanup(os.chdir, current_directory)

        nnp_datafile_dir = os.path.join(folder_nnp)
        os.chdir(nnp_datafile_dir)

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
        self.assertTrue(os.path.isfile("only_variables_0.in"))

    ###content tests

    def test_content_get(self):
        fullpath = os.path.join(folder_nnp, "only_variables.in")
        file = InputFile(fullpath)

        self.assertIsNotNone(file.content)
        self.assertEqual(file.content[0], "$float = 0.0 ")
        self.assertEqual(file.content[-1].name, "global")

    def test_content_set(self):
        fullpath = os.path.join(folder_nnp, "only_variables.in")
        file = InputFile(fullpath)

        file.content[0] = "$DUMMY = 1"
        self.assertEqual(file.content[0], "$DUMMY = 1")
        file.content["_entry_0"] = "DUMMY LINE"
        self.assertEqual(file.content[0], "DUMMY LINE")


class Test_nn3(unittest.TestCase):
    def test_load(self):
        fullpath = os.path.join(folder_nn3, "only_variables.in")

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

        fullpath = os.path.join(folder_nn3, "virtual_file.in")
        self.assertRaises(FileNotFoundError, InputFile, fullpath)

    def test_get_variables(self):
        fullpath = os.path.join(folder_nn3, "only_variables.in")
        file = InputFile(fullpath)

        self.assertEqual(file.variables["float"], file.get_variable("float"))
        self.assertRaises(KeyError, file.get_variable, name="new_variable")

    def test_set_variables(self):
        fullpath = os.path.join(folder_nn3, "only_variables.in")
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
        fullpath = os.path.join(folder_nn3, "only_variables.in")
        file = InputFile(fullpath)

        self.assertEqual(file.fullpath, fullpath)
        self.assertEqual(
            file.save(file.fullpath, overwrite=False),
            os.path.join(folder_nn3, "only_variables_0.in"),
        )
        os.remove(file.fullpath)

    def test_config(self):
        fullpath = os.path.join(folder_nn3, "only_variables.in")
        file = InputFile(fullpath)
        from nextnanopy import config

        for key, value in config.config["nextnano3"].items():
            self.assertEqual(file.default_command_args[key], value)

    def test_save(self):
        fullpath = os.path.join(folder_nn3, "only_variables.in")
        file = InputFile(fullpath)
        new_folder = os.path.join(folder_nn3, "temp")
        new_file = os.path.join(new_folder, "example_copy.in")
        self.assertRaises(
            FileNotFoundError, file.save, new_file, overwrite=True, automkdir=False
        )
        self.assertEqual(file.save(new_file, overwrite=True, automkdir=True), new_file)
        os.remove(file.fullpath)
        os.rmdir(new_folder)

    def test_text(self):
        fullpath_onlyvar = os.path.join(folder_nn3, "only_variables.in")
        fullpath_example = os.path.join(folder_nn3, "example.in")
        file = InputFile(fullpath_onlyvar)
        text = file.text

        new_file = InputFile(fullpath_example)
        # self.assertEqual(new_file.product, 'not valid')
        # self.assertEqual(new_file.fullpath, None)
        # self.assertEqual(new_file.text, '')
        # self.assertEqual(new_file.raw_lines, [])

        new_file.text = text

        self.assertEqual(new_file.product, "nextnano3")
        # self.assertEqual(new_file.fullpath, None)
        self.assertEqual(new_file.text, text)
        self.assertEqual(new_file.lines, file.lines)
        self.assertEqual(new_file.variables["MAYUS"].name, "MAYUS")
        self.assertEqual(new_file.variables["MAYUS"].value, "TEXT")
        self.assertEqual(new_file.variables["MAYUS"].comment, "")
        self.assertEqual(new_file.variables["MAYUS"].text, "%MAYUS = TEXT")
        # self.assertRaises(ValueError, new_file.save)
        self.assertEqual(
            new_file.save(file.fullpath, overwrite=False),
            os.path.join(folder_nn3, "only_variables_0.in"),
        )
        os.remove(new_file.fullpath)

    def test_set_and_save(self):
        fullpath = os.path.join(folder_nn3, "only_variables.in")
        file = InputFile(fullpath)
        file.set_variable(name="float", value=0.4)
        self.assertAlmostEqual(file.variables["float"].value, 0.4)

        self.addCleanup(os.remove, os.path.join(folder_nn3, "only_variables_0.in"))
        file.save()
        self.assertTrue(os.path.isfile(os.path.join(folder_nn3, "only_variables_0.in")))

    def test_same_dir(self):
        current_directory = os.getcwd()
        self.addCleanup(os.chdir, current_directory)

        nn3_datafile_dir = os.path.join(folder_nn3)
        os.chdir(nn3_datafile_dir)

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
        self.assertTrue(os.path.isfile("only_variables_0.in"))

    def test_content(self):
        fullpath = os.path.join(folder_nn3, "only_variables.in")
        file = InputFile(fullpath)

        self.assertIsNone(file.content)


class Test_negf_classic(unittest.TestCase):
    def test_load(self):
        fullpath = os.path.join(folder_negf, "example.xml")
        file = InputFile(fullpath)

        self.assertEqual(file.product, "nextnano.NEGF_classic")

        self.assertEqual(len(file.variables.keys()), 4)

        self.assertEqual(file.variables["variable1"].name, "variable1")
        self.assertEqual(file.variables["variable1"].value, float(0.24))
        self.assertEqual(file.variables["variable1"].comment, "Some comment")
        self.assertEqual(file.variables["variable1"].unit, "a.u.")

        self.assertEqual(file.variables["variable2"].name, "variable2")
        self.assertEqual(file.variables["variable2"].value, int(0))
        self.assertEqual(file.variables["variable2"].comment, "Another comment")
        self.assertEqual(file.variables["variable2"].unit, "meV")

        self.assertEqual(file.variables["text_var"].name, "text_var")
        self.assertEqual(file.variables["text_var"].value, "some text")

        self.assertEqual(file.variables["ref_var"].value, "$(1-variable1)")

        fullpath = os.path.join(folder_negf, "virtual_file.xml")
        self.assertRaises(FileNotFoundError, InputFile, fullpath)

    def test_get_variables(self):
        fullpath = os.path.join(folder_negf, "example.xml")
        file = InputFile(fullpath)

        self.assertEqual(file.variables["variable1"], file.get_variable("variable1"))

        self.assertRaises(KeyError, file.get_variable, name="new_variable")

    def test_set_variables(self):
        fullpath = os.path.join(folder_negf, "example.xml")
        file = InputFile(fullpath)

        file.set_variable("variable1", 0.137, "test comment", "test unit^2")
        self.assertEqual(file.variables["variable1"].value, float(0.137))
        self.assertEqual(file.variables["variable1"].comment, "test comment")
        self.assertEqual(file.variables["variable1"].unit, "test unit^2")
        # self.assertEqual(file.lines[19], '<Name Comment="Some comment">$variable1</Name>')

        file.set_variable("text_var", "string variable test")
        self.assertEqual(file.variables["text_var"].value, "string variable test")

        file.set_variable("ref_var", "$variable1 - 0.1")
        self.assertEqual(file.variables["ref_var"].value, "$variable1 - 0.1")

        self.assertRaises(KeyError, file.set_variable, name="new_variable")

    def test_fullpath(self):
        fullpath = os.path.join(folder_negf, "example.xml")
        file = InputFile(fullpath)

        self.assertEqual(file.fullpath, fullpath)
        self.assertEqual(
            file.save(file.fullpath, overwrite=False),
            os.path.join(folder_negf, "example_0.xml"),
        )
        os.remove(file.fullpath)

    def test_config(self):
        fullpath = os.path.join(folder_negf, "example.xml")
        file = InputFile(fullpath)
        from nextnanopy import config

        for key, value in config.config["nextnano.NEGF_classic"].items():
            self.assertEqual(file.default_command_args[key], value)

    def test_save(self):
        fullpath = os.path.join(folder_negf, "example.xml")
        file = InputFile(fullpath)

        new_folder = os.path.join(folder_negf, "temp")
        new_file = os.path.join(new_folder, "example_copy.in")
        self.assertRaises(
            FileNotFoundError, file.save, new_file, overwrite=True, automkdir=False
        )
        self.assertEqual(file.save(new_file, overwrite=True, automkdir=True), new_file)
        os.remove(file.fullpath)
        os.rmdir(new_folder)

    def test_set_and_save(self):
        fullpath = os.path.join(folder_negf, "example.xml")
        file = InputFile(fullpath)
        file.set_variable(name="variable1", value=0.4)
        self.assertAlmostEqual(file.variables["variable1"].value, 0.4)

        self.addCleanup(os.remove, os.path.join(folder_negf, "example_0.xml"))
        file.save()
        self.assertTrue(os.path.isfile(os.path.join(folder_negf, "example_0.xml")))

    def test_content(self):
        fullpath = os.path.join(folder_negf, "example.xml")
        file = InputFile(fullpath)

        self.assertIsNone(file.content)


class Test_negf(unittest.TestCase):
    # TODO: implement test for NEGF++ input file
    def test_load(self):
        fullpath = os.path.join(folder_negf, "Minimal_InputFile.negf")

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

        fullpath = os.path.join(folder_nnp, "virtual_file.in")
        self.assertRaises(FileNotFoundError, InputFile, fullpath)

    def test_get_variables(self):
        fullpath = os.path.join(folder_negf, "Minimal_InputFile.negf")
        file = InputFile(fullpath)

        self.assertEqual(
            file.variables["alloyComposition"], file.get_variable("alloyComposition")
        )
        self.assertRaises(KeyError, file.get_variable, name="new_variable")

    def test_set_variables(self):
        fullpath = os.path.join(folder_negf, "Minimal_InputFile.negf")
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
        fullpath = os.path.join(folder_negf, "Minimal_InputFile.negf")
        file = InputFile(fullpath)

        self.assertEqual(file.fullpath, fullpath)
        self.assertEqual(
            file.save(file.fullpath, overwrite=False),
            os.path.join(folder_negf, "Minimal_InputFile_0.negf"),
        )
        os.remove(file.fullpath)

    def test_config(self):
        fullpath = os.path.join(folder_negf, "Minimal_InputFile.negf")
        file = InputFile(fullpath)
        from nextnanopy import config

        for key, value in config.config["nextnano.NEGF"].items():
            self.assertEqual(file.default_command_args[key], value)

    # def test_text(self):
    #     fullpath = os.path.join(folder_nnp, 'only_variables.in')
    #
    #     file = InputFile(fullpath)
    #     text = file.text
    #
    #     new_file = InputFile()
    #     self.assertEqual(new_file.product, 'not valid')
    #     self.assertEqual(new_file.fullpath, None)
    #     self.assertEqual(new_file.text, '')
    #     self.assertEqual(new_file.raw_lines, [])
    #
    #     new_file.text = text
    #     self.assertEqual(new_file.product, 'nextnano++')
    #     self.assertEqual(new_file.fullpath, None)
    #     self.assertEqual(new_file.text, text)
    #     self.assertEqual(new_file.lines, file.lines)
    #     self.assertEqual(new_file.variables['MAYUS'].name, 'MAYUS')
    #     self.assertEqual(new_file.variables['MAYUS'].value, 'TEXT')
    #     self.assertEqual(new_file.variables['MAYUS'].comment, '')
    #     self.assertEqual(new_file.variables['MAYUS'].text, '$MAYUS = TEXT')
    #     self.assertRaises(ValueError, new_file.save)
    #     self.assertEqual(new_file.save(file.fullpath, overwrite=False),
    #                      os.path.join(folder_nnp, 'only_variables_0.in'))
    #     os.remove(new_file.fullpath)

    def test_set_and_save(self):
        fullpath = os.path.join(folder_negf, "Minimal_InputFile.negf")
        file = InputFile(fullpath)
        file.set_variable(name="alloyComposition", value=0.4)
        self.assertAlmostEqual(file.variables["alloyComposition"].value, 0.4)

        self.addCleanup(
            os.remove, os.path.join(folder_negf, "Minimal_InputFile_0.negf")
        )
        file.save()
        self.assertTrue(
            os.path.isfile(os.path.join(folder_negf, "Minimal_InputFile_0.negf"))
        )

    def test_same_dir_saving(self):
        current_directory = os.getcwd()
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
        self.assertTrue(os.path.isfile("Minimal_InputFile_0.negf"))

    ###content tests

    # def test_content_get(self): # LATER also check this
    #     fullpath = os.path.join(folder_nnp, 'only_variables.in')
    #     file = InputFile(fullpath)
    #
    #
    #     self.assertIsNotNone(file.content)
    #     self.assertEqual(file.content[0],'$float = 0.0 ')
    #     self.assertEqual(file.content[-1].name, 'global')
    #
    # def test_content_set(self):
    #     fullpath = os.path.join(folder_nnp, 'only_variables.in')
    #     file = InputFile(fullpath)
    #
    #
    #     file.content[0] = '$DUMMY = 1'
    #     self.assertEqual(file.content[0],'$DUMMY = 1')
    #     file.content['_entry_0'] = 'DUMMY LINE'
    #     self.assertEqual(file.content[0], 'DUMMY LINE')


class TestInputFile(unittest.TestCase):

    def test_access_by_index(self):
        fullpath = os.path.join(folder_nnp, "only_variables.in")
        file = InputFile(fullpath)
        for key, value in file.variables.items():
            self.assertEqual(file[key], value)

    def test_for_loop(self):
        fullpath = os.path.join(folder_nnp, "only_variables.in")
        file = InputFile(fullpath)
        for i, fi in enumerate(file):
            self.assertEqual(file.variables[i], fi)

    def test_fullpath(self):
        fullpath = os.path.join(folder_nnp, "only_variables.in")
        file = InputFile(fullpath)
        self.assertEqual(file.fullpath, fullpath)
        self.assertEqual(file.filename, "only_variables.in")
        self.assertEqual(file.filename_only, "only_variables")
        self.assertEqual(file.folder_input, folder_nnp)
        self.assertEqual(file.execute_info, {})

        file.filename = "new_name.in"
        self.assertEqual(file.filename, "new_name.in")
        self.assertEqual(file.filename_only, "new_name")
        self.assertEqual(file.fullpath, os.path.join(folder_nnp, "new_name.in"))
        self.assertEqual(file.folder_input, folder_nnp)

        file.filename_only = "another_filename"
        self.assertEqual(file.filename, "another_filename.in")
        self.assertEqual(file.filename_only, "another_filename")
        self.assertEqual(file.fullpath, os.path.join(folder_nnp, "another_filename.in"))
        self.assertEqual(file.folder_input, folder_nnp)

        npath = os.path.join("new", "folder")
        file.folder_input = npath
        self.assertEqual(file.filename, "another_filename.in")
        self.assertEqual(file.filename_only, "another_filename")
        self.assertEqual(file.fullpath, os.path.join(npath, "another_filename.in"))
        self.assertEqual(file.folder_input, npath)

        npath = os.path.join("random", "path")
        file.execute_info["outputdirectory"] = npath
        self.assertEqual(file.folder_output, npath)


class TestSweep(unittest.TestCase):
    def test_init(self):
        self.assertRaises(TypeError, Sweep)
        sweep = Sweep({})
        self.assertEqual(sweep.fullpath, None)
        self.assertEqual(sweep.var_sweep, {})
        self.assertRaises(ValueError, Sweep, {"Name": "some_name"})

    def test_nnp_init(self):
        fullpath = os.path.join(folder_nnp, "only_variables.in")
        self.assertRaises(ValueError, Sweep, {"Name": "some_name"}, fullpath)

        sweep = Sweep({}, fullpath)
        self.assertEqual(sweep.fullpath, fullpath)
        self.assertEqual(sweep.var_sweep, {})
        self.assertFalse(sweep.input_files)
        self.assertFalse(sweep.sweep_output_directory)

        self.assertRaises(ValueError, Sweep, {"float": 1})
        self.assertRaises(TypeError, Sweep, {"float": 1}, fullpath)

        sweep = Sweep({"float": [1, 2, 5]}, fullpath)
        self.assertEqual(sweep.fullpath, fullpath)
        self.assertEqual(sweep.var_sweep["float"], [1, 2, 5])

        self.addCleanup(
            delete_files,
            "only_variables",
            directory=folder_nnp,
            exceptions=["only_variables.in"],
        )

    def test_nnp_mkdir(self):
        fullpath = os.path.join(folder_nnp, "only_variables.in")
        sweep = Sweep({}, fullpath=fullpath)
        sweep.config.set("nextnano++", "outputdirectory", r"tests//outputs")
        created_directory = os.path.join(sweep.mk_dir(overwrite=True))
        self.assertTrue(
            os.path.samefile(
                created_directory,
                os.path.join("tests", "outputs", "only_variables_sweep"),
            )
        )
        self.assertTrue(
            os.path.isdir(os.path.join("tests", "outputs", "only_variables_sweep"))
        )

        self.addCleanup(
            os.rmdir, os.path.join("tests", "outputs", "only_variables_sweep")
        )
        self.addCleanup(
            delete_files,
            "only_variables",
            directory=folder_nnp,
            exceptions=["only_variables.in"],
        )

    def test_nnp_mkdir_specify(self):
        fullpath = os.path.join(folder_nnp, "only_variables.in")
        sweep = Sweep({}, fullpath=fullpath)
        created_directory = os.path.join(
            sweep.mk_dir(overwrite=True, output_directory=r"tests//outputs")
        )
        self.assertTrue(
            os.path.samefile(
                created_directory,
                os.path.join("tests", "outputs", "only_variables_sweep"),
            )
        )
        self.assertTrue(
            os.path.isdir(os.path.join("tests", "outputs", "only_variables_sweep"))
        )

        self.addCleanup(
            os.rmdir, os.path.join("tests", "outputs", "only_variables_sweep")
        )
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
        fullpath = os.path.join(folder_nnp, "only_variables.in")
        sweep = Sweep({"float": [1, 2], "str": ["test1", "test2"]}, fullpath)
        sweep.save_sweep()

        files_with_names = [
            file for file in os.listdir(folder_nnp) if "only_variables" in file
        ]
        self.assertEqual(len(files_with_names), 5)
        self.assertTrue(
            os.path.isfile(
                os.path.join(folder_nnp, "only_variables__float_2_str_test1_.in")
            )
        )

    # nn3 section
    def test_nn3_init(self):
        fullpath = os.path.join(folder_nn3, "only_variables.in")
        self.assertRaises(ValueError, Sweep, {"Name": "some_name"}, fullpath)

        sweep = Sweep({}, fullpath)
        self.assertEqual(sweep.fullpath, fullpath)
        self.assertEqual(sweep.var_sweep, {})
        self.assertFalse(sweep.input_files)
        self.assertFalse(sweep.sweep_output_directory)

        self.assertRaises(ValueError, Sweep, {"float": 1})
        self.assertRaises(TypeError, Sweep, {"float": 1}, fullpath)

        sweep = Sweep({"float": [1, 2, 5]}, fullpath)
        self.assertEqual(sweep.fullpath, fullpath)
        self.assertEqual(sweep.var_sweep["float"], [1, 2, 5])

        self.addCleanup(
            delete_files,
            "only_variables",
            directory=folder_nn3,
            exceptions=["only_variables.in"],
        )

    def test_nn3_mkdir(self):
        fullpath = os.path.join(folder_nn3, "only_variables.in")
        sweep = Sweep({}, fullpath=fullpath)
        sweep.config.set("nextnano3", "outputdirectory", r"tests//outputs")
        # self.assertEqual(os.path.normpath(os.path.join(sweep.mk_dir(overwrite=True))), os.path.normpath(r'tests//outputs\only_variables_sweep'))
        created_directory = os.path.join(sweep.mk_dir(overwrite=True))
        self.assertTrue(
            os.path.samefile(
                created_directory,
                os.path.join("tests", "outputs", "only_variables_sweep"),
            )
        )
        self.assertTrue(
            os.path.isdir(os.path.join("tests", "outputs", "only_variables_sweep"))
        )

        self.addCleanup(
            os.rmdir, os.path.join("tests", "outputs", "only_variables_sweep")
        )
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
        fullpath = os.path.join(folder_nn3, "only_variables.in")
        sweep = Sweep({"float": [1, 2], "str": ["test1", "test2"]}, fullpath)
        sweep.save_sweep()

        files_with_names = [
            file for file in os.listdir(folder_nn3) if "only_variables" in file
        ]
        self.assertEqual(len(files_with_names), 5)
        self.assertTrue(
            os.path.isfile(
                os.path.join(folder_nn3, "only_variables__float_2_str_test1_.in")
            )
        )

    # TODO test parallel sweeps with and without convergenceCheck
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        if os.path.isdir(r"tests//outputs\only_variables_sweep"):
            os.rmdir(r"tests//outputs\only_variables_sweep")
        delete_files(
            "only_variables", directory=folder_nnp, exceptions=["only_variables.in"]
        )
        delete_files(
            "only_variables", directory=folder_nn3, exceptions=["only_variables.in"]
        )


if __name__ == "__main__":
    unittest.main()

    file = os.path.join(folder_nnp, "only_variables.in")
    fi = InputFile(file)
    text = fi.text
