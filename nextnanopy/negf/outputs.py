import numpy as np
from nextnanopy.utils.mycollections import DictList
from nextnanopy.outputs import Output, AvsAscii, Vtk, DataFileTemplate, Dat
from nextnanopy.utils.datasets import Variable, Coord
import re
import os


class DataFile(DataFileTemplate):
    def __init__(self, fullpath, **loader_kwargs):
        super().__init__(fullpath, product="nextnano.NEGF")
        self.load(**loader_kwargs)

    def get_loader(self):
        if self.extension in [".v", ".fld", ".coord"]:
            loader = AvsAscii
        elif self.extension == ".vtr":
            loader = Vtk
        elif self.extension == ".txt":
            raise NotImplementedError(
                f"Loading nextnano.NEGF datafiles with extension.txt is not implemented yet"
            )
        elif self.extension == ".dat":
            loader = Dat
        else:
            raise NotImplementedError(
                f"Loading datafile with extension {self.extension} is not implemented yet"
            )
        return loader


def get_iv(path=""):
    piv = os.path.join(path, "Current_vs_Voltage.dat")
    return np.loadtxt(piv, skiprows=1, delimiter="\t", unpack=True)


def get_WannierStark_on(folder):
    ws = np.loadtxt(
        folder + r"\WannierStark\\WannierStark_statesOn.dat",
        skiprows=2,
        delimiter="\t",
        unpack=True,
    )
    #  print('Number of states: ', len(ws)-2)
    return ws


def get_WannierStark(folder):
    ws = np.loadtxt(
        folder + r"\WannierStark\\WannierStark_states.dat",
        skiprows=2,
        delimiter="\t",
        unpack=True,
    )
    #  print('Number of states: ', len(ws)-2)
    return ws


def get_WannierStark_norm(folder, scaling_factor=1):
    ws = np.loadtxt(
        folder + r"\WannierStark\\WannierStark_states.dat",
        skiprows=2,
        delimiter="\t",
        unpack=True,
    )
    #  print('Number of states: ', len(ws)-2)
    norm = min(ws[1])
    z = ws[0]
    pot = ws[1] - norm
    ws_norm = ws[2:] - norm
    ws_norm_scal = scale_wf(ws_norm, scaling_factor)
    return z, pot, ws_norm_scal


def get_WannierStark_norm_cpp(folder, scaling_factor=1):
    ws = np.loadtxt(
        folder + r"\EnergyEigenstates\\EigenStates.dat",
        skiprows=2,
        delimiter="\t",
        unpack=True,
    )
    #  print('Number of states: ', len(ws)-2)
    norm = min(ws[1])
    z = ws[0]
    pot = ws[1] - norm
    ws_norm = ws[2:] - norm
    ws_norm_scal = scale_wf(ws_norm, scaling_factor)
    return z, pot, ws_norm_scal


def scale_wf(wf_input, factor):
    scaled = np.copy(wf_input)
    for i, cur in enumerate(wf_input):
        mi = min(cur)
        ma = max(cur)
        scaled[i] = np.interp(cur, [mi, ma], [mi, factor * (ma - mi) + mi])

    return scaled
