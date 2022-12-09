import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt("../data/168.txt", delimiter=",")
plt.plot(data[15:, 1], data[15:, 0])
plt.show()

np.save("../data/met_data.npy", data)
