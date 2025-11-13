# -*- coding: utf-8 -*-
"""
Python script to obtain Figure 13.c in 

    Edlbauer et al. EPJ Quantum Technology (2022) 9:21
    https://doi.org/10.1140/epjqt/s40507-022-00139-w
    
The following nextnano++ sample input files are used:
    
    EPJQT2022_2D_TCW_nnp
    EPJQT2022_1D_slice_TCW_nnp
"""

import nextnanopy as nn
from nextnanopy.utils.misc import mkdir_if_not_exist
import os
import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.constants import m_e, hbar

device_length = 600e9 #  x nm = x e9 meters

effective_mass = 0.067 # GaAs

E_meV  = 9.2e-3 # fixed electron energy

#Conversion from eV to Joule
E = E_meV * 1.6e-19

software = 'nextnano++' # Specify software product here!
software_short = '_nnp'

folder_input = r"C:\Program Files\nextnano\2025_09_18\nextnano++\examples\transmission"

my_input_file = 'EPJQT2022_2D_TCW_nnp.nnp'

print("starting nextnano...")
input_file_path = os.path.join(folder_input, my_input_file)
input_file = nn.InputFile(input_file_path)
input_file.save(temp=True)
temp_path = input_file.fullpath

sweep_variable = 'tunnel_barrier_height'

sweep_values = [i*i for i in np.linspace(0.00, 1.00, 41)]

sweep = nn.Sweep({sweep_variable: sweep_values}, fullpath=temp_path)
print("Performing sweep for 2D simulation...")
sweep.save_sweep(integer_only_in_name=True)
sweep.execute_sweep(show_log=False, delete_input_files=True, parallel_limit=3)

transmission_13_at_fixed_energy=[]
transmission_14_at_fixed_energy=[]

sweep_infodict = sweep.sweep_output_infodict

barrier_values = []
for folder_path, var_dict in sweep_infodict.items():
    var_value = var_dict[sweep_variable]
    dfolder = nn.DataFolder(folder_path)
    file = dfolder.go_to('bias_00000', r"CBR", r"device", r"Gamma",  r"transmission.dat") 
    df = nn.DataFile(file, product=software)
    transmission_13_at_fixed_energy_x = df.variables['lead_1->lead_3'].value[int((E_meV - input_file.variables['E_min'].value)/input_file.variables['energy_resolution'].value) + 1]
    transmission_13_at_fixed_energy.append(transmission_13_at_fixed_energy_x)
    transmission_14_at_fixed_energy_x = df.variables['lead_1->lead_4'].value[int((E_meV - input_file.variables['E_min'].value)/input_file.variables['energy_resolution'].value) + 1]
    transmission_14_at_fixed_energy.append(transmission_14_at_fixed_energy_x)
    barrier_values.append(var_value)

# sort plot_values and corresponding transmission values
sorted_indices = np.argsort(barrier_values)
sweep_values = [barrier_values[i] for i in sorted_indices]
transmission_13_at_fixed_energy = [transmission_13_at_fixed_energy[i] for i in sorted_indices]
transmission_14_at_fixed_energy = [transmission_14_at_fixed_energy[i] for i in sorted_indices]



# 1D slice simulation

my_input_file = r'EPJQT2022_1D_slice_TCW_nnp.nnp'

print("Performing sweep for 1D slice simulation...")
input_file_name = os.path.join(folder_input, my_input_file)
input_file = nn.InputFile(input_file_name)
input_file.save(temp=True)
temp_path = input_file.fullpath

    
sweep_variable = 'tunnel_barrier_height'

sweep_values_2 = [i**3 for i in np.linspace(0.18, 1.00, 41)]

sweep = nn.Sweep(variables_to_sweep={sweep_variable: sweep_values_2}, fullpath=temp_path)

sweep.save_sweep(integer_only_in_name=True)
sweep.execute_sweep(show_log=False, delete_input_files=True, parallel_limit=3)

sweep_output_directory = sweep.sweep_output_directory

sweep_dfolder = nn.DataFolder(sweep_output_directory)

E_s = []
E_a = []
value_list = []
delta_k_list = []
scaling_factor = 44
sweep_infodict = sweep.sweep_output_infodict

barrier_values = []
for folder_path, var_dict in sweep_infodict.items():
    var_value = var_dict[sweep_variable]
    dfolder = nn.DataFolder(folder_path)
    file  = dfolder.go_to("bias_00000" , "Quantum", "cbr", "Gamma", "energy_spectrum_k00000.dat") 
    df    = nn.DataFile(file, product=software)

    E_s_x = df.variables['Energy'].value[0] 
    E_a_x = df.variables['Energy'].value[1] 
    
    E_s_j = E_s_x * 1.6e-19
    E_a_j = E_a_x * 1.6e-19
    
    delta_k = math.sqrt((2*effective_mass*m_e*(E-E_s_j))/hbar) - math.sqrt((2*effective_mass*m_e*(E-E_a_j))/hbar)
    delta_k_list.append(delta_k)
    value = math.cos(delta_k*device_length/scaling_factor)**2  # add **2 to square
    value_list.append(value)
    barrier_values.append(var_value)
    
# sort the values
sorted_indices = np.argsort(barrier_values)
sweep_values_2 = [barrier_values[i] for i in sorted_indices]
value_list = [value_list[i] for i in sorted_indices]




fig, ax = plt.subplots(1)

ax.plot(sweep_values, transmission_13_at_fixed_energy, 'c-', label='1->3')
ax.plot(sweep_values, transmission_14_at_fixed_energy, 'g-', label='1->4')

ax.plot(sweep_values_2, value_list, 'c.') 
ax.plot(sweep_values_2, [1-x for x in value_list], 'g.')  

ax.set_xlim(-0.00,1.0)
ax.set_ylim(0.0,1.0)
ax.set_xlabel('Tunneling barrier $V_{\mathrm{T}}$ (eV)', fontsize=14)
ax.set_ylabel('Transmission', fontsize=14)
ax.set_xticks(np.arange(0, 1.1, 0.1))

#fig.savefig('dotsandlines' + '.png', dpi=500, bbox_inches='tight',pad_inches = 0, transparent=True )
plt.show()
print('Done nextnanopy.')  
