import nextnanopy as nn
from nextnanopy.utils.misc import mkdir_if_not_exist
import sys,os
#import numpy as np
import matplotlib.pyplot as plt
import nextnanopy.negf.outputs as nnnegf

# config file is stored in C:\Users\<User>\.nextnanopy-config

#++++++++++++++++++++++++++++
# Specify output image format
#++++++++++++++++++++++++++++
fig_format = '.svg' # .svg, .jpg, .png, .pdf


#+++++++++++++++++++
# Specify input file  
#+++++++++++++++++++
input_folder = r'c:\Program Files\nextnano\2025_05_30\nextnano.NEGF\examples'

filename = r'THz_QCL_GaAs_AlGaAs_Fathololoumi_OptExpress2012_10K-FAST.negf'

software = "nextnano.NEGF" 

# execute the input file
print("starting nextnano...")
input_path = os.path.join(input_folder, filename)
input_file = nn.InputFile(input_path)

input_file.execute() # Put line into comment if you only want to do post-processing of results

folder_output = input_file.folder_output
# if you do not execute the input file, you can also specify the output folder manually here:
# folder_output = r"c:\Users\Heorhii\Documents\nextnano\OutputNnpy\THz_QCL_GaAs_AlGaAs_Fathololoumi_OptExpress2012_10K-FAST"

bias_folder_name = '2mV'  # example for nextnano.NEGF
data_folder = nn.DataFolder(folder_output)
bias_folder_fullpath = data_folder.go_to(bias_folder_name).fullpath
cb_data_file = data_folder.go_to(bias_folder_name, "ConductionBandEdge.dat")

# plot conduction band edge
print("Read in file:")
print(cb_data_file)
df = nn.DataFile(cb_data_file,software)

fig, ax = plt.subplots(1)
ax.plot(df.coords['Position'].value,df.variables[0].value,label='Conduction Band Edge') 
ax.set_xlabel(f"{df.coords['Position'].name} {df.coords['Position'].unit}")
ax.set_ylabel(f"Energy {df.variables[0].unit}")
ax.legend()
fig.tight_layout()
fig_location = os.path.join(folder_output, 'Conduction_BandEdge'+fig_format)
fig.savefig(fig_location)


# plot 2D plots: LDOS, Carrier density, Current density
extension2Dfile = ".vtr"
subfolder_2D = '2D_plots'
file_ldos = 'DensityOfStates.vtr'
file_density = 'CarrierDensity.vtr'
file_current = 'CurrentDensity_withDispersion.vtr'


for file, label in zip([file_ldos, file_density, file_current], ['Local density of states LDOS(x,E)', 'Carrier density n(x,E)', 'Current density j(x,E)']):
    file2D = data_folder.go_to(bias_folder_name, subfolder_2D, file)
    print("Plotting file: ",file2D)
    df_2D = nn.DataFile(file2D,product=software)
    cX = df_2D.coords['x']
    cY = df_2D.coords['y']
    cZ = df_2D.variables[0]
    fig, ax = plt.subplots()
    im1 = ax.pcolormesh(cX.value, cY.value, cZ.value.T, cmap='gnuplot')
    ax.plot(df.coords[0].value,df.variables[0].value,label='Conduction Band Edge',
            color='white', linestyle='-')
    ax.set_title(label)  
    filename = f"{file2D[:-4]}.jpg"
    print('Saving file: ',filename)
    fig.savefig(filename)


# plot normalized band structure
# TODO fix the name of the function in nextnanopy.negf.nnnegf
z,pot,ws = nnnegf.get_WannierStark_norm_cpp(bias_folder_fullpath,scaling_factor=0.3)
fig, ax = plt.subplots()
nsp = int(len(ws)/3)
ax.plot(z,pot,color='black')
for i in range(nsp-3,2*nsp+1):
    ax.plot(z,ws[i])
    spacer = 10
    ax.set_xlim(-spacer,(-1)*min(z)+spacer)
    ax.set_ylim(0.025,0.2)   
    ax.set(xlabel='z (nm)',ylabel='Energy (eV)')
    filename = bias_folder_fullpath+r'\psi_squared.jpg'
    print('Saving file: ',filename)
    fig.savefig(filename)

plt.show()
print('=====================================')  
print('Done nextnanopy.')  
print('=====================================')  
