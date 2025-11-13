from nextnanopy.outputs import DataFolder, DataFile
from nextnanopy.utils.misc import combinations
from collections.abc import Iterable
import os
import numpy as np
from scipy.optimize import minimize as sp_minimize
from scipy.optimize import fsolve

elementary_charge = 1.60217662e-19

def minimization_function(variables_values, inputfile, variables_names, target_filepath, target_variable, number =0, overwrite = True):
    for varvalue, varname in zip(variables_values, variables_names):
        inputfile.set_variable(name = varname, value = varvalue)
    inputfile.save(overwrite = True)
    inputfile.execute(show_log = False)
    output_folder = inputfile.folder_output
    datafolder = DataFolder(output_folder)
    datafile = DataFile(datafolder.go_to(os.path.join(target_filepath)))
    target = datafile.variables[target_variable].value[number]
    return target

def optimization_function(variables_values, inputfile, variables_names, target_filepath, target_variable, target_value, number =0, overwrite = True):
    for varvalue, varname in zip(variables_values, variables_names):
        inputfile.set_variable(name = varname, value = varvalue)
    inputfile.save(overwrite = True)
    inputfile.execute(show_log = False)
    output_folder = inputfile.folder_output
    datafolder = DataFolder(output_folder)
    datafile = DataFile(datafolder.go_to(os.path.join(target_filepath)), product = 'nextnano++')
    target = datafile.variables[target_variable].value[number]
    target = abs(target_value - target)
    return target

def minimize(input_file, variables_names, x0, target_filepath, target_variable,  number = 0, overwrite = True):
    if isinstance(variables_names, Iterable):
        if len(variables_names) != len(x0):
            raise ValueError('variables and x0 should be of the same length')
    result = sp_minimize(minimization_function, x0, args = (input_file, variables_names, target_filepath, target_variable, number, overwrite), tol = 1e-5)
    return result



def optimize(input_file, variables_names, x0, target_filepath, target_variable, target_value, number = 0, overwrite = True):
    if isinstance(variables_names,Iterable):
        if len(variables_names) != len(x0):
            raise ValueError('variables and x0 should be of the same length')
    result = fsolve(optimization_function, x0, args = (input_file, variables_names, target_filepath, target_variable, target_value, number, overwrite), xtol = 1e-5,factor=1)
    input_file.save(overwrite = True)
    return result





def get_target_value(input_file,target_filepath,target_variable,target_number = 0, product = 'nextnano++'):
    dfolder_output = DataFolder(input_file.folder_output)
    dfile_output = dfolder_output.go_to(target_filepath)
    dfile = DataFile(dfile_output, product = product)
    if target_number == 'all':
        val = dfile.variables[target_variable].value
    else:
        val = dfile.variables[target_variable].value[target_number]
    return val


def simple_optimize(input_file, sweep_dict, target_filepath, target_variable, target_number, goal = 'min', optimal_target_value = None, post_func = lambda x: x):
    """
    The function that run sweeps of input file over the given variables space
    and finds optimum value of target value (target value is part of the result of simulation)
    Parameters
    ----------
    input_file: str, input_file to execute
    sweep_dict: dict with keys: variabels names
                          values: list of variables values
    target_filepath: filepath to target value in output directory
    target_variable: target variable name
    target_number: the index number of the target value. If target_number = "all", the target is then list of values
    goal: str
            options: 'min' to minimize the target
                      'max' to maximize the target
                       'optimal' find the closest to optimal_target_value
    optimal_target_value
    post_func: if specifide post_func(target) will be optimize instead of target

    Returns
    -------

    """
    best_value_initial_dict = {'min': np.inf, 'max': -np.inf, 'optimal':0}
    var_names = sweep_dict.keys()
    var_values = sweep_dict.values()
    all_combinations = combinations(*var_values)
    optimal_combination = None
    best_value = best_value_initial_dict[goal]
    best_diff = np.inf
    for combination in all_combinations:
        for var_name,var_val in zip(var_names,combination):
            input_file.set_variable(var_name,var_val)
        input_file.save(overwrite = True)
        input_file.execute(show_log = False)
        target_val = post_func(get_target_value(input_file,target_filepath,target_variable,target_number))
        if goal == 'min':
            if target_val<best_value:
                best_value = target_val
                optimal_combination = combination
        elif goal == 'max':
            if target_val>best_value:
                best_value = target_val
                optimal_combination = combination
        elif goal == 'optimal':
            diff = np.abs(target_val - optimal_target_value)
            if diff < best_diff:
                best_value = target_val
                optimal_combination = combination
                best_diff = diff
        else:
            raise NotImplementedError
    return optimal_combination, best_value

def calculate_CV(output_directory_path, bias1 = None, bias2 = None, total = False, net_charge_sign = -1):
    """
    Calculates CV charateristic based on integrated_density_electron.dat and integrated_density_hole.dat files in ouput_directory
    Parameters
    ----------
    output_directory_path: str
    bias1:  str, name of the first reference bias, optional
    bias2: str, name of the second reference bias, optional
    total: calculate in all regions together (sum of all regions) (for now only False is valid, otherwise return NotImplementedError)

    Returns
    -------
    capacitance: numpy array with capacitance
    voltage: numpy array with voltages
    """

    dfolder = DataFolder(output_directory_path)

    dfile_hole  = DataFile(dfolder.find('integrated_density_hole.dat', deep=True)[0], FirstVarIsCoordFlag=False, product = 'nextnano++')
    dfile_electron = DataFile(dfolder.find('integrated_density_electron.dat', deep=True)[0], FirstVarIsCoordFlag=False, product = 'nextnano++')

    bias_hole_set = set([var.name for var in dfile_hole.variables if var.name.endswith('_bias')])
    bias_electron_set = set([var.name for var in dfile_electron.variables if var.name.endswith('_bias')])
    common_biases_list = list(bias_hole_set.intersection(bias_electron_set))

    """
    Here parameter voltage is found.
    if both bias1 and bias2 are present in holes and electrones file, voltage = bias2-bias1
    
    bias 2 is ignored if bias1 is None
    
    if bias1 is present in common_biases_list, voltage = bias1
    
    if bias1 = bias2 = None, voltage = first common bias
    """
    if not common_biases_list:
        raise ValueError('There is no common biases in integrated_density_hole.dat file and integrated_density_electron.dat file')

    if bias1:
        if bias1 not in common_biases_list:
            raise ValueError('Specified reference bias1 is not commmon bias for holes and electrons')

        if bias2:
            if bias2 not in common_biases_list:
                raise ValueError('Specified reference bias2 is not commmon bias for holes and electrons')
            else:
                voltage = dfile_hole.variables[bias2].value - dfile_hole.variables[bias1].value
        else:
            voltage = dfile_hole.variables[bias1].value

    else:
        bias = common_biases_list[0]
        voltage = dfile_hole.variables[bias].value

    regions_hole_set = set([var.name for var in dfile_hole.variables if not var.name.endswith('_bias')])
    regions_electron_set = set([var.name for var in dfile_electron.variables if not var.name.endswith('_bias')])



    common_regions_list = list(regions_hole_set.intersection(regions_electron_set))

    if not common_regions_list:
        return TypeError('integrated_density does not have common regions for holes and electrons')

    #voltage = voltage[:-1]

    num_bias_points = len(voltage)

    regions = []

    for region in common_regions_list:
        integrated_density_hole = dfile_hole[region].value
        integrated_density_electron = dfile_electron[region].value
        total_charge = net_charge_sign * elementary_charge * 1e6 * (integrated_density_hole-integrated_density_electron)
        c_list = []
        regions.append(c_list)

        for i in range(len(voltage)-1):
            voltage_val = voltage[i]
            voltage_val_next = voltage[i+1]
            charge_val = total_charge[i]
            charge_val_next = total_charge[i+1]

            if abs(voltage_val_next - voltage_val) < 1e-15:
                c_list.append(0)
            else:
                c_val = (charge_val_next-charge_val)/(voltage_val_next-voltage_val)
                c_list.append(c_val)

    voltage = voltage[:-1]

    return voltage, regions







