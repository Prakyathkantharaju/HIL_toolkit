import math
import os
import torch
import botorch.models import SingleTaskGP, FixedNoiseGP
from botorch.fit import fit_gpytorch_model
from gpytorch.mlls import ExactMarginalLogLikelihood
from botorch.acquisition import ExpectedImprovement, qExpectedImprovement, qNoisyExpectedImprovement

        


    




class BayesianOptimization(object):
    """
    Bayesian Optimization class for HIL
    """
    def __init__(self, n_parms:int = 1, range: npt.NDArray, Kernel: ) -> None:
        pass


