import nextnanopy as nn
from nextnanopy.utils.misc import mkdir_if_not_exist
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

software = 'nextnano++'


folder_examples_nnp    = Path(r'C:\Program Files\nextnano\2025_09_18\nextnano++\examples')

input_file_name = r'LaserDiode_InGaAs_1D_qm_nnp.nnp'

input_file_path = folder_examples_nnp / input_file_name

# create a temp copy
input_file = nn.InputFile(input_file_path)
bias_steps = 10 # you can decrease number of bias steps for quick testing

input_file.set_variable("BIAS_STEPS", bias_steps) 
input_file.save(temp=True) # save a temporary copy of the input file
input_file.execute()

output_folder_path = Path(input_file.folder_output)

bias_folder_list = [f"bias_{i:05d}" for i in range(0, bias_steps+1)] # list ["bias_00000", "bias_00001", ..., "bias_00010"]

bias_list = [i/(bias_steps) for i in range(bias_steps+1)] # list of bias values [0.0, ..., 1.0] in V

for bias_folder, bias in zip(bias_folder_list, bias_list):
    bandedges_file = output_folder_path / bias_folder / "bandedges.dat"
    bandedges_df = nn.DataFile(bandedges_file, product=software)

    # densities are 2D files
    el_density_file = output_folder_path / bias_folder / "electron_density_vs_energy.fld"
    el_density_df = nn.DataFile(el_density_file, product=software)

    hole_density_file = output_folder_path / bias_folder / "hole_density_vs_energy.fld"
    hole_density_df = nn.DataFile(hole_density_file, product=software)

    # plot electron density
    fig, ax = plt.subplots(1)
    x=el_density_df.coords['x']
    y=el_density_df.coords['y']
    el_density=el_density_df.variables[0]
    
    pcolor = ax.pcolormesh(x.value,y.value,el_density.value.T)
    fig.colorbar(pcolor, ax=ax, label='Electron Density (cm$^{-3}$eV$^{-1}$)')
    ax.set_title(f'Electron Density at Bias={bias} V')

    ax.plot(bandedges_df.coords[0].value,bandedges_df.variables[0].value, color='white', linestyle='-')
    ax.plot(bandedges_df.coords[0].value,bandedges_df.variables[1].value, color='white', linestyle='-')
    ax.plot(bandedges_df.coords[0].value,bandedges_df.variables[4].value, color='red',  linestyle='dotted', linewidth=1.8)
    ax.plot(bandedges_df.coords[0].value,bandedges_df.variables[5].value, color='green',  linestyle='dotted', linewidth=1.8)

    # fill background with 0 density when undefined
    cmap = plt.cm.viridis
    ax.set_facecolor(cmap(0.0))

    # plot hole density
    fig, ax = plt.subplots(1)
    x=hole_density_df.coords['x']
    y=hole_density_df.coords['y']
    hole_density=hole_density_df.variables[0]
    
    pcolor = ax.pcolormesh(x.value,y.value,hole_density.value.T)
    fig.colorbar(pcolor, ax=ax, label='Hole Density (cm$^{-3}$eV$^{-1}$)')
    ax.set_title(f'Hole Density at Bias={bias} V')

    ax.plot(bandedges_df.coords[0].value,bandedges_df.variables[0].value, color='white', linestyle='-')
    ax.plot(bandedges_df.coords[0].value,bandedges_df.variables[1].value, color='white', linestyle='-')
    ax.plot(bandedges_df.coords[0].value,bandedges_df.variables[4].value, color='red',  linestyle='dotted', linewidth=1.8)
    ax.plot(bandedges_df.coords[0].value,bandedges_df.variables[5].value, color='green',  linestyle='dotted', linewidth=1.8)

    # fill background with 0 density when undefined
    cmap = plt.cm.viridis
    ax.set_facecolor(cmap(0.0))

    # plot el + hole density

    fig, ax = plt.subplots(1)
    pcolor = ax.pcolormesh(x.value,y.value,hole_density.value.T)
    fig.colorbar(pcolor, ax=ax, label='Electron and hole densities (cm$^{-3}$eV$^{-1}$)')
    ax.set_title(f'Hole and Electron Density for bias={bias} V')

    ax.plot(bandedges_df.coords[0].value,bandedges_df.variables[0].value, color='white', linestyle='-')
    ax.plot(bandedges_df.coords[0].value,bandedges_df.variables[1].value, color='white', linestyle='-')
    ax.plot(bandedges_df.coords[0].value,bandedges_df.variables[4].value, color='red',  linestyle='dotted', linewidth=1.8)
    ax.plot(bandedges_df.coords[0].value,bandedges_df.variables[5].value, color='green',  linestyle='dotted', linewidth=1.8)

    # fill background with 0 density when undefined
    cmap = plt.cm.viridis
    ax.set_facecolor(cmap(0.0))
plt.show()


