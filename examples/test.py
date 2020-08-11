import numpy as np
import pandas as pd
import sys
import utmost_psr

names = np.genfromtxt("../utmost_psr/psr_timing_list.txt", dtype=str).tolist()
psr_df = utmost_psr.extract.get_psr_params(names)

P0 = np.array([float(i) for i in psr_df["P0"].values])
RAJ = np.array(psr_df["RAJ"].values)
DECJ = np.array(psr_df["DECJ"].values)
GL = np.array(psr_df["GL"].values)
GB = np.array(psr_df["GB"].values)
Fluxes = np.array([float(i) for i in psr_df["Flux"].values])/1e3
W50 = np.array([float(i) for i in psr_df["W50"].values])/360. * P0

T_sky_map = utmost_psr.sky.init()

psr_Tsky = np.array([])
dec_fix = np.array([])
for i in range(0,len(names)):
    psr_Tsky = np.append(psr_Tsky, utmost_psr.sky.get_temperature(GL[i], GB[i],
    T_sky_map))
    dec_fix = np.append(dec_fix, utmost_psr.functions.ddmmss_to_deg(DECJ[i]))

NS_params = utmost_psr.functions.UTMOST_NS_module_params()

SNR = utmost_psr.functions.radiometer_signal_to_noise(NS_params, Fluxes, P0,
    W50, psr_Tsky)

SNR_5min = SNR * utmost_psr.functions.Zenith_angle_correction(dec_fix,
    NS_params["Latitude"])

utmost_psr.plot.period_vs_flux(P0, SNR_5min, Fluxes)

sigma_toa = utmost_psr.functions.arrival_time_uncertainty(NS_params, Fluxes, P0,
    W50, dec_fix, 66.)

utmost_psr.plot.period_vs_toa(P0, sigma_toa, 66)
