import numpy as np
import nextnanopy as nn
import matplotlib.pyplot as plt
import math

def kkr_deltan(w, delta_alpha, cshift=1e-1):
    """Calculate the Kramers-Kronig transformation on variation of absorption to get variation of refractive index

    Doesn't correct for any artefacts resulting from finite window function.

    Args:
        w (np.array): the frequency grid, should be in rad/s!!

        eps_imag (np.array): A numpy array with dimensions (n), containing
            the imaginary part of the dielectric tensor.
        cshift (float, optional): The implemented method includes a small
            complex shift. A larger value causes a slight smoothing of the
            dielectric function.

    Returns:
        A numpy array with dimensions (n, 3, 3) containing the real part of the
        dielectric function.
    """
    delta_alpha = np.array(delta_alpha)
    cshift = complex(0, cshift)
    de = w[1] - w[0]
    # use cm/s, because alpha is in cm^-1
    c = 299792458 * 100  # speed of light in cm/s

    def integration_element(w_r):
        factor = 1 / (w**2 - w_r**2 + cshift)
        total = np.sum(delta_alpha * factor, axis=0)
        return (
            total * (c / math.pi) * de
        )  # no + 1, because we are looking at the variation of the refractive index

    return np.real([integration_element(w_r) for w_r in w])

def get_delta_alpha_energy_grid(FOLDER_PATH):
    """
    Get the variation of absorption coefficient from a folder with multiple bias folders
    0 bias is the reference
    """
    dfolder = nn.DataFolder(FOLDER_PATH)
    alpha_list = []
    for folder in dfolder.folders:
        if folder.name.startswith("bias"):
            filepath_list = folder.find_multiple(
                ["absorption", "TEy", "eV"], deep=True
            )
            if not filepath_list:
                raise ValueError("No eV file found in this folder")
            else:
                alpha_list.append(nn.DataFile(filepath_list[0], product='nextnano++'))
    delta_alpha_list = []
    coord = alpha_list[0].coords[0].value
    coord = 241.8*coord # convert from eV to THz
    alpha_base = alpha_list[0].variables[0].value
    for alpha in alpha_list[1:]:
        alpha_val = alpha.variables[0].value
        delta_alpha = alpha_val - alpha_base
        delta_alpha_list.append(delta_alpha)
    return coord, delta_alpha_list

# CHANGE THE OUTPUT FOLDER PATH TO YOUR SIMULATION FOLDER
output_folder = r"C:\Users\Heorhii\Documents\nextnano\Output\1D_Ge_GeSi_QCSE_Kuo2005_simplified_8kp_nnp_exciton"
coord, delta_alpha_list = get_delta_alpha_energy_grid(output_folder)

coord_angular = coord * 1e12 * 2 * np.pi  # in ra/s

delta_n_list = [
    kkr_deltan(coord_angular, delta_alpha) for delta_alpha in delta_alpha_list
]

coord_nm = 299792.458 / coord

bias_list = [1, 2, 3, 4]
bias_list_plot = [0, 1, 2, 3, 4]
wavelength_list = [1475, 1487, 1502, 1517]

closest_wavelength_list = []

plt.figure(figsize=(12, 8))

for wavelength in wavelength_list:
    # find the closest value in the coord_nm list
    idx_wavelength = np.argmin(np.abs(coord_nm - wavelength))

    closest_wavelength = coord_nm[idx_wavelength]
    closest_wavelength_list.append(closest_wavelength)
    delta_n = [0]
    for i, bias in enumerate(bias_list):
        delta_n.append(
            -delta_n_list[i][idx_wavelength]
        )  # minus because the sign is flipped
    plt.plot(bias_list_plot, delta_n, marker="o", label=f"{closest_wavelength:.1f} nm")

plt.xlabel("Bias (V)", fontsize=18)
plt.ylabel("Variation of refractive index", fontsize=22)
plt.grid()
plt.legend(fontsize=18)
# tick fontsize to 12
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.show()
