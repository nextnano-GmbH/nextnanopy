import nextnanopy as nn
from nextnanopy.utils.misc import mkdir_if_not_exist
import sys,os
#import numpy as np
import matplotlib.pyplot as plt
import nextnanopy.negf.outputs as nnnegf

# config file is stored in C:\Users\<User>\.nextnanopy-config

#++++++++++++++++++++++++++++++++++++++++++++++
# Specify output image format
#++++++++++++++++++++++++++++++++++++++++++++++
#FigFormat = '.pdf'
FigFormat = '.svg'
# FigFormat = '.jpg'
#FigFormat = '.png'


#++++++++++++++++++++++++++++++++++++++++++++++
# Specify input file folder  
#++++++++++++++++++++++++++++++++++++++++++++++
# nextnano++ examples
# input_folder = r'C:\Program Files\nextnano\2020_12_09\Sample files\nextnano++ sample files'
# nextnano3 examples
# input_folder = r'C:\Program Files\nextnano\2020_12_09\Sample files\nextnano3 sample files'
# nextnano.NEGF examples
input_folder = r'D:\nextnano Users\takuma.sato\nextnano\nextnano installation\nextnanoNEGF_2020_11_16\nextnano.NEGF sample files'
# nextnano.MSB examples
# input_folder = r'D:\nextnano.MSB\nextnano.MSB_2017_12_20\nextnano\2017_12_20\nextnano.MSB sample files'


#--------------------------------------------------------
# Specify input file WITH file extension '.in'/.'xml'
#--------------------------------------------------------
filename = r'THz_QCL_GaAs_AlGaAs_Fathololoumi_OptExpress2012_10K-FAST.xml'


#%%
# define a function to detect which software to execute
def detect_software(folder_path, filename):
    if not '.' in filename:
        print('ERROR: Please specify input file with extension (.in or .xml)')
        sys.exit()

    InputPath = os.path.join(folder_path, filename)
    with open(InputPath,'r') as file:
        for line in file:
            if 'simulation-flow-control' in line:
                software = 'nextnano3'
                software_short = '_nn3'
                FileExtension = '.in'
                break
            elif 'run{' in line:
                software = 'nextnano++'
                software_short = '_nnp'
                FileExtension = '.in'
                break
            elif '<nextnano.NEGF' in line:
                software = 'nextnano.NEGF_classic'
                software_short = '_nnNEGF_classic'
                FileExtension = '.xml'
                break            
            elif 'nextnano.NEGF{' in line:
                software = 'nextnano.NEGF'
                software_short = '_nnNEGF'
                FileExtension = '.negf'
                break
            elif '<nextnano.MSB' in line:
                software = 'nextnano.MSB'
                software_short = '_nnMSB'
                FileExtension = '.xml'
                
    if not software:   # if the variable is empty
        print('ERROR: Software cannot be detected! Please check your input file.')
        sys.exit()
    else: 
        print('Software detected: ', software)
    
    return software, software_short, FileExtension

# detect software based on input file
software, software_short, FileExtension = detect_software(input_folder, filename)

# Define output folders. If they do not exist, they are created.
folder_output        = nn.config.config[software]['outputdirectory']
folder_output_python = os.path.join(folder_output, r'nextnanopy')
mkdir_if_not_exist(folder_output_python)
print("Output folder:        ",folder_output)
print("Output folder python: ",folder_output_python)





# plt.ion() # interactive mode
print("starting nextnano...")
input_path = os.path.join(input_folder, filename)
input_file = nn.InputFile(input_path)

filename_no_extension = filename.replace(FileExtension, '')

folder_total = os.path.join(folder_output, filename_no_extension)
print("output folder_total:")
print(folder_total)

my_input_file_python = os.path.join(folder_output_python, filename)
my_input_file_new    = os.path.join(folder_total, filename)
print("input file:")
print(my_input_file_new)

input_file.save(my_input_file_python, overwrite=True, automkdir=True)
input_file.save(my_input_file_new, overwrite=True, automkdir=True)

print('')  
print('=====================================')  
  ############################
  # Execute nextnano software
  ############################
input_file.execute() # Put line into comment if you only want to to post-processing of results
print('=====================================')  

#plotL = bool(0) # false
plotL = bool(1) # true

if(plotL):
  
  print('=====================================')  
  print('Now generate plots in output folder')  
  print(folder_output)  
  print('=====================================')  

  folder = nn.config.config[software]['outputdirectory']
  print("output folder:")
  print(folder)

  if(software=="nextnano++"):
      print("nextnano++ not implemented!")
  elif(software=="nextnano3"):
      print("nextnano3 not implemented!")
  elif(software=="nextnano.NEGF_classic"):

      folder_results = filename_no_extension
      print("output folder_results:")
      print(folder_results)

      folder_total = os.path.join(folder,folder_results)
      print("output folder_total:")
      print(folder_total)

      folder_bias = folder_results+r'\2mV'
      print("output folder_bias:")
      print(folder_bias)

      folder_total_bias = os.path.join(folder,folder_bias)
      print("output folder_total_bias:")
      print(folder_total_bias)

      file_cb = folder_total_bias+r'\Conduction_BandEdge.dat'
  elif(software=="nextnano.MSB"):

      folder_results = filename_no_extension+r'\BarrierThickness=2'
      print("output folder_results:")
      print(folder_results)

      folder_total = os.path.join(folder,folder_results)
      print("output folder_total:")
      print(folder_total)

      folder_bias = folder_results+r'\Source=0V, Drain=0V'
      print("output folder_bias:")
      print(folder_bias)

      folder_total_bias = os.path.join(folder,folder_bias)
      print("output folder_total_bias:")
      print(folder_total_bias)

      file_cb = folder_total_bias+r'\BandProfile'+r'\BandEdge_conduction.dat'
#===========================
# Conduction band edge
#===========================
  print("Read in file:")
  print(file_cb)
  df = nn.DataFile(file_cb,software)

  fig, ax = plt.subplots(1)
  ax.plot(df.coords['Position'].value,df.variables['Conduction Band Edge'].value,label='Conduction Band Edge')
  
  ax.set_xlabel(f"{df.coords['Position'].name} {df.coords['Position'].unit}")
  ax.set_ylabel(f"Energy {df.variables['Conduction Band Edge'].unit}")
  ax.legend()
  fig.tight_layout()
# plt.show()
  fig.savefig(file_cb+'.jpg')


  if(software=="nextnano.MSB"):
     extension2Dfile = '.vtr'
   # extension2Dfile = '.avs.fld'
  else:
     extension2Dfile = '.vtr'
   # extension2Dfile = '.fld'
      
  if(software=="nextnano++"):
      file_LDOS = ''
      file_Density = ''
      file_Current = ''
  elif(software=="nextnano3"):
      file_LDOS = ''
      file_Density = ''
      file_Current = ''
  elif(software=="nextnano.NEGF_classic"):
      subfolder = '2D_plots'
      file_LDOS = 'DOS_energy_resolved'+extension2Dfile
      file_Density = 'CarrierDensity_energy_resolved'+extension2Dfile
      file_Current = 'CurrentDensity_energy_resolved'+extension2Dfile
  elif(software=="nextnano.MSB"):
      file_LDOS = 'DOS_position_resolved'+extension2Dfile
      file_Density = 'CarrierDensity_energy_resolved'+extension2Dfile
      file_Current = 'CurrentDensity_energy_resolved'+extension2Dfile

  folder2Dplots = os.path.join(folder,folder_bias)
  for i in range(3):
      if(i == 0):
          if(software=="nextnano.MSB"): subfolder = 'DOS'
          label = 'Local density of states LDOS(x,E)'
          file = file_LDOS
      elif(i == 1):
          if(software=="nextnano.MSB"): subfolder = 'CarrierDensity'
          label = 'Carrier density n(x,E)'
          file = file_Density
      elif(i == 2):
          if(software=="nextnano.MSB"): subfolder = 'CurrentDensity'
          label = 'Current density j(x,E)'
          file = file_Current

      folder2D = os.path.join(folder2Dplots,subfolder)
      file2D = os.path.join(folder2D,file)
      print("Plotting file: ",file2D)
      dff = nn.DataFile(file2D,product=software)
      print("List of coordinates in the current datafile: {dff.coords}")
      print("List of variables in the current datafile: {dff.variables}")
      cX = dff.coords['x']
      cY = dff.coords['y']
      cZ = dff.variables[0]
      fD, a2D1 = plt.subplots()
      im1 = a2D1.pcolormesh(cX.value, cY.value, cZ.value.T, cmap='gnuplot')
      a2D1.plot(df.coords[0].value,df.variables[0].value,label='Conduction Band Edge',
              color='white', linestyle='-')
      a2D1.set_title(label)  
      filename = file2D+'.jpg'
      print('Saving file: ',filename)
      fD.savefig(filename)


  #%% Bandstructure - normalized
  z,pot,ws = nnnegf.get_WannierStark_norm(folder_total_bias,scaling_factor=0.3)
  fws, aws = plt.subplots()
  nsp = int(len(ws)/3)
  aws.plot(z,pot,color='black')
  for i in range(nsp-3,2*nsp+1):
      aws.plot(z,ws[i])
    
      #sel = (15,17)
      #trans = nnd.get_transition(40,sel)
      #aws.plot(z,trans[0],color='red')
      #aws.plot(z,trans[1],color='red',label='$\Delta E$ = ' + str(np.round(trans[2],2)) + ', f* = ' + str(np.round(trans[3],2)))
      #aws.legend()

      spacer = 10
      aws.set_xlim(-spacer,(-1)*min(z)+spacer)
      aws.set_ylim(0.025,0.2)   
      aws.set(xlabel='z (nm)',ylabel='Energy (eV)')

      filename = folder_total_bias+r'\psi_squared.jpg'
      print('Saving file: ',filename)
      fws.savefig(filename)

  if(software=="nextnano.NEGF"):
       # IV curve
      print('folder_results =', folder_total)  
      iv = nnnegf.get_iv(folder_total)
      f,a = plt.subplots()
      a.plot(iv[0],iv[1],'o-')
      a.set(xlabel= 'Voltage (mV/period)',ylabel='Current density (A/cm$^2$)')
      filename = folder_total+r'\IV_curve.jpg'
      print('Saving file: ',filename)
      f.savefig(filename)

print('=====================================')  
print('Done nextnanopy.')  
print('=====================================')  
