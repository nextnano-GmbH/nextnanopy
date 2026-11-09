import os
import nextnanopy as nn

print(f'The nextnanopy config file is stored in: {nn.config.fullpath}')

#++++++++++++++++++++++++++++++++++++++++++++++++++
# Specify your license folder
#++++++++++++++++++++++++++++++++++++++++++++++++++
path_license         = r"C:\Users\homer.simpson\Documents\nextnano\License"

#++++++++++++++++++++++++++++++++++++++++++++++++++
# Specify your output folder
#++++++++++++++++++++++++++++++++++++++++++++++++++
path_nextnano_output = r"C:\Users\homer.simpson\Documents\nextnano\Output"            

#++++++++++++++++++++++++++++++++++++++++++++++++++
# Specify your nextnano installation folder
#++++++++++++++++++++++++++++++++++++++++++++++++++
path_nextnano        = r"C:\Program Files\nextnano\2026_07_03"           # nextnano++, nextnano3, nextnano.NEGF and nextnano.MSB software            


# NO NEED TO CHANGE THE FOLLOWING -----------------------------

nn.config.to_default() # initialize to default values
#---------------------------
# Location of output folder
#---------------------------
nn.config.set('nextnano++'   , 'outputdirectory', path_nextnano_output)
nn.config.set('nextnano3'    , 'outputdirectory', path_nextnano_output)
nn.config.set('nextnano.NEGF', 'outputdirectory', path_nextnano_output)
nn.config.set('nextnano.MSB' , 'outputdirectory', path_nextnano_output)

#---------------------------
# Location of license files
#---------------------------
nn.config.set('nextnano++'   , 'license', os.path.join(path_license, r'License_nnp.lic'))
nn.config.set('nextnano3'    , 'license', os.path.join(path_license, r'License_nnp.lic'))
nn.config.set('nextnano.MSB' , 'license', os.path.join(path_license, r'License_nnp.lic'))
nn.config.set('nextnano.NEGF', 'license', os.path.join(path_license, r'License_nnNEGF.lic'))
nn.config.set('nextnano optimizers', 'license', os.path.join(path_license, r'License_nnopti.lic'))

#----------------------------------------------------------
# Location of nextnano++ files:    executable and database
#----------------------------------------------------------
nn.config.set('nextnano++', 'exe'     , os.path.join(path_nextnano, r'nextnano++\bin\nextnano++_Intel_64bit.exe'))
nn.config.set('nextnano++', 'database', os.path.join(path_nextnano, r'nextnano++\database\database.nnp'))

#----------------------------------------------------------
# Location of nextnano3 files:     executable and database
#----------------------------------------------------------
nn.config.set('nextnano3', 'exe'     , os.path.join(path_nextnano, r'nextnano3\bin\nextnano3_Intel_ifx.exe'))
nn.config.set('nextnano3', 'database', os.path.join(path_nextnano, r'nextnano3\database\database.nn3'))

#----------------------------------------------------------
# Location of nextnano.NEGF files: executable and database
#----------------------------------------------------------
nn.config.set('nextnano.NEGF', 'exe'     , os.path.join(path_nextnano, r'nextnano.NEGF\bin\nextnano.NEGF_win.exe'))
nn.config.set('nextnano.NEGF', 'database', os.path.join(path_nextnano, r'nextnano.NEGF\database\Material_Database.negf'))

#----------------------------------------------------------
# Location of nextnano.MSB files: executable and database
#----------------------------------------------------------
nn.config.set('nextnano.MSB', 'database', os.path.join(path_nextnano, r'nextnano.MSB\database\materials.msb'))
nn.config.set('nextnano.MSB', 'exe'     , os.path.join(path_nextnano, r'nextnano.MSB\bin\nextnano.MSB_Intel.exe'))
nn.config.save() # save modifications

print("The nextnanopy config file has been updated and saved.")
