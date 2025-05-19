import unittest
from nextnanopy.utils import mycollections
import os
from nextnanopy import defaults
from nextnanopy.nnp import defaults as nnp_defaults
from nextnanopy.nn3 import defaults as nn3_defaults
from nextnanopy.negf import defaults as negf_defaults
from nextnanopy.msb import defaults as msb_defaults


folder_nnp = os.path.join("tests", "datafiles", "nextnano++")
folder_nn3 = os.path.join("tests", "datafiles", "nextnano3")
folder_negf = os.path.join("tests", "datafiles", "nextnano.NEGF")


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
    def test_nn3(self):
        fullpath = os.path.join(folder_nn3, "example.in")
        self.assertTrue(nn3_defaults.is_nn3_input_file(fullpath))
        self.assertFalse(nnp_defaults.is_nnp_input_file(fullpath))
        self.assertFalse(negf_defaults.is_negf_classic_input_file(fullpath))
        self.assertFalse(negf_defaults.is_negf_input_file(fullpath))
        self.assertEqual(defaults.input_file_type(fullpath), "nextnano3")
        self.assertEqual(defaults.get_fmt("nextnano3")["var_char"], "%")
        self.assertEqual(defaults.get_fmt("nextnano3")["com_char"], "!")
        self.assertEqual(
            defaults.get_fmt("nextnano3")["input_pattern"], "$end_simulation-dimension"
        )

    def test_nnp(self):
        fullpath = os.path.join(folder_nnp, "example.in")
        self.assertFalse(nn3_defaults.is_nn3_input_file(fullpath))
        self.assertTrue(nnp_defaults.is_nnp_input_file(fullpath))
        self.assertFalse(negf_defaults.is_negf_classic_input_file(fullpath))
        self.assertFalse(negf_defaults.is_negf_input_file(fullpath))
        self.assertEqual(defaults.input_file_type(fullpath), "nextnano++")
        self.assertEqual(defaults.get_fmt("nextnano++")["var_char"], "$")
        self.assertEqual(defaults.get_fmt("nextnano++")["com_char"], "#")
        self.assertEqual(defaults.get_fmt("nextnano++")["input_pattern"], "global{")

    def test_negf_classic(self):
        fullpath = os.path.join(folder_negf, "example.xml")
        self.assertFalse(nn3_defaults.is_nn3_input_file(fullpath))
        self.assertFalse(nnp_defaults.is_nnp_input_file(fullpath))
        self.assertFalse(negf_defaults.is_negf_input_file(fullpath))
        self.assertTrue(negf_defaults.is_negf_classic_input_file(fullpath))
        self.assertEqual(defaults.input_file_type(fullpath), "nextnano.NEGF_classic")
        self.assertEqual(defaults.get_fmt("nextnano.NEGF_classic")["var_char"], "$")
        self.assertEqual(defaults.get_fmt("nextnano.NEGF_classic")["com_char"], "<!--")
        self.assertEqual(
            defaults.get_fmt("nextnano.NEGF_classic")["input_pattern"], "<Simulation"
        )

    # TODO:
    def test_negf(self):
        # TODO: prepare an NEGF++ .negf input example for test
        fullpath = os.path.join(folder_negf, "Minimal_InputFile.negf")
        self.assertFalse(nn3_defaults.is_nn3_input_file(fullpath))
        self.assertFalse(nnp_defaults.is_nnp_input_file(fullpath))
        self.assertFalse(negf_defaults.is_negf_classic_input_file(fullpath))
        self.assertTrue(negf_defaults.is_negf_input_file(fullpath))
        self.assertEqual(defaults.input_file_type(fullpath), "nextnano.NEGF")
        self.assertEqual(defaults.get_fmt("nextnano.NEGF")["var_char"], "$")
        self.assertEqual(defaults.get_fmt("nextnano.NEGF")["com_char"], "#")
        self.assertEqual(
            defaults.get_fmt("nextnano.NEGF")["input_pattern"], "nextnano.NEGF{"
        )


if __name__ == "__main__":
    unittest.main()
