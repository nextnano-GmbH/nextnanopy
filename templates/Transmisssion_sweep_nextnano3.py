import nextnanopy as nn
import os
import matplotlib.pyplot as plt

# set to False to only have one plot with all transmissions
plot_individual_transmissions = True

this_dir = os.path.dirname(__file__)
# Specify output image format
FigFormat = '.jpg' # other options: .pdf, .svg, .png

# Specify input file folder  (please adjust path if necessary)
# nextnano++ examples
input_folder = r'C:\Program Files\nextnano\2025_08_21\nextnano3\examples\education\lecture_on_quantum_mechanics'

# specify input file name
filename = r'Transmission_Double_Barrier_1D_nn3.nn3'

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

print("Plotting local density of states...")

for path, combination in sweep.sweep_output_infodict.items():
    val = combination[sweep_variable]
    data_folder = nn.DataFolder(path)
    file_ldos = data_folder.go_to("Results", "LocalDOS_sg1_deg1.fld")
    file_cb = data_folder.go_to("Results", "cb_Gamma.dat")
    datafile_cb = nn.DataFile(file_cb, product="nextnano3")
    datafile_ldos = nn.DataFile(file_ldos, product="nextnano3")

    x=datafile_ldos.coords['x']
    y=datafile_ldos.coords['y']
    z=datafile_ldos.variables[0]

    fig, ax = plt.subplots(1)
    pcolor = ax.pcolormesh(x.value, y.value, z.value.T)
    cbar = fig.colorbar(pcolor)
    cbar.set_label(f"{z.name} ({z.unit})")
    ax.plot(datafile_cb.coords[0].value,datafile_cb.variables[0].value, label="cb",
            color='white', linestyle='-')

    ax.set_xlabel(f"{x.name} ({x.unit})")
    ax.set_ylabel(f"{y.name} ({y.unit})")
    ax.set_title(f'Local density of states {sweep_variable}={val}')
    fig.tight_layout()
    fig.savefig(os.path.join(path, f'LDOS_{sweep_variable}_{val}{FigFormat}'))

print("Plotting transmission...")

fig, ax = plt.subplots(1)

for path, combination in sweep.sweep_output_infodict.items():
    val = combination[sweep_variable]
    data_folder = nn.DataFolder(path)
    transmission_file = data_folder.go_to("Results", "Transmission_cb_sg1_deg1.dat")
    df = nn.DataFile(transmission_file, product="nextnano3")
    ax.plot(df.coords[0].value, df.variables[0].value, label=f"{sweep_variable}={val}")
    if plot_individual_transmissions:
        fig2, ax2 = plt.subplots(1)
        ax2.plot(df.coords[0].value, df.variables[0].value, label=f"{sweep_variable}={val}")
        ax2.set_xlabel(f"{df.coords[0].name} ({df.coords[0].unit})", size=14)
        ax2.set_ylabel(f"{df.variables[0].name} ({df.variables[0].unit})", size=14)
        ax2.set_title(f'Transmission {sweep_variable}={val}', size=16)
        fig2.savefig(os.path.join(path, f'Transmission_{sweep_variable}_{val}{FigFormat}'))

# Bring the first figure window to the front
plt.figure(fig.number)
ax.set_xlabel(f"{df.coords[0].name} ({df.coords[0].unit})", size=14)
ax.set_ylabel(f"{df.variables[0].name} ({df.variables[0].unit})", size=14)
ax.set_title('Transmission', size=16)
ax.legend()
# optional figure formatting
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(sweep.sweep_output_directory, f'Transmission_{sweep_variable}{FigFormat}'))



plt.show()

print('Done.')