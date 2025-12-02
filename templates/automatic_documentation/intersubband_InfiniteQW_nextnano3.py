import nextnanopy as nn
from nextnanopy.utils.misc import mkdir_if_not_exist
import sys,os
#import numpy as np
import matplotlib.pyplot as plt
from math import pi,exp
from scipy.constants import hbar,Boltzmann,elementary_charge,electron_mass

#import config_nextnano     # This should be your default configuration.
import config_nextnano_temp # This could be a modified configuration file.
# config file is stored in C:\Users\<User>\.nextnanopy-config

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
#software = 'nextnano++'
software = 'nextnano3'
#software = 'nextnano.NEGF'
#software = 'nextnano.MSB'
#===========================

folder_examples_nnp    = r'C:\Program Files\nextnano\2021_12_12\Sample files\nextnano++ sample files'
folder_examples_nn3    = r'C:\Program Files\nextnano\2021_12_12\Sample files\nextnano3 sample files'
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
#folder_examples = folder_python_input

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
file_docu.write(r"The following Python script was used: ``intersubband_InfiniteQW_nextnano3.py``"+"\n")
file_docu.write("\n")
file_docu.write(r"----------------------"+"\n") # horizontal line
file_docu.write("\n")

file_docu.write("\n")
file_docu.write(r"The following figures have been generated using the |nextnano3| software."+"\n")
# Note: The umlaut for Schrödinger is not written correctly!!!
#file_docu.write(r"Self-consistent Schrödinger-Poisson calculations have been performed for three different structures."+"\n")
file_docu.write(r"Self-consistent Schroedinger-Poisson calculations have been performed for an infinite quantum well."+"\n")
file_docu.write("\n")
file_docu.write(r"A single-band effective mass approach has been used, i.e. not |k_dot_p|."+"\n")
file_docu.write("\n")
file_docu.write(r"The absorption has been calculated assuming a parabolic energy dispersion :math:`E(k)`."+"\n")
file_docu.write("\n")
file_docu.write("\n")


for nn_file in range(1):

    print (nn_file)

#   sys.exit()

    #--------------------------------------------------------
    # Specify input file without file extension '.in'/.'xml'
    #--------------------------------------------------------
    #my_input_file_no_extension_nnp = r'Jogai_AlGaNGaN_FET_JAP2003_GaNcap_Fig6Fig5_1D_nnp'
    #my_input_file_no_extension_nn3 = r'Jogai_AlGaNGaN_FET_JAP2003_GaNcap_Fig6Fig5_1D_nn3'
    #my_input_file_no_extension_nn3 = r'2D_CBR_MamaluySabathilJAP2003_AharonovBohm'
    #my_input_file_no_extension_nn3 = r'2D_CBR_square'
    my_input_file_no_extension_nnp = r'1D_IntersubbandAbsorption_InfiniteWell_GaAs_Chuang_sg_nnp'
    my_input_file_no_extension_nn3 = r'1D_IntersubbandAbsorption_InfiniteWell_GaAs_Chuang_sg_nn3'
    my_input_file_no_extension_nnNEGF = r'THz_QCL_GaAs_AlGaAs_Fathololoumi_OptExpress2012_10K-FAST'
    my_input_file_no_extension_nnMSB = r'1D_Transmission_DoubleBarrier_CBR_paper_MSB'
    


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
    

    for OuterSweep in range(2):

        if (OuterSweep == 0):
           #++++++++++++++++++++++++++++++++++++++++++++++
           # Sweep #1
           #++++++++++++++++++++++++++++++++++++++++++++++
           HeadlineSweep = '**Parameter sweep: Well width**'
           CaptionSweep = 'for different well widths'
           SweepExplanation = ( 'The following figure shows the absorption for different **quantum well widths** (Variable: ``$QuantumWellWidth``). '+
                                'The larger the well, the closer the energy level spacings. '+
                                'Therefore the peak occurs at smaller energies. '+
                                'The larger wells show absorption also for transitions other than E\ :sub:`21`.' )
           SweepVariable = 'QuantumWellWidth'
           ListOfValues = [10,13,16,19]
         # ListOfValues = [10] # 10 nm [ChuangOpto1995]
           unitC = 'nm' # It would be better to get the units from (DisplyUnit:nm)
           #++++++++++++++++++++++++++++++++++++++++++++++
        elif (OuterSweep == 1):
           # Set back variable of previous sweep.
           input_file.set_variable(SweepVariable, value=ListOfValues[0], comment='<= PYTHON <= ' + comment_original)

           #++++++++++++++++++++++++++++++++++++++++++++++
           # Sweep #2
           #++++++++++++++++++++++++++++++++++++++++++++++
           HeadlineSweep = '**Parameter sweep: Doping concentration**'
           CaptionSweep = 'for different doping concentrations'        
           SweepExplanation = ( 'The following figure shows the absorption for different **doping concentrations** (Variable: ``$DopingConcentration``). '+
                                'The peak absorption coefficient increases with the doping concentration N\ :sub:`D`.' )
           SweepVariable = 'DopingConcentration'
           ListOfValues = [0.9e18,1.0e18,1.1e18]
           unitC = 'cm^-3' # It would be better to get the units from (DisplyUnit:cm^-3)
           #++++++++++++++++++++++++++++++++++++++++++++++
    
        comment_original = input_file.variables[SweepVariable].comment
        df_absV=[]
        SweepVariableStringV=[]
    
        docuL       = True        
        docu_absL   = True
        docu_sweepL = True
    
        loop = 0   
     
        for x in ListOfValues:
    
          if (OuterSweep == 0):            

              loop = loop + 1
          
              if (loop == 1):
                 docuL       = True
                 docu_absL   = True
              else:
                 docu_absL   = False
          elif (OuterSweep == 1):            
              docuL       = False
              docu_absL   = False

    
          input_file.set_variable(SweepVariable, value=x, comment='<= PYTHON <= ' + comment_original)
    
          for var in input_file.variables.values():
            # print(f'${var.name} = {var.value} ! {var.comment}')
            # print(f'{var.text}') # --> better method to preview
              print(var.text)      # --> better method to preview
        
          SweepVariableCaption = "(" + SweepVariable + " = " + str(x) + " " + unitC + ")"
          SweepVariableString = SweepVariable+'_'+str(x)
          SweepVariableStringV.append(SweepVariableString)
          
    
          input_file_name_variable = my_input_file_no_extension+'_'+SweepVariableString
        
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
                file_cb  = os.path.join(folder_output,input_file_name_variable+r'\bias_000_000'+r'\bandedge_Gamma.dat') 
                file_psi = os.path.join(folder_output,input_file_name_variable+r'\Schroedinger_1band'+r'\cb1_sg1_deg1_psi_squared_shift.dat') 
                file_abs = os.path.join(folder_output,input_file_name_variable+r'\optics'+r'\absorption_intraband_cb1_sg1_deg1.dat') 
            elif(software=="nextnano3"):
                file_cb  = os.path.join(folder_output,input_file_name_variable+r'\band_structure'+r'\BandEdges.dat') 
                file_psi = os.path.join(folder_output,input_file_name_variable+r'\Schroedinger_1band'+r'\cb1_sg1_deg1_psi_squared_shift.dat') 
                file_abs = os.path.join(folder_output,input_file_name_variable+r'\optics'+r'\absorption_intraband_cb1_sg1_deg1.dat') 
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
        
            print(f"Read in file:")
            print(file_abs)
            df_abs = nn.DataFile(file_abs,product=software)
            df_absV.append(df_abs)
    
            print(f"current datafile: ",file_cb)
            print(f"List of coordinates in the current datafile: {df_cb.coords}")
            print(f"List of variables in the current datafile: {df_cb.variables}")
    
            print(f"current datafile: ",file_psi)
            print(f"List of coordinates in the current datafile: {df_psi.coords}")
            print(f"List of variables in the current datafile: {df_psi.variables}")
        
            print(f"current datafile: ",file_abs)
            print(f"List of coordinates in the current datafile: {df_abs.coords}")
            print(f"List of variables in the current datafile: {df_abs.variables}")
        
    
            fig_psi, ax_psi = plt.subplots(1)
    
            NameOfStructure = 'Infinite Quantum Well' 
            NameOfStructureFile = 'InfiniteQuantumWell'
            Caption = 'an infinite quantum well'
            ax_psi.plot(df_cb.coords['position'].value,df_cb.variables['Gamma_bandedge'].value,label=SweepVariableString)
            ax_psi.plot(df_cb.coords['position'].value,df_cb.variables['FermiLevel_el'].value,label=SweepVariableString)
            ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_3'].value,label=SweepVariableString)
            ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_2'].value,label=SweepVariableString)
            ax_psi.plot(df_psi.coords['position'].value,df_psi.variables['psi^2_1'].value,label=SweepVariableString)
            ax_psi.legend(['$E_c$','$E_F$','$\psi_3^2$','$\psi_2^2$','$\psi_1^2$'])
        
            ax_psi.set_title(NameOfStructure+" "+SweepVariableCaption)
            ax_psi.set_xlabel(f"{df_psi.coords['position'].name} ({df_psi.coords['position'].unit})")
            ax_psi.set_ylabel(f"energy ({df_psi.variables[0].unit})")
            axes = plt.gca()
            axes.set_ylim([-0.4,1.0])
            fig_psi.tight_layout()
          # plt.show()
    
            
            #---------------------
            # Write documentation
            #---------------------
            image_path = '/images/nextnanoplus/tutorials/intersubband_InfiniteQW/'
    
            if (docuL):
               filename_cb_psi = 'cb_psi'+'_'+NameOfStructureFile+SweepVariableString+software_short+'.jpg'
               fig_psi.savefig(os.path.join(folder_python_output,filename_cb_psi))
               file_docu.write(r"**"+NameOfStructure+"**"+" "+SweepVariableCaption+"\n")
               file_docu.write("\n")
    
               file_docu.write(r".. figure:: "+image_path+filename_cb_psi+"\n")
               file_docu.write(r"   :alt: "+NameOfStructureFile+"\n")
               file_docu.write(r"   :align: center"+"\n")
               file_docu.write("\n")
               file_docu.write(r"   Conduction band edge, Fermi level and confined electron states of "+Caption +" ")
               file_docu.write(SweepVariableCaption)
               file_docu.write("\n")
               file_docu.write("\n")
    
    
    
            if (docu_absL):
               fig_abs, ax_abs = plt.subplots(1)
               ax_abs.plot(df_abs.variables['photon_energy'].value,df_abs.variables['absorption'].value,label=SweepVariableString)
        
           #   ax.plot(df.coords['position'].value,df.variables['T_1_2'].value,label='Transmission')
           #   ax.plot(df.variables['energy'].value,df.variables['T_1_2'].value,label='Transmission')
           #   ax.plot(df.coords['position'].value,df.variables['FermiLevel_el'].value, label='FermiLevel_el')
           #   ax.plot(df.coords['energy'].value,df.variables['Gamma_bandedge'].value,label='Gamma')
        
             # ax.set_xlabel(f"{df.coords['position'].name} {df.coords['position'].unit}")
             # ax.set_ylabel(f"Energy {df.variables['T_1_2'].unit}")
        
               ax_abs.set_xlabel(f"photon energy ({df_abs.variables['photon_energy'].unit})")
               ax_abs.set_ylabel(f"{df_abs.variables['absorption'].name} ({df_abs.variables['absorption'].unit})")
               ax_abs.set_title('Absorption of '+NameOfStructure+" "+SweepVariableCaption)
               ax_abs.legend(['Absorption'])
               fig_abs.tight_layout()
             # plt.show()
        
               filename_abs = 'absorption'+'_'+NameOfStructureFile+SweepVariableString+software_short+'.jpg'
               fig_abs.savefig(os.path.join(folder_python_output,filename_abs))
               file_docu.write(r".. figure:: "+image_path+filename_abs+"\n")
               file_docu.write(r"   :alt: "+NameOfStructureFile+"\n")
               file_docu.write(r"   :align: center"+"\n")
               file_docu.write("\n")
               file_docu.write(r"   Calculated absorption :math:`\alpha(E)` of "+Caption +" ")
               file_docu.write(SweepVariableCaption)
               file_docu.write("\n")
               file_docu.write("\n")
        
        #++++++++++++++++++++++++++++++++++++++++++++++
        # These lines have to be adjusted by the user.  
        # 2D plot
        #++++++++++++++++++++++++++++++++++++++++++++++
            if(software=="nextnano3"):
             #  file = os.path.join(folder_output,input_file_name_variable+r'\Schroedinger_1band'+r'\2Dcb1_qc1_sg1_deg1_psi_squared_ev001.fld') 
                file = os.path.join(folder_output,input_file_name_variable+r'\optics'+r'\absorption_position_resolved_intraband_cb1_sg1_deg1.vtr') 
             #  file = os.path.join(folder_output,input_file_name_variable+r'\Results'+r'\LocalDOS_sg1_deg1.vtr')
                datafile_2d = nn.DataFile(file,product=software)
                print(f"current datafile: ",file)
                print(f"List of coordinates in the current datafile: {datafile_2d.coords}")
                print(f"List of variables in the current datafile: {datafile_2d.variables}")
            
                x=datafile_2d.coords['x']
                y=datafile_2d.coords['y']
              # z=datafile_2d.variables['psi_squared']
                z=datafile_2d.variables[0]
        
                fig_abs2D, ax_abs2D = plt.subplots(1)
    ###CHECK:   ax_abs2D.plot(df_cb.coords['position'].value,df_cb.variables[0].value,label=SweepVariableString,
    ###CHECK:       color='white', linestyle='-')
                pcolor = ax_abs2D.pcolormesh(x.value,y.value,z.value.T)
                cbar = fig_abs2D.colorbar(pcolor)
                cbar.set_label(f"{z.name} ({z.unit})")
        
             #   ax.plot(df_cb.coords['position'].value,df_cb.variables[1].value,color='yellow')
            #    for i in range(2,len(ws)):
            #        ax.plot(df_cb.coords['position'].value,ws[i],color='yellow')
            
                ax_abs2D.set_xlabel(f"{df_psi.coords['position'].name} ({df_psi.coords['position'].unit})")
                ax_abs2D.set_ylabel(f"photon energy ({df_abs.variables['photon_energy'].unit})")
                ax_abs2D.set_title('Absorption of '+NameOfStructure+" "+SweepVariableCaption)
                fig_abs2D.tight_layout()
              # plt.show()
    
                if (docuL):
                   filename_abs2D = 'absorption2D'+'_'+NameOfStructureFile+SweepVariableString+software_short+'.jpg'
                   fig_abs2D.savefig(os.path.join(folder_python_output,filename_abs2D))
                   file_docu.write(r".. figure:: "+image_path+filename_abs2D+"\n")
                   file_docu.write(r"   :alt: "+NameOfStructureFile+"\n")
                   file_docu.write(r"   :align: center"+"\n")
                   file_docu.write("\n")
                   file_docu.write(r"   Calculated position resolved absorption :math:`\alpha(x,E)` of "+Caption +" ")
                   file_docu.write(SweepVariableCaption)
                   file_docu.write("\n")
                   file_docu.write("\n")
    
        docuL = True
    
        fig, ax = plt.subplots(1)
    
        for i,j in zip(df_absV,SweepVariableStringV):
            ax.plot(i.variables[0].value,i.variables[1].value,label=j)
    
        ax.set_xlabel(f"photon energy ({df_abs.variables['photon_energy'].unit})")
        ax.set_ylabel(f"{df_abs.variables['absorption'].name} ({df_abs.variables['absorption'].unit})")
        ax.set_title('Absorption of '+NameOfStructure)
        ax.legend()
        fig.tight_layout()
        #plt.show()
    
        if (docu_sweepL):
           filename_abs_sweep = 'absorption'+'_'+NameOfStructureFile+'_sweep_'+SweepVariable+software_short+'.jpg'
           fig.savefig(os.path.join(folder_python_output,filename_abs_sweep))
           file_docu.write("\n")
           file_docu.write(HeadlineSweep+"\n")
           file_docu.write("\n")
           file_docu.write(SweepExplanation+"\n")
           file_docu.write("\n")
           file_docu.write(r".. figure:: "+image_path+filename_abs_sweep+"\n")
           file_docu.write(r"   :alt: "+NameOfStructureFile+"\n")
           file_docu.write(r"   :align: center"+"\n")
           file_docu.write("\n")
           file_docu.write(r"   Calculated absorption :math:`\alpha(E)` of "+Caption +" ")
           file_docu.write(CaptionSweep)
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

mass_electron_GaAs = 0.0665 # Chuang
#temperature = 298.15 # K
temperature = 300 # K # Chuang
kBT = temperature * Boltzmann / elementary_charge # eV
print(kBT,' eV')  

m0_by_pi_hbar2_eV = electron_mass / (pi * hbar**2 / elementary_charge )    # m0 / (pi hbar^2) = 

print(m0_by_pi_hbar2_eV,' eV^-1 m^-2 ( = 4.177 10^18 eV^-1 m^-2)')  

N = 1e18 * 1e6   #  doping cm^-3 => m^-3  Chuang
Lz = 10e-9 # 10 nm Chuang

N_s = mass_electron_GaAs * m0_by_pi_hbar2_eV * kBT   # Chuang
E_F_minus_E_1 = kBT * ( exp(N * Lz / N_s) - 1 )

print(E_F_minus_E_1 * 1e-3, ' meV (Chuang: 78 meV)')
print(N_s * 1e-11 * 1e-4 ,' 10^11 cm^-2; Chuang: 7.19 * 10^11 cm^-2')  
   
print(f'=====================================')  
print(f'Done nextnanopy.')  
print(f'=====================================')  
