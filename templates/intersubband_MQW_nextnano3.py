import nextnanopy as nn
from nextnanopy.utils.misc import mkdir_if_not_exist
import sys,os
#import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from nextnanopy.utils.plotting import use_nxt_style, NXT_BLUE, WILD_STRAWBERRY, GREEN, NXT_BLUE_COLORMAP
use_nxt_style()

#================================
# Specify software product here!
#================================
software = 'nextnano++'

folder_examples    = r'C:\Program Files\nextnano\2025_09_18\nextnano3\examples'

input_files_sg = [
    r"1DSirtoriPRB1994_OneWell_sg_self-consistent_nn3.nn3",
    r"1DSirtoriPRB1994_TwoCoupledWells_sg_self-consistent_nn3.nn3",
    r"1DSirtoriPRB1994_ThreeCoupledWells_sg_self-consistent_nn3.nn3"
]

# if true, the calculation time increases significantly
self_consistent_kp = False #  if true, => self-consistent k.p calculations, else quantum-only k.p calculations

if self_consistent_kp:
    input_files_kp = [
        r"1DSirtoriPRB1994_OneWell_kp_self-consistent_nn3.nn3",
        r"1DSirtoriPRB1994_TwoCoupledWells_kp_self-consistent_nn3.nn3",
        r"1DSirtoriPRB1994_ThreeCoupledWells_kp_self-consistent_nn3.nn3"
    ]
else: 
    input_files_kp = [
        r"1DSirtoriPRB1994_OneWell_kp_quantum-only_nn3.nn3",
        r"1DSirtoriPRB1994_TwoCoupledWells_kp_quantum-only_nn3.nn3",
        r"1DSirtoriPRB1994_ThreeCoupledWells_kp_quantum-only_nn3.nn3"
    ]

output_folders_sg = [] # output folders for single band calculations

for input_file_name in input_files_sg:
    input_file_path = Path(folder_examples) / input_file_name
    input_file = nn.InputFile(input_file_path)
    input_file.execute()
    output_folder = input_file.folder_output
    output_folders_sg.append(output_folder)

labels = ['One Well', 'Two Coupled Wells', 'Three Coupled Wells']  
fig, axes_states = plt.subplots(1, 3, figsize=(15, 5)) # 1x3 grid of subplots
axes_states = axes_states.flatten()
number_of_states_localized = [2, 3, 3] # Number of localized states to plot for each structure
# plot states 
for output_folder, label, ax, number_of_states in zip(output_folders_sg, labels, axes_states, number_of_states_localized):
    dfolder = nn.DataFolder(output_folder)
    bandedges_file = dfolder.go_to("band_structure", "BandEdges.dat")
    band_structure_df = nn.DataFile(bandedges_file, product=software)
   
    wf_file = dfolder.go_to("Schroedinger_1band", "cb1_sg1_deg1_psi_squared_shift.dat")
    wf_df = nn.DataFile(wf_file, product=software)

    ax.set_title(f'Effective mass, {label}') 
    # plot band edges and states
    coord = band_structure_df.coords[0].value
    cb = band_structure_df.variables["Gamma_bandedge"].value

    ax.plot(coord, cb, label=f'CB', color=WILD_STRAWBERRY)

    coord_wf = wf_df.coords[0].value
    for i in range(1, number_of_states+1):
        var = wf_df.variables[f'psi^2_{i}']
        prob_density = var.value
        ax.plot(coord_wf, prob_density, color=NXT_BLUE, label=f'Probability density')  # scaled and shifted for visibility
    fermi_level = band_structure_df.variables['FermiLevel_el'].value
    ax.plot(coord, fermi_level, linestyle='--', color=GREEN, label='Fermi Level')
    ax.set_ylim(-0.4, 0.5)
    ax.set_xlabel('Position (nm)')
    ax.set_ylabel('Energy (eV)')
    
    # legend with unique labels only
    handles, plot_labels = ax.get_legend_handles_labels()
    unique = dict(zip(plot_labels, handles))
    ax.legend(unique.values(), unique.keys(), loc="lower center")

# plot absorption spectra

fig, ax = plt.subplots(figsize=(8, 6))
for output_folder, label in zip(output_folders_sg, labels):
    dfolder = nn.DataFolder(output_folder)
    absorption_file = dfolder.go_to("optics", "absorption_intraband_cb1_sg1_deg1_z.dat")
    absorption_df = nn.DataFile(absorption_file, product=software)

    energy = absorption_df.coords[0].value  # in eV
    absorption = absorption_df.variables[0].value  # in 1/cm

    ax.plot(energy, absorption, label=label)
fig.suptitle("Intersubband Absorption Spectra, effective mass approximation")
ax.legend()
ax.set_xlabel('Energy (eV)')
ax.set_ylabel('Absorption coefficient (1/cm)')


# plot spatially resolved absorption spectra (2D files)
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
for output_folder, label, ax in zip(output_folders_sg, labels, axes):
    dfolder = nn.DataFolder(output_folder)
    absorption_file_2d = dfolder.go_to("optics", "absorption_position_resolved_intraband_cb1_sg1_deg1_z.vtr")
    absorption_df_2d = nn.DataFile(absorption_file_2d, product=software)

    x=absorption_df_2d.coords['x']
    y=absorption_df_2d.coords['y']
# z=absorption_df_2d.variables['psi_squared']
    z=absorption_df_2d.variables[0]

    pcolor = ax.pcolormesh(x.value,y.value,z.value.T, cmap=NXT_BLUE_COLORMAP, vmin=0, vmax=30000)

    ax.set_xlabel('Position (nm)')
    ax.set_ylabel('Energy (eV)')
    ax.set_title(f'{label}')
cbar = fig.colorbar(pcolor)
cbar.set_label(f"{z.name} ({z.unit})")
fig.tight_layout()
fig.suptitle("Spatially Resolved Absorption Spectra, effective mass approximation")

# =================================================================================================================
# THE SAME FOR k.p CALCULATIONS ###################################################################################
# =================================================================================================================

output_folders_kp = [] # output folders for k.p calculations

for input_file_name in input_files_kp:
    input_file_path = Path(folder_examples) / input_file_name
    input_file = nn.InputFile(input_file_path)
    input_file.execute()
    output_folder = input_file.folder_output
    output_folders_kp.append(output_folder)

labels = ['One Well', 'Two Coupled Wells', 'Three Coupled Wells']  
fig, axes_states = plt.subplots(1, 3, figsize=(15, 5)) # 1x3 grid of subplots
axes_states = axes_states.flatten()

# plot states 
for output_folder, label, ax, number_of_states in zip(output_folders_kp, labels, axes_states, number_of_states_localized):
    dfolder = nn.DataFolder(output_folder)
    bandedges_file = dfolder.go_to("band_structure", "BandEdges.dat")
    band_structure_df = nn.DataFile(bandedges_file, product=software)

    wf_file = dfolder.go_to('Schroedinger_kp', 'kp8_psi_squared_el_kpar001_shift.dat')
    wf_df = nn.DataFile(wf_file, product=software)

    ax.set_title(f'8-band k.p, {label}') 
    # plot band edges and states
    coord = band_structure_df.coords[0].value
    cb = band_structure_df.variables["Gamma_bandedge"].value

    ax.plot(coord, cb, label=f'CB', color=WILD_STRAWBERRY)

    coord_wf = wf_df.coords[0].value
    for i in range(1, number_of_states*2+1): # factor 2 because of spin degeneracy
        var = wf_df.variables[f'psi^2_{i}']
        prob_density = var.value
        ax.plot(coord_wf, prob_density, color=NXT_BLUE, label=f'Probability density')  # scaled and shifted for visibility
    fermi_level = band_structure_df.variables['FermiLevel_el'].value
    ax.plot(coord, fermi_level, linestyle='--', color=GREEN, label='Fermi Level')
    ax.set_ylim(-0.3, 0.7)
    ax.set_xlabel('Position (nm)')
    ax.set_ylabel('Energy (eV)')
    
    # legend with unique labels only
    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    ax.legend(unique.values(), unique.keys(), loc="lower center")
fig.suptitle("8-band k.p")
# plot absorption spectra only if self-consistent k.p calculations were performed

if self_consistent_kp: # for quantum-only k.p calculations, absorption is not adequately calculated
    fig, ax = plt.subplots(figsize=(8, 6))
    for output_folder, label in zip(output_folders_kp, labels):
        dfolder = nn.DataFolder(output_folder)
        absorption_file = dfolder.go_to("optics", "absorption_intraband_cb1_kp8_z.dat")
        absorption_df = nn.DataFile(absorption_file, product=software)

        energy = absorption_df.coords[0].value  # in eV
        absorption = absorption_df.variables[0].value  # in 1/cm

        ax.plot(energy, absorption, label=label)
    fig.suptitle("Intersubband Absorption Spectra, 8-band k.p")
    ax.legend()
    ax.set_xlabel('Energy (eV)')
    ax.set_ylabel('Absorption coefficient (1/cm)')

    # plot spatially resolved absorption spectra (2D files)
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for output_folder, label, ax in zip(output_folders_kp, labels, axes):
        dfolder = nn.DataFolder(output_folder)
        absorption_file_2d = dfolder.go_to("optics", "absorption_position_resolved_intraband_cb1_kp8_z.vtr")
        absorption_df_2d = nn.DataFile(absorption_file_2d, product=software)

        x=absorption_df_2d.coords['x']
        y=absorption_df_2d.coords['y']
    # z=absorption_df_2d.variables['psi_squared']
        z=absorption_df_2d.variables[0]

        pcolor = ax.pcolormesh(x.value,y.value,z.value.T, cmap=NXT_BLUE_COLORMAP, vmin=0, vmax=30000)

        ax.set_xlabel('Position (nm)')
        ax.set_ylabel('Energy (eV)')
        ax.set_title(f'{label}')
    cbar = fig.colorbar(pcolor)
    cbar.set_label(f"{z.name} ({z.unit})")
    fig.tight_layout()
    fig.suptitle("Spatially Resolved Absorption Spectra, 8-band k.p")

plt.show()
