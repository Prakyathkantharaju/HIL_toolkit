import numpy as np
import matplotlib.pyplot as plt

# HIL toolbox import
from HIL.cost_processing.metabolic_cost.ppe import PPE


# loading the sample data
# This data should be in shape of (time, met)
met_data = np.load("data/met_data.npy")


# estimated metabolic cost

steady_state_estimation_mean = []
steady_state_estimation_std = []
steady_state_time = []
# estimating the metabolic cost
for time, met in met_data:
    ppe = PPE()
    mean, std = ppe.estimate(met, time)
    steady_state_estimation_mean.append(mean)
    steady_state_estimation_std.append(std)

    steady_state_time.append(time)

# plotting the results
plt.plot(met_data[:, 0], met_data[:,1], label="raw metabolic data", alpha = 0.5)
plt.plot(steady_state_time, steady_state_estimation_mean, label="steady state mean")
plt.show()

