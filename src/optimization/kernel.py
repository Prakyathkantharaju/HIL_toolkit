import torch
import gpytorch
from gpytorch.kernels import ScaleKernel, RBFKernel, LinearKernel, MaternKernel
from gpytorch.constraints import GreaterThan, Interval
from gpytorch.likelihoods import GaussianLikelihood

# Typing
import numpy.typing as npt
from typing import Any

from abc import abstractmethod, ABC

DEVICE = torch.device("cpu")


class kernel(ABC):
    def __init__(self) -> None:
        """
        Parent class for kernels
        """
        pass
    @abstractmethod 
    def get_covr_module(self) -> Any:
        raise NotImplementedError


class SE(kernel):
    def __init__(self, length_scale : tuple[int, ...] = (0, 10), variance_constraints: tuple[int, ...] = (0, 10) )-> None :
        """
        SE kernel
        parms:
            length_scale: tuple[int, int] = (0, 10) length scale constraints
            variance_constraints: tuple[int, int] = (0, 10) variance_constraints
        Call
        SE.get_covr_module() to get the covar_module
        """
        super().__init__()
        self.length_scale_constraints = Interval(length_scale[0], length_scale[1]) #type: ignore
        self.variance_constraints = Interval(variance_constraints[0], variance_constraints[1]) #type: ignore
        self.covar_module = ScaleKernel(RBFKernel(lengthscale_constraint= self.length_scale_constraints) + LinearKernel())

    def get_covr_module(self) -> Any:
        """
        returns the covar_module
        """
        return self.covar_module
    

class Matern(kernel):
    def __init__(self, length_scale : tuple[int, ...] = (0, 10), variance_constraints: tuple[int, ...] = (0, 10) )-> None :
        """
        SE kernel
        parms:
            length_scale: tuple[int, int] = (0, 10) length scale constraints
            variance_constraints: tuple[int, int] = (0, 10) variance_constraints
        Call
        SE.get_covr_module() to get the covar_module
        """
        super().__init__()
        self.length_scale_constraints = Interval(length_scale[0], length_scale[1]) #type: ignore
        self.variance_constraints = Interval(variance_constraints[0], variance_constraints[1]) #type: ignore
        self.covar_module = ScaleKernel(RBFKernel(lengthscale_constraint= self.length_scale_constraints) + LinearKernel())

    def get_covr_module(self) -> Any:
        """
        returns the covar_module
        """
        return self.covar_module

