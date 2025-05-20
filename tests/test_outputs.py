import unittest
import warnings

import nextnanopy.outputs as outputs
from nextnanopy.utils.datasets import default_unit
from os.path import join
import os

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
# folder_nnp = os.path.join(TESTS_DIR, 'datafiles', 'nextnano++')
# folder_nn3 = os.path.join(TESTS_DIR, 'datafiles', 'nextnano3')
# folder_negf = os.path.join(TESTS_DIR, 'datafiles', 'nextnano.NEGF')
# folder_msb = os.path.join(TESTS_DIR, 'datafiles', 'nextnano.MSB')

folder_nnp = os.path.join("tests", "datafiles", "nextnano++")
folder_nn3 = os.path.join("tests", "datafiles", "nextnano3")
folder_negf = os.path.join("tests", "datafiles", "nextnano.NEGF")
folder_msb = os.path.join("tests", "datafiles", "nextnano.MSB")


class TestOutputs_nnp(unittest.TestCase):

    def test_dat(self):
        df = outputs.DataFile(
            join(folder_nnp, "bandedges_1d.dat"), product="nextnano++"
        )
        self.assertEqual(len(df.coords.keys()), 1)
        self.assertEqual(df.coords["x"].name, "x")
        self.assertEqual(df.coords["x"].unit, "nm")
        self.assertEqual(df.coords["x"].value.size, 548)
        self.assertEqual(len(df.variables.keys()), 4)
        self.assertEqual(df.variables["Gamma"].name, "Gamma")
        self.assertEqual(df.variables["Gamma"].unit, "eV")
        self.assertEqual(df.variables["Gamma"].value.size, 548)
        self.assertEqual(df.metadata["ndim"], 1)
        self.assertEqual(df.metadata["dkeys"], [0])

        df = outputs.DataFile(
            join(folder_nnp, "wf_occupation_1d.dat"), product="nextnano++"
        )
        self.assertEqual(len(df.coords.keys()), 1)
        self.assertEqual(len(df.variables.keys()), 1)
        self.assertEqual(df.coords["no."].name, "no.")
        self.assertEqual(df.coords["no."].unit, default_unit)
        self.assertEqual(df.coords["no."].value.size, 10)
        self.assertEqual(df.variables["Occupation"].name, "Occupation")
        self.assertEqual(df.variables["Occupation"].unit, "electrons/cm^2")
        self.assertEqual(df.variables["Occupation"].value.size, 10)
        self.assertEqual(df.metadata["ndim"], 1)
        self.assertEqual(df.metadata["dkeys"], [0])

    def test_dat_FirstVarFlag(self):
        df = outputs.DataFile(
            join(folder_nnp, "bandedges_1d.dat"),
            product="nextnano++",
            FirstVarIsCoordFlag=False,
        )
        self.assertEqual(len(df.coords.keys()), 0)
        self.assertEqual(len(df.variables.keys()), 5)
        self.assertEqual(df.variables["x"].name, "x")
        self.assertEqual(df.variables["x"].unit, "nm")
        self.assertEqual(df.variables["x"].value.size, 548)
        self.assertEqual(df.variables["Gamma"].name, "Gamma")
        self.assertEqual(df.variables["Gamma"].unit, "eV")
        self.assertEqual(df.variables["Gamma"].value.size, 548)
        self.assertEqual(df.metadata["ndim"], 0)
        self.assertEqual(df.metadata["dkeys"], [])

        df = outputs.DataFile(
            join(folder_nnp, "wf_occupation_1d.dat"),
            product="nextnano++",
            FirstVarIsCoordFlag=True,
        )
        self.assertEqual(len(df.coords.keys()), 1)
        self.assertEqual(len(df.variables.keys()), 1)
        self.assertEqual(df.coords["no."].name, "no.")
        self.assertEqual(df.coords["no."].unit, default_unit)
        self.assertEqual(df.coords["no."].value.size, 10)
        self.assertEqual(df.variables["Occupation"].name, "Occupation")
        self.assertEqual(df.variables["Occupation"].unit, "electrons/cm^2")
        self.assertEqual(df.variables["Occupation"].value.size, 10)
        self.assertEqual(df.metadata["ndim"], 1)
        self.assertEqual(df.metadata["dkeys"], [0])

    # test creating the document
    # self.assertRaises(NotImplementedError, df.export, filename='TESTEXPORT.dat', format='dat')

    def test_avs(self):
        df = outputs.DataFile(
            join(folder_nnp, "bandedges_2d.fld"), product="nextnano++"
        )
        self.assertEqual(len(df.coords.keys()), 2)
        self.assertEqual(list(df.coords.keys()), ["x", "y"])
        self.assertEqual(df.coords["x"].unit, "nm")
        self.assertEqual(df.coords["x"].value.size, 164)
        self.assertEqual(df.coords["x"].dim, 0)
        self.assertEqual(df.coords["y"].unit, "nm")
        self.assertEqual(df.coords["y"].value.size, 79)
        self.assertEqual(df.coords["y"].dim, 1)
        self.assertEqual(len(df.variables.keys()), 2)
        self.assertEqual(df.variables["Gamma"].name, "Gamma")
        self.assertEqual(df.variables["Gamma"].unit, "eV")
        self.assertEqual(df.variables["Gamma"].value.shape, (164, 79))
        self.assertEqual(df.metadata["ndim"], 2)
        self.assertEqual(df.metadata["dims"], [164, 79])
        self.assertEqual(df.metadata["field"], "rectilinear")

        # test creating the document
        self.assertRaises(
            NotImplementedError,
            df.export,
            filename="TESTEXPORT2D.fld",
            format="AVSAscii",
        )

    def test_avs3D(self):
        df = outputs.DataFile(join(folder_nnp, "potential.fld"), product="nextnano++")
        self.assertEqual(len(df.coords.keys()), 3)
        self.assertEqual(list(df.coords.keys()), ["x", "y", "z"])
        self.assertEqual(df.coords["x"].unit, "nm")
        self.assertEqual(df.coords["x"].value.size, 11)
        self.assertEqual(df.coords["x"].dim, 0)
        self.assertEqual(df.coords["y"].unit, "nm")
        self.assertEqual(df.coords["y"].value.size, 11)
        self.assertEqual(df.coords["y"].dim, 1)
        self.assertEqual(df.coords["z"].unit, "nm")
        self.assertEqual(df.coords["z"].value.size, 76)
        self.assertEqual(df.coords["z"].dim, 2)
        self.assertEqual(len(df.variables.keys()), 1)
        self.assertEqual(df.variables["potential"].name, "potential")
        self.assertEqual(df.variables["potential"].unit, default_unit)
        self.assertEqual(df.variables["potential"].value.shape, (11, 11, 76))
        self.assertEqual(df.metadata["ndim"], 3)
        self.assertEqual(df.metadata["dims"], [11, 11, 76])
        self.assertEqual(df.metadata["field"], "rectilinear")

        # test creating the document
        self.assertRaises(
            NotImplementedError,
            df.export,
            filename="TESTEXPORT3D.fld",
            format="AVSAscii",
        )

    def test_vtr_potential(self):
        df = outputs.DataFile(join(folder_nnp, "potential.vtr"), product="nextnano++")

        self.assertEqual(len(df.coords.keys()), 3)
        self.assertEqual(list(df.coords.keys()), ["x", "y", "z"])
        self.assertEqual(df.coords["x"].unit, default_unit)
        self.assertEqual(df.coords["x"].value.size, 11)
        self.assertEqual(df.coords["x"].dim, 0)
        self.assertEqual(df.coords["y"].unit, default_unit)
        self.assertEqual(df.coords["y"].value.size, 11)
        self.assertEqual(df.coords["y"].dim, 1)
        self.assertEqual(df.coords["z"].unit, default_unit)
        self.assertEqual(df.coords["z"].value.size, 76)
        self.assertEqual(df.coords["z"].dim, 2)
        self.assertEqual(len(df.variables.keys()), 1)
        self.assertEqual(df.variables["potential"].name, "potential")
        self.assertEqual(df.variables["potential"].unit, default_unit)
        self.assertEqual(df.variables["potential"].value.shape, (11, 11, 76))
        self.assertEqual(df.metadata, {})

    def test_vtr_bandedges(self):
        df = outputs.DataFile(join(folder_nnp, "bandedges.vtr"), product="nextnano++")

        self.assertEqual(len(df.coords.keys()), 3)
        self.assertEqual(list(df.coords.keys()), ["x", "y", "z"])
        self.assertEqual(df.coords["x"].unit, default_unit)
        self.assertEqual(df.coords["x"].value.size, 11)
        self.assertEqual(df.coords["x"].dim, 0)
        self.assertEqual(df.coords["y"].unit, default_unit)
        self.assertEqual(df.coords["y"].value.size, 11)
        self.assertEqual(df.coords["y"].dim, 1)
        self.assertEqual(df.coords["z"].unit, default_unit)
        self.assertEqual(df.coords["z"].value.size, 76)
        self.assertEqual(df.coords["z"].dim, 2)
        self.assertEqual(len(df.variables.keys()), 4)
        self.assertEqual(df.variables["Gamma"].name, "Gamma")
        self.assertEqual(df.variables["Gamma"].unit, "eV")
        self.assertEqual(df.variables["Gamma"].value.shape, (11, 11, 76))
        self.assertEqual(df.metadata, {})

    def test_txt(self):
        df = outputs.DataFile(
            join(folder_nnp, "variables_input.txt"), product="nextnano++"
        )
        self.assertEqual(len(df.coords.keys()), 0)
        self.assertEqual(len(df.variables.keys()), 3)
        self.assertEqual(df.variables["var_1"].name, "var_1")
        self.assertEqual(df.variables["var_1"].unit, default_unit)
        self.assertEqual(df.variables["var_1"].value, -47.5)
        self.assertEqual(df.variables["var_2"].value, 75)
        self.assertEqual(df.variables["string"].value, '"hello"')

        df = outputs.DataFile(
            join(folder_nnp, "variables_database.txt"), product="nextnano++"
        )
        self.assertEqual(len(df.coords.keys()), 0)
        self.assertEqual(len(df.variables.keys()), 0)

        df = outputs.DataFile(
            join(folder_nnp, "total_charges.txt"), product="nextnano++"
        )
        self.assertEqual(len(df.coords.keys()), 0)
        self.assertEqual(len(df.variables.keys()), 6)
        print(df.variables["fixed"].value)
        self.assertAlmostEqual(df.variables["fixed"].value, 0.0)
        self.assertEqual(df.variables[0].name, "electron")
        self.assertEqual(df.variables[0].unit, "e/cm^2")

        files = [
            "simulation_database.txt",
            "simulation_info.txt",
            "simulation_input.txt",
        ]
        for file in files:
            self.assertRaises(
                NotImplementedError,
                outputs.DataFile,
                join(folder_nnp, file),
                "nextnano++",
            )

    def test_rest(self):
        files = ["example.log", "example.in"]
        for file in files:
            self.assertRaises(
                NotImplementedError,
                outputs.DataFile,
                join(folder_nnp, file),
                "nextnano++",
            )

    def test_all_2D(self):
        files = [
            r"AvsAscii\bandedges.avs.fld",
            r"AvsAscii_one_file\bandedges.fld",
            r"AvsBinary\bandedges.avs.fld",
            r"AvsBinary_one_file\bandedges.fld",
            r"VTKAscii\bandedges.vtr",
        ]
        for file in files:
            filepath = os.path.join(folder_nnp, file)
            datafile = outputs.DataFile(filepath, product="nextnano++")
            self.assertEqual(len(datafile.coords), 2)
            self.assertEqual(len(datafile.variables), 6)

    # TODO add tests for loading Origin like file
    # TODO add tests for exporting binary data


class TestOutputs_nn3(unittest.TestCase):

    def test_dat(self):
        df = outputs.DataFile(join(folder_nn3, "bandedges_1d.dat"), product="nextnano3")
        self.assertEqual(len(df.coords.keys()), 1)
        self.assertEqual(df.coords["position"].name, "position")
        self.assertEqual(df.coords["position"].unit, "nm")
        self.assertEqual(df.coords["position"].value.size, 258)
        self.assertEqual(len(df.variables.keys()), 6)
        self.assertEqual(df.variables["Gamma_bandedge"].name, "Gamma_bandedge")
        self.assertEqual(df.variables["Gamma_bandedge"].unit, "eV")
        self.assertEqual(df.variables["Gamma_bandedge"].value.size, 258)
        self.assertEqual(df.metadata["ndim"], 1)
        self.assertEqual(df.metadata["dkeys"], [0])

        df = outputs.DataFile(join(folder_nn3, "wf_shift_1d.dat"), product="nextnano3")
        self.assertEqual(len(df.coords.keys()), 1)
        self.assertEqual(len(df.variables.keys()), 10)
        self.assertEqual(df.coords["position"].name, "position")
        self.assertEqual(df.coords["position"].unit, "nm")
        self.assertEqual(df.coords["position"].value.size, 121)
        self.assertEqual(df.variables["psi^2_1"].name, "psi^2_1")
        self.assertEqual(df.variables["psi^2_1"].unit, default_unit)
        self.assertEqual(df.variables["psi^2_1"].value.size, 121)
        self.assertEqual(df.metadata["ndim"], 1)
        self.assertEqual(df.metadata["dkeys"], [0])

        df = outputs.DataFile(
            join(folder_nn3, "bandedges_2d_cut.dat"), product="nextnano3"
        )
        self.assertEqual(len(df.coords.keys()), 1)
        self.assertEqual(df.coords["position"].name, "position")
        self.assertEqual(df.coords["position"].unit, "nm")
        self.assertEqual(df.coords["position"].value.size, 258)
        self.assertEqual(len(df.variables.keys()), 6)
        self.assertEqual(df.variables["Gamma_bandedge"].name, "Gamma_bandedge")
        self.assertEqual(df.variables["Gamma_bandedge"].unit, "eV")
        self.assertEqual(df.variables["Gamma_bandedge"].value.size, 258)
        self.assertEqual(df.metadata["ndim"], 1)
        self.assertEqual(df.metadata["dkeys"], [0])

    def test_dat_FirstVarIsCoord(self):
        df = outputs.DataFile(
            join(folder_nn3, "bandedges_1d.dat"),
            product="nextnano3",
            FirstVarIsCoordFlag=False,
        )
        self.assertEqual(len(df.coords.keys()), 0)
        self.assertEqual(len(df.variables.keys()), 7)
        self.assertEqual(df.variables["position"].name, "position")
        self.assertEqual(df.variables["position"].unit, "nm")
        self.assertEqual(df.variables["position"].value.size, 258)
        self.assertEqual(df.variables["Gamma_bandedge"].name, "Gamma_bandedge")
        self.assertEqual(df.variables["Gamma_bandedge"].unit, "eV")
        self.assertEqual(df.variables["Gamma_bandedge"].value.size, 258)
        self.assertEqual(df.metadata["ndim"], 0)
        self.assertEqual(df.metadata["dkeys"], [])

        df = outputs.DataFile(
            join(folder_nn3, "wf_shift_1d.dat"),
            product="nextnano3",
            FirstVarIsCoordFlag=True,
        )
        self.assertEqual(len(df.coords.keys()), 1)
        self.assertEqual(len(df.variables.keys()), 10)
        self.assertEqual(df.coords["position"].name, "position")
        self.assertEqual(df.coords["position"].unit, "nm")
        self.assertEqual(df.coords["position"].value.size, 121)
        self.assertEqual(df.variables["psi^2_1"].name, "psi^2_1")
        self.assertEqual(df.variables["psi^2_1"].unit, default_unit)
        self.assertEqual(df.variables["psi^2_1"].value.size, 121)
        self.assertEqual(df.metadata["ndim"], 1)
        self.assertEqual(df.metadata["dkeys"], [0])

    def test_avs1D(self):
        df = outputs.DataFile(join(folder_nn3, "cb_Gamma_avs.fld"), product="nextnano3")
        self.assertEqual(len(df.coords.keys()), 1)
        self.assertEqual(list(df.coords.keys()), ["x"])
        self.assertEqual(df.coords["x"].unit, "nm")
        self.assertEqual(df.coords["x"].value.size, 105)
        self.assertEqual(df.coords["x"].dim, 0)
        self.assertEqual(len(df.variables.keys()), 1)
        self.assertEqual(df.variables["cb_Gamma"].name, "cb_Gamma")
        self.assertEqual(df.variables["cb_Gamma"].unit, "eV")
        self.assertEqual(df.variables["cb_Gamma"].value.shape, (105,))
        self.assertEqual(df.metadata["ndim"], 1)
        self.assertEqual(df.metadata["dims"], [105])
        self.assertEqual(df.metadata["field"], "rectilinear")

    def test_avs(self):
        df = outputs.DataFile(join(folder_nn3, "bandedges_2d.fld"), product="nextnano3")
        self.assertEqual(len(df.coords.keys()), 2)
        self.assertEqual(list(df.coords.keys()), ["x", "y"])
        self.assertEqual(df.coords["x"].unit, "nm")
        self.assertEqual(df.coords["x"].value.size, 258)
        self.assertEqual(df.coords["x"].dim, 0)
        self.assertEqual(df.coords["y"].unit, "nm")
        self.assertEqual(df.coords["y"].value.size, 11)
        self.assertEqual(df.coords["y"].dim, 1)
        self.assertEqual(len(df.variables.keys()), 6)
        self.assertEqual(df.variables["Gamma_bandedge"].name, "Gamma_bandedge")
        self.assertEqual(df.variables["Gamma_bandedge"].unit, "eV")
        self.assertEqual(df.variables["Gamma_bandedge"].value.shape, (258, 11))
        self.assertEqual(df.metadata["ndim"], 2)
        self.assertEqual(df.metadata["dims"], [258, 11])
        self.assertEqual(df.metadata["field"], "rectilinear")

    def test_avs2D(self):
        df = outputs.DataFile(
            join(folder_nn3, "2Dcb1_sg1_deg1_psi_ev001.fld"), product="nextnano3"
        )
        self.assertEqual(len(df.coords.keys()), 2)
        self.assertEqual(list(df.coords.keys()), ["x", "y"])
        self.assertEqual(df.coords["x"].unit, "nm")
        self.assertEqual(df.coords["x"].value.size, 61)
        self.assertEqual(df.coords["x"].dim, 0)
        self.assertEqual(df.coords["y"].unit, "nm")
        self.assertEqual(df.coords["y"].value.size, 61)
        self.assertEqual(df.coords["y"].dim, 1)
        self.assertEqual(df.variables[0], df.variables["psi_real"])
        self.assertEqual(df.variables[0].name, "psi_real")
        self.assertEqual(df.variables[0].unit, "nm^-1")
        self.assertEqual(df.variables[0].value.shape, (61, 61))
        self.assertEqual(df.variables[1], df.variables["psi_imag"])
        self.assertEqual(df.variables[1].name, "psi_imag")
        self.assertEqual(df.variables[1].unit, "nm^-1")
        self.assertEqual(df.variables[1].value.shape, (61, 61))
        self.assertEqual(df.metadata["ndim"], 2)
        self.assertEqual(df.metadata["dims"], [61, 61])
        self.assertEqual(df.metadata["field"], "rectilinear")

    def test_avs3D(self):
        df = outputs.DataFile(
            join(folder_nn3, "3Dcb1_sg1_deg1_psi_squared_ev001.fld"),
            product="nextnano3",
        )
        self.assertEqual(len(df.coords.keys()), 3)
        self.assertEqual(list(df.coords.keys()), ["x", "y", "z"])
        self.assertEqual(df.coords["x"].unit, "nm")
        self.assertEqual(df.coords["x"].value.size, 19)
        self.assertEqual(df.coords["x"].dim, 0)
        self.assertEqual(df.coords["y"].unit, "nm")
        self.assertEqual(df.coords["y"].value.size, 19)
        self.assertEqual(df.coords["y"].dim, 1)
        self.assertEqual(df.coords["z"].unit, "nm")
        self.assertEqual(df.coords["z"].value.size, 9)
        self.assertEqual(df.coords["z"].dim, 2)
        self.assertEqual(len(df.variables.keys()), 1)
        self.assertEqual(df.variables["psi_squared"].name, "psi_squared")
        self.assertEqual(df.variables["psi_squared"].unit, "nm^-3")
        self.assertEqual(df.variables[0].value.shape, (19, 19, 9))
        self.assertEqual(df.metadata["ndim"], 3)
        self.assertEqual(df.metadata["dims"], [19, 19, 9])
        self.assertEqual(df.metadata["field"], "rectilinear")

    def test_vtr_LocalDOS(self):
        df = outputs.DataFile(
            join(folder_nn3, "LocalDOS_sg1_deg1_Lead1.vtr"), product="nextnano3"
        )

        self.assertEqual(len(df.coords.keys()), 2)
        self.assertEqual(list(df.coords.keys()), ["x", "y"])
        self.assertEqual(df.coords["x"].unit, default_unit)
        self.assertEqual(df.coords["x"].value.size, 51)
        self.assertEqual(df.coords["x"].dim, 0)
        self.assertEqual(df.coords["y"].unit, default_unit)
        self.assertEqual(df.coords["y"].value.size, 101)
        self.assertEqual(df.coords["y"].dim, 1)
        self.assertEqual(len(df.variables.keys()), 1)
        self.assertEqual(
            df.variables["LocalDOS_sg1_deg1_Lead1"].name, "LocalDOS_sg1_deg1_Lead1"
        )
        self.assertEqual(df.variables["LocalDOS_sg1_deg1_Lead1"].unit, "nm^-1eV^-1")
        self.assertEqual(df.variables["LocalDOS_sg1_deg1_Lead1"].value.shape, (51, 101))
        self.assertEqual(df.metadata, {})

    def test_vtr_2Dcb1(self):
        df = outputs.DataFile(
            join(folder_nn3, "2Dcb1_sg1_deg1_psi_ev001.vtr"), product="nextnano3"
        )

        self.assertEqual(len(df.coords.keys()), 2)
        self.assertEqual(list(df.coords.keys()), ["x", "y"])
        self.assertEqual(df.coords["x"].unit, default_unit)
        self.assertEqual(df.coords["x"].value.size, 61)
        self.assertEqual(df.coords["x"].dim, 0)
        self.assertEqual(df.coords["y"].unit, default_unit)
        self.assertEqual(df.coords["y"].value.size, 61)
        self.assertEqual(df.coords["y"].dim, 1)
        self.assertEqual(len(df.variables.keys()), 2)
        self.assertEqual(df.variables[0], df.variables["psi_real"])
        self.assertEqual(df.variables[0].name, "psi_real")
        self.assertEqual(df.variables[0].unit, "nm^-1")
        self.assertEqual(df.variables[0].value.shape, (61, 61))
        self.assertEqual(df.variables[1], df.variables["psi_imag"])
        self.assertEqual(df.variables[1].name, "psi_imag")
        self.assertEqual(df.variables[1].unit, "nm^-1")
        self.assertEqual(df.variables[1].value.shape, (61, 61))
        self.assertEqual(df.metadata, {})

    def test_vtr_3Dcb1(self):
        df = outputs.DataFile(
            join(folder_nn3, "3Dcb1_sg1_deg1_psi_squared_ev001.vtr"),
            product="nextnano3",
        )

        self.assertEqual(len(df.coords.keys()), 3)
        self.assertEqual(list(df.coords.keys()), ["x", "y", "z"])
        self.assertEqual(df.coords["x"].unit, default_unit)
        self.assertEqual(df.coords["x"].value.size, 19)
        self.assertEqual(df.coords["x"].dim, 0)
        self.assertEqual(df.coords["y"].unit, default_unit)
        self.assertEqual(df.coords["y"].value.size, 19)
        self.assertEqual(df.coords["y"].dim, 1)
        self.assertEqual(df.coords["z"].unit, default_unit)
        self.assertEqual(df.coords["z"].value.size, 9)
        self.assertEqual(df.coords["z"].dim, 2)
        self.assertEqual(len(df.variables.keys()), 1)
        self.assertEqual(df.variables["psi_squared"].name, "psi_squared")
        self.assertEqual(df.variables["psi_squared"].unit, "nm^-3")
        self.assertEqual(df.variables["psi_squared"].value.shape, (19, 19, 9))
        self.assertEqual(df.metadata, {})

    def test_txt(self):
        df = outputs.DataFile(
            join(folder_nn3, "variables_input.txt"), product="nextnano3"
        )
        self.assertEqual(len(df.coords.keys()), 0)
        self.assertEqual(len(df.variables.keys()), 3)
        self.assertEqual(df.variables["var_1"].name, "var_1")
        self.assertEqual(df.variables["var_1"].unit, default_unit)
        self.assertEqual(df.variables["var_1"].value, -47.5)
        self.assertEqual(df.variables["var_2"].value, 75)
        self.assertEqual(df.variables["string"].value, '"hello"')

        df = outputs.DataFile(
            join(folder_nn3, "variables_database.txt"), product="nextnano3"
        )
        self.assertEqual(len(df.coords.keys()), 0)
        self.assertEqual(len(df.variables.keys()), 0)

    def test_rest(self):
        files = ["example.log", "example.in"]
        for file in files:
            self.assertRaises(
                NotImplementedError,
                outputs.DataFile,
                join(folder_nnp, file),
                "nextnano3",
            )

    # TODO add tests for loading binary (different binary + avs not one file)


class TestOutputs_negf(unittest.TestCase):

    def test_dat(self):
        df = outputs.DataFile(
            join(folder_negf, "ReducedRealSpaceModes.dat"), product="nextnano.NEGF"
        )
        self.assertEqual(len(df.coords.keys()), 1)
        self.assertEqual(df.coords["Position"], df.coords[0])
        self.assertEqual(df.coords["Position"].name, "Position")
        self.assertEqual(df.coords["Position"].unit, "nm")
        self.assertEqual(df.coords["Position"].value.size, 608)
        self.assertEqual(len(df.variables.keys()), 19)
        self.assertEqual(df.variables["Conduction_BandEdge"], df.variables[0])
        self.assertEqual(
            df.variables["Conduction_BandEdge"].name, "Conduction_BandEdge"
        )
        self.assertEqual(df.variables["Conduction_BandEdge"].unit, "eV")
        self.assertEqual(df.variables["Conduction_BandEdge"].value.size, 608)
        self.assertEqual(df.variables["Psi_1 (lev.1 per.0)"], df.variables[1])
        self.assertEqual(
            df.variables["Psi_1 (lev.1 per.0)"].name, "Psi_1 (lev.1 per.0)"
        )
        self.assertEqual(df.variables["Psi_1 (lev.1 per.0)"].unit, "a.u.")
        self.assertEqual(df.variables["Psi_1 (lev.1 per.0)"].value.size, 608)
        self.assertEqual(df.metadata["ndim"], 1)
        self.assertEqual(df.metadata["dkeys"], [0])

        df = outputs.DataFile(
            join(folder_negf, "E_p (Kane energy).dat"), product="nextnano.NEGF"
        )
        self.assertEqual(df.coords["Position"], df.coords[0])
        self.assertEqual(df.coords["Position"].name, "Position")
        self.assertEqual(df.coords["Position"].unit, "nm")
        self.assertEqual(df.coords["Position"].value.size, 203)
        self.assertEqual(len(df.variables.keys()), 1)
        self.assertEqual(df.variables["E_p"].name, "E_p")
        self.assertEqual(df.variables["E_p"].unit, default_unit)
        self.assertEqual(df.variables["E_p"].value.size, 203)
        self.assertEqual(df.metadata["ndim"], 1)
        self.assertEqual(df.metadata["dkeys"], [0])

    def test_dat_FirstVarIsCoordFlag(self):
        df = outputs.DataFile(
            join(folder_negf, "ReducedRealSpaceModes.dat"),
            product="nextnano.NEGF",
            FirstVarIsCoordFlag=False,
        )
        self.assertEqual(len(df.coords.keys()), 0)
        self.assertEqual(len(df.variables.keys()), 20)
        self.assertEqual(df.variables["Position"].name, "Position")
        self.assertEqual(df.variables["Position"].unit, "nm")
        self.assertEqual(df.variables["Position"].value.size, 608)
        self.assertEqual(df.variables["Conduction_BandEdge"], df.variables[1])
        self.assertEqual(
            df.variables["Conduction_BandEdge"].name, "Conduction_BandEdge"
        )
        self.assertEqual(df.variables["Conduction_BandEdge"].unit, "eV")
        self.assertEqual(df.variables["Conduction_BandEdge"].value.size, 608)
        self.assertEqual(df.variables["Psi_1 (lev.1 per.0)"], df.variables[2])
        self.assertEqual(
            df.variables["Psi_1 (lev.1 per.0)"].name, "Psi_1 (lev.1 per.0)"
        )
        self.assertEqual(df.variables["Psi_1 (lev.1 per.0)"].unit, "a.u.")
        self.assertEqual(df.variables["Psi_1 (lev.1 per.0)"].value.size, 608)
        self.assertEqual(df.metadata["ndim"], 0)
        self.assertEqual(df.metadata["dkeys"], [])

        df = outputs.DataFile(
            join(folder_negf, "E_p (Kane energy).dat"),
            product="nextnano.NEGF",
            FirstVarIsCoordFlag=True,
        )
        self.assertEqual(df.coords["Position"], df.coords[0])
        self.assertEqual(df.coords["Position"].name, "Position")
        self.assertEqual(df.coords["Position"].unit, "nm")
        self.assertEqual(df.coords["Position"].value.size, 203)
        self.assertEqual(len(df.variables.keys()), 1)
        self.assertEqual(df.variables["E_p"].name, "E_p")
        self.assertEqual(df.variables["E_p"].unit, default_unit)
        self.assertEqual(df.variables["E_p"].value.size, 203)
        self.assertEqual(df.metadata["ndim"], 1)
        self.assertEqual(df.metadata["dkeys"], [0])

    def test_dat_no_units(self):
        df = outputs.DataFile(
            join(folder_negf, "datafile_with_no_units.dat"), product="nextnano.NEGF"
        )
        self.assertEqual(len(df.coords.keys()), 1)
        self.assertEqual(df.coords["Photon Energy"], df.coords[0])
        self.assertEqual(df.coords[0].name, "Photon Energy")
        self.assertEqual(df.coords["Photon Energy"].unit, "meV")
        self.assertEqual(df.coords["Photon Energy"].value.size, 3670)
        self.assertEqual(len(df.variables.keys()), 36)
        self.assertEqual(df.variables["Transition 2 => 3"], df.variables[0])
        self.assertEqual(df.variables["Transition 2 => 3"].unit, "a.u.")

        self.assertEqual(df.metadata["ndim"], 1)
        self.assertEqual(df.metadata["dkeys"], [0])

    def test_vtr(self):
        df = outputs.DataFile(
            join(folder_negf, "CarrierDensity_energy_resolved.vtr"),
            product="nextnano.NEGF",
        )
        self.assertEqual(len(df.coords.keys()), 2)
        self.assertEqual(list(df.coords.keys()), ["x", "y"])
        self.assertEqual(df.coords["x"].unit, default_unit)
        self.assertEqual(df.coords["x"].value.size, 176)
        self.assertEqual(df.coords["x"].dim, 0)
        self.assertEqual(df.coords["y"].unit, default_unit)
        self.assertEqual(df.coords["y"].value.size, 82)
        self.assertEqual(df.coords["y"].dim, 1)
        self.assertEqual(len(df.variables.keys()), 1)
        self.assertEqual(df.variables["Carrier density"].name, "Carrier density")
        self.assertEqual(df.variables["Carrier density"].unit, "cm^-3 eV^-1")
        self.assertEqual(df.variables["Carrier density"].value.shape, (176, 82))
        self.assertEqual(df.metadata, {})

    def test_rest(self):
        files = [
            "example.log",
            "example.in",
            "Material_Database.xml",
            "Convergence.txt",
        ]
        for file in files:
            self.assertRaises(
                NotImplementedError,
                outputs.DataFile,
                join(folder_negf, file),
                "nextnano.NEGF",
            )


# NEGF C# and NEGF C++ have identical outputs. Maybe no need to test.


class TestOutputs_msb(unittest.TestCase):

    def test_dat(self):
        df = outputs.DataFile(
            join(folder_msb, "BandEdge_conduction.dat"), product="nextnano.MSB"
        )
        self.assertEqual(len(df.coords.keys()), 1)
        self.assertEqual(df.coords["Position"].name, "Position")
        self.assertEqual(df.coords["Position"].unit, "nm")
        self.assertEqual(df.coords["Position"].value.size, 100)
        self.assertEqual(len(df.variables.keys()), 1)
        self.assertEqual(
            df.variables["Conduction Band Edge"].name, "Conduction Band Edge"
        )
        self.assertEqual(df.variables["Conduction Band Edge"].unit, "eV")
        self.assertEqual(df.variables["Conduction Band Edge"].value.size, 100)
        self.assertEqual(df.metadata["ndim"], 1)
        self.assertEqual(df.metadata["dkeys"], [0])

    def test_dat_FirstVarIsCoordFlag(self):
        df = outputs.DataFile(
            join(folder_msb, "BandEdge_conduction.dat"),
            product="nextnano.MSB",
            FirstVarIsCoordFlag=False,
        )
        self.assertEqual(len(df.coords.keys()), 0)
        self.assertEqual(len(df.variables.keys()), 2)
        self.assertEqual(df.variables["Position"].name, "Position")
        self.assertEqual(df.variables["Position"].unit, "nm")
        self.assertEqual(df.variables["Position"].value.size, 100)
        self.assertEqual(
            df.variables["Conduction Band Edge"].name, "Conduction Band Edge"
        )
        self.assertEqual(df.variables["Conduction Band Edge"].unit, "eV")
        self.assertEqual(df.variables["Conduction Band Edge"].value.size, 100)
        self.assertEqual(df.metadata["ndim"], 0)
        self.assertEqual(df.metadata["dkeys"], [])

        df = outputs.DataFile(
            join(folder_msb, "BandEdge_conduction.dat"),
            product="nextnano.MSB",
            FirstVarIsCoordFlag=True,
        )
        self.assertEqual(len(df.coords.keys()), 1)
        self.assertEqual(df.coords["Position"].name, "Position")
        self.assertEqual(df.coords["Position"].unit, "nm")
        self.assertEqual(df.coords["Position"].value.size, 100)
        self.assertEqual(len(df.variables.keys()), 1)
        self.assertEqual(
            df.variables["Conduction Band Edge"].name, "Conduction Band Edge"
        )
        self.assertEqual(df.variables["Conduction Band Edge"].unit, "eV")
        self.assertEqual(df.variables["Conduction Band Edge"].value.size, 100)
        self.assertEqual(df.metadata["ndim"], 1)
        self.assertEqual(df.metadata["dkeys"], [0])

    def test_vtr(self):
        df = outputs.DataFile(
            join(folder_msb, "DOS_Lead_Source_position_resolved.vtr"),
            product="nextnano.MSB",
        )
        self.assertEqual(len(df.coords.keys()), 2)
        self.assertEqual(list(df.coords.keys()), ["x", "y"])
        self.assertEqual(df.coords["x"].unit, default_unit)
        self.assertEqual(df.coords["x"].value.size, 50)
        self.assertEqual(df.coords["x"].dim, 0)
        self.assertEqual(df.coords["y"].unit, default_unit)
        self.assertEqual(df.coords["y"].value.size, 401)
        self.assertEqual(df.coords["y"].dim, 1)
        self.assertEqual(len(df.variables.keys()), 1)
        self.assertEqual(df.variables[0], df.variables["Density of States (Source)"])
        self.assertEqual(df.variables[0].name, "Density of States (Source)")
        self.assertEqual(df.variables[0].unit, "1/eV/nm")
        self.assertEqual(df.variables[0].value.shape, (50, 401))
        self.assertEqual(df.metadata, {})


class TestOutput(unittest.TestCase):

    def test_data(self):
        df = outputs.DataFile(
            join(folder_nnp, "bandedges_2d.fld"), product="nextnano++"
        )
        self.assertEqual(len(df.data), len(df.coords) + len(df.variables))
        for key, value in df.coords.items():
            self.assertEqual(df.data[key], value)
        for key, value in df.variables.items():
            self.assertEqual(df.data[key], value)

    def test_access_by_index(self):
        df = outputs.DataFile(
            join(folder_nnp, "bandedges_2d.fld"), product="nextnano++"
        )
        for key, value in df.coords.items():
            self.assertEqual(df[key], value)
        for key, value in df.variables.items():
            self.assertEqual(df[key], value)

    def test_for_loop(self):
        df = outputs.DataFile(
            join(folder_nnp, "bandedges_2d.fld"), product="nextnano++"
        )
        for i, dfi in enumerate(df):
            self.assertEqual(df.data[i], dfi)


class TestDataFolder(unittest.TestCase):
    def test_init(self):
        dummy_folder = os.path.join("tests", "dummy")
        self.assertRaises(ValueError, outputs.DataFolder, dummy_folder)

        tests_folder = "tests"
        datafolder = outputs.DataFolder(tests_folder)
        self.assertTrue("datafiles" in datafolder.folders)
        self.assertTrue(
            os.path.join(tests_folder, "test_mycollections.py") in datafolder.files
        )
        self.assertTrue(
            os.path.join(tests_folder, "test_outputs.py") in datafolder.files
        )
        self.assertFalse("NotExistedFile.py" in datafolder.files)
        self.assertFalse(
            os.path.join(tests_folder, "NotExistedFile.py") in datafolder.files
        )

        datafolder = outputs.DataFolder(folder_nnp)

        self.assertTrue(datafolder.folders)
        self.assertTrue(datafolder.files)

        self.assertEqual(len(datafolder.files), 17)
        self.assertTrue(
            os.path.join(folder_nnp, "bandedges_2d_old.fld") in datafolder.files
        )

    def test_navigation(self):
        tests_folder = "tests"
        datafolder = outputs.DataFolder(tests_folder)
        self.assertTrue("configs" in datafolder.__dict__)
        self.assertIsInstance(datafolder.configs, outputs.DataFolder)
        self.assertIsInstance(datafolder.datafiles.nextnano3, outputs.DataFolder)
        self.assertIsInstance(
            datafolder.datafiles.folders["nextnano++"], outputs.DataFolder
        )
        nnp_folder = datafolder.datafiles.folders["nextnano++"]
        self.assertTrue(os.path.samefile(nnp_folder.fullpath, folder_nnp))
        self.assertTrue(
            os.path.join(folder_nnp, "bandedges_2d_old.fld") in nnp_folder.files
        )

    def test_filenamess(self):

        datafolder = outputs.DataFolder(folder_nnp)
        self.assertIn("only_variables.in", datafolder.filenames())
        self.assertNotIn("only_variables_0.in", datafolder.filenames())
        self.assertNotIn(
            os.path.join(folder_nnp, "only_variables.in"), datafolder.filenames()
        )
        self.assertEqual(len(datafolder.filenames()), 17)
        tests_folder = "tests"
        datafolder = outputs.DataFolder(tests_folder)

        self.assertIn("test_all.py", datafolder.filenames())
        self.assertIn("test_outputs.py", datafolder.filenames())

        self.assertNotIn("only_variables.in", datafolder.filenames())
        self.assertNotIn(
            os.path.join(folder_nnp, "only_variables.in"), datafolder.filenames()
        )

    def test_find(self):
        tests_folder = "tests"
        datafolder = outputs.DataFolder(tests_folder)
        self.assertEqual(len(datafolder.find("")), 12)

        self.assertIn(os.path.join(tests_folder, "__init__.py"), datafolder.find(""))
        self.assertIn(
            os.path.join(tests_folder, "test_commands.py"), datafolder.find("")
        )

        self.assertNotIn(
            os.path.join(folder_nnp, "only_variables.in"), datafolder.find("")
        )
        self.assertNotIn("only_variables.in", datafolder.find(""))

        self.assertNotIn(
            os.path.join(tests_folder, "__init__.py"), datafolder.find("test")
        )
        self.assertIn(
            os.path.join(tests_folder, "test_commands.py"), datafolder.find("test")
        )

        self.assertNotIn(
            os.path.join(folder_nnp, "only_variables.in"), datafolder.find("test")
        )
        self.assertNotIn("only_variables.in", datafolder.find("test"))
        self.assertNotIn(
            os.path.join(tests_folder, "test_commands.py"), datafolder.find("test_i")
        )
        self.assertEqual(len(datafolder.find(".vtr")), 0)

        datafolder = outputs.DataFolder(folder_nnp)
        self.assertNotIn(
            os.path.join(tests_folder, "__init__.py"), datafolder.find("tests")
        )
        self.assertNotIn(
            os.path.join(tests_folder, "test_commands.py"), datafolder.find("tests")
        )

        self.assertNotIn(
            os.path.join(folder_nnp, "only_variables.in"), datafolder.find("tests")
        )
        self.assertIn(
            os.path.join(folder_nnp, "only_variables.in"), datafolder.find("only")
        )
        self.assertEqual(len(datafolder.find("bandedges")), 7)
        self.assertNotIn("only_variables.in", datafolder.find("abls"))
        self.assertEqual(len(datafolder.find(".vtr")), 2)

        # deep
        datafolder = outputs.DataFolder(tests_folder)
        self.assertIn(
            os.path.join(tests_folder, "__init__.py"), datafolder.find("", deep=True)
        )
        self.assertIn(
            os.path.join(tests_folder, "test_commands.py"),
            datafolder.find("", deep=True),
        )
        self.assertIn(
            os.path.join(folder_nnp, "only_variables.in"),
            datafolder.find("", deep=True),
        )
        self.assertNotIn("only_variables.in", datafolder.find("", deep=True))

        self.assertNotIn(
            os.path.join(tests_folder, "__init__.py"),
            datafolder.find("test", deep=True),
        )
        self.assertIn(
            os.path.join(tests_folder, "test_commands.py"),
            datafolder.find("test", deep=True),
        )

        self.assertNotIn(
            os.path.join(folder_nnp, "only_variables.in"),
            datafolder.find("test", deep=True),
        )
        self.assertIn(
            os.path.join(folder_nnp, "only_variables.in"),
            datafolder.find("only", deep=True),
        )
        self.assertNotIn(
            os.path.join(folder_nnp, "only_variables.in"),
            datafolder.find("nextnano", deep=True),
        )
        self.assertNotIn("only_variables.in", datafolder.find("only"))
        self.assertNotIn(
            os.path.join(tests_folder, "test_commands.py"),
            datafolder.find("test_i", deep=True),
        )
        self.assertNotEqual(len(datafolder.find(".vtr", deep=True)), 0)

        datafolder = outputs.DataFolder(folder_nnp)

        self.assertNotIn(
            os.path.join(tests_folder, "__init__.py"), datafolder.find("", deep=True)
        )
        self.assertNotIn(
            os.path.join(tests_folder, "test_commands.py"),
            datafolder.find("", deep=True),
        )
        self.assertIn(
            os.path.join(folder_nnp, "only_variables.in"),
            datafolder.find("", deep=True),
        )
        self.assertNotIn("only_variables.in", datafolder.find("", deep=True))

        self.assertNotIn(
            os.path.join(folder_nnp, "only_variables.in"),
            datafolder.find("test", deep=True),
        )
        self.assertIn(
            os.path.join(folder_nnp, "only_variables.in"),
            datafolder.find("only", deep=True),
        )
        self.assertNotIn(
            os.path.join(folder_nnp, "only_variables.in"),
            datafolder.find("nextnano", deep=True),
        )
        self.assertNotIn("only_variables.in", datafolder.find("only"))
        self.assertNotIn(
            os.path.join(tests_folder, "test_commands.py"),
            datafolder.find("test_i", deep=True),
        )
        self.assertNotEqual(len(datafolder.find(".vtr", deep=True)), 0)
        self.assertEqual(len(datafolder.find("bandedges", deep=True)), 17)

    def test_find_multiple(self):
        tests_folder = "tests"
        datafolder = outputs.DataFolder(tests_folder)
        self.assertEqual(len(datafolder.find_multiple(("",))), 12)

        self.assertIn(
            os.path.join(tests_folder, "__init__.py"), datafolder.find_multiple(("",))
        )

        self.assertNotIn("only_variables.in", datafolder.find_multiple(("",)))

        datafolder = outputs.DataFolder(folder_nnp)
        self.assertNotIn(
            os.path.join(tests_folder, "__init__.py"),
            datafolder.find_multiple(("tests",)),
        )

        self.assertEqual(len(datafolder.find_multiple(("bandedges",))), 7)
        self.assertEqual(len(datafolder.find_multiple(("bandedges", "2d"))), 5)

        self.assertNotIn("only_variables.in", datafolder.find_multiple(("abls",)))

        self.assertEqual(len(datafolder.find_multiple((".vtr",))), 2)
        self.assertEqual(len(datafolder.find_multiple((".vt", "r"))), 2)

    def test_go_to(self):
        tests_folder = "tests"
        datafolder = outputs.DataFolder(tests_folder)
        self.assertIsInstance(datafolder.go_to("datafiles"), outputs.DataFolder)
        self.assertIsInstance(datafolder.go_to("__init__.py"), str)
        self.assertTrue(
            os.path.samefile(
                datafolder.go_to("__init__.py"),
                os.path.join(tests_folder, "__init__.py"),
            )
        )
        self.assertFalse(
            os.path.samefile(
                datafolder.go_to("__init__.py"), os.path.join(tests_folder)
            )
        )

        datafolder_nnp = datafolder.go_to("datafiles", "nextnano++")

        self.assertTrue(os.path.samefile(datafolder_nnp.fullpath, folder_nnp))
        self.assertEqual(len(datafolder_nnp.files), 17)

    def test_file(self):
        tests_folder = "tests"
        datafolder = outputs.DataFolder(tests_folder)
        self.assertRaises(ValueError, datafolder.file, "hello_world")

        self.assertEqual(
            datafolder.datafiles.folders["nextnano++"].file("bandedges.vtr"),
            os.path.join(folder_nnp, "bandedges.vtr"),
        )

        self.assertRaises(
            ValueError,
            datafolder.datafiles.folders["nextnano++"].file,
            "bandedgesxxxx.vtr",
        )
        warnings.filterwarnings("ignore", "More than one file match")
        self.assertTrue(datafolder.datafiles.folders["nextnano++"].file("bandedges"))
        warnings.filterwarnings("default")

    def test_make_tree(self):
        tests_folder = "tests"
        datafolder = outputs.DataFolder(tests_folder)

        tree_list = datafolder.make_tree()
        self.assertEqual(tree_list[1], "    configs/")
        self.assertEqual(tree_list[2], "        .nnconfig")
        self.assertEqual(tree_list[5], "        nextnano++/")


if __name__ == "__main__":
    unittest.main()
