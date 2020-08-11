import numpy as np
import pandas as pd
import os
from psrqpy import QueryATNF

from utmost_psr import utils, plot, functions


def get_psr_params(psr_names, spectral_index=-1.8, data_dir="Jankowski2019"):
    """
    ...

    input:
    ------
    psr_names: list, str
        Names of pulsars to extract parameters for (J2000)
    spectral_index: float, optional
        Standard pulsar spectral index [Default = -1.8]
    data_dir: str, optional
        Directory in which input flux/width data resides.

    output:
    -------
    psr_params: dict
        Dictionary of pulsar parameters (JNAME, DECJ [deg], P0 [s], Flux [mJy],
        W50 [deg])
    """

    # Check if pulsar parameters have already been extracted. Return if true.
    if os.path.exists(os.path.join(
        os.path.join(os.path.dirname(__file__), "data"), "psr_params.csv")
        ) == True:

        filename = os.path.join(os.path.join(os.path.dirname(__file__), "data"),
        "psr_params.csv")

        return pd.read_csv(filename)

    # Import pulsar fluxes & widths from Jankowski et al. (2019) table:
    if data_dir == "Jankowski2019":
        data_dir = os.path.join(os.path.dirname(__file__), "Jankowski2019")

    filename = os.path.join(data_dir, "fluxwidths_table_C1.csv")
    Jankowski_table = pd.read_csv(filename, delimiter=";")

    # Get pulsar DECJ + remaning fluxes & W50 values from psrcat:
    psr_params = ["JNAME" ,"RAJ", "DECJ", "P0", "S400", "S1400", "W50"]
    query = QueryATNF(psrs=psr_names, params=psr_params)

    # Get fluxes & widths:
    p0 = []
    decj = []
    flux = []
    w50 = []
    for PSR in psr_names:

        # Fluxes & widths for pulsars with known S843 values
        if PSR in Jankowski_table["PSRJ"].values:
            # Retrieve P0 & DECJ from psrcat query:
            query_position = np.argwhere(query["JNAME"] == PSR)[0][0]
            p0.append(query["P0"][query_position])
            decj.append(query["DECJ"][query_position])

            # Find pulsar position in Table & append values to arrays:
            tab_position = np.argwhere(
                Jankowski_table["PSRJ"].values == PSR)[0][0]
            flux.append(Jankowski_table["S843"].values[tab_position])
            w50.append(Jankowski_table["W50"].values[tab_position])

        # Get fluxes & widths from psrcat S400 & S1400 values
        elif PSR in query["JNAME"]:
            # Retrieve DECJ from psrcat query:
            query_position = np.argwhere(query["JNAME"] == PSR)[0][0]
            p0.append(query["P0"][query_position])
            decj.append(query["DECJ"][query_position])

            # Retreive S843 scaled from either S400 or S1400
            S400 = query["S400"][query_position]
            S1400 = query["S1400"][query_position]

            if S1400 != "--":
                flux.append(functions.get_extrapolated_flux(S1400, 1400.0,
                    spectral_index))
            elif S1400 == "--":
                flux.append(functions.get_extrapolated_flux(S400, 400.0,
                    spectral_index))
            else:
                flux.append(np.nan)

            w50.append(query["W50"][query_position])

        else:
            # Set NaNs for pulsars not in Jankowski et al. (2019) & psrcat
            p0.append(np.nan)
            decj.append(np.nan)
            flux.append(np.nan)
            w50.append(np.nan)

    # Input params to pandas DataFrame
    psr_params = pd.DataFrame({
        "JNAME": psr_names,
        "P0": p0,
        "DECJ": decj,
        "Flux": flux,
        "W50": w50
        })

    # Save pandas DataFrame as .csv file
    out_filename = os.path.join(os.path.join(os.path.dirname(__file__), "data"),
    "psr_params.csv")

    psr_params.to_csv(out_filename, sep=",", encoding='utf-8')

    return psr_params
