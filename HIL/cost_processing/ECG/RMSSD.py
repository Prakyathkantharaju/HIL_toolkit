# general imports
import logging
import numpy as np
import math
import pylsl
import time
import os
import copy
import abc

# processing
import neurokit2 as nk

# typing
from typing import List

from HIL.cost_processing.utils.inlet import InletOutlet


    

class RMSSDInOut(InletOutlet):
    dtypes = [[], np.float32, np.float64, None, np.int32, np.int16, np.int8, np.int64]

    def __init__(self, info: pylsl.StreamInfo, data_length: int, sampling_rate: int = 133, skip_threshold: int = 40) -> None:
        """Main class which handles the input of the ECG data and output of the rmssd data to the pylsl.

        Args:
            info (pylsl.StreamInfo): information aboute the input stream
            data_length (int): Data length to process to get the RMSSD, generally 1000 -> ~9s considering 133 Hz sampling rate
            sampling_rate (int, optional): Sampling rate of the signal. Defaults to 133.
            skip_threshold (int, optional): This is the higher level threshold, above which RMSSD is not sent, (Generally standing threshold is picked). Defaults to 40.
        """
        super().__init__(info, data_length)
        buffer_size = (2 * math.ceil(info.nominal_srate() * data_length), info.channel_count())
        self.buffer = np.empty(buffer_size, dtype = self.dtypes[info.channel_format()])

        # placeholders
        self.store_data = np.array([])

        # Information about the outlet stream
        info  = pylsl.StreamInfo('ECG_processed',  'Marker', 1, 0, 'float32', 'myuidw43537') #type: ignore
        self.outlet = pylsl.StreamOutlet(info)

        # logging
        self._logger = logging.getLogger()

        # setting some large RMMSD value at the start.
        self.previous_HR = 1000
        self.skip_threshold = skip_threshold
        self.SAMPLING_RATE = sampling_rate

        # Main processing class
        self.rmssd = RMSSD(self.SAMPLING_RATE)

        # flags
        self.first_data = True


    def get_data(self) -> None:
        """Class to get the ECG data and process it

        Returns:
            None: early return if the stream if not ECG
        """
        _, ts = self.inlet.pull_chunk(timeout = 0.0, 
                max_samples=self.buffer.shape[0],
                dest_obj=self.buffer)

        if not ts or self.name != "polar ECG":
            self._logger.warning(f"Time stamp is: {ts}, name of the stream: {self.name}")
            return None
        
        ts = np.array(ts)
        # For first time
        if self.first_data:
            self.store_data = self.buffer[0:ts.size,:]
            self.first_data = False

        else:
            self.store_data = np.append(self.store_data.flatten(), self.buffer)
            self.rmssd.add_data(self.store_data)
            

            # check if there is a nan in the data
            if np.isnan(self.cleaned).any(): #type: ignore
                self._logger.warn(f"nan found in data")

    def send_data(self) -> None:
        """Send the processed data to the pylsl

        """
        rmssd = self.rmssd.get_rmssd()

        if self.previous_HR == 1000: # this is the first
            self.previous_HR = rmssd

        if len(self.cleaned) < 2000: #type: ignore
            self._logger.info(f"Not enough clean data {len(self.cleaned)}") #type: ignore
            return

        if rmssd == -1:
            # something wrong with the data do not send
            return 


        if self.skip_threshold < rmssd:
            self._logger.warn(f"rmssd is greater than the threshold: {rmssd}")
            self.store_data = np.array([])
            self.first_data = True
            return

        self.outlet.push_sample([rmssd])

        self.new_data = True

        self._logger.info(f"Sending the RMSSD value {rmssd}")

class RMSSD():
    def __init__(self, sampling_rate: int ) -> None:
        """Main processing class for the RMSSD data

        Args:
            sampling_rate (int): Sampling rate of the data
        """
        self.SAMPLING_RATE = sampling_rate
        self.cleaned = np.array([])
        
    def add_data(self, data: np.ndarray) -> None:
        """Add data which needs to processed

        Args:
            data (np.ndarray): The ECG data in the form of np.ndarray
        """
        self.raw_data = data

    def _clean_quality(self) -> None:

        """Clean the data and perform a quality check
        """
        self.cleaned = nk.ecg_clean(self.raw_data, sampling_rate=self.SAMPLING_RATE)

        try:
            self.quality = nk.ecg_quality(self.cleaned, method = 'zhao', sampling_rate=self.SAMPLING_RATE)
        except ValueError:
            self.quality = 0

    def _process_data(self) -> float:
        """Process the cleaned data

        Returns:
            float: RMSSD value
        """
        if self.cleaned is None:
            return -1
        
        cleaned = copy.copy(self.cleaned)

        peaks, info = nk.ecg_peaks(cleaned, sampling_rate = self.SAMPLING_RATE)

        try:
            signal = nk.hrv_time(peaks, sampling_rate=self.SAMPLING_RATE, show = False)

            # setting the new data
            return signal['HRV_RMSSD'].value[0]
        except IndexError:
            return -1

    def get_rmssd(self) -> float:
        """Send the processed RMSSD value"""
        return self._process_data()

    
class RMSSDFromStream():
    def __init__(self, config: dict) -> None:
        """Class for getting RMSSD live from stream

        Args:
            config (dict): Configs parsed output of the yaml config files
        """
        self.inlets: List[InletOutlet] = []
        self.streams = pylsl.resolve_streams()
        self.wait_time = config['Pub_rate']

        for info in self.streams:
            print(info.name())
            if info.name() == config['stream_name']:
                self.inlets.append(RMSSDInOut(info, config['Data_buffer_length'], 
                        sampling_rate=config['Sampling_rate'], skip_threshold=config['Skip_threshold']))

    def run(self) -> None:
        """Main run ( in the while loop )
        """

        # This is the main while loop
        while True:
            time.sleep(self.wait_time)
            for inlet in self.inlets:
                inlet.get_data()
                # Checking the inlet data size and send the data to the pylsl stream.
                if len(inlet.store_data) > 250:
                    inlet.send_data()
                else:
                    logging.warn(f"{__name__}: no data to send")