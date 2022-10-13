# This file is for metabolic estimation using ppe
from typing import Tuple, Any
import numpy as np
import scipy.signal as signal
import neurokit2 as nk
import pylsl
import abc

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
    def __init__(self, upsample_number: int = 10, cutoff: float = 0.02) -> None:
        self.UPSAMPLE = upsample_number
        self.HIGHCUT = cutoff
        self.MAX_ITER = 500
        self.N_COMPONENTS = 10


        self._raw_met = np.array([])
        self._raw_time = np.array([])
        self._filtered_met = np.array([])

    def estimate(self, raw_met: np.ndarray, raw_time: np.ndarray) -> Tuple[float, float]:
        # slightly differnt from the paper, performs better
        # Upsample data
        up_sampled = self._up_sample(raw_met, raw_time)

        # perform filter
        filtered_data = self._filter_data(up_sampled)

        # convert to phase plane
        phase_plane = self._get_phase_plane(filtered_data)

        # updated phase plane
        self._phase_plane = phase_plane

        # estimte the prediction with mean and std of the prediction
        mean, cov = self._estimate_steady_state(phase_plane)

        assert len(mean) == 1, "mean is not one, check gmm prediction"
        assert len(cov) == 1, "mean is not one, check gmm prediction"

        # std
        std = np.sqrt(cov)

        return mean,std

    def _up_sample(self, raw_met : np.ndarray, raw_time: np.ndarray) -> np.ndarray:
        up_sample = signal.resample(raw_met, raw_time[-1] * self.UPSAMPLE)
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

    def _estimate_steady_state(self, phase_plane: np.ndarray) -> Tuple[Any, Any]:

        # Fit the BGMM and the GMR
        random_state = check_random_state(0)
        bgmm = BayesianGaussianMixture(n_components=self.N_COMPONENTS, max_iter= self.MAX_ITER, init_params='kmeans++').fit(phase_plane)
        gmm = GMM(n_components=self.N_COMPONENTS, 
                priors=bgmm.weights_,
                means=bgmm.means_,
                covariances=bgmm.covariances_,
                random_state=random_state)

        # Regression
        conditional_gmm = gmm.condition([1], np.array([0])) # [1] -> because conditioning along y axis, 0 because the prediction is on x axis 

        # converting to single  distribution
        conditional_mvn = conditional_gmm.to_mvn()

        # store conditional multi variant normal
        self._conditional_mvn = conditional_mvn

        return conditional_mvn.mean, conditional_mvn.covariance