from PyQt5.QtCore import pyqtSignal, QObject
import pyqtgraph as pg
import numpy as np
import colorsys


pg.setConfigOptions(antialias=False)

class Signals(QObject):
	set_plot_title = pyqtSignal(str)

class Plot():

	def __init__(self, win, plot_index):
		self.win = win
		self.signals = Signals()
		self.signals.set_plot_title.connect(self.set_plot_title)

		self.waterfall_max_vertical_size = 70 # Y - AXIS

		# SPECTRUM
		self.spectrum = getattr(self.win, f'graphSpectrum_{plot_index}')
		self.spectrum.hideButtons()
		self.spectrum.setMouseEnabled(x=True, y=False)
		self.spectrum.getAxis("left").setWidth(50)
		# mouse connection
		self.spectrum.scene().sigMouseMoved.connect(self.mouse_moved)
		# Створення вертикальної лінії
		self.vLine = pg.InfiniteLine(angle=90, movable=False)
		self.vLine.setZValue(1000)
		self.spectrum.addItem(self.vLine, ignoreBounds=True)
		# #
		# create curves
		self.curve = self.spectrum.plot(pen=pg.mkColor("y"))
		self.curve.setZValue(900)

		# WATERFALL
		waterfall_plot = getattr(self.win, f'graphWFall_{plot_index}')
		waterfall_plot.hideButtons()
		waterfall_plot.setMouseEnabled(x=False, y=False)
		waterfall_plot.getAxis("left").setWidth(50)
		waterfall_plot.getAxis("left").setStyle(showValues=False)
		waterfall_plot.getAxis("bottom").setStyle(tickTextOffset=20, showValues=False)
		self.waterfall = pg.ImageItem()
		waterfall_plot.addItem(self.waterfall)
		# set palette
		self.waterfall.setLookupTable(self.charolastra_palette())

		# waterfall history
		self.waterfall_data = None

	def update(self, sdr_data):
		x_val, y_val = self.get_xy_for_spectrum(sdr_data)
		# SPECTRUM
		self.update_curve(x_val, y_val)
		# WATERFALL
		self.update_waterfall(y_val)

	def update_curve(self, x, y):
		self.curve.setData(x, y)

	def update_waterfall(self, y):
		if self.waterfall_data is None:
			self.waterfall_data = np.full((len(y), self.waterfall_max_vertical_size), -100)

		for i in range(-self.waterfall_max_vertical_size, -1, 1):
			self.waterfall_data[:, i] = self.waterfall_data[:, i+1]

		self.waterfall_data[:, -1] = y

		self.waterfall.setImage(self.waterfall_data, autoLevels=False, levels=(-100, 0))  # Встановлення широкого діапазону рівнів кольорів



	def get_xy_for_spectrum(self, data):
		x_vals = []
		y_vals = []

		for entry in data:
			x_vals.append(float(entry['frequency']))
			y_vals.append(float(entry['dbi']))

		return x_vals, y_vals

	def charolastra_palette(self):
		p = [(0, 0, 0)]  # Додаємо чорний колір на початок палітри
		for i in range(1, 1024):  # Починаємо з 1, оскільки перший колір - чорний
			g = i / 1023.0
			c = colorsys.hsv_to_rgb(0.65-(g-0.08), 1, 0.2+g)
			p.append((int(c[0]*256), int(c[1]*256), int(c[2]*256)))
		return p

	
	def emit_plot_title(self, title):
		self.signals.set_plot_title.emit(title)
	def set_plot_title(self, title):
		try:
			self.spectrum.setTitle(title, color='white', size='18pt')
		except Exception as e:
			print("set_plot_title() error: ", e)

	# Update crosshair when mouse is moved
	def mouse_moved(self, evt):
		pos = evt  # Отримання позиції миші
		if self.spectrum.sceneBoundingRect().contains(pos):
			viewbox = self.spectrum.getViewBox()  # get ViewBox from PlotWidget
			mousePoint = viewbox.mapSceneToView(pos)  # get mouse position

			# set vert line position
			self.vLine.setPos(mousePoint.x())

			# label update
			self.win.X_coord_label.setText(f"MHz: {mousePoint.x():.1f}")

	def reset(self):
		self.emit_plot_title('')
		self.curve.clear()
		self.waterfall.clear()
		self.waterfall_data = None

