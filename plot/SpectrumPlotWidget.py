import pyqtgraph as pg


class SpectrumPlotWidget:
	"""Main spectrum plot"""
	def __init__(self, layout, title):
		self.layout = layout
		self.title = title
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
		self.plot.setLabel("bottom", "Frequency", units="MHz")
		self.plot.setLimits(xMin=0)
		self.plot.hideButtons()
		self.plot.setMouseEnabled(x=False, y=False)  # Disable both panning and zooming
		# Set a specific width for the left axis
		self.plot.getAxis("left").setWidth(50)

		self.plot.setTitle(self.title, color='white', size='22pt')

		self.create_curve()

		# Create crosshair
		"""self.vLine = pg.InfiniteLine(angle=90, movable=False)
		self.vLine.setZValue(1000)
		self.hLine = pg.InfiniteLine(angle=0, movable=False)
		self.vLine.setZValue(1000)
		self.plot.addItem(self.vLine, ignoreBounds=True)
		self.plot.addItem(self.hLine, ignoreBounds=True)
		self.mouseProxy = pg.SignalProxy(self.plot.scene().sigMouseMoved,
										 rateLimit=60, slot=self.mouse_moved)"""

	def create_curve(self):
		"""Create main spectrum curve"""
		self.curve = self.plot.plot(pen=self.main_color)
		self.curve.setZValue(900)

	def update_curve(self, x_val, y_val):
		self.curve.setData(x_val, y_val)


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