"""Defines colors and styles for nextnano plots."""
from matplotlib.colors import LinearSegmentedColormap

NXT_BLUE = (19/256, 173/256, 181/256) #13adb5 
WILD_STRAWBERRY = (255/256, 41/256, 103/256) #ff2966
GREEN = (0/256, 155/256, 85/256) #009b55
DANDELION = (240/256, 200/256, 0) #f0c800

GOLDEN = (253/256, 188/256, 66/256) #fdbc42, not part of palette anymore, substituted by dandelion

_NXT_COLORS = [
    (1, 1, 1),  # white
    NXT_BLUE,
    (0, 0, 0),  # black
    WILD_STRAWBERRY,
    (1, 1, 1),  # white
]

_NXT_BLUE_COLORS = [
    (0, 0, 0),  # black
    NXT_BLUE,
    (1, 1, 1),  # white
]

_NXT_STRAWBERRY_COLORS = [
    (0, 0, 0),  # black
    WILD_STRAWBERRY,
    (1, 1, 1),  # white
]

NXT_COLORMAP = LinearSegmentedColormap.from_list("NXT", _NXT_COLORS, N=1042)
NXT_BLUE_COLORMAP = LinearSegmentedColormap.from_list("NXT_BLUE", _NXT_BLUE_COLORS, N=1042)
NXT_STRAWBERRY_COLORMAP = LinearSegmentedColormap.from_list("NXT_STRAWBERRY", _NXT_STRAWBERRY_COLORS, N=1042)

import matplotlib.pyplot as plt
import importlib.resources as pkg_resources

def use_nxt_style():
    with pkg_resources.path("nextnanopy.utils.styles", "nxt_style.mplstyle") as style_path:
        plt.style.use(style_path)