import numpy as np
import os
import matplotlib
if "DISPLAY" not in os.environ:
    # set a rendering backend that does not require an X server
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cmasher as cmr


def get_rc_params():
    """
    Get the rcParams that will be used in all the plots.
    Run: plt.rcParams.update(get_rc_params())
    """

    rc_params = {
        "text.usetex": True,
        "font.family": "serif",

        "figure.dpi": 125,
        "legend.fontsize": 12,
        "legend.frameon": True,
        "legend.markerscale": 1.0,
        "lines.markersize": 3.0,

        "axes.labelsize": 14,

        "xtick.direction": 'in',
        "xtick.labelsize": 14,
        "xtick.minor.visible": True,
        "xtick.top": True,
        "xtick.major.width": 1,

        "ytick.direction": 'in',
        "ytick.labelsize": 14,
        "ytick.minor.visible": True,
        "ytick.right": True,
        "ytick.major.width": 1,
    }

    return rc_params


def period_vs_flux(period, snr, flux_density, thresh=10.):
    """
    Plot of pulse preriod vs. pulsar flux density at 843 MHz.

    input:
    ------
    period: list, floats
        Pulsar spin periods (s)
    snr: list, floats
        Pulsar S/N
    flux_density: list, floats
        Pulsar flux densities at 843 MHz (mJy)
    thresh: float, optional
        Threshold S/N (default = 10)
    """

    snr_6_cassette = snr * 6
    snr_36_cassette = snr * 6 * 6
    snr_66_cassette = snr * 6 * 12

    thresh_1 = np.argwhere(snr > thresh)
    thresh_6 = np.argwhere(snr_6_cassette > thresh)
    thresh_36 = np.argwhere(snr_36_cassette > thresh)
    thresh_66 = np.argwhere(snr_66_cassette > thresh)

    colours = cmr.take_cmap_colors("cmr.chroma_r", 4, (0.2, 0.85),
        return_hex=True)

    plt.rcParams.update(get_rc_params())

    plt.figure(figsize=(7,7))
    plt.loglog(period, flux_density, "+", color="tab:grey")

    plt.loglog(period[thresh_66], flux_density[thresh_66], "o",
        color=colours[3], label="66 Cassettes")

    plt.loglog(period[thresh_36], flux_density[thresh_36], "o",
        color=colours[2], label="36 Cassettes")

    plt.loglog(period[thresh_6], flux_density[thresh_6], "o", color=colours[1],
        label="6 Cassettes")

    plt.loglog(period[thresh_1], flux_density[thresh_1], "o", color=colours[0],
        label="1 Cassette")

    plt.xlabel("Period (s)")
    plt.ylabel("Flux density (mJy)")

    plt.legend(loc="best", fontsize=8)
    plt.tight_layout()
    plt.savefig("Period_vs_flux.png", dpi=150)
    plt.show()
    plt.close()


def period_vs_toa(period, sigma_toa, n_cassette=1.):
    """
    Plot of pulse preriod vs. predicted pulse time of arrival uncertainty.

    input:
    ------
    period: list, floats
        Pulsar spin periods (s)
    sigma_toa: list, floats
        Predicted time of arrival uncertainty (s)
    n_cassette: float, optional
        Number of North-South cassettess (default = 1)
    """

    plt.rcParams.update(get_rc_params())

    plt.figure(figsize=(7,7))
    plt.loglog(period, sigma_toa, "x", color="tab:blue")
    plt.axhline(1e-3, color="k", ls="--")
    plt.text(0.0015, 2e-3, r"$\sigma_{\rm ToA}$ = 1 ms")

    plt.xlabel("Period (s)")
    plt.ylabel(r"Predicted $\sigma_{\rm ToA}$ for "+str(n_cassette)+" cassettes"
        )

    plt.tight_layout()
    plt.savefig("Period_vs_toa.png", dpi=150)
    plt.show()
    plt.close()
