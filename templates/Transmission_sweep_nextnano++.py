import nextnanopy as nn
import os
import matplotlib.pyplot as plt

this_dir = os.path.dirname(__file__)
# Specify output image format
FigFormat = '.jpg' # other options: .pdf, .svg, .png

# Specify input file folder  (please adjust path if necessary)
# nextnano++ examples
input_folder = r'C:\Program Files\nextnano\2024_03_28\nextnano++\examples\transmission'

# specify input file name
filename = r'transmission-double-barrier_Birner_JCEL_2009_1D_nnp.in'

# specify variable and its values
sweep_variable = 'Barrier_Width'
sweep_values = [2.0, 4.0, 10.0] 

# plt.ion() # interactive mode
print("starting nextnano...")
input_path = os.path.join(input_folder, filename)
# save a copy in this folder. Only necessary if input file is in program files folder to avoid permission denyed errors
input_file = nn.InputFile(input_path)
input_file.save(os.path.join(this_dir, filename), overwrite=True)
input_path = input_file.fullpath

# create a sweep to execute
sweep = nn.Sweep(variables_to_sweep={sweep_variable: sweep_values}, fullpath=input_path)
sweep.save_sweep(integer_only_in_name=True)
# execute the sweep
sweep.execute_sweep(delete_input_files=True, parallel_limit=3, show_log=False) # parallel limit is number of parallel executions, best is number of CPU cores - 1 
# plot the results 
print("Plotting the data...")
fig, ax = plt.subplots(1)

for path, combination in sweep.sweep_output_infodict.items():
    val = combination[sweep_variable]
    data_folder = nn.DataFolder(path)
    transmission_file = data_folder.go_to("bias_00000", "CBR", "transmission_cbr_Gamma.dat")
    df = nn.DataFile(transmission_file, product="nextnano++")
    ax.plot(df.coords[0].value, df.variables[1].value, label=f"{sweep_variable}={val}")


ax.set_xlabel(f"{df.coords[0].name} ({df.coords[0].unit})", size=14)
ax.set_ylabel(f"{df.variables[1].name} ({df.variables[1].unit})", size=14)
ax.set_title('Transmission', size=16)
ax.legend()
# optional figure formatting
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(sweep.sweep_output_directory, f'Transmission_{sweep_variable}{FigFormat}'))
plt.show()

print('Done.')