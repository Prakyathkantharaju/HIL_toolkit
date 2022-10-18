
import sys
import time

import numpy as np

from matplotlib.backends.qt_compat import QtWidgets #type: ignore
from matplotlib.backends.backend_qtagg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar) #type: ignore
from matplotlib.figure import Figure

import pylsl

import neurokit2 as nk


# import Qt imports
from PyQt5 import QtCore, QtGui, QtWidgets

# local imports
from peaks_rmssd_plot import Ui_MainWindow
from Receive_ecg import Inlet, DataInlet, MarkerInlet

class main_plotting:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.MainWindow = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)
        self._setup_constants()
        self._setup_buttons()
        self._setup_inlets()
        self._plot_canvas()
        self._timer_setup()
        self.start()


    def _setup_constants(self):
        self.SHOW_ECG = True
        self.SHOW_PEAKS = False
        self.SHOW_RMSSD = False

    def _setup_buttons(self):
        self.ui.pushButton_3.clicked.connect(self._ECG_button_clicked)
        self.ui.pushButton_2.clicked.connect(self._shown_peaks_button_clicked)
        self.ui.pushButton.clicked.connect(self._shown_RMSSD_button_clicked)

    def _ECG_button_clicked(self):
        self.SHOW_ECG = not self.SHOW_ECG

    def _shown_peaks_button_clicked(self):
        self.SHOW_PEAKS = not self.SHOW_PEAKS

    def _shown_RMSSD_button_clicked(self):
        self.SHOW_RMSSD = not self.SHOW_RMSSD


    def _setup_inlets(self):
        self.data = np.array([])
        self.peaks = np.array([])
        self.rmssd = []
        self.inlets:list[Inlet] = []
        print("Looking for an ECG stream...")
        self.streams = pylsl.resolve_stream()
        for info in self.streams: #type: ignore
            if info.nominal_srate() != pylsl.IRREGULAR_RATE \
                    and info.channel_format() != pylsl.cf_string:
                if info.name() == 'polar ECG':
                    print('Adding data inlet: ' + info.name())
                    self.inlets.append(DataInlet(info))
            else:
                print('Don\'t know what to do with stream ' + info.name())


    def _plot_canvas(self):
        self.fig_1 = Figure()
        self.ax_1 = self.fig_1.add_subplot(111)
        self.ax_1.plot(np.random.rand(5))
        self.ECG_plot = FigureCanvas(self.fig_1)
        self.ui.ECG_layou.addWidget(self.ECG_plot)
        #self.ui.ECG_layou.addWidget(NavigationToolbar(self.ECG_plot, self))

        self.fig_2 = Figure()
        self.ax_2 = self.fig_2.add_subplot(111)
        self.ax_2.plot(np.random.rand(5))
        self.RMSSD_plot = FigureCanvas(self.fig_2)
        self.ui.RMSSD_layou.addWidget(self.RMSSD_plot)
        #self.ui.RMSSD_layou.addWidget(NavigationToolbar(self.RMSSD_plot, self))

    def _timer_setup(self):
        self.timer_1 = self.ECG_plot.new_timer(interval=1000)
        self.timer_1.add_callback(self.update_plot_1)

        self.timer_2 = self.RMSSD_plot.new_timer(interval=1000)
        self.timer_2.add_callback(self.update_plot_2)


        self.timer_1.start()
        self.timer_2.start()

    def update_plot_1(self):
        self.ax_1.clear()
        incoming_data = self.inlets[0].pull(5)
        if incoming_data is not None and self.SHOW_ECG:
            if len(self.data) < 2 or len(self.data) > 100000:
                self.data = incoming_data[1]
            else:
                self.data = np.append(self.data.flatten(), incoming_data[1].flatten(), axis=0)
            print(self.data.shape)
            print(incoming_data[1].shape)
            self.ax_1.plot(self.data[-500:])
            if self.data.shape[0] > 500 and self.SHOW_PEAKS:
                self._calculate_peaks()
                self.ax_1.plot(self.peaks, self.data[-500:][self.peaks], 'ro')
        else:
            self.ax_1.plot(np.zeros(500))

        self.ax_1.set_ylabel('ECG')
        self.ax_1.set_title('ECG and peaks')
        self.ECG_plot.draw()

    def _calculate_peaks(self):
        self.peaks = nk.ecg_peaks(self.data[-500:], sampling_rate=133, show = False)[1]['ECG_R_Peaks']

    def update_plot_2(self):
        self.ax_2.clear()
        if self.SHOW_RMSSD:
            self._calculate_rmssd()
            self.ax_2.plot(self.rmssd)
        else:
            self.ax_2.plot(np.zeros(500))

        self.ax_2.set_ylabel('RMSSD')
        self.ax_2.set_title('RMSSD')
        self.RMSSD_plot.draw()

    def _calculate_rmssd(self):
        peaks, info = nk.ecg_peaks(self.data[-1330:], sampling_rate=133, show = False)
        time_analysis = nk.hrv_time(peaks, sampling_rate=133, show = False)
        if len(self.data) > 1330 and 'HRV_RMSSD' in time_analysis.columns:
            self.rmssd.append(time_analysis['HRV_RMSSD'].values[0])

    def start(self):
        self.MainWindow.show()
        sys.exit(self.app.exec_())


if __name__ == '__main__':
    main_plotting()
