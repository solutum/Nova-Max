# https://youtu.be/RHmTgapLu4s
import numpy as np
import pyqtgraph as pg

from collections import defaultdict

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer

# from qspectrumanalyzer.data import DataStorage
from utils import read_lines_from_file
from heatmap import Heatmap


# Basic PyQtGraph settings
pg.setConfigOptions(antialias=True)


class SpectrumPlotWidget:
	"""Main spectrum plot"""
	def __init__(self, layout):
		# if not isinstance(layout, pg.GraphicsLayoutWidget):
		# 	raise ValueError("layout must be instance of pyqtgraph.GraphicsLayoutWidget")

		self.layout = layout

		self.main_curve = True
		self.main_color = pg.mkColor("y")
		self.persistence = False
		self.persistence_length = 5
		self.persistence_decay = "exponential"
		self.persistence_color = pg.mkColor("g")
		self.persistence_data = None
		self.persistence_curves = None

		self.create_plot()

	def create_plot(self):
		"""Create main spectrum plot"""
		# self.posLabel = self.layout.addLabel(row=0, col=0, justify="right")
		self.plot = self.layout.addPlot(row=0, col=0)
		self.plot.showGrid(x=True, y=True)
		self.plot.setLabel("left", "Power", units="dB")
		self.plot.setLabel("bottom", "Frequency", units="Hz")
		self.plot.setLimits(xMin=0)
		self.plot.hideButtons()
		self.plot.setMouseEnabled(x=False, y=False)  # Disable both panning and zooming
		# Set a specific width for the left axis
		self.plot.getAxis("left").setWidth(50)


		self.create_main_curve()

		# Create crosshair
		"""self.vLine = pg.InfiniteLine(angle=90, movable=False)
		self.vLine.setZValue(1000)
		self.hLine = pg.InfiniteLine(angle=0, movable=False)
		self.vLine.setZValue(1000)
		self.plot.addItem(self.vLine, ignoreBounds=True)
		self.plot.addItem(self.hLine, ignoreBounds=True)
		self.mouseProxy = pg.SignalProxy(self.plot.scene().sigMouseMoved,
										 rateLimit=60, slot=self.mouse_moved)"""

	def create_main_curve(self):
		"""Create main spectrum curve"""
		self.curve = self.plot.plot(pen=self.main_color)
		self.curve.setZValue(900)

	# def update_plot(self, data_storage, force=False):
	# 	"""Update main spectrum curve"""
	# 	if data_storage.x is None:
	# 		return

	# 	if self.main_curve or force:
	# 		self.curve.setData(data_storage.x, data_storage.y)
	# 		if force:
	# 			self.curve.setVisible(self.main_curve)

	def mouse_moved(self, evt):
		"""Update crosshair when mouse is moved"""
		pos = evt[0]
		if self.plot.sceneBoundingRect().contains(pos):
			mousePoint = self.plot.vb.mapSceneToView(pos)
			# ! змінюється розмір коли навожу мишку
			"""self.posLabel.setText(
				"<span style='font-size: 12pt'>f={:0.3f} MHz, P={:0.3f} dB</span>".format(
					mousePoint.x() / 1e6,
					mousePoint.y()
				)
			)"""
			self.vLine.setPos(mousePoint.x())
			self.hLine.setPos(mousePoint.y())

	def clear_plot(self):
		"""Clear main spectrum curve"""
		self.curve.clear()


class WaterfallPlotWidget:
	"""Waterfall plot"""
	def __init__(self, layout):

		self.layout = layout
		# self.histogram_layout = histogram_layout

		self.history_size = 100
		self.counter = 0
		self.waterfall_img = None

		self.create_plot()

	def create_plot(self):
		"""Create waterfall plot"""
		self.plot = self.layout.addPlot(row=1, col=0)
		self.plot.setLabel("bottom", "Frequency", units="Hz")
		# self.plot.setLabel("left", "Time")

		self.plot.setXRange(0, 2048)
		self.plot.setYRange(-self.history_size, 0)
		self.plot.setLimits(xMax=2048)
		self.plot.hideButtons()
		#self.plot.setAspectLocked(True)
		self.plot.setMouseEnabled(x=False, y=False)  # Disable both panning and zooming
		# self.plot.autoRange()

		self.waterfall_img = pg.ImageItem()
		self.plot.addItem(self.waterfall_img)

		# Set a specific width for the left axis
		self.plot.getAxis("left").setWidth(50)

		#self.plot.setDownsampling(mode="peak")
		#self.plot.setClipToView(True)

		# Setup histogram widget (for controlling waterfall plot levels and gradients)
		"""if self.histogram_layout:
			self.histogram = pg.HistogramLUTItem()
			self.histogram_layout.addItem(self.histogram)
			self.histogram.gradient.loadPreset("flame")
			#self.histogram.setHistogramRange(-50, 0)
			#self.histogram.setLevels(-50, 0)"""

	
	def update_image(self, img_array, img_offset):
		"""Update the image in the waterfall plot"""
		self.waterfall_img.setImage(img_array)

		self.waterfall_img.scale()
		self.waterfall_img.setPos(0, img_offset)


	def clear_plot(self):
		"""Clear waterfall plot"""
		self.counter = 0

class SpectrumData:
	def __init__(self):
		pass

	def frange(self, start, stop, step):
		i = 0
		f = start
		while f <= stop:
			f = start + step*i
			yield f
			i += 1

	def flatten_xy_for_spectrum(self, data):
		x_vals = []
		y_vals = []

		sums = defaultdict(float)
		counts = defaultdict(int)

		# data = g.csv_data[0] # GET only 1st row
		data = data.strip().split(', ')
		low = int(data[2])
		high = int(data[3])
		step = float(data[4])
		weight = int(data[5])
		dbm = [float(d) for d in data[6:]]
		for f,d in zip(self.frange(low, high, step), dbm):
			sums[f] += d*weight
			counts[f] += weight

		ave = defaultdict(float)
		for f in sums:
			ave[f] = sums[f] / counts[f]

		for f in sorted(ave):
			# print(','.join([str(f), str(ave[f])]))
			x_vals.append(float(f))
			y_vals.append(float(ave[f]))
			# x_vals[-1] += g.offset
			x_vals[-1] /= 1000000.0

		return x_vals, y_vals


class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.spectrum_data = SpectrumData()
		self.heatmap = Heatmap()


		self.csv_sdr_data_filename = "sdr_data.csv"
		self.csv_data_counter = 0
		self.waterfall_vertical_size = 1
		self.waterfall_max_vertical_size = 100

		self.initUI()
		self.start_animation()


	def initUI(self):
		# Основне вікно
		self.setWindowTitle('Spectrum and Waterfall Plot')
		self.setGeometry(100, 100, 1000, 600)

		# Віджет для розміщення графіки
		self.central_widget = pg.GraphicsLayoutWidget()
		self.setCentralWidget(self.central_widget)

		# Додаємо віджет для спектра
		self.spectrum_plot_widget = SpectrumPlotWidget(self.central_widget)

		# Додаємо віджет для водоспаду
		self.waterfall_plot_widget = WaterfallPlotWidget(self.central_widget)

		# Відображення головного вікна
		self.show()


	def start_animation(self):
		# Create a QTimer to update the spectrum plot widget periodically
		self.timer = QTimer()
		self.timer.timeout.connect(self.update_plot)
		self.timer.start(1000)  # Update every 1 (1000ms) second

	def update_plot(self):
		# Generate new random data and update the spectrum plot widget
		sdr_data = read_lines_from_file(self.csv_sdr_data_filename, self.csv_data_counter, self.waterfall_vertical_size)
		if self.waterfall_vertical_size < self.waterfall_max_vertical_size:
			self.waterfall_vertical_size += 1
		else:
			self.csv_data_counter += 1


		# SPECTRUM
		x_val, y_val = self.spectrum_data.flatten_xy_for_spectrum(sdr_data[-1])
		self.spectrum_plot_widget.curve.setData(x_val, y_val)

		# WATERFALL
		self.heatmap.set_sdr_data(sdr_data)
		self.heatmap.summarize_pass()
		img = self.heatmap.push_pixels()

		# Convert PIL image to numpy array
		img_array = np.array(img)
		# print(img_array.shape)

		self.waterfall_plot_widget.update_image(img_array, self.waterfall_vertical_size * -1)



if __name__ == '__main__':
	app = QApplication([])
	mainWindow = MainWindow()
	app.exec_()
	#  sys.exit(app.exec_()) # ?