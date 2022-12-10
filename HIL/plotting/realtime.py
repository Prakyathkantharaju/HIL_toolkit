from abc import ABC, abstractmethod
from typing import List

import matplotlib.pyplot as plt
import numpy as np
# This file will have plotting functions that are used in the HIL toolbox.
# Main abstract class for plotting
class Plotting(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def _create_figure(self):
        pass

    @abstractmethod
    def update_plot(self):
        pass

    #TODO remove the box and unwanted axis from the plot


# 1d optimization
class Optimization1D(Plotting):
    def __init__(self, x_range: List[int], n_parms : int, title: List[str], xlabel: List[str], 
                ylabel: List[str]) -> None:
        self.x_range = np.linspace(x_range[0], x_range[1], n_parms)
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self._create_figure()

    def _create_figure(self) -> None:
        self.fig, self.ax = plt.subplots(2, 1, figsize=(20, 10))
        self._post_update()

    def _post_update(self) -> None:
        self.ax[0].set_title(self.title[0])
        self.ax[0].set_xlabel(self.xlabel[0])
        self.ax[0].set_ylabel(self.ylabel[0])
        self.ax[1].set_title(self.title[1])
        self.ax[1].set_xlabel(self.xlabel[1])
        self.ax[1].set_ylabel(self.ylabel[1])
        plt.pause(0.001)

    def update_plot(self, GP_mean: np.ndarray, GP_std: np.ndarray, x_points: np.ndarray, y_points: np.ndarray,
                    acq_function: List[float], best_function_pos: int) -> None:
        # GP plotting
        self.ax[0].plot(self.x_range, GP_mean, label="GP mean")
        self.ax[0].fill_between(self.x_range, GP_mean + GP_std ,  GP_mean -  GP_std  , alpha=0.5, a) #type:ignore
        self.ax[0].scatter(x_points, y_points, s = 5,c='r', label="points")
        self.ax[0].legend()

        # Acquisition function plotting
        self.ax[1].plot(self.x_range, acq_function, label="acq function")
        self.ax[1].scatter(best_function_pos, acq_function[best_function_pos], s = 5,c='r', label="best function")
        self.ax[1].legend()

        # Post update
        self._post_update()

        return None 



# 2d optimization
class Optimization2D(Plotting):
    def __init__(self, x_range: List[int], y_range: List[int], n_parms : int, title: List[str], xlabel: List[str],
                ylabel: List[str]) -> None:
        self.x_range = np.linspace(x_range[0], x_range[1], n_parms)
        self.y_range = np.linspace(y_range[0], y_range[1], n_parms)
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self._create_figure()

    def _create_figure(self) -> None:
        self.fig, self.ax = plt.subplots(2, 1, figsize=(20, 10))
        self._post_update()

    def _post_update(self) -> None:
        self.ax[0].set_title(self.title[0])
        self.ax[0].set_xlabel(self.xlabel[0])
        self.ax[0].set_ylabel(self.ylabel[0])
        self.ax[1].set_title(self.title[1])
        self.ax[1].set_xlabel(self.xlabel[1])
        self.ax[1].set_ylabel(self.ylabel[1])
        plt.pause(0.001)

    def update_plot(self, GP_mean: np.ndarray, GP_std: np.ndarray, x_points: np.ndarray, y_points: np.ndarray, z_points: np.ndarray,
                    acq_function: List[float], best_function_pos: List[int]) -> None:
        # GP plotting
        self.ax[0].plot_surface(self.x_range, self.y_range, GP_mean, label="GP mean") #type:ignore
        # TODO: std
        # self.ax[0].fill_between(self.x_range, GP_mean + GP_std ,  GP_mean -  GP_std  , alpha=0.5, a)
        self.ax[0].scatter(x_points, y_points, z_point ,ms = 5, c='r', label="points") #type:ignore

        # Acquisition function plotting
        self.ax[1].plot_surface(self.x_range, self.y_range, acq_function, label="acq function") #type:ignore
        self.ax[1].scatter(best_function_pos[0], best_function_pos[1], 
                acq_function[best_function_pos[0], best_function_pos[1]], ms = 5, c='r', label="best function") #type:ignore

        # Post update
        self._post_update()


# Metabolic cost estimation



# ECG estimation



