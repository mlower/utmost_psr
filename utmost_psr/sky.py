import numpy as np
import os


def init():
    """
    Read in the Haslam et al. (2004) sky temperature map from an ASCII file.

    output:
    -------
    Tsky_map: numpy array
        Array containing the coarse resolution sky temperature map in galactic
        longitude & latitude (K).
    """

    table = os.path.join(os.path.join(os.path.dirname(__file__), "data"),
        "tsky1.ascii")

    data = np.loadtxt(fname=table, dtype="float")
    Tsky_map = np.reshape(data, (180, 360)) * 0.1

    return Tsky_map

# Get tsky at a particular l,b pair using array returned by tsky_init
def get_temperature(Gl, Gb, Tsky_map):
    """
    Get sky temperature at a partciular Gl & Gb.

    input:
    ------
    Gl: float
        Input galactic longitude (deg)
    Gb: float
        Input galatic latitude (deg)

    output:
    -------
    T_sky: float
        Sky temperature at the input Gl & Gb (K).
    """
    i = np.int(Gl+0.5)
    if (i>359):
        i = 359
    j = np.int(Gb+90.5)
    if (j>179):
        j = 179

    T_sky = Tsky_map[j,i]

    return T_sky
