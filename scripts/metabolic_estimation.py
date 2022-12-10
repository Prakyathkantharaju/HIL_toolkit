import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import imageio
import scipy.stats as stats
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from scipy import linalg
from tqdm import tqdm
import itertools

# HIL toolbox import
from HIL.cost_processing.metabolic_cost.ppe import PPE

# HIL plotting utils
from HIL.plotting.utils import plot_elipses, plot_mean_estimation

# plotting ellipses
# from gmr import plot_error_ellipse

# def plot_elipses(means, covariances, ax):
#     color_iter = itertools.cycle(["navy", "c", "cornflowerblue", "gold", "darkorange"])
#     for i, (mean, covar, color) in enumerate(zip(means, covariances, color_iter)):
#         v, w = linalg.eigh(covar) #type:ignore
#         v = 2.0 * np.sqrt(2.0) * np.sqrt(v)
#         u = w[0] / linalg.norm(w[0]) #type:ignore

#         angle = np.arctan(u[1] / u[0])
#         angle = 180.0 * angle / np.pi  # convert to degrees
#         ell = mpl.patches.Ellipse(mean, v[0], v[1], angle=180.0 + angle, color=color) #type:ignore
#         ell.set_clip_box(ax.bbox)
#         ell.set_alpha(0.1)
#         ax.add_artist(ell)

# def plot_mean_estimation(mean, std, ax):
#     ax.plot(mean[0], 0, "o", color="red", markersize=5)
#     ax.plot([mean[0] + 3 *std[0][0], mean[0] - 3*std[0][0]],[0,0], color="b", linewidth=5, alpha=0.5)




# loading the sample data
# This data should be in shape of (time, met)
met_data = np.load("../data/met_data.npy")


# estimated metabolic cost
steady_state_estimation_mean = []
steady_state_estimation_std = []
steady_state_time = []
ax_list = []

# estimating the metabolic cost
for i in tqdm(range(10, met_data.shape[0])):
    met = met_data[:i, 0]
    time = met_data[:i, 1]

    ppe = PPE()
    mean, std = ppe.estimate(met, time)
    # print(mean, std)
    steady_state_estimation_mean.append(mean)
    steady_state_estimation_std.append(std)
    steady_state_time.append(time[-1])
    fig, ax = plt.subplots()
    ax.plot(ppe.phase_plane[:, 0], ppe.phase_plane[:, 1], label="phase plane") #type:ignore
    plot_elipses(ppe.gmm.means_, ppe.gmm.covariances_, ax) #type:ignore
    plot_mean_estimation(mean, std, ax)
    plt.xlabel("Metabolic cost (W)")
    plt.ylabel("d(Metabolic cost) (W)")
    canvas = FigureCanvas(fig)
    canvas.draw()       # draw the canvas, cache the renderer

    image = np.frombuffer(canvas.tostring_rgb(), dtype='uint8') #type:ignore
    image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    ax_list.append(image)


plt.close("all")
# # plotting the results
# plt.figure()
# plt.plot(met_data[:, 1], met_data[:,0], label="raw metabolic data", alpha = 0.5)
# plt.plot(steady_state_time, steady_state_estimation_mean, label="steady state mean")
# plt.show()
writer = imageio.get_writer('test.mp4', fps=20)

for im in ax_list:
    writer.append_data(im)
writer.close()





