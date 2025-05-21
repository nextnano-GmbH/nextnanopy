import nextnanopy as nn
from nextnanopy.utils.misc import mkdir_if_not_exist
import sys,os
#import numpy as np
import matplotlib.pyplot as plt
import pathlib

# config file is stored in C:\Users\<User>\.nextnanopy-config (home directory)

#++++++++++++++++++++++++++++++++++++++++++++++
# Specify output image format
#++++++++++++++++++++++++++++++++++++++++++++++
#FigFormat = '.pdf'
FigFormat = '.svg'
# FigFormat = '.jpg'
#FigFormat = '.png'


#++++++++++++++++++++++++++++++++++++++++++++++
# Specify input file WITH file extension .in or .xml
#++++++++++++++++++++++++++++++++++++++++++++++
#filename = r'Jogai_AlGaNGaN_FET_JAP2003_GaNcap_Fig6Fig5_1D_nnp.in'
#filename = r'Jogai_AlGaNGaN_FET_JAP2003_GaNcap_Fig6Fig5_1D_nn3.in'
#filename = r'2D_CBR_MamaluySabathilJAP2003_AharonovBohm.in'
#filename = r'2D_CBR_square.in'
filename = r'AlGaN_nnp.in'
# filename = r'AlGaN_nn3.in'
# filename = r'Transmission_Double_Barrier_1D_nnp.in'
# filename = r'Transmission_Double_Barrier_1D_nn3.in'


#++++++++++++++++++++++++++++++++++++++++++++++
# Input file is located on Github
#++++++++++++++++++++++++++++++++++++++++++++++
InputFolder = os.path.join(pathlib.Path(__file__).parent.resolve(), r'input files')


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
software, software_short, FileExtension = detect_software(InputFolder, filename)


# Define output folders. If they do not exist, they are created.
folder_output        = nn.config.config[software]['outputdirectory']
folder_output_python = os.path.join(folder_output, r'nextnanopy')
mkdir_if_not_exist(folder_output_python)


# plt.ion() # interactive mode
print("starting nextnano...")
input_path = os.path.join(InputFolder, filename)
input_file = nn.InputFile(input_path)


print(f"List of variables: {input_file.variables}")
for var in input_file.variables.values():
  # print(f'${var.name} = {var.value} ! {var.comment}')
    print(f'{var.text}') # --> better method to preview

#SweepVariable = 'NO_STRAIN' # A)
SweepVariable = 'STRAIN'    # A)
 
SweepVariable = 'Al_substrate'    # B)

comment_original = input_file.variables[SweepVariable].comment
#ListOfValues = ["10.0"]
#ListOfValues = ["10.0", "15.0", "20.0"]
#ListOfValues = ["1","2","3","4","5","7","9","11","12","13","14","15","17","20","25","30"]
# ListOfValues = ["0","1"] # A)
ListOfValues = ["0.0","0.5","1.0"] # B)


filename_no_extension = filename.replace(FileExtension, '')
dfV=[]
df_cbV=[]
SweepVariableStringV=[]
loop = 0
for x in ListOfValues:
  loop = loop + 1

  input_file.set_variable(SweepVariable, value=x, comment='<= PYTHON <= ' + comment_original)

  for var in input_file.variables.values():
    # print(f'${var.name} = {var.value} ! {var.comment}')
    # print(f'{var.text}') # --> better method to preview
      print(var.text)      # --> better method to preview

  SweepVariableString = SweepVariable+'_'+x
  SweepVariableStringV.append(SweepVariableString)

  input_file_name_variable = filename_no_extension+'_'+SweepVariableString

  my_input_file_new = os.path.join(folder_output, input_file_name_variable+FileExtension)
  print(my_input_file_new)

  input_file.save(my_input_file_new, overwrite=True, automkdir=True)

#  if(loop==0):               # A)
#     labelC = r'unstrained'  # A)
#  elif(loop==1):             # A)
#     labelC = r'strained'    # A)

  if(loop==1):                 # B)
      labelC = r'on GaN'  # B)
  elif(loop==2):               # B)
      labelC = r'on Al$_{0.5}$Ga$_{0.5}$N'    # B)
  elif(loop==3):               # B)
      labelC = r'on AlN'    # B)

  print('')  
  print('=====================================')  
  ############################
  # Execute nextnano software
  ############################
  input_file.execute() # Put line into comment if you only want to to post-processing of results
  print('=====================================')  

# plotL = bool(0) # false
  plotL = bool(1) # true

  if(plotL):
  
    print('=====================================')  
    print('Now generate plots in output folder')  
    print(folder_output)  
    print('=====================================')  

#++++++++++++++++++++++++++++++++++++++++++++++
# These lines have to be adjusted by the user.  
#++++++++++++++++++++++++++++++++++++++++++++++
#===========================
    if(software=="nextnano++"):
        file = os.path.join(folder_output, input_file_name_variable+r'\bias_00000'+r'\bandedges.dat') 
    elif(software=="nextnano3"):
        file = os.path.join(folder_output, input_file_name_variable+r'\band_structure'+r'\BandEdges.dat') 
#===========================
    df = nn.DataFile(file, product=software)
    dfV.append(df)

    fig, ax = plt.subplots(1)
#++++++++++++++++++++++++++++++++++++++++++++++
# These lines have to be adjusted by the user.  
#++++++++++++++++++++++++++++++++++++++++++++++
#===========================
    if(software=="nextnano++"):
      # ax.plot(df.coords['x'].value, df.variables['Gamma'].value, label='Gamma')
        ax.plot(df.coords['x'].value, df.variables['HH'].value, label='heavy hole')
        ax.plot(df.coords['x'].value, df.variables['LH'].value, label='light hole')
        ax.plot(df.coords['x'].value, df.variables['SO'].value, label='crystal-field hole')

        ax.set_ylabel(f"Energy ({df.variables['Gamma'].unit})")
    elif(software=="nextnano3"):
      # ax.plot(df.coords['position'].value, df.variables['Gamma_bandedge'].value, label='Gamma')
        ax.plot(df.coords['position'].value, df.variables['hh_bandedge'].value, label='heavy hole')
        ax.plot(df.coords['position'].value, df.variables['lh_bandedge'].value, label='light hole')
        ax.plot(df.coords['position'].value, df.variables['ch_bandedge'].value, label='crystal-field hole')

        ax.set_ylabel(f"Energy ({df.variables['Gamma_bandedge'].unit})")
    ax.set_xlabel("Al alloy content")
    ax.legend()
    ax.set_title(software + " Valence band edges of Al$_x$Ga$_{1-x}$N" + " (" + labelC + ')')
    fig.tight_layout()
  # plt.show()
    filename = 'band_edges'+'_'+SweepVariableString+FigFormat
    fig.savefig(os.path.join(folder_output_python, filename))
  
print('=====================================')  
print('Done nextnanopy.')  
print('=====================================')  
