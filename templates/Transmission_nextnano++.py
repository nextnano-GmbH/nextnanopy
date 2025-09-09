import nextnanopy as nn
import sys,os
#import numpy as np
import matplotlib.pyplot as plt

this_dir = os.path.dirname(__file__)

# Specify input file folder  (please adjust path if necessary)
# nextnano++ examples
input_folder = r'C:\Program Files\nextnano\2025_08_21\nextnano++\examples\transmission'

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
input_file.save(input_file_modified_location, overwrite=True)
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
plt.show()

