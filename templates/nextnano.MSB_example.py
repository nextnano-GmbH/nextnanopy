import nextnanopy as nn
import matplotlib.pyplot as plt
from pathlib import Path
from nextnanopy.utils.plotting import use_nxt_style, NXT_BLUE_COLORMAP, WILD_STRAWBERRY

# optional: set nextnano style for plots
use_nxt_style()

# specify input file
software = 'nextnano.MSB'
folder_examples = r"c:\Program Files\nextnano\2025_09_18\nextnano.MSB\examples"
input_file_name = r"1D_Transmission_DoubleBarrier_CBR_paper.msb"

input_file_path = Path(folder_examples) / input_file_name

# excecute input file
input_file = nn.InputFile(input_file_path)
input_file.execute()

# plot results
output_folder = input_file.folder_output
data_folder = nn.DataFolder(output_folder)

bandedges_file = data_folder.go_to("Source=0V, Drain=0V", "BandProfile", "BandEdge_conduction.dat")
bandedges_df = nn.DataFile(bandedges_file, product=software)

# conduction band edge 
plt.figure()
plt.plot(bandedges_df.coords[0].value, bandedges_df.variables['Conduction Band Edge'].value, label='Conduction Band Edge', color=WILD_STRAWBERRY)
plt.xlabel('Position (nm)')
plt.ylabel('Energy (eV)')
plt.title('Conduction Band Edge Profile')

# local density of states

plt.figure()
ldos_file = data_folder.go_to("Source=0V, Drain=0V", "DOS", "DOS_position_resolved.vtr")
ldos_df = nn.DataFile(ldos_file, product=software)
x = ldos_df.coords['x'].value
y = ldos_df.coords['y'].value
ldos = ldos_df.variables[0].value

plt.pcolormesh(x, y, ldos.T, shading='auto', cmap=NXT_BLUE_COLORMAP)
plt.colorbar(label='LDOS (1/eV cm)')

plt.xlabel('Position (nm)')
plt.ylabel('Energy (eV)')
plt.title('Local Density of States LDOS(x, E)')
plt.plot(bandedges_df.coords[0].value, bandedges_df.variables['Conduction Band Edge'].value, color=WILD_STRAWBERRY, label='Conduction Band Edge')


# plot carrier density

plt.figure()
ldos_file = data_folder.go_to("Source=0V, Drain=0V", "CarrierDensity", "CarrierDensity_energy_resolved.vtr")
ldos_df = nn.DataFile(ldos_file, product=software)
x = ldos_df.coords['x'].value
y = ldos_df.coords['y'].value
density = ldos_df.variables[0].value

plt.pcolormesh(x, y, density.T, shading='auto', cmap=NXT_BLUE_COLORMAP)
plt.colorbar(label='Carrier Density (1e18 $eV^{-1}$ $cm^{-3}$)')

plt.xlabel('Position (nm)')
plt.ylabel('Energy (eV)')
plt.title('Carrier Density n(x, E)')
plt.plot(bandedges_df.coords[0].value, bandedges_df.variables['Conduction Band Edge'].value, color=WILD_STRAWBERRY, label='Conduction Band Edge')


# plot current density
plt.figure()
current_file = data_folder.go_to("Source=0V, Drain=0V", "CurrentDensity", "CurrentDensity_energy_resolved.vtr")
current_df = nn.DataFile(current_file, product=software)
x = current_df.coords['x'].value
y = current_df.coords['y'].value
current = current_df.variables[0].value
plt.pcolormesh(x, y, current.T, shading='auto', cmap=NXT_BLUE_COLORMAP)
plt.colorbar(label='Current Density (A/cm$^2$eV$^{-1}$)')
plt.xlabel('Position (nm)')
plt.ylabel('Energy (eV)')
plt.title('Current Density J(x, E)')
plt.plot(bandedges_df.coords[0].value, bandedges_df.variables['Conduction Band Edge'].value, color=WILD_STRAWBERRY, label='Conduction Band Edge')

plt.show()





