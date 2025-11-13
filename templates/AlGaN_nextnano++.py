import nextnanopy as nn
from nextnanopy.utils.misc import mkdir_if_not_exist
import sys,os
import matplotlib.pyplot as plt
import pathlib

# config file is stored in C:\Users\<User>\.nextnanopy-config (home directory)

#++++++++++++++++++++++++++++++++++++++++++++++
# Specify output image format
#++++++++++++++++++++++++++++++++++++++++++++++
#FigFormat = '.pdf'
FigFormat = '.svg'
# FigFormat = '.jpg'
#FigFormat = '.png'

filename = r'AlGaN_nnp.nnp'



#++++++++++++++++++++++++++++++++++++++++++++++
# Input file is located on Github
#++++++++++++++++++++++++++++++++++++++++++++++
input_folder = os.path.join(pathlib.Path(__file__).parent.resolve(), r'input files')

# detect software based on input file
software = "nextnano++"
software_short = "nnp"
FileExtension = ".nnp"

def plot_vb_bandedges(ax, bandedges_data_file):
    """
    Plots the vb bandedges as a function of position
    """
    coord = bandedges_data_file.coords[0].value
    hh = bandedges_data_file.variables["HH"].value
    lh = bandedges_data_file.variables["LH"].value
    so = bandedges_data_file.variables["SO"].value
    ax.plot(coord, hh, label='heavy hole')
    ax.plot(coord, lh, label='light hole')
    ax.plot(coord, so, label='crystall-field hole')


input_path = os.path.join(input_folder, filename)

sweep_variables = {"Al_substrate": ["0.0","0.5","1.0"]}  
title_endings = ["On GaN", "On Al0.5Ga0.5N", "On AlN"]


sweep = nn.Sweep(variables_to_sweep=sweep_variables, fullpath=input_path)

sweep.save_sweep(integer_only_in_name=True)
sweep.execute_sweep(show_log=False, delete_input_files=True, parallel_limit=3)

sweep_datafolder = nn.DataFolder(sweep.sweep_output_directory)


for folder, title_ending in zip(sweep_datafolder.folders, title_endings):
    fig, ax = plt.subplots()
    bandedges_file_path = folder.go_to("bias_00000", "bandedges.dat")
    bandedges_data_file = nn.DataFile(bandedges_file_path, product=software)
    plot_vb_bandedges(ax, bandedges_data_file)
    ax.set_xlabel("Al alloy content")
    ax.legend()
    ax.set_title(software + " Valence band edges of Al$_x$Ga$_{1-x}$N" + " (" + title_ending + ')')
    ax.set_ylabel(f"Energy (eV)")
    fig.tight_layout()
    fig.savefig(os.path.join(folder.fullpath, 'vb_band_edges'+FigFormat))
plt.show()
