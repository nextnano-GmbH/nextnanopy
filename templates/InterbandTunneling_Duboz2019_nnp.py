"""
Created: 2022/06/09
Updated: 2023/04/27

This Python script computes interband tunneling current through a highly-doped nitride heterojunction.
[nextnano++ tutorial]
https://www.nextnano.de/manual/nn_products/nextnanoplus/tutorials/tricks_and_hacks/1D_interband_tunneling_in_nitride_junction.html

The usage of this script is explained in
'InterbandTunneling_Duboz2019_doc.ipynb'.

For the equations and approximations, please refer to the the documentation
'InterbandTunneling_Duboz2019_formulation.pdf'.

This scripts uses the shortcut methods in Chikuwaq/nextnanopy-wrapper:
https://github.com/Chikuwaq/nextnanopy-wrapper

@author: takuma.sato@nextnano.com
"""

# Python libraries
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simpson as simps
from pathlib import Path

# nextnanopy
import nextnanopy as nn
from nextnanopy.utils.plotting import use_nxt_style
from nextnanopy.utils.misc import mkdir_if_not_exist

use_nxt_style()
# shortcuts
# from nnShortcuts.common import CommonShortcuts
# s = CommonShortcuts()
# from nnHelpers import SweepHelper
from pathlib import Path
# stopwatch
import timeit
start = timeit.default_timer()

# physics constants
eV_in_J = 1.602176634e-19 # [J]
electron_mass_in_kg = 9.1093837015e-31 # [kg]
Angstrom_in_nm = 0.1 # [nm]
elementary_charge_in_C = 1.602176634e-19 # [C]
hbar = 1.054571817E-34   # Planck constant / 2Pi in [J.s]
scale1ToCenti = 1e2 

# grid conversion utility function
def convert_grid(data_y, x, x_new):
    x = np.asarray(x)
    data_y = np.asarray(data_y)
    x_new = np.asarray(x_new)

    return np.interp(x_new, x, data_y)

# ===== user definition begin ===================================

#================================================================
# Specify your input file WITH EXTENSION
#================================================================
# TODO
# folder_path = r'c:\Program Files\nextnano\2025_12_20\nextnano++\examples\tricks_and_hacks'
folder_path = r"c:\Users\Heorhii\source\Workspaces\nextnanoplus\nextnano\examples\tricks_and_hacks"
# input file
filename = 'InterbandTunneling_Duboz2019_nnp.nnp'


#================================================================
# Modify the input parameters & simulation settings
#================================================================
num_ev_CB = 30              # number of conduction band eigenvalues (without spin)
num_of_valence_bands = 6    # how many valence bands to be considered in the transition matrix. (min: 1, max: 6)

layer_thickness = 20   # thickness of p- and n-region [nm]

# bias sweep
sweep_variable = 'BIAS'
sweep_values = np.linspace(-0.2, -1.0, 9) # min, max, number of points
# sweep_ranges =  {
#     sweep_variable: ([-0.2, -1.0], 9)  # ([min, max], number of points)
# }

# choose either 6-band k.p or single-band simulation for the valence band. You can also set both to False when you do not want to run simulation (only postprocessing with KP6 output data).
RUN_KP6 = True   # run 6-band k.p simulation
# RUN_KP6 = False
# RUN_SINGLE_BAND = True   # run single-band (HH, LH, SO) simulation
RUN_SINGLE_BAND = False


# RemoveInputFile = True   # remove the temporary input file(s) after bias sweep
# RemoveInputFile = False   # keep the temporary input file(s) in the input folder

CALCULATE_EFFECTIVE_FIELD_FROM_OUTPUT = True   # calculate effective field from nextnano output
# CALCULATE_EFFECTIVE_FIELD_FROM_OUTPUT = False   # specify effective field by hand
# user_defined_effective_field = 1.0   # [V/nm] test

KaneParameter_fromOutput = True   # use nextnano database value for k.p Kane parameter
# KaneParameter_fromOutput = False   # specify Kane parameter by hand
# user_defined_Kane_EP1 = 15   # E_P1 [eV] Duboz2019

# CALCULATE_REDUCED_MASS_FROM_OUTPUT = True   # calculate reduced mass from nextnano output
CALCULATE_REDUCED_MASS_FROM_OUTPUT = False   # specify reduced mass by hand

user_defined_mass_r = 0.18 * electron_mass_in_kg                # m_r [kg] Duboz2019

# highest valence band. Necesarry info for bandgap calculation, but does not make much difference in dipole matrix element
highestVB = 'LH'

#================================================================
# Select output figure format
#================================================================
# fig_format = '.pdf'
# fig_format = '.svg'
# fig_format = '.jpg'
fig_format = '.png'


# ===== user definition END =====================================

#%% nextnanopy pre-processing
do_not_run_simulation = False

# decide simulation type
if RUN_KP6 and RUN_SINGLE_BAND:
    raise RuntimeError('nextnano can only run either multiband or single-band simulation for valence band. Do not set RUN_KP6 = RUN_SINGLE_BAND = True.')
if not RUN_KP6 and not RUN_SINGLE_BAND:
    print('KP6 and single-band simulations skipped.')
    do_not_run_simulation = True
    simulation_type = 'kp6'
if RUN_KP6 and not RUN_SINGLE_BAND:
    simulation_type = 'kp6'
if not RUN_KP6 and RUN_SINGLE_BAND:
    simulation_type = 'SingleBand'


# number of valence band eigenvalues
if RUN_KP6 or do_not_run_simulation:
    num_ev_VB = num_of_valence_bands * num_ev_CB
elif RUN_SINGLE_BAND:
    num_ev_VB = num_ev_CB

# To import Kane parameter from the nextnano database, you have to run (fast) 8-band k.p simulation.
RunKP8 = KaneParameter_fromOutput


# load the input file
InputPath  = os.path.join(folder_path, filename)
input_file = nn.InputFile(InputPath)

# automatically detect the software
software, FileExtension = "nextnano++", ".nnp"
filename_no_extension = Path(filename).stem

# Define output folders based on .nextnanopy-config file. If they do not exist, they are created.
# NOT NEEDED
# TODO: delete
# folder_output = nn.config.get(software, 'outputdirectory')
# folder_output_python = os.path.join(folder_output, os.path.join(r'nextnanopy', filename_no_extension))
# mkdir_if_not_exist(folder_output_python)


# modify the parameters in the input file
input_file.set_variable('num_ev_CB', value=num_ev_CB)
input_file.set_variable('num_ev_VB', value=num_ev_VB)
input_file.set_variable('Thickness', value=layer_thickness)


print('Modified input parameter: ', input_file.get_variable('num_ev_CB').text)
print('Modified input parameter: ', input_file.get_variable('num_ev_VB').text)
print('Modified input parameter: ', input_file.get_variable('Thickness').text)
print('')




#%% Run nextnano simulations

# To obtain kp parameters, (fast) 8-band k.p simulation must be performed.
if RunKP8:
    print('\n------------------------------------------')
    print(f'Running {software} 8-band k.p simulation to obtain material parameters...')
    print('------------------------------------------\n')

    # adjust simulation settings in the input file
    input_file.set_variable('RunKP8',      value=1)
    input_file.set_variable('Single_band', value=0)
    input_file.set_variable('Multi_band',  value=0)

    # put bias to zero
    input_file.set_variable('BIAS', value=0.0)

    # filename_kp8 = filename.replace(FileExtension, '_kp8' + FileExtension)
    # InputPath_kp8 = os.path.join(folder_path, filename_kp8)
    input_file.save(temp=True)
    print("Executing 8-band k.p simulation...")
    input_file.execute(convergenceCheck=True, show_log=False)
    output_folder_kp8 = input_file.folder_output
    data_folder_kp8 = nn.DataFolder(output_folder_kp8)
else:
    print('KP8 calculation skipped.')


# adjust simulation settings in the input file for 6-band or single-band simulation
input_file.set_variable('RunKP8',      value=0,                 ) # do not perform 8-band k.p in the following
input_file.set_variable('Single_band', value=int(RUN_SINGLE_BAND))
input_file.set_variable('Multi_band',  value=int(RUN_KP6),      )


input_file.save(temp=True)

# instantiate nextnanopy-wrapper.SweepHelper to facilitate simulation execution and postprocessing
# helper = SweepHelper(sweep_ranges, input_file)
sweep = nn.Sweep({sweep_variable: sweep_values}, fullpath=input_file.fullpath)

if RUN_KP6 or RUN_SINGLE_BAND:
    print('\n------------------------------------------')
    print(f'Running {software} {simulation_type} simulation')
    print('------------------------------------------\n')
    # TODO !!!
    # sweep.save_sweep(integer_only_in_name=True, temp=True)
    # sweep.execute_sweep(parallel_limit=4, delete_input_files=True, show_log=False) # overwrite=True to avoid enumeration of output folders for secure output data access
    sweep_output_directory = sweep.sweep_output_directory
    # sweep_output_infodict = sweep.sweep_output_infodict
    import json 
    sweep_output_directory = r"c:\Users\Heorhii\Documents\nextnano\OutputNnpy\InterbandTunneling_Duboz2019_nnp_1_sweep__BIAS0"
    sweep_output_infodict = json.load(open(Path(sweep_output_directory) / 'sweep_infodict.json', 'r'))


#%% Postprocessing (calculate tunnel current)

# data containers for the I-V curve
voltages = list()
currents = list()

# Read out simulation results and calculate tunnel current for each bias
for sweep_subfolder, combination in sweep_output_infodict.items():

    var_value = combination[sweep_variable]

    print('\n------------------------------------------')
    print(f"nextnanopy postprocessing for {sweep_variable}={var_value}")
    print('------------------------------------------\n')

    data_folder = nn.DataFolder(sweep_subfolder)
    # extract values from simulation - electrostatic potential gradient
    df_potential = nn.DataFile(data_folder.go_to("bias_00000", 'potential.dat'), product=software)
    x = df_potential.coords['x'].value      # this is the simulation grid

    if CALCULATE_EFFECTIVE_FIELD_FROM_OUTPUT:

        Potential = df_potential.variables['Potential'].value
        PotentialGrad = np.gradient(Potential, x)   # derivative

        fig, ax1 = plt.subplots()
        color = 'tab:red'
        ax1.plot(x, Potential, color=color)
        ax1.set_xlabel(f'{df_potential.coords["x"].label}')
        ax1.set_ylabel(f'{df_potential.variables["Potential"].label}', color=color)
        # ax1.set_title('Electrostatic potential and its gradient')
        ax1.tick_params(axis='y', labelcolor=color)

        ax2 = ax1.twinx()   # instantiate a second axes that shares the same x-axis
        color = 'tab:blue'
        ax2.set_ylabel('Gradient (V/nm)', color=color)
        ax2.plot(x, PotentialGrad, color=color, label=f'{sweep_variable}={var_value:.2f}')
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.legend()
        fig.tight_layout()
        # plt.show()
        print('PLOT: electrostatic potential and its gradient')

    elif not user_defined_effective_field:
        raise RuntimeError('Please specify effective field [V/nm] or set CALCULATE_EFFECTIVE_FIELD_FROM_OUTPUT = True.')
    else:
        PotentialGrad = np.array([user_defined_effective_field] * len(x))   # user-defined effective field
        print('Using user-defined effective field...')


    # extract values from simulation - conduction band envelope functions
    print('Reading in the envelope functions...')
    print('No. of conduction band eigenvalues (without spin degeneracy) = ', num_ev_CB)
    print('No. of valence band eigenvalues (considering different spin states) = ', num_ev_VB)

    amplitude_Gamma_path = data_folder.go_to("bias_00000", "Quantum", "QuantumRegion", 'Gamma', "amplitudes_k00000.dat")
    df_amplitude_Gamma = nn.DataFile(amplitude_Gamma_path, product=software)
    # x = df_amplitudeGamma.coords['x'].value  # numpy.array
    amplitude_Gamma = np.zeros((num_ev_CB, len(x)), dtype = np.float64)    # (CB eigenvalue index, position x). For effective mass model the amplitude is a real function.
    for i in range(num_ev_CB):
        amplitude_Gamma[i,] = df_amplitude_Gamma.variables[f'Psi_{i+1}'].value   # envelope amplitude

    # extract values from simulation - valence band complex envelope functions
    if RUN_KP6 or do_not_run_simulation:
        amplitude_VB_path = data_folder.go_to("bias_00000", "Quantum", "QuantumRegion", 'kp6', "amplitudes_k00000_SXYZ.dat")
        df_amplitude_VB = nn.DataFile(amplitude_VB_path, product=software)
        amplitude_VB_x1 = np.zeros((num_ev_VB, len(x)), dtype = np.complex128)          # (VB eigenvalue index, position x). For k.p model the amplitude is a complex function.
        amplitude_VB_x2 = np.zeros((num_ev_VB, len(x)), dtype = np.complex128)          # In nn++, x, y, and z components refers to the simulation coordinates and not the crystal coordinates. Growth direction = x.
        for j in range(num_ev_VB):
            for pos in range(len(x)):
                amplitude_VB_x1[j, pos] = complex(df_amplitude_VB.variables[f'Psi_{j+1}_x1_real'].value[pos], df_amplitude_VB.variables[f'Psi_{j+1}_x1_imag'].value[pos])   # envelope amplitude
                amplitude_VB_x2[j, pos] = complex(df_amplitude_VB.variables[f'Psi_{j+1}_x2_real'].value[pos], df_amplitude_VB.variables[f'Psi_{j+1}_x2_imag'].value[pos])
    elif RUN_SINGLE_BAND:
        amplitude_VB_path = data_folder.go_to("bias_00000", "Quantum", "QuantumRegion", 'SO', "amplitudes_k00000.dat")
        df_amplitude_VB = nn.DataFile(amplitude_VB_path, product=software)
        amplitude_VB_SO = np.zeros((num_ev_VB, len(x)), dtype = np.float64)
        for j in range(num_ev_VB):
            for pos in range(len(x)):
                amplitude_VB_SO[j,] = df_amplitude_VB.variables[f'Psi_{j+1}'].value   # envelope amplitude




    # extract values from simulation - bandgap
    print('Extracting bandgap...')
    bandgap_path = data_folder.go_to("bias_00000", 'bandgap.dat')
    df_bandgap = nn.DataFile(bandgap_path, product=software)
    bandgap_gamma = eV_in_J * df_bandgap.variables['Bandgap_Gamma'].value # in J



    # extract values from simulation - crystal-field and spin-orbit splitting
    print('Reading in the position-dependent material parameters...')
    splitting_path = data_folder_kp8.go_to("Structure", "spin_orbit_coupling_energies.dat")
    df_splitting = nn.DataFile(splitting_path, product=software)
    Crystal_splitting = eV_in_J * df_splitting.variables['Delta_1'].value     # Delta_1 = Delta_crystal
    SpinOrbit_splitting = eV_in_J * df_splitting.variables['Delta_2'].value   # Delta_2 = Delta_parallel


    # convert from material grid to simulation grid
    x_material_grid = df_splitting.coords['x'].value   # material grid
    Crystal_splitting_on_sim_grid   = convert_grid(Crystal_splitting, x_material_grid, x)
    SpinOrbit_splitting_on_sim_grid = convert_grid(SpinOrbit_splitting, x_material_grid, x)

    # obtain Kane parameter P_1
    if KaneParameter_fromOutput:
        # extract values from simulation - Kane parameter
        kpParam_path = data_folder_kp8.go_to("Structure", "kp_parameters_kp8.dat")
        df_kpParam = nn.DataFile(kpParam_path, product=software)
        Kane_P1 = eV_in_J * Angstrom_in_nm * df_kpParam.variables['P1'].value   # P_1 = along the c crystal axis. Units translated to [J nm]
        Kane_P1_on_sim_grid = convert_grid(Kane_P1, x_material_grid, x)   # convert from material to simulation grid
    elif not user_defined_Kane_EP1:
        raise RuntimeError('Please specify Kane energy parameter [eV] or set KaneParameter_fromOutput = True.')
    else:
        # TODO ??
        P1 = s.scale1ToNano * np.sqrt(hbar**2 * (eV_in_J * user_defined_Kane_EP1) / 2 / s.electron_mass)   # user-defined Kane parameter. Units translated to [J nm]
        Kane_P1_on_sim_grid = np.array([P1] * len(x))


    # bandedge shift due to crystal splitting and spin-orbit coupling
    SpinOrbit_splitting_perp_on_sim_grid = SpinOrbit_splitting_on_sim_grid   # nextnano database assumes delta_perp = delta_para
    bandshift_HH = Crystal_splitting_on_sim_grid + SpinOrbit_splitting_on_sim_grid
    p = (Crystal_splitting_on_sim_grid - SpinOrbit_splitting_on_sim_grid) / 2.
    bandshift_LH = p + np.sqrt(p**2 + 2*SpinOrbit_splitting_perp_on_sim_grid**2)


    # calculate dipole_moment = <Z|z|S> = P1/Eg
    if highestVB == 'HH':
        Eg = bandgap_gamma + bandshift_HH
    elif highestVB == 'LH':
        Eg = bandgap_gamma + bandshift_LH
    else:
        raise RuntimeError('Please specify the highest valence band (HH or LH).')

    dipole_moment = Kane_P1_on_sim_grid / Eg


    # for single band, coefficient beta' is needed
    beta_squared = bandshift_LH**2 / (bandshift_LH**2 + 2*SpinOrbit_splitting_on_sim_grid**2)


    # remove the grid points within contacts, and
    # cut off the edges by one more grid to exclude the effect of contact on dipole moment.
    # (Contacts should be excluded from the integration because the bandgap is zero.)
    indices_in_contacts = [ i for i in range(len(x)) if bandgap_gamma[i] == 0 ]

    dipole_moment_cut = np.delete(dipole_moment, indices_in_contacts)
    PotentialGrad_cut = np.delete(PotentialGrad, indices_in_contacts)
    x_cut             = np.delete(x, indices_in_contacts)
    beta_squared_cut  = np.delete(beta_squared, indices_in_contacts)   # for single band
    print(f'Integration performed from x = {x_cut[0]} to {x_cut[-1]}')

    amplitude_Gamma_cut = np.zeros((num_ev_CB, len(x_cut)), dtype=np.float64)
    for i in range(num_ev_CB):
            amplitude_Gamma_cut[i,] = np.delete(amplitude_Gamma[i,], indices_in_contacts)

    if RUN_KP6 or do_not_run_simulation:
        amplitude_VB_x1_cut = np.zeros((num_ev_VB, len(x_cut)), dtype=np.complex128)
        amplitude_VB_x2_cut = np.zeros((num_ev_VB, len(x_cut)), dtype=np.complex128)
        for j in range(num_ev_VB):
            amplitude_VB_x1_cut[j,] = np.delete(amplitude_VB_x1[j,], indices_in_contacts)
            amplitude_VB_x2_cut[j,] = np.delete(amplitude_VB_x2[j,], indices_in_contacts)
    elif RUN_SINGLE_BAND:
        amplitude_VB_SO_cut = np.zeros((num_ev_VB, len(x_cut)), dtype=np.complex128)
        for j in range(num_ev_VB):
            amplitude_VB_SO_cut[j,] = np.delete(amplitude_VB_SO[j,], indices_in_contacts)



    if RUN_KP6 or do_not_run_simulation:
        # calculate the integrand for each spin
        integrand1 = np.zeros((num_ev_CB, num_ev_VB, len(x_cut)), dtype = np.complex128)  # create a (num_ev_CB * num_ev_VB) matrix with position-dependent elements
        integrand2 = np.zeros((num_ev_CB, num_ev_VB, len(x_cut)), dtype = np.complex128)
        for i in range(num_ev_CB):
            for j in range(num_ev_VB):
                integrand1[i, j, ] = dipole_moment_cut * np.conjugate(amplitude_VB_x1_cut[j, ]) * amplitude_Gamma_cut[i, ] * elementary_charge_in_C * PotentialGrad_cut
                integrand2[i, j, ] = dipole_moment_cut * np.conjugate(amplitude_VB_x2_cut[j, ]) * amplitude_Gamma_cut[i, ] * elementary_charge_in_C * PotentialGrad_cut

        # integrate over position
        integral1 = simps(integrand1, x_cut)   # [J/nm] integrated over [nm] gives [J]
        integral2 = simps(integrand2, x_cut)
        print('Transition matrix (row, column): ', np.shape(integral1))

        # read in the spinor composition from nextnano output
        spinor_path = data_folder.go_to("bias_00000", "Quantum", "QuantumRegion", 'kp6', "spinor_composition_k00000_SXYZ.dat")
        df_spinor = nn.DataFile(spinor_path, product=software)
        spinor_x1_squared = df_spinor.variables['x1'].value   # list of spinor x1 components squared for all eigenstates j
        spinor_x2_squared = df_spinor.variables['x2'].value   # list of spinor x2 components squared for all eigenstates j

        # multiply by spinor components & sum over spin
        M_absoluteSquared_spinsum = np.zeros((num_ev_CB, num_ev_VB), dtype = np.float64)
        for i in range(num_ev_CB):
            for j in range(num_ev_VB):
                M_absoluteSquared_spinsum[i,j] = spinor_x1_squared[j] * np.absolute(integral1[i,j]) **2
                M_absoluteSquared_spinsum[i,j] += spinor_x2_squared[j] * np.absolute(integral2[i,j]) **2

    elif RUN_SINGLE_BAND:
        # calculate the integrand
        integrand = np.zeros((num_ev_CB, num_ev_VB, len(x_cut)), dtype = np.complex128)  # create a (num_ev_CB * num_ev_VB) matrix with position-dependent elements
        for i in range(num_ev_CB):
            for j in range(num_ev_VB):
                integrand[i, j, ] = np.sqrt(beta_squared_cut) * dipole_moment_cut * amplitude_VB_SO_cut[j, ] * amplitude_Gamma_cut[i, ] * elemenery_charge_in_C * PotentialGrad_cut

        # integrate over position
        M = simps(integrand, x_cut)   # [J/nm] integrated over [nm] gives [J]


        # sum over spin
        M_absoluteSquared_spinsum = 2 * np.absolute(M) * np.absolute(M)





    # reduced mass
    if CALCULATE_REDUCED_MASS_FROM_OUTPUT:
        # extract values from simulation - mass
        print('Extracting masses and calculating reduced mass...')
        mass_path = data_folder.go_to("Structure", "charge_carrier_masses.dat")
        df_mass = nn.DataFile(mass_path, product=software)

        mass_CB = df_mass.variables['Gamma_mass_t'].value       # effective mass along in-plane direction [unit: m_0]
        mass_VB = df_mass.variables['SO_mass_t'].value          # we take SO effective mass as it contributes dominantly.

        # translate to the simulation grid
        mass_CB_on_sim_grid = convert_grid(mass_CB, x_material_grid, x)
        mass_VB_on_sim_grid = convert_grid(mass_VB, x_material_grid, x)

        # calculate reduced mass m_r
        mass_r = electron_mass_in_kg * mass_CB_on_sim_grid * mass_VB_on_sim_grid / (mass_CB_on_sim_grid + mass_VB_on_sim_grid)
        mass_r_averaged = np.average(mass_r)   # average the reduced mass over the system ???

    elif not user_defined_mass_r:   # if the variable is empty
        raise RuntimeError('Please specify the reduced mass, or set CALCULATE_REDUCED_MASS_FROM_OUTPUT = True.')
    else:
        mass_r_averaged = user_defined_mass_r
        print('Using user-defined reduced mass...')





    # calculate tunnel current for the transition j -> i
    I_ij = scale1ToCenti**(-2) * elementary_charge_in_C * mass_r_averaged * M_absoluteSquared_spinsum / hbar**3   # [A/cm^2]


    # sum over possible transitions (energy levels)
    I = 0.
    num_possible_transitions = 0
    ev_CB_path = data_folder.go_to("bias_00000", "Quantum", "QuantumRegion", 'Gamma', 'energy_spectrum_k00000.dat')
    df_ev_CB     = nn.DataFile(ev_CB_path, product=software)

    if RUN_KP6 or do_not_run_simulation:
        ev_VB_path = data_folder.go_to("bias_00000", "Quantum", "QuantumRegion", 'kp6', 'energy_spectrum_k00000.dat')
        df_ev_VB = nn.DataFile(ev_VB_path, product=software)
    elif RUN_SINGLE_BAND:
        ev_VB_path = data_folder.go_to("bias_00000", "Quantum", "QuantumRegion", 'SO', 'energy_spectrum_k00000.dat')
        df_ev_VB = nn.DataFile(ev_VB_path, product=software)


    for i in range(num_ev_CB):
        eigenvalue_CB = df_ev_CB.variables['Energy'].value[i]

        for j in range(num_ev_VB):
            eigenvalue_VB = df_ev_VB.variables['Energy'].value[j]
            if eigenvalue_VB >= eigenvalue_CB:
                I += I_ij[i][j]
                num_possible_transitions += 1
                print(f'possible transition VB{j+1} --> CB{i+1}')
    print(f'\nNumber of possible transitions at the bias {var_value}: {num_possible_transitions} out of ', num_ev_CB * num_ev_VB)

    voltages.append(-var_value)   # minus sign converts the backward bias to positive values
    currents.append(I)


    # wave function overlap. Not used during simulation, for reference
    sum_overlap_squared = 0.
    for i in range(num_ev_CB):
        eigenvalue_CB = df_ev_CB.variables['Energy'].value[i]
        for j in range(num_ev_VB):
            eigenvalue_VB = df_ev_VB.variables['Energy'].value[j]
            if RUN_KP6 or do_not_run_simulation:
                overlap = simps(np.conjugate(amplitude_VB_x1_cut[j,]) * amplitude_Gamma_cut[i,], x_cut)
            elif RUN_SINGLE_BAND:
                overlap = simps(amplitude_VB_SO_cut[j,] * amplitude_Gamma_cut[i,], x_cut)

            if eigenvalue_VB >= eigenvalue_CB:
                sum_overlap_squared += np.absolute(overlap)**2
    print('\nij-sum of envelope overlap squared (not used during simulation, for reference): ', sum_overlap_squared)


# plot m_r in units of s.electron_mass
if CALCULATE_REDUCED_MASS_FROM_OUTPUT:
    fig, ax = plt.subplots()
    ax.plot(x, mass_r / electron_mass_in_kg)
    ax.set_xlabel(f"{df_potential.coords['x'].label}")
    ax.set_ylabel('(m_0)')
    ax.set_title('Reduced mass')
    print('\nPLOT: reduced mass\n')

# plot material parameters & dipole moment (independent of bias)
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
ax1.plot(x, bandgap_gamma / eV_in_J , label='bandgap c-hh [eV]')
ax1.plot(x, Crystal_splitting_on_sim_grid / eV_in_J, label='crystal splitting [eV]')
ax1.plot(x, SpinOrbit_splitting_on_sim_grid / eV_in_J, label='spin-orbit splitting [eV]')
if KaneParameter_fromOutput:
    ax1.plot(x, Kane_P1_on_sim_grid / eV_in_J, label='Kane parameter P1 [eV nm]')
ax1.set_xlabel(f"{df_potential.coords['x'].label}")
ax1.set_title('Position-dependent material parameters')
ax1.legend(bbox_to_anchor=(1,1), loc='upper left')

ax2.plot(x_cut, dipole_moment_cut)
ax2.set_xlabel(f"{df_potential.coords['x'].label}")
ax2.set_ylabel('(nm)')
ax2.set_title('dipole matrix element <Z|z|S>')
fig.tight_layout()
print('\nPLOT: bandgap, position-dependent material parameters and dipole moment\n')


# tunnel current vs. bias plot
fig, ax = plt.subplots()
plt.yscale('log')
plt.ylim([1e-6, 1e1])
ax.plot(voltages, currents, 'o-')
ax.set_xlabel('bias [V]')
ax.set_ylabel('[A/cm^2]')
ax.set_title('Tunnel current simulated by 6-band k.p model')
fig.savefig(os.path.join(sweep_output_directory,'TunnelCurrent_vs_bias' + fig_format))  # save plot

# tunnel current vs. bias data file
a = os.path.join(sweep_output_directory, f'TunnelCurrent_vs_bias_{simulation_type}.dat')
with open(a, 'w') as f:
    f.write('bias(V)\ttunnel current(A/cm^2)\n')
    for bias, current in zip(voltages, currents):
        f.write(f'{bias}\t{current}')
        f.write('\n')
print(f'\nTotal tunnel current has been plotted and saved in the folder {sweep_output_directory}\n')


stop = timeit.default_timer()
runtime_sec = stop - start
runtime_min = runtime_sec / 60
print('-------------------------------------------------------------')
print('nextnanopy DONE.')
print(f'Run Time ({software} and nextnanopy): {runtime_sec:.3f} [sec]  ({runtime_min:.3f} [min])' )
print('-------------------------------------------------------------')

plt.show()
