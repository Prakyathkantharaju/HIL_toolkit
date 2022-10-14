import abc
import pylsl
import numpy as np




# TODO write documentation
class InletOutlet:
    def __init__(self, info: pylsl.StreamInfo, data_length: int) -> None:
        """Main inlet class the which captures metadata an provides the stream handle

        Args:
            info (pylsl.StreamInfo): pylsl info 
            data_length (int): data inlet to read everytime
        """
        self.inlet = pylsl.StreamInlet(info, max_buflen= data_length, 
            processing_flags=pylsl.proc_clocksync | pylsl.proc_dejitter)

        self.name = info.name()
        self.channel_count = info.channel_count()
        self.new_data = False
        self.store_data = np.array([])

    @abc.abstractclassmethod
    def get_data(self) -> None:
        """Abstract class method to read the data

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError

    @abc.abstractclassmethod
    def send_data(self) -> None:
        """Abstract class method to send data to the pylsl after processing

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError