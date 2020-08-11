import numpy as np
import pandas as pd
import os
from psrqpy import QueryATNF

from utmost_psr import utils, plot

def UTMOST_NS_module_params():
    """
    System parameters for a single UTMOST-2D North-South module.

    output:
    -------
    UTMOST_NS_module: dict
        Dictionary containing module parameters (Gain [K/Jy], Bandwidth [MHz],
        Freq [MHz], T_sys [K], N_pol, Latitude [deg])
    """

    UTMOST_NS_module = {
        "Gain": 0.0028,
        "Bandwidth": 45.0,
        "Freq": "843 MHz",
        "T_sys": 70.0,
        "N_pol": 2.0,
        "Latitude": -35.3707088333
        }

    return UTMOST_NS_module


def radiometer_signal_to_noise(obs_params, flux_density, period, width,
    psr_Tsky, t_int=300.0):
    """
    Predicted signal to noise ratio from the radiometer equation: see Equation
    A1.21 in Kramer & Lorimer (2004).

    input:
    ------
    obs_params: dict
        Dictionary containing observatory parameters (Gain [K/Jy],
        Bandwidth [MHz], Freq [MHz], T_sys [K], N_pol)
    flux_density: list, floats
        Pulsar flux_density [Jy]
    period: list, floats
        Pulsar period [s]
    width: list, floats
        Pulsar width -- W50 [s]
    psr_Tsky: list, floats
        Sky temperature at pulsar positions (K)
    t_int: float, optional
        Observation length in seconds (default = 300 seconds)

    output:
    -------
    snr: float
        Radiometer signal to noise ratio
    """

    # System Equivalent Flux Density: Gain / T_sys
    sefd = obs_params["Gain"] / (obs_params["T_sys"] + psr_Tsky)

    # Pulsar duty cycle
    duty_cycle = np.sqrt((period - width)/width)

    # Signal to noise ratio
    snr = flux_density * sefd * np.sqrt(obs_params["N_pol"] *
        t_int * obs_params["Bandwidth"]*1e6) * duty_cycle

    return snr


def Zenith_angle_correction(psr_DECJ, Latitude):
    """
    Corrects the detected pulsar S/N based on the pulsar distance from zenith.

    input:
    ------
    psr_DECJ: float
        Declination of the pulsar in fractional degrees.
    Latitude: float
        Latitude of the telescope in fractional degrees.

    output:
    ------
    zenith_corrected_snr: float
        S/N correction for distance from zenith.
    """

    zenith_corrected_snr = np.cos((psr_DECJ - Latitude) * np.pi/180.)

    return zenith_corrected_snr


def ddmmss_to_deg(position):
    """
    Converts positions in deg:min:sec format to fractional degrees.

    input:
    ------
    position: str
        Position in deg:min:sec format.

    output:
    -------
    position_deg: float
        Position in fractional degrees.
    """

    split_position = position.split(":")

    # Check if positive or negative:
    if float(split_position[0]) <= 0:
        if len(split_position) == 3:
            position_deg = float(split_position[0]) - (
                float(split_position[1])/60. + float(split_position[2])/3600.)
        else:
            position_deg = float(split_position[0]) - (
                float(split_position[1])/60.)
    else:
        if len(split_position) == 3:
            position_deg = float(split_position[0]) + (
                float(split_position[1])/60. + float(split_position[2])/3600.)
        else:
            position_deg = float(split_position[0]) + (
                float(split_position[1])/60.)

    return position_deg


def arrival_time_uncertainty(obs_params, flux_density, period, width, psr_DECJ,
    n_cassette, t_int=300.):
    """
    Predicted pulse time of arrival (ToA) uncertainty: see see Equation 8.2 in
    Kramer & Lorimer (2004).

    input:
    ------
    obs_params: dict
        Dictionary containing observatory parameters (Gain [K/Jy],
        Bandwidth [MHz], Freq [MHz], T_sys [K], N_pol)
    flux_density: list, floats
        Pulsar flux_density [Jy]
    period: list, floats
        Pulsar period [s]
    width: list, floats
        Pulsar width -- W50 [s]
    psr_DECJ: list, floats
        Pulsar declination [deg]
    n_cassette: scalar, optional
        Number of UTMOST-NS cassettes (default = 1)
    t_int: float, optional
        Observation length in seconds (default = 300 seconds)

    output:
    -------
    sigma_toa: list, floats
        Estimated ToA uncertainty (us)
    """

    # System Equivalent Flux Density: Gain / T_sys
    sefd = obs_params["Gain"] / obs_params["T_sys"] * n_cassette

    # Pulsar duty cycle
    duty_cycle = np.sqrt((period - width)/width)

    snr_corr = Zenith_angle_correction(psr_DECJ, obs_params["Latitude"])

    sigma_toa = (width/flux_density) * (1/(sefd)*snr_corr) * (1/np.sqrt(
        obs_params["N_pol"] * t_int * obs_params["Bandwidth"]*1e6)) * (
        1/duty_cycle)

    return sigma_toa


def get_extrapolated_flux(flux_ref, freq_ref, spectral_index):
    """
    Computes the flux density at 843 MHz extrapolated from a higher/lower flux
    density measurement & some assumed spectral index.

    input:
    ------
    flux_ref: float
        Reference flux density, usually S400 or S1400 [mJy].
    freq_ref: float
        Refrence frequency, usually 400 or 1400 MHz.

    output:
    -------
    S843: float
        Extrapolated flux density at 843 MHz [mJy]
    """

    S843 = flux_ref * (843.0 / freq_ref)**(spectral_index)

    return S843
