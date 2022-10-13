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

# TODO write documentation
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


    

class DataInlet(Inlet):
    dtypes = [[], np.float32, np.float64, None, np.int32, np.int16, np.int8, np.int64]

    def __init__(self, info: pylsl.StreamInfo, data_length: int, sampling_rate: int = 133, skip_threshold: int = 40) -> None:
        super().__init__(info, data_length)
        buffer_size = (2 * math.ceil(info.nominal_srate() * data_length), info.channel_count())
        self.buffer = np.empty(buffer_size, dtype = self.dtypes[info.channel_format()])
        self.first_data = True
        self.store_data = np.array([])
        info  = pylsl.StreamInfo('ECG_processed',  'Marker', 1, 0, 'float32', 'myuidw43537') #type: ignore
        self.outlet = pylsl.StreamOutlet(info)
        self._logger = logging.getLogger()
        # self.communication = MainCommunication()
        # setting some large RMMSD value at the start.
        self.previous_HR = 1000
        self.skip_threshold = skip_threshold
        self.skip_counter = 0
        self.cleaned = None
        self.SAMPLING_RATE = sampling_rate

    def get_data(self) -> None:
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
            self.cleaned = nk.ecg_clean(self.store_data, sampling_rate=self.SAMPLING_RATE)

            # check if there is a nan in the data
            if np.isnan(self.cleaned).any(): #type: ignore
                self._logger.warn(f"nan found in data")

            try:
                self.quality = nk.ecg_quality(self.cleaned, method = 'zhao', sampling_rate=self.SAMPLING_RATE)
            except ValueError:
                self.quality = 0
            
# TODO make a seperate class for RMSSD processing.

    def _process_data(self) -> float:
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


    def send_data(self) -> None:
        rmssd = self._process_data()

        if self.previous_HR == 1000: # this is the first
            self.previous_HR = rmssd

        if len(self.cleaned) < 2000: #type: ignore
            self._logger.info(f"Not enough clean data {len(self.cleaned)}") #type: ignore
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
    def __init__(self, config: dict):
        self.inlets: List[Inlet] = []
        self.streams = pylsl.resolve_streams()
        self.wait_time = config['Pub_rate']

        for info in self.streams:
            print(info.name())
            if info.name() == config['stream_name']:
                self.inlets.append(DataInlet(info, config['Data_buffer_length'], 
                        sampling_rate=config['Sampling_rate'], skip_threshold=config['Skip_threshold']))

    def run(self):

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




        

        

            






