from plot.Plot import Plot


class Graph():

	def __init__(self, win):
		self.win = win

		self.plot_list = {}
		self.worker_range_graph_id = {}
		self.graph_id_list = []

		for i in range(0, self.win.NUM_OF_RANGES):
			self.plot_list[i] = Plot(win, i)
			self.graph_id_list.append(i)

	def update(self, sdr_data):
		# TODO getting graph
		key = f'{sdr_data['scan_range']['start']}-{sdr_data['scan_range']['end']}'
		try:
			plot_id = self.worker_range_graph_id[key]
			self.plot_list[plot_id].update(sdr_data['signals']['all'])
		except:
			plot_id = self.graph_id_list.pop(0)
			self.worker_range_graph_id[key] = plot_id
			self.plot_list[plot_id].emit_plot_title(f'{sdr_data['scan_range']['start']} - {sdr_data['scan_range']['end']}MHz')


	def reset(self):
		print("reset()")
		self.worker_range_graph_id = {}
		self.graph_id_list = []
		for i in range(0, self.win.NUM_OF_RANGES):
			self.graph_id_list.append(i)
			self.plot_list[i].reset()
