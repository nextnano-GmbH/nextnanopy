import nextnanopy as nn
from nextnanopy.utils.misc import mkdir_if_not_exist
from nextnanopy.utils.plotting import use_nxt_style, NXT_BLUE, WILD_STRAWBERRY, GREEN
import sys,os
#import numpy as np
import matplotlib.pyplot as plt
from math import pi,exp
from scipy.constants import hbar,Boltzmann,elementary_charge,electron_mass
from pathlib import Path

use_nxt_style()
#FigFormat = '.pdf'
#FigFormat = '.svg'
FigFormat = '.jpg'
#FigFormat = '.png'

software = 'nextnano3'

folder_examples    = r'C:\Program Files\nextnano\2025_09_18\nextnano3\examples'


#++++++++++++++++++++++++++++++++++++++++++++++
# These lines have to be adjusted by the user.  
#++++++++++++++++++++++++++++++++++++++++++++++
#folder_examples_nn3 = r'N:\users\nextnano\nextnano GmbH - Tutorials\Tutorials\2D The CBR method (Transmission)'
#===========================

software_short    = '_nn3'




#==========================================================================
# Define input and output folders. If they do not exist, they are created.
#==========================================================================

folder_output        = nn.config.config[software]['outputdirectory']

folder_python_output = folder_output
#folder_examples = folder_python_input

mkdir_if_not_exist(folder_output)
mkdir_if_not_exist(folder_python_output)


input_file_name = r'1D_IntersubbandAbsorption_InfiniteWell_GaAs_Chuang_sg_nn3.nn3'
input_file_path = Path(folder_examples) / input_file_name
input_file = nn.InputFile(input_file_path)

input_file.save(temp=True) # save a temporary copy of the input file
input_file_path = input_file.fullpath

sweep_variable = "QuantumWellWidth"
sweep_values = [i for i in range(10, 20, 3)]  # in nm

sweep  = nn.Sweep({sweep_variable: sweep_values}, fullpath=input_file_path)
sweep.save_sweep(integer_only_in_name=True)
sweep.execute_sweep(show_log=False, delete_input_files=True, parallel_limit=3, separate_sweep_dir=False)
sweep_infodict = sweep.sweep_output_infodict

fig_states, axes_states = plt.subplots(2, 2, figsize=(10, 8)) # 2x2 grid of subplots, change if needed

axes_states = axes_states.flatten()  # Flatten to easily iterate over

# plot bandedges and states
for i, (folder_path, var_dict) in enumerate(sweep_infodict.items()):
    var_value = var_dict[sweep_variable]
    dfolder = nn.DataFolder(folder_path)
    bandedges_file = dfolder.go_to("band_structure", "BandEdges.dat")
    band_structure_df = nn.DataFile(bandedges_file, product=software)

    wf_file = dfolder.go_to("Schroedinger_1band", "cb1_sg1_deg1_psi_squared_shift.dat")
    wf_df = nn.DataFile(wf_file, product=software)

    ax = axes_states[i]
    ax.set_title(f'Well Width: {var_value} nm') 
    # plot band edges and states
    coord = band_structure_df.coords[0].value
    cb = band_structure_df.variables["Gamma_bandedge"].value

    ax.plot(coord, cb, label=f'CB', color=WILD_STRAWBERRY)

    coord_wf = wf_df.coords[0].value
    for i in range(1, 5):
        var = wf_df.variables[f'psi^2_{i}']
        prob_density = var.value
        ax.plot(coord_wf, prob_density, color=NXT_BLUE, lw=1.0, label=f'Probability density')  # scaled and shifted for visibility
    fermi_level = band_structure_df.variables['FermiLevel_el'].value
    ax.plot(coord, fermi_level, linestyle='--', color=GREEN, label='Fermi Level')
    ax.set_ylim(-0.4, 1.0)
    ax.set_xlabel('Position (nm)')
    ax.set_ylabel('Energy (eV)')
    
    # legend with unique labels only
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax.legend(unique.values(), unique.keys(), loc="lower center")
fig_states.tight_layout()

# plot absorption spectrum
plt.figure(figsize=(8, 6)) # make a new figure for absorption
for folder_path, var_dict in sweep_infodict.items():
    var_value = var_dict[sweep_variable]
    dfolder = nn.DataFolder(folder_path)
    absorption_file = dfolder.go_to("optics", "absorption_intraband_cb1_sg1_deg1_z.dat")
    absorption_df = nn.DataFile(absorption_file, product=software)

    energy = absorption_df.coords[0].value
    absorption = absorption_df.variables[0].value

    plt.plot(energy, absorption, label=f'Well Width: {var_value} nm')
plt.xlim(0, 0.6)
plt.legend()
plt.xlabel('Energy (eV)')
plt.ylabel('Absorption Coefficient (cm^-1)')

# doping concentration sweep

sweep_variable = "DopingConcentration"
sweep_values = [9e17, 1e18, 1.1e18]  # in cm^-3

sweep  = nn.Sweep({sweep_variable: sweep_values}, fullpath=input_file_path)
sweep.save_sweep(integer_only_in_name=True)
sweep.execute_sweep(show_log=False, delete_input_files=True, parallel_limit=3, separate_sweep_dir=False)
sweep_infodict = sweep.sweep_output_infodict


plt.figure(figsize=(8, 6)) # make a new figure for absorption
for folder_path, var_dict in sweep_infodict.items():
    var_value = var_dict[sweep_variable]
    dfolder = nn.DataFolder(folder_path)
    absorption_file = dfolder.go_to("optics", "absorption_intraband_cb1_sg1_deg1_z.dat")
    absorption_df = nn.DataFile(absorption_file, product=software)
    energy = absorption_df.coords[0].value
    absorption = absorption_df.variables[0].value
    plt.plot(energy, absorption, label=f'Doping: {var_value:.1e} cm$^{{-3}}$')
plt.xlim(0, 0.6)
plt.legend()
plt.xlabel('Energy (eV)')
plt.ylabel('Absorption Coefficient (cm^-1)')

    

plt.show()





