import pyqtgraph as pg
import numpy as np
import colorsys


class WaterfallPlotWidget:
	def __init__(self, layout, history_size):
		self.layout = layout
		self.history_size = history_size
		self.counter = 0
		self.waterfall_img = None
		self.waterfall_data = None

		self.create_plot()

	def create_plot(self):
		"""Create waterfall plot"""
		self.plot = self.layout.addPlot(row=1, col=0)
		# self.plot.setLabel("bottom", "Frequency", units="Hz")
		# self.plot.setLabel("left", "Time")

		# self.plot.setXRange(0, 2048)
		# self.plot.setYRange(-self.history_size, 0)
		# self.plot.setLimits(xMax=2048)
		self.plot.hideButtons()
		#self.plot.setAspectLocked(True)
		self.plot.setMouseEnabled(x=False, y=False)  # Disable both panning and zooming
		# self.plot.autoRange()

		self.waterfall_img = pg.ImageItem()
		self.plot.addItem(self.waterfall_img)

		# Set a specific width for the left axis
		self.plot.getAxis("left").setWidth(50)
		# hide markdown
		self.plot.getAxis("bottom").setStyle(tickTextOffset=20, showValues=False)


	
	def update_image(self, img_array, img_offset):
		"""Update the image in the waterfall plot"""
		self.waterfall_img.setImage(img_array)

		self.waterfall_img.scale()
		self.waterfall_img.setPos(0, img_offset)


	def my_update_image(self, y):
		if self.waterfall_data is None:
			self.waterfall_data = np.zeros((len(y), self.history_size))

		for i in range(-self.history_size, -1, 1):
			self.waterfall_data[:, i] = self.waterfall_data[:, i+1]

		self.waterfall_data[:, -1] = y

		# Оновлення графіка "водоспаду"
		self.waterfall_img.setImage(self.waterfall_data, autoLevels=True, levels=(0, 1))  # Встановлення автоматичних рівнів для кольорової палітри

		# Встановлення кольорної палітри
		palette = self.charolastra_palette()
		self.waterfall_img.setLookupTable(palette)


	def clear_plot(self):
		"""Clear waterfall plot"""
		self.counter = 0

	def charolastra_palette(self):
		p = []
		for i in range(1024):
			g = i / 1023.0
			c = colorsys.hsv_to_rgb(0.65-(g-0.08), 1, 0.2+g)
			p.append((int(c[0]*256), int(c[1]*256), int(c[2]*256)))
		return p