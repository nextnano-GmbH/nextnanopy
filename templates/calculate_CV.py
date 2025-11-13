import nextnanopy as nn
import matplotlib.pyplot as plt
from nextnanopy.postprocess import calculate_CV
import os

this_dir = os.path.dirname(__file__)
input_file_path = os.path.join(this_dir, r'input files\MIS_CV_1nmSiO2_1D_nnp.in')

input_file = nn.InputFile(input_file_path)

input_file.execute()

output_directory = input_file.folder_output

voltage, C_regions = calculate_CV(output_directory_path=output_directory,
                                  bias1='SiContact_bias', bias2='GateContact_bias', net_charge_sign=-1)

for region in C_regions:
    plt.plot(voltage, region)

plt.xlabel('Voltage at GateContact (V)')
plt.ylabel(r'Capacitance ($\mu F/cm ^{2}$)')
plt.show()
