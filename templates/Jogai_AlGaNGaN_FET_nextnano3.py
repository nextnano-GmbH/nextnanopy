import nextnanopy as nn
from nextnanopy.utils.misc import mkdir_if_not_exist
from nextnanopy.utils.plotting import use_nxt_style, NXT_BLUE, WILD_STRAWBERRY, GREEN
import matplotlib.pyplot as plt
from pathlib import Path
use_nxt_style()

software = 'nextnano3'

folder_examples    = r'C:\Program Files\nextnano\2025_09_18\nextnano3\examples'


input_file_name = r'Jogai_AlGaNGaN_FET_JAP2003_GaNcap_Fig6Fig5_1D_nn3.nn3'
input_file_path = Path(folder_examples) / input_file_name
input_file = nn.InputFile(input_file_path)

input_file.save(temp=True) # save a temporary copy of the input file
input_file_path = input_file.fullpath

sweep_variable = "ThicknessGaNcap"
sweep_values = [1, 3, 7, 12, 20, 30]  # in nm

sweep  = nn.Sweep({sweep_variable: sweep_values}, fullpath=input_file_path)
sweep.save_sweep(integer_only_in_name=True)
sweep.execute_sweep(show_log=False, delete_input_files=True, parallel_limit=3, separate_sweep_dir=False)
sweep_infodict = sweep.sweep_output_infodict

fig_states, axes_states = plt.subplots(2, 3, figsize=(15, 8)) # 2x3 grid of subplots, change if needed

axes_states = axes_states.flatten()  # Flatten to easily iterate over

# plot bandedges and states
for i, (folder_path, var_dict) in enumerate(sweep_infodict.items()):
    var_value = var_dict[sweep_variable]
    dfolder = nn.DataFolder(folder_path)
    bandedges_file = dfolder.go_to("band_structure", "BandEdges.dat")
    band_structure_df = nn.DataFile(bandedges_file, product=software)

    ax = axes_states[i]
    ax.set_title(f'GaN cap thickness: {var_value} nm') 
    # plot band edges and states
    coord = band_structure_df.coords[0].value
    cb = band_structure_df.variables["Gamma_bandedge"].value

    ax.plot(coord, cb, label=f'CB', color=WILD_STRAWBERRY)

    fermi_level = band_structure_df.variables['FermiLevel_el'].value
    ax.plot(coord, fermi_level, linestyle='--', color=GREEN, label='Fermi Level')
    # ax.set_ylim(-0.4, 1.0)
    ax.set_xlabel('Position (nm)')
    ax.set_ylabel('Energy (eV)')
    ax.legend()

fig_states.tight_layout()

plt.show()

