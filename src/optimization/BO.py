import math
import os
from telnetlib import GA
from tkinter import E
from tokenize import Single
from pandas import Interval
import torch
from botorch.models import SingleTaskGP, FixedNoiseGP
from botorch.fit import fit_gpytorch_model
from gpytorch.mlls import ExactMarginalLogLikelihood
from botorch.acquisition import ExpectedImprovement, qExpectedImprovement, qNoisyExpectedImprovement
from botorch.acquisition.analytic import ProbabilityOfImprovement
from gpytorch.likelihoods import GaussianLikelihood
from botorch.sampling import IIDNormalSampler

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
    def __init__(self, n_parms:int = 1, range: np.ndarray = np.array([0,1]), noise_range :np.ndarray = np.array([0.005, 10]), acq: str = "ei",
        Kernel: str = "SE", model_save_path : str = "", device : str = "cpu" , plot: bool = False) -> None:
        """Main Bayesian Optimization class

        Args:
            n_parms (int, optional): Number of parameters to be optimized. Defaults to 1.
            range (np.ndarray, optional): (lower and upper) In shape (2xn_parms). Defaults to np.array([0,1]).
            noise_range (np.ndarray, optional): (lower and upper) In shape (2xn_parms). Defaults to np.array([0.005,10]).
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

        # Noise constraints
        self._noise_constraints = noise_range 
        self.likelihood = GaussianLikelihood(Interval(self._noise_constraints[0], self._noise_constraints[1]))

        # number of sampling in the acquisition points
        self.N_POINTS = 200

        # acquisition function type
        self.acq_type = acq

        


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
        mll = ExactMarginalLogLikelihood(self.likelihood, self.model)
        fit_gpytorch_model(mll) # check I need to change anything

        if self.acq_type == "ei":
            ei = qNoisyExpectedImprovement(self.model, self.x, sampler=IIDNormalSampler(self.N_POINTS, see = 1234))

        else:
            # TODO add other acquisition functions
            # identify the best x 
            pi = ProbabilityOfImprovement(self.model, self.xc, sampler=IIDNormalSampler(self.N_POINTS, see = 1234))
            pass
        new_point, value 

        

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

        # TODO check the dimension of the input variables.

        self.x = torch.tensor(x).to(self.device)
        self.y = torch.tensor(y).to(self.device)

        if not reload_hyper:
            self.kernel.reset()
            self.likelihood = GaussianLikelihood(noise_constraint = Interval(self._noise_constraints[0], self._noise_constraints[1]))
            self.model = SingleTaskGP(self.x, self.y, likelihood = self.likelihood, covar_module = self.kernel.get_covr_module()) # TODO check if this ok for multi dimension models
            self.model.to(self.device)

        else:
            # keeping the likehood save and kernel parameters so no need to reset those
            self.model = SingleTaskGP(self.x, self.y, likelihood = self.likelihood, covar_module = self.kernel.get_covr_module())
            self.model.to(self.device)

        # fi the model and get the next parameter.
        new_parameter = self._step()
        


