# This file is for metabolic estimation using ppe
from typing import Tuple, Any
import numpy as np
import scipy.signal as signal
import neurokit2 as nk
import pylsl
import abc
from scipy import linalg

# Gaussian mixture model specific imports
from sklearn.mixture import BayesianGaussianMixture
from gmr import GMM
from gmr.utils import check_random_state


# TODO: put this in the utils ?
class Inlet:
    def __init__(self, info: pylsl.StreamInfo, data_length: int) -> None:
        self.inlet = pylsl.StreamInlet(info, max_buflen= data_length, 
            processing_flags=pylsl.proc_clocksync | pylsl.proc_dejitter)

        self.name = info.name()
        self.channel_count = info.channel_count()
        self.new_data = False
        self.store_data = np.array([])

    @abc.abstractclassmethod
    def get_data(self) -> None:
        raise NotImplementedError

    @abc.abstractclassmethod
    def send_data(self) -> None:
        raise NotImplementedError


class MetInlet(Inlet):
    def __init__(self, info: pylsl.StreamInfo, data_length: int) -> None:
        super().__init__(info, data_length)




# Only estimation class
class PPE(object):
    def __init__(self, upsample_number: int = 20, cutoff: float = 0.01, GMM_filter:bool = True) -> None:
        self.UPSAMPLE = upsample_number
        self.HIGHCUT = cutoff
        self.MAX_ITER = 1000
        self.N_COMPONENTS = 5
        self.FILTER = GMM_filter


        self._raw_met = np.array([])
        self._raw_time = np.array([])
        self._filtered_met = np.array([])

    @property
    def phase_plane(self) -> np.ndarray:
        assert self._phase_plane is not None, "phase plane is not calculated yet"
        return self._phase_plane

    @property
    def gmm(self) -> Any:
        assert self._gmm is not None, "gmm is not calculated yet"
        return self._gmm
    
    @property
    def means(self) -> np.ndarray:
        assert self._means is not None, "means is not calculated yet"
        return self._means

    @property
    def covariances(self) -> np.ndarray:
        assert self._covariances is not None, "covariances is not calculated yet"
        return self._covariances

    def estimate(self, raw_met: np.ndarray, raw_time: np.ndarray, estimate: bool = True) -> Tuple[float, float]:
        # slightly differnt from the paper, performs better
        # Upsample data
        up_sampled = self._up_sample(raw_met, raw_time)

        # perform filter
        filtered_data = self._filter_data(up_sampled)

        # convert to phase plane
        phase_plane = self._get_phase_plane(filtered_data)

        # updated phase plane
        self._phase_plane = phase_plane

        if not estimate:
            return 0,0

        # estimte the prediction with mean and std of the prediction
        mean, cov = self._estimate_steady_state(phase_plane) #ignore 

        assert len(mean) == 1, "mean is not one, check gmm prediction"
        assert len(cov) == 1, "mean is not one, check gmm prediction"

        # std
        std = np.sqrt(cov)

        return mean,std


    def _up_sample(self, raw_met : np.ndarray, raw_time: np.ndarray) -> np.ndarray:
        up_sample = signal.resample(raw_met, int(raw_time[-1]) * self.UPSAMPLE)
        return up_sample #type:ignore


    def _filter_data(self, up_sampled:np.ndarray) -> np.ndarray:
        # Filtering is performed thoroug
        filter_data = nk.signal_filter(up_sampled, sampling_rate = self.UPSAMPLE, highcut=self.HIGHCUT, show=False)
        return filter_data

    def _get_phase_plane(self, filtred_data: np.ndarray) -> np.ndarray:

        # N-1 x 2
        phase_plane = np.zeros((len(filtred_data) - 1, 2))

        # x_axis
        phase_plane[:,0] = filtred_data[1:]

        # y_axis
        phase_plane[:,1] = np.diff(filtred_data)

        return phase_plane

    def _post_processing(self, bgmm) -> Tuple[Any, Any, Any]:
        # filters the mean and covaraince to avoid negative values, which is part of phase plane which does not contribute to the estimation.

        weights = bgmm.weights_
        means = bgmm.means_
        covariances = bgmm.covariances_
        # print("covariances: ", covariances.shape)
        filtered_means = []
        filtered_covariances = []
        filtered_weights = []
        for i, (mean, covar, weight) in enumerate(zip(means, covariances, weights)):
            v, w = linalg.eigh(covar) #type:ignore
            v = 2.0 * np.sqrt(2.0) * np.sqrt(v)
            u = w[0] / linalg.norm(w[0]) #type:ignore
            angle = np.arctan(u[1] / u[0])
            angle = 180.0 * angle / np.pi  # convert to degrees
            if angle < 0:
                continue
            else:
                filtered_means.append(mean)
                filtered_covariances.append(covar)
                filtered_weights.append(weight)

        # the data is too small, so we just use the original means and covariances
        if len(filtered_means) == 0:
            filtered_means = means
            filtered_covariances = covariances
            filtered_weights = weights
        else:
            # convert to numpy array
            filtered_means = np.array(filtered_means)
            filtered_covariances = np.array(filtered_covariances)
            filtered_weights = np.array(filtered_weights)
            # print("filtered means: ", filtered_means.shape)
            # print("filtered covariances: ", filtered_covariances.shape)
            # print("filtered weights: ", filtered_weights.shape)
        return filtered_means, filtered_covariances, filtered_weights


    def _estimate_steady_state(self, phase_plane: np.ndarray) -> Tuple[Any, Any]:

        # Fit the BGMM and the GMR
        random_state = check_random_state(0)
        bgmm = BayesianGaussianMixture(n_components=self.N_COMPONENTS, max_iter= self.MAX_ITER, init_params='kmeans').fit(phase_plane)
        # print(bgmm.weights_)

        if self.FILTER:
            # Post processing
            filtered_means, filtered_covariances, filtered_weights = self._post_processing(bgmm)
        else:
            filtered_means = bgmm.means_
            filtered_covariances = bgmm.covariances_
            filtered_weights = bgmm.weights_

        # store the means and covariances
        self._means = filtered_means
        self._covariances = filtered_covariances

        gmm = GMM(n_components= len(filtered_weights), 
                priors=filtered_weights,
                means=filtered_means,
                covariances=filtered_covariances,
                random_state=random_state)
        self._gmm = bgmm

        
        # Regression
        conditional_gmm = gmm.condition([1], np.array([0])) # [1] -> because conditioning along y axis, 0 because the prediction is on x axis 

        # converting to single  distribution
        conditional_mvn = conditional_gmm.to_mvn()

        # store conditional multi variant normal
        self._conditional_mvn = conditional_mvn

        return conditional_mvn.mean, conditional_mvn.covariance