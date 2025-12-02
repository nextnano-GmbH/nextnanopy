import nextnanopy as nn
from nextnanopy.utils.misc import mkdir_if_not_exist
import sys,os
#import numpy as np
import matplotlib.pyplot as plt

import config_nextnano     # This should be your default configuration.
#import config_nextnano_temp # This could be a modified configuration file.
#config file is stored in C:\Users\<User>\.nextnanopy-config

#FigFormat = '.pdf'
#FigFormat = '.svg'
FigFormat = '.jpg'
#FigFormat = '.png'

#++++++++++++++++++++++++++++++++++++++++++++++
# These lines have to be adjusted by the user.  
#++++++++++++++++++++++++++++++++++++++++++++++
#================================
# Specify software product here!
#================================
software = 'nextnano++'
#software = 'nextnano3'
#software = 'nextnano.NEGF'
#software = 'nextnano.MSB'
#===========================

folder_examples_nnp    = r'C:\Program Files\nextnano\2020_12_09\Sample files\nextnano++ sample files'
folder_examples_nn3    = r'C:\Program Files\nextnano\2020_12_09\Sample files\nextnano3 sample files'
folder_examples_nnNEGF = r'D:\nextnano.NEGF\nextnanoNEGF_2020_11_16\nextnano.NEGF sample files'
folder_examples_nnMSB  = r'D:\nextnano.MSB\nextnano.MSB_2017_12_20\nextnano\2017_12_20\nextnano.MSB sample files'

#++++++++++++++++++++++++++++++++++++++++++++++
# These lines have to be adjusted by the user.  
#++++++++++++++++++++++++++++++++++++++++++++++
#folder_examples_nn3 = r'N:\users\nextnano\nextnano GmbH - Tutorials\Tutorials\2D The CBR method (Transmission)'
#===========================
if(software=="nextnano++"):
    subfolder = ''
  # subfolder = r'\Quantum Mechanics examples'
elif(software=="nextnano3"):
    subfolder = ''
  # subfolder = r'\Quantum Mechanics examples'
elif(software=="nextnano.NEGF"):
    subfolder = ''
elif(software=="nextnano.MSB"):
    subfolder = ''
#===========================

software_short_nnp    = '_nnp'
software_short_nn3    = '_nn3'
software_short_nnNEGF = '_nnNEGF'
software_short_nnMSB  = '_nnMSB'

#===========================
if(software=="nextnano++"):
    software_short = software_short_nnp
elif(software=="nextnano3"):
    software_short = software_short_nn3
elif(software=="nextnano.NEGF"):
    software_short = software_short_nnNEGF
elif(software=="nextnano.MSB"):
    software_short = software_short_nnMSB
#===========================

#===========================
if(software=="nextnano++"):
    folder_examples = folder_examples_nnp + subfolder   # nextnano++
elif(software=="nextnano3"):
    folder_examples = folder_examples_nn3 + subfolder   # nextnano3
elif(software=="nextnano.NEGF"):
    folder_examples = folder_examples_nnNEGF + subfolder # nextnano.NEGF
elif(software=="nextnano.MSB"):
    folder_examples = folder_examples_nnMSB + subfolder # nextnano.MSB
#===========================

#==========================================================================
# Define input and output folders. If they do not exist, they are created.
#==========================================================================
home_directory = r'C:\Users\stefan.birner.NEXTNANO\Documents\nextnano'
folder_output        = nn.config.config[software]['outputdirectory']
folder_python_input  = os.path.join(home_directory,r'nextnanopy\input')
folder_python_output = os.path.join(home_directory,r'nextnanopy\output')
folder_examples = folder_python_input

mkdir_if_not_exist(folder_output)
mkdir_if_not_exist(folder_python_output)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Open reStructured Text file (.rst) for documentation
#++++++++++++++++++++++++++++++++++++++++++++++++++++++
file_docu =  open(os.path.join(folder_python_output,'documentation'+software_short+'.rst'),"w+")

DocuInfo = "**Automatic documentation: Running simulations, generating figures and reStructured Text (*.rst) using nextnanopy**"

file_docu.write("\n")
file_docu.write("\n")
file_docu.write(r"----------------------"+"\n") # horizontal line
file_docu.write("\n")
file_docu.write("\n")
file_docu.write(r"--- Begin ---"+"\n")
file_docu.write("\n")
file_docu.write(DocuInfo+"\n")
file_docu.write("\n")
file_docu.write(r"The following documentation and figures were generated automatically using |nextnanopy|."+"\n")
file_docu.write("\n")
file_docu.write(r"The following Python script was used: ``intersubband_MQW_"+software+".py``"+"\n")
file_docu.write("\n")
file_docu.write(r"----------------------"+"\n") # horizontal line
file_docu.write("\n")

file_docu.write("\n")
file_docu.write(r"The following figures have been generated using the |"+software+"| software."+"\n")
# Note: The umlaut for Schrödinger is not written correctly!!!
#file_docu.write(r"Self-consistent Schrödinger-Poisson calculations have been performed for three different structures."+"\n")
file_docu.write(r"Self-consistent Schroedinger-Poisson calculations have been performed for three different structures."+"\n")
file_docu.write("\n")
file_docu.write(r"* Single Quantum Well"+"\n")
file_docu.write("\n")
file_docu.write(r"* Two coupled Quantum Wells"+"\n")
file_docu.write("\n")
file_docu.write(r"* Three coupled Quantum Wells"+"\n")
file_docu.write("\n")
file_docu.write("\n")
file_docu.write(r"The single-band effective mass and the 8-band |k_dot_p| results are compared to each other."+"\n")
file_docu.write(r"In both cases the wave functions and the quantum density are calculated self-consistently."+"\n")
file_docu.write(r"The |k_dot_p| quantum density has been calculated taking into account the solution at different :math:`k_\parallel` vectors."+"\n")
file_docu.write("\n")
file_docu.write(r"The absorption has been calculated using a simple model assuming a parabolic energy dispersion."+"\n")
file_docu.write(r"The dipole moment :math:`z_{ij}=<i|z|j>` has been evaluated only at :math:`k_\parallel =0`. "+"\n")
file_docu.write(r"The subband density is used to calculate the absorption."+"\n")
file_docu.write(r"For the |k_dot_p| calculation, the density was calculated taking into account a nonparabolic energy dispersion, i.e. including all relevant :math:`k_\parallel` vectors."+"\n")
file_docu.write("\n")
file_docu.write("\n")

df_absV=[]

for nn_file in range(6):

    print (nn_file)

#   sys.exit()

    #--------------------------------------------------------
    # Specify input file without file extension '.in'/.'xml'
    #--------------------------------------------------------
    #my_input_file_no_extension_nnp = r'Jogai_AlGaNGaN_FET_JAP2003_GaNcap_Fig6Fig5_1D_nnp'
    #my_input_file_no_extension_nn3 = r'Jogai_AlGaNGaN_FET_JAP2003_GaNcap_Fig6Fig5_1D_nn3'
    #my_input_file_no_extension_nn3 = r'2D_CBR_MamaluySabathilJAP2003_AharonovBohm'
    #my_input_file_no_extension_nn3 = r'2D_CBR_square'
    my_input_file_no_extension_nnNEGF = r'THz_QCL_GaAs_AlGaAs_Fathololoumi_OptExpress2012_10K-FAST'
    my_input_file_no_extension_nnMSB = r'1D_Transmission_DoubleBarrier_CBR_paper_MSB'
    

    if nn_file == 0:    
       my_input_file_no_extension_nn3 = r'1DSirtoriPRB1994_OneWell_sg_self-consistent_nn3'
       my_input_file_no_extension_nnp = r'1DSirtoriPRB1994_OneWell_sg_self-consistent_nnp'
       MQW = 1
       sg_kp = "sg"
    elif nn_file == 1:    
       my_input_file_no_extension_nn3 = r'1DSirtoriPRB1994_OneWell_kp_self-consistent_nn3'
     # my_input_file_no_extension_nnp = r'1DSirtoriPRB1994_OneWell_kp_self-consistent_nnp'
       my_input_file_no_extension_nnp = r'1DSirtoriPRB1994_OneWell_kp_quantum-only_nnp'
       MQW = 1
       sg_kp = "kp"
    elif nn_file == 2:    
       my_input_file_no_extension_nn3 = r'1DSirtoriPRB1994_TwoCoupledWells_sg_self-consistent_nn3'
       my_input_file_no_extension_nnp = r'1DSirtoriPRB1994_TwoCoupledWells_sg_self-consistent_nnp'
       MQW = 2
       sg_kp = "sg"
    elif nn_file == 3:    
       my_input_file_no_extension_nn3 = r'1DSirtoriPRB1994_TwoCoupledWells_kp_self-consistent_nn3'
     # my_input_file_no_extension_nnp = r'1DSirtoriPRB1994_TwoCoupledWells_kp_self-consistent_nnp'
       my_input_file_no_extension_nnp = r'1DSirtoriPRB1994_TwoCoupledWells_kp_quantum-only_nnp'
       MQW = 2
       sg_kp = "kp"
    elif nn_file == 4:    
       my_input_file_no_extension_nn3 = r'1DSirtoriPRB1994_ThreeCoupledWells_sg_self-consistent_nn3'
       my_input_file_no_extension_nnp = r'1DSirtoriPRB1994_ThreeCoupledWells_sg_self-consistent_nnp'
       MQW = 3
       sg_kp = "sg"
    elif nn_file == 5:    
       my_input_file_no_extension_nn3 = r'1DSirtoriPRB1994_ThreeCoupledWells_kp_self-consistent_nn3'
     # my_input_file_no_extension_nnp = r'1DSirtoriPRB1994_ThreeCoupledWells_kp_self-consistent_nnp'
       my_input_file_no_extension_nnp = r'1DSirtoriPRB1994_ThreeCoupledWells_kp_quantum-only_nnp'
       MQW = 3
       sg_kp = "kp"

    if sg_kp == 'sg':
       type_of_calculation = " (single-band)"
    elif sg_kp == 'kp':
       type_of_calculation = " (k.p)"

    #===========================
    if(software=="nextnano++"):
        my_input_file_no_extension = my_input_file_no_extension_nnp
    elif(software=="nextnano3"):
        my_input_file_no_extension = my_input_file_no_extension_nn3
    elif(software=="nextnano.NEGF"):
        my_input_file_no_extension = my_input_file_no_extension_nnNEGF
    elif(software=="nextnano.MSB"):
        my_input_file_no_extension = my_input_file_no_extension_nnMSB
    #===========================
    
    if(software=="nextnano.NEGF" or software=="nextnano.MSB"):
        FileExtension = '.xml' # for nextnano.NEGF and nextnano.MSB
    else:
        FileExtension = '.in'  # for nextnano++ and nextnano3
    
    my_input_file = my_input_file_no_extension+FileExtension
    
    # plt.ion() # interactive mode
    
    print(f"starting nextnano...")
    input_file_name = os.path.join(folder_examples,my_input_file)
    input_file = nn.InputFile(input_file_name)
    print(input_file)

   
    #++++++++++++++++++++++++++++++++++++++++++++++
    # These lines have to be adjusted by the user.  
    #++++++++++++++++++++++++++++++++++++++++++++++
    print(f"List of variables: {input_file.variables}")
    for var in input_file.variables.values():
      # print(f'${var.name} = {var.value} ! {var.comment}')
        print(f'{var.text}') # --> better method to preview
    
    ListOfValues = ["none"]
    
    for x in ListOfValues:
    

      for var in input_file.variables.values():
        # print(f'${var.name} = {var.value} ! {var.comment}')
        # print(f'{var.text}') # --> better method to preview
          print(var.text)      # --> better method to preview
    
      SweepVariableString = ''
    
      input_file_name_variable = my_input_file_no_extension
    
      my_input_file_new = os.path.join(folder_output,input_file_name_variable+FileExtension)
      print(my_input_file_new)
    
      input_file.save(my_input_file_new,overwrite=True,automkdir=True)
    
      print(f'')  
      print(f'=====================================')  
      ############################
      # Execute nextnano software
      ############################
      input_file.execute() # Put line into comment if you only want to to post-processing of results
      print(f'=====================================')  
   
      #plotL = bool(0) # false
      plotL = bool(1) # true
    
      if(plotL):
      
        print(f'=====================================')  
        print(f'Now generate plots in output folder')  
        print(folder_output)  
        print(f'=====================================')  
    
    #++++++++++++++++++++++++++++++++++++++++++++++
    # These lines have to be adjusted by the user.  
    #++++++++++++++++++++++++++++++++++++++++++++++
    #===========================
        if(software=="nextnano++"):
            file_cb  = os.path.join(folder_output,input_file_name_variable+r'\bias_00000'+r'\bandedges.dat') 
            if sg_kp == 'sg':
               file_psi = os.path.join(folder_output,input_file_name_variable+r'\bias_00000'+r'\Quantum'+r'\wf_probabilities_shift_quantum_region_Gamma_0000.dat') 
            elif sg_kp == 'kp':
               file_psi = os.path.join(folder_output,input_file_name_variable+r'\bias_00000'+r'\Quantum'+r'\wf_probabilities_shift_quantum_region_kp8_0000.dat') 
        elif(software=="nextnano3"):
            file_cb  = os.path.join(folder_output,input_file_name_variable+r'\band_structure'+r'\BandEdges.dat') 
            if sg_kp == 'sg':
               file_psi = os.path.join(folder_output,input_file_name_variable+r'\Schroedinger_1band'+r'\cb1_sg1_deg1_psi_squared_shift.dat') 
               file_abs = os.path.join(folder_output,input_file_name_variable+r'\optics'+r'\absorption_intraband_cb1_sg1_deg1.dat') 
            elif sg_kp == 'kp':
               file_psi = os.path.join(folder_output,input_file_name_variable+r'\Schroedinger_kp'+r'\kp8_psi_squared_el_kpar001_1D_neu_shift.dat') 
               file_abs = os.path.join(folder_output,input_file_name_variable+r'\optics'+r'\absorption_intraband_cb1_kp8.dat') 
    #===========================
    
        #===========================
        # Conduction band edge
        #===========================
        print(f"Read in file:")
        print(file_cb)
        df_cb = nn.DataFile(file_cb,product=software)

        print(f"Read in file:")
        print(file_psi)
        df_psi = nn.DataFile(file_psi,product=software)
    
        print(f"current datafile: ",file_cb)
        print(f"List of coordinates in the current datafile: {df_cb.coords}")
        print(f"List of variables in the current datafile: {df_cb.variables}")

        print(f"current datafile: ",file_psi)
        print(f"List of coordinates in the current datafile: {df_psi.coords}")
        print(f"List of variables in the current datafile: {df_psi.variables}")
    

        fig_psi, ax_psi = plt.subplots(1)

        if MQW == 1:
           NameOfStructure = 'Quantum Well' + type_of_calculation 
           NameOfStructureFile = 'OneWell' 
           Caption = 'a quantum well'
           if(software=="nextnano++"):
              ax_psi.plot(df_cb.coords['x'].value,df_cb.variables['Gamma'].value,label=SweepVariableString)
              ax_psi.plot(df_cb.coords['x'].value,df_cb.variables['electron_Fermi_level'].value,label=SweepVariableString)
           elif(software=="nextnano3"):
              ax_psi.plot(df_cb.coords['position'].value,df_cb.variables['Gamma_bandedge'].value,label=SweepVariableString)
              ax_psi.plot(df_cb.coords['position'].value,df_cb.variables['FermiLevel_el'].value,label=SweepVariableString)
           if sg_kp == 'sg':
              if(software=="nextnano++"):
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_2'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_1'].value,label=SweepVariableString)
              elif(software=="nextnano3"):
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_2'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_1'].value,label=SweepVariableString)
              ax_psi.legend(['$E_c$','$E_F$','$\psi_2^2$','$\psi_1^2$'])
           elif sg_kp == 'kp':  
              if(software=="nextnano++"):
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_4'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_3'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_2'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_1'].value,label=SweepVariableString)
              elif(software=="nextnano3"):
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_4'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_3'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_2'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_1'].value,label=SweepVariableString)
              ax_psi.legend(['$E_c$','$E_F$','$\psi_4^2$','$\psi_3^2$','$\psi_2^2$','$\psi_1^2$'])
        elif MQW == 2:
           NameOfStructure = 'Two Coupled Quantum Wells' + type_of_calculation
           NameOfStructureFile = 'TwoWells' 
           Caption = 'two coupled quantum wells'
           if(software=="nextnano++"):
              ax_psi.plot(df_cb.coords['x'].value,df_cb.variables['Gamma'].value,label=SweepVariableString)
              ax_psi.plot(df_cb.coords['x'].value,df_cb.variables['electron_Fermi_level'].value,label=SweepVariableString)
           elif(software=="nextnano3"):
              ax_psi.plot(df_cb.coords['position'].value,df_cb.variables['Gamma_bandedge'].value,label=SweepVariableString)
              ax_psi.plot(df_cb.coords['position'].value,df_cb.variables['FermiLevel_el'].value,label=SweepVariableString)
           if sg_kp == 'sg':
              if(software=="nextnano++"):
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_3'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_2'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_1'].value,label=SweepVariableString)
              elif(software=="nextnano3"):
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_3'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_2'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_1'].value,label=SweepVariableString)
              ax_psi.legend(['$E_c$','$E_F$','$\psi_3^2$','$\psi_2^2$','$\psi_1^2$'])
           elif sg_kp == 'kp':
              if(software=="nextnano++"):
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_6'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_5'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_4'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_3'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_2'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_1'].value,label=SweepVariableString)
              elif(software=="nextnano3"):
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_6'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_5'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_4'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_3'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_2'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_1'].value,label=SweepVariableString)
              ax_psi.legend(['$E_c$','$E_F$','$\psi_6^2$','$\psi_5^2$','$\psi_4^2$','$\psi_3^2$','$\psi_2^2$','$\psi_1^2$'])
        elif MQW == 3:
           NameOfStructure = 'Three Coupled Quantum Wells' + type_of_calculation
           NameOfStructureFile = 'ThreeWells' 
           Caption = 'three coupled quantum wells'
           if(software=="nextnano++"):
              ax_psi.plot(df_cb.coords['x'].value,df_cb.variables['Gamma'].value,label=SweepVariableString)
              ax_psi.plot(df_cb.coords['x'].value,df_cb.variables['electron_Fermi_level'].value,label=SweepVariableString)
           elif(software=="nextnano3"):
              ax_psi.plot(df_cb.coords['position'].value,df_cb.variables['Gamma_bandedge'].value,label=SweepVariableString)
              ax_psi.plot(df_cb.coords['position'].value,df_cb.variables['FermiLevel_el'].value,label=SweepVariableString)
           if sg_kp == 'sg':
              if(software=="nextnano++"):
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_3'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_2'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_1'].value,label=SweepVariableString)
              elif(software=="nextnano3"):
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_3'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_2'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_1'].value,label=SweepVariableString)
              ax_psi.legend(['$E_c$','$E_F$','$\psi_3^2$','$\psi_2^2$','$\psi_1^2$'])
           elif sg_kp == 'kp':
              if(software=="nextnano++"):
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_6'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_5'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_4'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_3'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_2'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_1'].value,label=SweepVariableString)
              elif(software=="nextnano3"):
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_6'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_5'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_4'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_3'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_2'].value,label=SweepVariableString)
                 ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_1'].value,label=SweepVariableString)
              ax_psi.legend(['$E_c$','$E_F$','$\psi_6^2$','$\psi_5^2$','$\psi_4^2$','$\psi_3^2$','$\psi_2^2$','$\psi_1^2$'])
    
        ax_psi.set_title(NameOfStructure)
        if(software=="nextnano++"):
           ax_psi.set_xlabel(f"{df_psi.coords['x'].name} ({df_psi.coords['x'].unit})")
        elif(software=="nextnano3"):
           ax_psi.set_xlabel(f"{df_psi.coords['position'].name} ({df_psi.coords['position'].unit})")
        ax_psi.set_ylabel(f"energy ({df_psi.variables[0].unit})")
        fig_psi.tight_layout()
      # plt.show()
        filename_cb_psi = 'cb_psi'+'_'+NameOfStructureFile+'_'+sg_kp+software_short+'.jpg'
        fig_psi.savefig(os.path.join(folder_python_output,filename_cb_psi))

        
        #---------------------
        # Write documentation
        #---------------------
        file_docu.write(r"**"+NameOfStructure+"**"+"\n")
        file_docu.write("\n")

        image_path = '/images/nextnanoplus/tutorials/intersubband_MQW/'

        file_docu.write(r".. figure:: "+image_path+filename_cb_psi+"\n")
        file_docu.write(r"   :alt: "+NameOfStructureFile+"\n")
        file_docu.write(r"   :align: center"+"\n")
        file_docu.write("\n")
        file_docu.write(r"   Conduction band edge, Fermi level and confined electron states of "+Caption+"\n")
        file_docu.write("\n")
        file_docu.write("\n")



#++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Close reStructured Text file (.rst) for documentation
#++++++++++++++++++++++++++++++++++++++++++++++++++++++
file_docu.write("\n")
file_docu.write(r"----------------------"+"\n") # horizontal line
file_docu.write("\n")
file_docu.write(DocuInfo+"\n")
file_docu.write("\n")
file_docu.write(r"--- End ---"+"\n")
file_docu.write("\n")
file_docu.write(r"----------------------"+"\n") # horizontal line
file_docu.write("\n")
file_docu.write("\n")
file_docu.close() 
    
print(f'=====================================')  
print(f'Done nextnanopy.')  
print(f'=====================================')  
