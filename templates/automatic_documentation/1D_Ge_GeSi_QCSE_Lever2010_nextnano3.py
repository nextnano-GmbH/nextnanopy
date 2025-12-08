import nextnanopy as nn
from nextnanopy.utils.misc import mkdir_if_not_exist
import sys,os
#import numpy as np
import matplotlib.pyplot as plt

#import config_nextnano     # This should be your default configuration.
# import config_nextnano_temp # This could be a modified configuration file.
#config file is stored in C:\Users\<User>\.nextnanopy-config

FigFormat1 = '.pdf' # high quality
#FigFormat = '.svg' # high quality'
FigFormat2 = '.jpg' # poor quality
#FigFormat = '.png' # poor quality

#++++++++++++++++++++++++++++++++++++++++++++++
# These lines have to be adjusted by the user.  
#++++++++++++++++++++++++++++++++++++++++++++++
#================================
# Specify software product here!
#================================
#software = 'nextnano++'
software = 'nextnano3'
#===========================

folder_examples_nnp    = r'C:\Program Files\nextnano\2020_12_09\Sample files\nextnano++ sample files'
folder_examples_nn3    = r'C:\Program Files\nextnano\2020_12_09\Sample files\nextnano3 sample files'

#++++++++++++++++++++++++++++++++++++++++++++++
# These lines have to be adjusted by the user.  
#++++++++++++++++++++++++++++++++++++++++++++++
#folder_examples_nn3 = r'N:\users\nextnano\nextnano GmbH - Tutorials\Tutorials\2D The CBR method (Transmission)'
#===========================
if(software=="nextnano++"):
    subfolder = ''
elif(software=="nextnano3"):
    subfolder = ''
#===========================

software_short_nnp    = '_nnp'
software_short_nn3    = '_nn3'

#===========================
if(software=="nextnano++"):
    software_short = software_short_nnp
elif(software=="nextnano3"):
    software_short = software_short_nn3
#===========================

#===========================
if(software=="nextnano++"):
    folder_examples = folder_examples_nnp + subfolder   # nextnano++
elif(software=="nextnano3"):
    folder_examples = folder_examples_nn3 + subfolder   # nextnano3
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
file_docu =  open(os.path.join(folder_python_output,'documentation'+'.rst'),"w+")

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
file_docu.write(r"The following Python script was used: ``intersubband_MQW_nextnano3_kp.py``"+"\n")
file_docu.write("\n")
file_docu.write(r"----------------------"+"\n") # horizontal line
file_docu.write("\n")

file_docu.write("\n")
file_docu.write(r"The following figures have been generated using the |nextnano3| software."+"\n")
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
file_docu.write(r"The dipole moment :math:`x_{ij}=<i|x|j>` has been evaluated only at :math:`k_\parallel =0`. "+"\n")
file_docu.write(r"The subband density is used to calculate the absorption."+"\n")
file_docu.write(r"For the |k_dot_p| calculation, the density was calculated taking into account a nonparabolic energy dispersion, i.e. including all relevant :math:`k_\parallel` vectors."+"\n")
file_docu.write("\n")
file_docu.write("\n")

df_absV=[]

for nn_file in range(3):

    print (nn_file)

#   sys.exit()

    #--------------------------------------------------------
    # Specify input file without file extension '.in'/.'xml'
    #--------------------------------------------------------

    if nn_file == 0:    
       my_input_file_no_extension_nn3 = r'1D_Ge_GeSi_QCSE_Lever2010_square_nn3_CALCULATION_1'
       my_input_file_no_extension_nnp = r'1D_Ge_GeSi_QCSE_Lever2010_square_nnp_CALCULATION_1'
     # my_input_file_no_extension_nnp = r'1D_Ge_GeSi_QCSE_Lever2010_nnp_CALCULATION_1'
       MQW = 1
       sg_kp = "sg"
    elif nn_file == 1:    
       my_input_file_no_extension_nn3 = r'1D_Ge_GeSi_QCSE_Lever2010_square_nn3_CALCULATION_2'
       my_input_file_no_extension_nnp = r'1D_Ge_GeSi_QCSE_Lever2010_square_nnp_CALCULATION_2'
     # my_input_file_no_extension_nnp = r'1D_Ge_GeSi_QCSE_Lever2010_nnp_CALCULATION_2'
       MQW = 1
       sg_kp = "sg_kp6"
    elif nn_file == 2:    
       my_input_file_no_extension_nn3 = r'1D_Ge_GeSi_QCSE_Lever2010_square_nn3_CALCULATION_3'
       my_input_file_no_extension_nnp = r'1D_Ge_GeSi_QCSE_Lever2010_square_nnp_CALCULATION_3'
     # my_input_file_no_extension_nnp = r'1D_Ge_GeSi_QCSE_Lever2010_nnp_CALCULATION_3'
       MQW = 1
       sg_kp = "kp8"

    if sg_kp == 'sg':
       type_of_calculation = " (single-band)"
    elif sg_kp == 'sg_kp6':
       type_of_calculation = " (single-band / 6-band k.p)"
    elif sg_kp == 'kp8':
       type_of_calculation = " (8-band k.p)"

    #===========================
    if(software=="nextnano++"):
        my_input_file_no_extension = my_input_file_no_extension_nnp
    elif(software=="nextnano3"):
        my_input_file_no_extension = my_input_file_no_extension_nn3
    #===========================
    
    FileExtension = '.in'  # for nextnano++ and nextnano3
    
    my_input_file = my_input_file_no_extension+FileExtension
    
    # plt.ion() # interactive mode
    
    print(f"starting nextnano...")
    input_file_name = os.path.join(folder_examples,my_input_file)
    input_file = nn.InputFile(input_file_name)
   
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
               file_psi    = os.path.join(folder_output,input_file_name_variable+r'\bias_00000'+r'\Quantum'+r'\probabilities_shift_quantum_region_Gamma_00000.dat') 
               file_psi_hh = os.path.join(folder_output,input_file_name_variable+r'\bias_00000'+r'\Quantum'+r'\probabilities_shift_quantum_region_HH_00000.dat') 
               file_psi_lh = os.path.join(folder_output,input_file_name_variable+r'\bias_00000'+r'\Quantum'+r'\probabilities_shift_quantum_region_LH_00000.dat') 
            elif sg_kp == 'sg_kp6':
               file_psi    = os.path.join(folder_output,input_file_name_variable+r'\bias_00000'+r'\Quantum'+r'\probabilities_shift_quantum_region_Gamma_00000.dat') 
               file_psi_h  = os.path.join(folder_output,input_file_name_variable+r'\bias_00000'+r'\Quantum'+r'\probabilities_shift_quantum_region_kp6_00000.dat') 
            elif sg_kp == 'kp8':
               file_psi    = os.path.join(folder_output,input_file_name_variable+r'\bias_00000'+r'\Quantum'+r'\probabilities_shift_quantum_region_kp8_00000.dat') 
               file_psi_h  = os.path.join(folder_output,input_file_name_variable+r'\bias_00000'+r'\Quantum'+r'\probabilities_shift_quantum_region_kp8_00000.dat') 
        elif(software=="nextnano3"):
            file_cb  = os.path.join(folder_output,input_file_name_variable+r'\Band_profile'+r'\BandEdges.dat') 
            if sg_kp == 'sg':
               file_psi = os.path.join(folder_output,input_file_name_variable+r'\Quantum_sg'+r'\cb1_sg1_deg1_kSL001_psi_squared_shift.dat') 
               file_psi_hh = os.path.join(folder_output,input_file_name_variable+r'\Quantum_sg'+r'\vb1_sg1_deg1_kSL001_psi_squared_shift.dat') 
               file_psi_lh = os.path.join(folder_output,input_file_name_variable+r'\Quantum_sg'+r'\vb2_sg2_deg1_kSL001_psi_squared_shift.dat') 
               file_abs = os.path.join(folder_output,input_file_name_variable+r'\optics'+r'\absorption_intraband_cb1_sg1_deg1.dat') 
            elif sg_kp == 'sg_kp6':
               file_psi = os.path.join(folder_output,input_file_name_variable+r'\Quantum_sg'+r'\cb1_sg1_deg1_kSL001_psi_squared_shift.dat') 
               file_psi_h = os.path.join(folder_output,input_file_name_variable+r'\Quantum_kp'+r'\kp6_psi_squared_hl_kpar001_1D_per_shift.dat') 
             #  file_abs = os.path.join(folder_output,input_file_name_variable+r'\optics'+r'\absorption_intraband_cb1_kp8.dat') 
            elif sg_kp == 'kp8':
               file_psi = os.path.join(folder_output,input_file_name_variable+r'\Quantum_kp'+r'\kp8_psi_squared_el_kpar001_1D_per_shift.dat') 
               file_psi_h = os.path.join(folder_output,input_file_name_variable+r'\Quantum_kp'+r'\kp8_psi_squared_hl_kpar001_1D_per_shift.dat') 
             # file_abs = os.path.join(folder_output,input_file_name_variable+r'\optics'+r'\absorption_intraband_cb1_kp8.dat') 
    #===========================
    
        #===========================
        # Conduction band edge
        #===========================
        print(f"Read in file:")
        print(file_cb)
        df_cb = nn.DataFile(file_cb,product=software)

        # Electrons
        print(f"Read in file:")
        print(file_psi)
        df_psi = nn.DataFile(file_psi,product=software)

        print(f"Read in file:")
        if nn_file == 0:
           print(file_psi_hh)
           print(file_psi_lh)
           df_psi_hh = nn.DataFile(file_psi_hh,product=software)
           df_psi_lh = nn.DataFile(file_psi_lh,product=software)
        elif nn_file == 1:
           print(file_psi_h)
           df_psi_h = nn.DataFile(file_psi_h,product=software)
        elif nn_file == 2:
           print(file_psi_h)
           df_psi_h = nn.DataFile(file_psi_h,product=software)
    
        print(f"Read in file:")
        if(software=="nextnano3"):
           print(file_abs)
           df_abs = nn.DataFile(file_abs,product=software)
           df_absV.append(df_abs)

        print(f"current datafile: ",file_cb)
        print(f"List of coordinates in the current datafile: {df_cb.coords}")
        print(f"List of variables in the current datafile: {df_cb.variables}")

        print(f"current datafile: ",file_psi)
        print(f"List of coordinates in the current datafile: {df_psi.coords}")
        print(f"List of variables in the current datafile: {df_psi.variables}")
    
        if(software=="nextnano3"):
           print(f"current datafile: ",file_abs)
           print(f"List of coordinates in the current datafile: {df_abs.coords}")
           print(f"List of variables in the current datafile: {df_abs.variables}")


        fig_band, ax_band = plt.subplots(1)
        fig_psi, ax_psi = plt.subplots(1)

        if(software=="nextnano++"):
           ax_band.plot(df_cb.coords['x'].value,df_cb.variables['Gamma'].value,label=SweepVariableString)
           ax_band.plot(df_cb.coords['x'].value,df_cb.variables['L_1'].value,label=SweepVariableString)
           ax_band.plot(df_cb.coords['x'].value,df_cb.variables['X_1'].value,label=SweepVariableString)
           ax_band.plot(df_cb.coords['x'].value,df_cb.variables['X_2'].value,label=SweepVariableString)
           ax_band.plot(df_cb.coords['x'].value,df_cb.variables['electron_Fermi_level'].value,label=SweepVariableString)
           ax_band.plot(df_cb.coords['x'].value,df_cb.variables['HH'].value,label=SweepVariableString)
           ax_band.plot(df_cb.coords['x'].value,df_cb.variables['LH'].value,label=SweepVariableString)
           ax_band.plot(df_cb.coords['x'].value,df_cb.variables['SO'].value,label=SweepVariableString)
        elif(software=="nextnano3"):
           ax_band.plot(df_cb.coords['position'].value,df_cb.variables['Gamma_bandedge'].value,label=SweepVariableString)
           ax_band.plot(df_cb.coords['position'].value,df_cb.variables['L_bandedge'].value,label=SweepVariableString)
           ax_band.plot(df_cb.coords['position'].value,df_cb.variables['X_bandedge_a'].value,label=SweepVariableString)
           ax_band.plot(df_cb.coords['position'].value,df_cb.variables['X_bandedge_b'].value,label=SweepVariableString)
           ax_band.plot(df_cb.coords['position'].value,df_cb.variables['FermiLevel_el'].value,label=SweepVariableString)
           ax_band.plot(df_cb.coords['position'].value,df_cb.variables['hh_bandedge'].value,label=SweepVariableString)
           ax_band.plot(df_cb.coords['position'].value,df_cb.variables['lh_bandedge'].value,label=SweepVariableString)
           ax_band.plot(df_cb.coords['position'].value,df_cb.variables['so_bandedge'].value,label=SweepVariableString)

        ax_band.legend(['$\Gamma$','$L$','$\Delta _a$','$\Delta _b$','$E_F$','$hh$','$lh$','$so$'])

        if(software=="nextnano++"):
           ax_psi.plot(df_cb.coords['x'].value,df_cb.variables['Gamma'].value,label=SweepVariableString)
           ax_psi.plot(df_cb.coords['x'].value,df_cb.variables['L_1'].value,label=SweepVariableString)
           ax_psi.plot(df_cb.coords['x'].value,df_cb.variables['electron_Fermi_level'].value,label=SweepVariableString)
           ax_psi.plot(df_cb.coords['x'].value,df_cb.variables['HH'].value,label=SweepVariableString)
           ax_psi.plot(df_cb.coords['x'].value,df_cb.variables['LH'].value,label=SweepVariableString)
        elif(software=="nextnano3"):
           ax_psi.plot(df_cb.coords['position'].value,df_cb.variables['Gamma_bandedge'].value,label=SweepVariableString)
           ax_psi.plot(df_cb.coords['position'].value,df_cb.variables['L_bandedge'].value,label=SweepVariableString)
           ax_psi.plot(df_cb.coords['position'].value,df_cb.variables['FermiLevel_el'].value,label=SweepVariableString)
           ax_psi.plot(df_cb.coords['position'].value,df_cb.variables['hh_bandedge'].value,label=SweepVariableString)
           ax_psi.plot(df_cb.coords['position'].value,df_cb.variables['lh_bandedge'].value,label=SweepVariableString)

        NameSiGe = r'9 nm Ge/Si$_{0.4}$Ge$_{0.6}$ QW'

        if nn_file == 0:
           NameOfStructure = NameSiGe + type_of_calculation 
           NameOfStructureFile = 'sg' 
           Caption = 'a quantum well'
           if(software=="nextnano++"):
              ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_3'].value,label=SweepVariableString)
              ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_2'].value,label=SweepVariableString)
              ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_1'].value,label=SweepVariableString)

              ax_psi.plot(df_psi_hh.coords['x'].value,df_psi_hh.variables['Psi^2_3'].value,label=SweepVariableString)
              ax_psi.plot(df_psi_hh.coords['x'].value,df_psi_hh.variables['Psi^2_2'].value,label=SweepVariableString)
              ax_psi.plot(df_psi_hh.coords['x'].value,df_psi_hh.variables['Psi^2_1'].value,label=SweepVariableString)
              ax_psi.plot(df_psi_lh.coords['x'].value,df_psi_lh.variables['Psi^2_1'].value,label=SweepVariableString)
           elif(software=="nextnano3"):
              ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_3'].value,label=SweepVariableString)
              ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_2'].value,label=SweepVariableString)
              ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_1'].value,label=SweepVariableString)

              ax_psi.plot(df_psi_hh.coords['position'].value,df_psi_hh.variables['psi^2_3'].value,label=SweepVariableString)
              ax_psi.plot(df_psi_hh.coords['position'].value,df_psi_hh.variables['psi^2_2'].value,label=SweepVariableString)
              ax_psi.plot(df_psi_hh.coords['position'].value,df_psi_hh.variables['psi^2_1'].value,label=SweepVariableString)
              ax_psi.plot(df_psi_lh.coords['position'].value,df_psi_lh.variables['psi^2_1'].value,label=SweepVariableString)

           ax_psi.legend(['$\Gamma$','$L$','$E_F$','$hh$','$lh$','$\psi_3^2$','$\psi_2^2$','$\psi_1^2$'])

        elif nn_file == 1:
           NameOfStructure = NameSiGe + type_of_calculation
           NameOfStructureFile = 'sg_kp6' 
           Caption = 'a quantum well'
           if(software=="nextnano++"):
              ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_3'].value,label=SweepVariableString)
              ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_2'].value,label=SweepVariableString)
              ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_1'].value,label=SweepVariableString)

              ax_psi.plot(df_psi_h.coords['x'].value,df_psi_h.variables['Psi^2_1'].value,label=SweepVariableString)
              ax_psi.plot(df_psi_h.coords['x'].value,df_psi_h.variables['Psi^2_3'].value,label=SweepVariableString)
              ax_psi.plot(df_psi_h.coords['x'].value,df_psi_h.variables['Psi^2_5'].value,label=SweepVariableString)
              ax_psi.plot(df_psi_h.coords['x'].value,df_psi_h.variables['Psi^2_7'].value,label=SweepVariableString)
           elif(software=="nextnano3"):
              ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_3'].value,label=SweepVariableString)
              ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_2'].value,label=SweepVariableString)
              ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_1'].value,label=SweepVariableString)

              ax_psi.plot(df_psi_h.coords['position'].value,df_psi_h.variables['psi^2_1'].value,label=SweepVariableString)
              ax_psi.plot(df_psi_h.coords['position'].value,df_psi_h.variables['psi^2_3'].value,label=SweepVariableString)
              ax_psi.plot(df_psi_h.coords['position'].value,df_psi_h.variables['psi^2_5'].value,label=SweepVariableString)
              ax_psi.plot(df_psi_h.coords['position'].value,df_psi_h.variables['psi^2_7'].value,label=SweepVariableString)

           ax_psi.legend(['$\Gamma$','$L$','$E_F$','$hh$','$lh$','$\psi_3^2$','$\psi_2^2$','$\psi_1^2$'])

        elif nn_file == 2:
           NameOfStructure = NameSiGe + type_of_calculation
           NameOfStructureFile = 'kp8' 
           Caption = 'a quantum well'
           if(software=="nextnano++"):
              ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_25'].value,label=SweepVariableString)
              ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_27'].value,label=SweepVariableString)
              ax_psi.plot(df_psi.coords['x'].value,df_psi.variables['Psi^2_29'].value,label=SweepVariableString)
              ax_psi.plot(df_psi_h.coords['x'].value,df_psi_h.variables['Psi^2_23'].value,label=SweepVariableString)
              ax_psi.plot(df_psi_h.coords['x'].value,df_psi_h.variables['Psi^2_21'].value,label=SweepVariableString)
              ax_psi.plot(df_psi_h.coords['x'].value,df_psi_h.variables['Psi^2_19'].value,label=SweepVariableString)
              ax_psi.plot(df_psi_h.coords['x'].value,df_psi_h.variables['Psi^2_17'].value,label=SweepVariableString)
           elif(software=="nextnano3"):
              ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_5'].value,label=SweepVariableString)
              ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_3'].value,label=SweepVariableString)
              ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_1'].value,label=SweepVariableString)
              ax_psi.plot(df_psi_h.coords['position'].value,df_psi_h.variables['psi^2_1'].value,label=SweepVariableString)
              ax_psi.plot(df_psi_h.coords['position'].value,df_psi_h.variables['psi^2_3'].value,label=SweepVariableString)
              ax_psi.plot(df_psi_h.coords['position'].value,df_psi_h.variables['psi^2_5'].value,label=SweepVariableString)
              ax_psi.plot(df_psi_h.coords['position'].value,df_psi_h.variables['psi^2_7'].value,label=SweepVariableString)

           ax_psi.legend(['$\Gamma$','$L$','$E_F$','$hh$','$lh$','$\psi_5^2$','$\psi_3^2$','$\psi_1^2$'])

        ax_band.set_title(NameOfStructure)
      # ax_band.set_xlabel(f"{df_cb.coords['position'].name} ({df_cb.coords['position'].unit})")
        ax_band.set_xlabel(f"{df_cb.coords[0].name} ({df_cb.coords[0].unit})")
        ax_band.set_ylabel(f"energy ({df_cb.variables[0].unit})")
        fig_band.tight_layout()

        filename_cb = 'cb'+'_'+NameOfStructureFile+'_'+sg_kp+software_short+FigFormat1
        fig_band.savefig(os.path.join(folder_python_output,filename_cb))

        filename_cb = 'cb'+'_'+NameOfStructureFile+'_'+sg_kp+software_short+FigFormat2
        fig_band.savefig(os.path.join(folder_python_output,filename_cb))

        ax_psi.set_title(NameOfStructure)
      # ax_psi.set_xlabel(f"{df_psi.coords['position'].name} ({df_psi.coords['position'].unit})")
        ax_psi.set_xlabel(f"{df_psi.coords[0].name} ({df_psi.coords[0].unit})")
        ax_psi.set_ylabel(f"energy ({df_psi.variables[0].unit})")
        fig_psi.tight_layout()
      # plt.show()

        filename_cb_psi = 'cb_psi'+'_'+NameOfStructureFile+'_'+sg_kp+software_short+FigFormat1
        fig_psi.savefig(os.path.join(folder_python_output,filename_cb_psi))

        filename_cb_psi = 'cb_psi'+'_'+NameOfStructureFile+'_'+sg_kp+software_short+FigFormat2
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


      # sys.exit()
    
    #++++++++++++++++++++++++++++++++++++++++++++++
    # These lines have to be adjusted by the user.  
    # 2D plot
    #++++++++++++++++++++++++++++++++++++++++++++++
        if(software=="nextnano3"):
            if sg_kp == 'sg':
               file = os.path.join(folder_output,input_file_name_variable+r'\optics'+r'\absorption_position_resolved_intraband_cb1_sg1_deg1.vtr') 
            elif sg_kp == 'kp':
               file = os.path.join(folder_output,input_file_name_variable+r'\optics'+r'\absorption_position_resolved_intraband_cb1_kp8.vtr') 
         #  file = os.path.join(folder_output,input_file_name_variable+r'\Results'+r'\LocalDOS_sg1_deg1.vtr')
            datafile_2d = nn.DataFile(file,product=software)
            print(f"current datafile: ",file)
            print(f"List of coordinates in the current datafile: {datafile_2d.coords}")
            print(f"List of variables in the current datafile: {datafile_2d.variables}")
        
            x=datafile_2d.coords['x']
            y=datafile_2d.coords['y']
          # z=datafile_2d.variables['psi_squared']
            z=datafile_2d.variables[0]
    
  #          fig_abs2D, ax_abs2D = plt.subplots(1)
###CHECK:   ax_abs2D.plot(df_cb.coords['position'].value,df_cb.variables[0].value,label=SweepVariableString,
###CHECK:       color='white', linestyle='-')
  #          pcolor = ax_abs2D.pcolormesh(x.value,y.value,z.value.T)
   #         cbar = fig_abs2D.colorbar(pcolor)
      #      cbar.set_label(f"{z.name} ({z.unit})")
    
         #   ax.plot(df_cb.coords['position'].value,df_cb.variables[1].value,color='yellow')
        #    for i in range(2,len(ws)):
        #        ax.plot(df_cb.coords['position'].value,ws[i],color='yellow')
        
    #        ax_abs2D.set_xlabel(f"{df_psi.coords['position'].name} ({df_psi.coords['position'].unit})")
     #       ax_abs2D.set_ylabel(f"photon energy ({df_abs.variables['photon_energy'].unit})")
      #      ax_abs2D.set_title('Absorption of '+NameOfStructure)
        #    fig_abs2D.tight_layout()
          # plt.show()
        #    filename_abs2D = 'absorption2D'+'_'+NameOfStructureFile+'_'+sg_kp+software_short+'.jpg'
       #     fig_abs2D.savefig(os.path.join(folder_python_output,filename_abs2D))

#            file_docu.write(r".. figure:: "+image_path+filename_abs2D+"\n")
 #           file_docu.write(r"   :alt: "+NameOfStructureFile+"\n")
  #          file_docu.write(r"   :align: center"+"\n")
   #         file_docu.write("\n")
    #        file_docu.write(r"   Calculated position resolved absorption :math:`\alpha(x,E)` of "+Caption+"\n")
     #       file_docu.write("\n")
      #      file_docu.write("\n")

        if ( nn_file == 7 or nn_file == 8):

           fig_abs, ax_abs = plt.subplots(1)
           ax_abs.plot(df_absV[nn_file-1].variables['photon_energy'].value,df_absV[nn_file-1].variables['absorption'].value,label=SweepVariableString) # sg
           ax_abs.plot(df_absV[nn_file  ].variables['photon_energy'].value,df_absV[nn_file  ].variables['absorption'].value,label=SweepVariableString) # kp
    
       #   ax.plot(df.coords['position'].value,df.variables['T_1_2'].value,label='Transmission')
       #   ax.plot(df.variables['energy'].value,df.variables['T_1_2'].value,label='Transmission')
       #   ax.plot(df.coords['position'].value,df.variables['FermiLevel_el'].value, label='FermiLevel_el')
       #   ax.plot(df.coords['energy'].value,df.variables['Gamma_bandedge'].value,label='Gamma')
    
         #  ax.set_xlabel(f"{df.coords['position'].name} {df.coords['position'].unit}")
         #  ax.set_ylabel(f"Energy {df.variables['T_1_2'].unit}")
    
           ax_abs.set_xlabel(f"photon energy ({df_abs.variables['photon_energy'].unit})")
           ax_abs.set_ylabel(f"{df_abs.variables['absorption'].name} ({df_abs.variables['absorption'].unit})")
           ax_abs.set_title('Absorption of '+NameOfStructure)
           ax_abs.legend(['single-band','k.p'])
        #   fig_abs.tight_layout()
         # plt.show()
           filename_abs = 'absorption'+'_'+NameOfStructureFile+software_short+'.jpg'
           fig_abs.savefig(os.path.join(folder_python_output,filename_abs))
    

           file_docu.write(r".. figure:: "+image_path+filename_abs+"\n")
           file_docu.write(r"   :alt: "+NameOfStructureFile+"\n")
           file_docu.write(r"   :align: center"+"\n")
           file_docu.write("\n")
           file_docu.write(r"   Calculated absorption :math:`\alpha(E)` of "+Caption+"\n")
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
