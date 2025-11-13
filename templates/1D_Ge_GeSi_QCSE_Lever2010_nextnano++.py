import nextnanopy as nn
from nextnanopy.utils.misc import mkdir_if_not_exist
import sys,os
#import numpy as np
import matplotlib.pyplot as plt


FigFormat1 = '.pdf' # high quality
#FigFormat = '.svg' # high quality'
FigFormat2 = '.jpg' # poor quality
#FigFormat = '.png' # poor quality

software = 'nextnano++'

def plot_bandedges(ax, bandedges_data_file):
    "Handy function to plot bandedges and states"
    coord = bandedges_data_file.coords[0].value
    cb = bandedges_data_file.variables["Gamma"].value
    hh = bandedges_data_file.variables["HH"].value
    lh = bandedges_data_file.variables["LH"].value
    so = bandedges_data_file.variables["SO"].value
    ax.plot(coord, cb, label='CB')
    ax.plot(coord, hh, label='HH')
    ax.plot(coord, lh, label='LH')
    ax.plot(coord, so, label='SO')
    ax.set_xlabel('Position (nm)')
    ax.set_ylabel('Energy (eV)')

def plot_states(ax, states_data_file):
    coord = states_data_file.coords[0].value
    for var in states_data_file.variables:
       if var.name.startswith("E"):
          # ignore energy variables
          continue
       prob_density = var.value
       ax.plot(coord, prob_density, color="grey", alpha=0.7, lw=0.5)



folder_examples_nnp    = r'C:\Program Files\nextnano\2025_09_18\nextnano++\examples\optical_spectra'

file_name = "1D_Ge_GeSi_QCSE_Lever2010_8kp_nnp_exciton.nnp"

input_file_path = os.path.join(folder_examples_nnp, file_name)

input_file = nn.InputFile(input_file_path)

input_file.save(temp=True) # save a temporary copy of the input file

input_file.execute()

output_folder = input_file.folder_output

print('Output folder: ', output_folder)

bias_list = [0, 1, 2, 3]
el_field_list = [0, 40, 80, 120 ] # in kV/cm
datafolder = nn.DataFolder(output_folder)
# plot states for every bias
for bias in bias_list:
    bias_folder_name = f"bias_0000{bias}"
    bandedges_file_path = datafolder.go_to(bias_folder_name, "bandedges.dat")
    states_file_path = datafolder.go_to(bias_folder_name, "quantum", "quantum_region", "kp8", "probabilities_shift_k00000.dat")
    bandedges_data_file = nn.DataFile(bandedges_file_path, product=software)
    states_data_file = nn.DataFile(states_file_path, product=software)
    fig, ax = plt.subplots()
    plot_bandedges(ax, bandedges_data_file)
    plot_states(ax, states_data_file)
    fig.savefig(os.path.join(output_folder, f"bandedges_states_bias_{bias}{FigFormat1}"))

# plot absorption spectrum
fig, ax = plt.subplots()
for bias, el_field in zip(bias_list, el_field_list):
    bias_folder_name = f"bias_0000{bias}"
    absorption_file_path = datafolder.go_to(bias_folder_name, "OpticsQuantum", "quantum_region", "absorption_coeff_spectrum_TE_nm.dat")
    data_file = nn.DataFile(absorption_file_path, product=software)
    wavelength = data_file.coords[0].value
    absorption_coeff = data_file.variables[0].value
    ax.plot(wavelength, absorption_coeff, label=f"{el_field} kV/cm")


# plot vertical lin at 1310 nm
ax.axvline(x=1310, color='grey', linestyle='--')
ax.set_xlabel('Wavelength (nm)')
ax.set_ylabel('Absorption Coefficient (1/cm)')
ax.legend()
ax.set_xlim(1250, 1360) # zoom to first peak for better visibility
fig.savefig(os.path.join(output_folder, f"bandedges_states_bias_{bias}{FigFormat1}"))

plt.show()

