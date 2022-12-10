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




# loading the sample data
# This data should be in shape of (time, met)
met_data = np.load("../data/met_data.npy")


# estimated metabolic cost
steady_state_estimation_mean = []
steady_state_estimation_std = []
steady_state_time = []
ax_list = []
fig, ax = plt.subplots(2,1, figsize=(20, 10))
# estimating the metabolic cost
for i in tqdm(range(15, met_data.shape[0])):
    met = met_data[:i, 0]
    time = met_data[:i, 1]


    # Estimating the metabolic cost
    # you can change the upsampling parameter to get a better estimation
    ppe = PPE()
    mean, std = ppe.estimate(met, time)
    # print(mean, std)

    # Done with the estimation not plotting the results
    # Need to find a better way to do this, but for now this is fine.
    steady_state_estimation_mean.append(mean)
    steady_state_estimation_std.append(std)
    steady_state_time.append(time[-1])

    # comment out plotting if you don't want to plot the results or speed up the estimation process.
    # Phase plane plotting.
    ax[0].plot(ppe.phase_plane[:, 0], ppe.phase_plane[:, 1], label="phase plane") #type:ignore
    plot_elipses(ppe.gmm.means_, ppe.gmm.covariances_, ax[0]) #type:ignore
    plot_mean_estimation(mean, std, ax[0], label = "estimated mean")
    ax[0].set_xlabel("Metabolic cost (W)")
    ax[0].set_ylabel("d(Metabolic cost) (W)")

    # Plotting the metabolic cost
    ax[1].plot(time, met, label="metabolic cost")
    ax[1].plot(steady_state_time, steady_state_estimation_mean, label="estimated mean")
    ax[1].set_ylabel("Metabolic cost (W)")
    ax[1].set_xlabel("Time (s)")

    # legend
    ax[0].legend()
    ax[1].legend()

    # This is to record the video
    canvas = FigureCanvas(fig)
    canvas.draw()       # draw the canvas, cache the renderer
    image = np.frombuffer(canvas.tostring_rgb(), dtype='uint8') #type:ignore
    image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    ax_list.append(image)

    # not clearing the last plot
    if i == met_data.shape[0] - 1:
        break
    ax[0].cla()
    ax[1].cla()

plt.savefig("Results/figures/metabolic_cost_estimation.png")

plt.close("all")
writer = imageio.get_writer('Results/videos/metabolic_cost_estimation.mp4', fps=20)

for im in ax_list:
    writer.append_data(im)
writer.close()

# saving it as gif
imageio.mimsave('Results/videos/metabolic_cost_estimation.gif', ax_list, fps=20)




