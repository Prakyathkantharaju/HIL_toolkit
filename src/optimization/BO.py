import math
import os
import torch
import botorch.models import SingleTaskGP, FixedNoiseGP
from botorch.fit import fit_gpytorch_model
from gpytorch.mlls import ExactMarginalLogLikelihood
from botorch.acquisition import ExpectedImprovement, qExpectedImprovement, qNoisyExpectedImprovement
from gpytorch.likelihoods import GaussianLikelihood

#TODO install the application to have realteive imports
# local imports
from src.optimization.kernel import SE, Matern 

import numpy as np

# utils
import logging
from typing import Any, Optional

    




class BayesianOptimization(object):
    """
    Bayesian Optimization class for HIL
    """
    def __init__(self, n_parms:int = 1, range: np.ndarray = np.array([0,1]), 
        Kernel: str = "SE", model_save_path : str = "", device : str = "cpu" , plot: bool = False) -> None:
        """Main Bayesian Optimization class

        Args:
            n_parms (int, optional): Number of parameters to be optimized. Defaults to 1.
            range (np.ndarray, optional): (lower and upper) In shape (2xn_parms). Defaults to np.array([0,1]).
            Kernel (str, optional): string to choose from SE or Matern. Defaults to "SE".
            model_save_path (str, optional): Path to save the file, defaults to data folder. Defaults to "".
            device (str, optional): pytorch device. Defaults to "cpu".
        """
        if Kernel == "SE":
            self.kernel = SE()
            self.covar_module = self.kernel.get_covar_module()

        else:
            self.kernel = Matern()
            self.covar_module = self.kernel.get_covar_module()
        
        self.n_parms = n_parms
        self.range = range 
        
        if len(model_save_path):
            self.model_save_path = model_save_path
        else:
            # this is temp
            self.model_save_path = "data/"

        self.likelihood = GaussianLikelihood()

        # place holder for model
        self.model = None

        # place to store the parameters
        self.x = torch.tensor([])
        self.y = torch.tensor([])

        # device 
        self.device = device

        # plotting
        self.plot - plot

        # logging
        self.logger = logging.getLogger()


    def _step(self) -> np.ndarray:
        """ Fit the model and identify the next parameter, also plots the model if plot is true

        Returns:
            np.ndarray: Next parameter to sampled
        """

        parameter = self._fit()
        new_parameter = parameter.detach().cpu().numpy()

        self.logger.info(f"Next parameter is {new_parameter}")

        self._save_model()

        return new_parameter

    #TODO Fill out and test the BO optimization 
    def _fit(self) -> torch.tensor:
        pass

    def _save_model(self) -> None:
        pass

    def _plot(self) -> None:
        pass

    def run(self, x: np.ndarray, y: np.ndarray, reload_hyper: bool  = True ) -> np.ndarray:
        """Run the optimization with input data points

        Args:
            x (NxM np.ndarray): Input parameters N -> n_parms, M -> iter
            y (Mx1): Cost function array
            reload_hyper (bool, optional): Reload the hyper parameter trained in the previous iter. Defaults to True.

        Returns:
            np.ndarray: parameter to sample next
        """
        pass

