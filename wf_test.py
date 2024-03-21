import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow
from PIL import Image

from utils import read_lines_from_file
from plot.heatmap import Heatmap


# Basic PyQtGraph settings
pg.setConfigOptions(antialias=True)


class WaterfallPlotWidget:
	"""Waterfall plot"""
	def __init__(self, layout, histogram_layout=None):
		if not isinstance(layout, pg.GraphicsLayoutWidget):
			raise ValueError("layout must be instance of pyqtgraph.GraphicsLayoutWidget")

		if histogram_layout and not isinstance(histogram_layout, pg.GraphicsLayoutWidget):
			raise ValueError("histogram_layout must be instance of pyqtgraph.GraphicsLayoutWidget")

		self.layout = layout
		self.histogram_layout = histogram_layout

		self.history_size = 100
		self.counter = 0

		self.image_item = None

		self.create_plot()

	def create_plot(self):
		"""Create waterfall plot"""
		self.plot = self.layout.addPlot(row=1, col=0)
		self.plot1 = self.layout.addPlot(row=0, col=0) # add another graph
		self.plot.setLabel("bottom", "Frequency", units="Hz")
		# self.plot.setLabel("left", "Time")

		self.plot1.setTitle("Назва графіку", color='white', size='22pt')


		# Set the Y-range to cover the entire negative range of the image
		self.plot.setYRange(-self.history_size, 0)
		self.plot.setXRange(0, 2200)

		self.plot.setLimits(xMin=0, yMax=0)
		self.plot1.setLimits(xMin=0, yMax=0)
		self.plot.showButtons()
		self.plot.setMouseEnabled(x=False, y=False)  # Disable both panning and zooming
		self.plot.autoRange()

		self.image_item = pg.ImageItem()
		self.plot.addItem(self.image_item)

		# Set a specific width for the left axis
		self.plot.getAxis("left").setWidth(50)
		self.plot1.getAxis("left").setWidth(50)

		# Hide axis labels and tick marks in self.plot
		# self.plot.getAxis("left").setStyle(tickTextOffset=20, showValues=False)
		# self.plot.getAxis("bottom").setStyle(tickTextOffset=20, showValues=False)

	def update_image(self, image_array):
		"""Update the image in the waterfall plot"""
		self.image_item.setImage(image_array)

		self.image_item.scale()
		self.image_item.setPos(0, -50)
		
		# Adjust aspect ratio to match image
		# height, width = image_array.shape[0], image_array.shape[1]  # Get height and width from the shape of the image array
		# self.plot.setAspectLocked(lock=True, ratio=width/height)  # Set aspect ratio based on image width/height ratio



class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.heatmap = Heatmap()

		self.csv_sdr_data_filename = "sdr_data.csv"
		self.csv_data_counter = 0
		self.waterfall_vertical_size = 50
		self.waterfall_max_vertical_size = 69

		# Основне вікно
		self.setWindowTitle('Spectrum and Waterfall Plot')
		self.setGeometry(100, 100, 900, 600)

		# Віджет для розміщення графіки
		self.central_widget = pg.GraphicsLayoutWidget()
		self.setCentralWidget(self.central_widget)

		# Додаємо віджет для водоспаду
		self.waterfall_plot_widget = WaterfallPlotWidget(self.central_widget)

		# Відображення головного вікна
		self.show()

		# Generate new random data and update the spectrum plot widget
		sdr_data = read_lines_from_file(self.csv_sdr_data_filename, self.csv_data_counter, self.waterfall_vertical_size)
		self.csv_data_counter += 1
		if self.waterfall_vertical_size < self.waterfall_max_vertical_size:
			self.waterfall_vertical_size += 1

		# WATERFALL
		self.heatmap.set_sdr_data(sdr_data)
		self.heatmap.summarize_pass()
		img = self.heatmap.push_pixels()
		
		w1, h1 = img.size
		print(w1, h1)


		# Convert PIL image to numpy array
		img_array = np.array(img)
		print(img_array.shape)

		self.waterfall_plot_widget.update_image(img_array)


if __name__ == '__main__':
	app = QApplication([])
	mainWindow = MainWindow()
	app.exec_()
