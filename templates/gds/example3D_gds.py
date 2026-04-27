import os
import nextnanopy as nn
from nextnanopy.nnp.shapes import GdsPolygons
from nextnanopy.nnp.assistants import InputAssistant
import matplotlib.pyplot as plt
import numpy as np
plt.ion()

def find_line_by_pattern(_str, lines):
    for i, line in enumerate(lines):
        if _str in line:
            return i
    raise ValueError(f'{_str} is not in the input file')


input_template = nn.InputFile(r'example3D_gds.nnp')

raw_lines = list(input_template.lines)

# Here gates
gdspols = GdsPolygons(r'example3.gds')
gdspols.labels = ['up', 'down']
if True:
    fig, ax = plt.subplots(1)
    gdspols.show(ax=ax)

f = InputAssistant()  # Helper for generating text for nextnano++ input files
zi = 0  # nm, gate initial z
zf = 50  # nm, gate final z
pols = gdspols.get_polygonal_prisms(zi, zf)  # get the polygonal_prisms text

# Generate the region block with the contact name and the material
gate_regions = []
for name, pol in zip(gdspols.labels, pols):
    text = f.region_block(
        f.region_contact(name=name),
        f.region_binary(name='GaAs'),
        pol.text,
    )
    lines = list(f.split_lines(text))
    gate_regions.extend(lines)

# Insert regions into the input file
idx = find_line_by_pattern('GATES-REGION', raw_lines)
raw_lines = raw_lines[0:idx + 1] + gate_regions + raw_lines[idx + 1:]

# Generate the contact block with the contact name and the material
contacts = []
for name in gdspols.labels:
    text = f.contacts_schottky(name=name, bias=0, barrier=0.75)
    lines = list(f.split_lines(text))
    contacts.extend(lines)

# Insert contacts into the input file
idx = find_line_by_pattern('GATES-CONTACT', raw_lines)
raw_lines = raw_lines[0:idx + 1] + contacts + raw_lines[idx + 1:]

text = f.lines(*raw_lines)
new_input = nn.InputFile()
new_input.text = text
new_input.fullpath = os.path.join(os.getcwd(), 'example3D_with_gds.nnp')  # save at current working directory
new_input.product = "nextnano++"
new_input.save(overwrite=True)
new_input.execute()

# Quick plot
bias_folder = os.path.join(new_input.folder_output, 'bias_00000')# use 'bias_000_000_000' instead for older versions
bandedge = os.path.join(bias_folder, 'bandedges_2d_rectangle_z_40.fld')
df = nn.DataFile(bandedge, product='nextnano++')
x, y, z = df['x'], df['y'], df['Gamma']
xv, yv, zv = x.value, y.value, z.value

fig, ax = plt.subplots(1)
pcolor = ax.pcolormesh(x.value, y.value, z.value.T, cmap='viridis')
ax.set_xlabel(x.label)
ax.set_ylabel(y.label)
if True:  # Add gds polygons on top of the plot
    gdspols.show(ax=ax, fill_kw=dict(color='r', alpha=0.2), onebyone=False)
fig.savefig(os.path.join(bias_folder, 'bandedges_2d_rectangle_z_40.png'))