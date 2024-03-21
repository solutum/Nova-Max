# https://youtu.be/RHmTgapLu4s
# import numpy as np
import pyqtgraph as pg
from collections import defaultdict
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer

from utils import read_lines_from_file
from plot.oldHeatmap import Heatmap
from plot.SpectrumData import SpectrumData
from plot.SpectrumPlotWidget import SpectrumPlotWidget
from plot.WaterfallPlotWidget import WaterfallPlotWidget


pg.setConfigOptions(antialias=False)

class PlotWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		try:
			self.spectrum_data = SpectrumData()
			self.heatmap = Heatmap()

			self.csv_sdr_data_filename = "/Users/max/PythonProjects/SDR/nova-max/sdr_data.csv"
			self.csv_data_counter = 0
			self.waterfall_vertical_size = 1
			self.waterfall_max_vertical_size = 70

			self.animation_delay = 750 # msec/ 1000 == 1sec

			self.initUI()
			self.start_animation()
		except Exception as e:
			print(f'Error: {e}')


	def initUI(self):
		# Основне вікно
		self.setWindowTitle('Nova Max v0.1')
		self.setGeometry(100, 100, 1000, 600)

		# Віджет для розміщення графіки
		self.central_widget = pg.GraphicsLayoutWidget()
		self.setCentralWidget(self.central_widget)

		# Додаємо віджет для спектра
		self.spectrum_plot_widget = SpectrumPlotWidget(self.central_widget, "Тут текст")

		# Додаємо віджет для водоспаду
		self.waterfall_plot_widget = WaterfallPlotWidget(self.central_widget, self.waterfall_max_vertical_size)

		# Відображення головного вікна
		self.show()


	def start_animation(self):
		# Create a QTimer to update the spectrum plot widget periodically
		self.timer = QTimer()
		self.timer.timeout.connect(self.update_plot)
		self.timer.start(self.animation_delay)  # Update every 1 (1000ms) second

	def update_plot(self):
		# Generate new random data and update the spectrum plot widget
		sdr_data = read_lines_from_file(self.csv_sdr_data_filename, self.csv_data_counter, self.waterfall_vertical_size)
		if self.waterfall_vertical_size < self.waterfall_max_vertical_size:
			self.waterfall_vertical_size += 1
		else:
			self.csv_data_counter += 1


		# SPECTRUM
		print(sdr_data[-1])
		x_val, y_val = self.spectrum_data.flatten_xy_for_spectrum(sdr_data[-1])
		# self.spectrum_plot_widget.curve.setData(x_val, y_val)
		self.spectrum_plot_widget.update_curve(x_val, y_val)

		# WATERFALL
		self.heatmap.set_sdr_data(sdr_data)
		self.heatmap.summarize_pass()
		img = self.heatmap.push_pixels()

		self.waterfall_plot_widget.update_image(img, self.waterfall_vertical_size * -1)



if __name__ == '__main__':
	app = QApplication([])
	plotWindow = PlotWindow()
	app.exec_()
	#  sys.exit(app.exec_()) # ?