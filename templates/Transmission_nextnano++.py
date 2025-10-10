import nextnanopy as nn
import sys,os
#import numpy as np
import matplotlib.pyplot as plt

this_dir = os.path.dirname(__file__)

# Specify input file folder  (please adjust path if necessary)
# nextnano++ examples
input_folder = r'C:\Program Files\nextnano\2025_09_18\nextnano++\examples\transmission'

# specify input file name
filename = r'transmission-double-barrier_Birner_JCEL_2009_1D_nnp.nnp'

# load input file
input_path = os.path.join(input_folder, filename)
input_file = nn.InputFile(input_path)

# specify variable and its values
variable = 'Barrier_Width'
value = 4.0

print("Starting nextnano...")
input_path = os.path.join(input_folder, filename)
input_file = nn.InputFile(input_path)

# modify and save the input file in the working directory
input_file.set_variable(variable, value=value, comment='<= PYTHON <= modified variable')
input_file_modified_location = os.path.join(this_dir, filename)
input_file.save(temp=True)
print("Executing nextnano++ ...")
input_file.execute(show_log=False) # change to True if you want to see the log in the console
# get path to output folder
output_folder = input_file.folder_output

print("Plotting the data...")
# get the path of the file. You can use os.path.join instead as well
data_folder = nn.DataFolder(output_folder)
transmission_file = data_folder.go_to("bias_00000", "CBR", "cbr", "Gamma", "transmission.dat")
data_file = nn.DataFile(transmission_file, product="nextnano++")

# data_file.plot(y_axis_name = 'Transmission') # simple way to plot all data in one line
plt.plot(data_file.coords[0].value, data_file.variables[1].value, label=f"{variable}={value}")
plt.xlabel(f"{data_file.coords[0].name} ({data_file.coords[0].unit})", size=14)
plt.ylabel(f"{data_file.variables[1].name} ({data_file.variables[1].unit})", size=14)
plt.title('Transmission', size=16)
plt.legend()
plt.grid(alpha=0.3)


# plot the ldos
file_ldos = data_folder.go_to("bias_00000", "CBR", "cbr", "Gamma", "ldos_total.fld")
file_cb = data_folder.go_to("bias_00000", "bandedge_Gamma.dat")
datafile_cb = nn.DataFile(file_cb, product="nextnano++")
datafile_ldos = nn.DataFile(file_ldos, product="nextnano++")

x=datafile_ldos.coords['x']
y=datafile_ldos.coords['y']
z=datafile_ldos.variables[0]

fig, ax = plt.subplots(1)
pcolor = ax.pcolormesh(x.value, y.value, z.value.T)
cbar = fig.colorbar(pcolor)
cbar.set_label(f"{z.name} ({z.unit})")
ax.plot(datafile_cb.coords[0].value,datafile_cb.variables[0].value, label="cb",
        color='white', linestyle='-')

ax.set_xlim(x.value.min(), x.value.max())
ax.set_xlabel(f"{x.name} ({x.unit})")
ax.set_ylabel(f"{y.name} ({y.unit})")
ax.set_title('Local density of states')
fig.tight_layout()
plt.show()

