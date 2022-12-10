from scipy import linalg
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import itertools


def plot_elipses(means, covariances, ax):
    color_iter = itertools.cycle(["navy", "c", "cornflowerblue", "gold", "darkorange"])
    for i, (mean, covar, color) in enumerate(zip(means, covariances, color_iter)):
        v, w = linalg.eigh(covar) #type:ignore
        v = 2.0 * np.sqrt(2.0) * np.sqrt(v)
        u = w[0] / linalg.norm(w[0]) #type:ignore

        angle = np.arctan(u[1] / u[0])
        angle = 180.0 * angle / np.pi  # convert to degrees
        ell = mpl.patches.Ellipse(mean, v[0], v[1], angle=180.0 + angle, color=color) #type:ignore
        ell.set_clip_box(ax.bbox)
        ell.set_alpha(0.1)
        ax.add_artist(ell)

def plot_mean_estimation(mean, std, ax, label=None):
    if label is not None:
        ax.plot(mean[0], 0, "o", color="red", markersize=5, label = "estimation")
    else:
        ax.plot(mean[0], 0, "o", color="red", markersize=5, label = label)
    ax.plot([mean[0]+std[0][0], mean[0] - std[0][0]],[0,0], color="b", linewidth=5, alpha=0.5, label="std")
