import math
import colorsys
import datetime
import numpy as np

class Heatmap():
	def __init__(self):
		self.init()

	def init(self):
		self.sdr_data = []

		self.tape_height = 25
		self.tape_pt = 10

		args = {}
		args['offset_freq'] = 0
		args['time_tick'] = None
		args['db_limit'] = None
		args['compress'] = 0.0
		args['low_freq'] = None
		args['high_freq'] = None
		args['begin_time'] = None
		args['end_time'] = None
		args['head_time'] = None
		args['tail_time'] = None
		args['palette'] = self.charolastra_palette
		r, g, b, x, y = ('000:255:255:025:150').split(":")
		args['rgbxy'] = (int(r), int(g), int(b), int(x), int(y))
		args['nolabels'] = True
		self.args = args

	def set_sdr_data(self, sdr_data):
		self.args['db_limit'] = None  # otherwise error accumulating
		self.sdr_data = sdr_data

	def frange(self, start, stop, step):
		i = 0
		while (i * step + start <= stop):
			yield i * step + start
			i += 1

	def floatify(self, zs):
		zs2 = []
		previous = 0
		for z in zs:
			try:
				z = float(z)
			except ValueError:
				z = previous
			if math.isinf(z):
				z = previous
			if math.isnan(z):
				z = previous
			zs2.append(z)
			previous = z
		return zs2

	def date_parse(self, s):
		return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f')

	def time_compression(self, y, decay):
		return int(round((1 / decay) * math.exp(y * decay) - 1 / decay))

	def slice_columns(self, columns, low_freq, high_freq, low, high):
		start_col = 0
		stop_col = len(columns)
		if low_freq is not None and low <= low_freq <= high:
			start_col = sum(f < low_freq for f in columns)
		if high_freq is not None and low <= high_freq <= high:
			stop_col = sum(f <= high_freq for f in columns)
		return start_col, stop_col - 1

	def summarize_pass(self):
		freqs = set()
		f_cache = set()
		times = set()
		labels = set()
		min_z = 0
		max_z = -100
		start, stop = None, None
		
		# print(self.sdr_data)
		# exit()

		for entry in self.sdr_data:
			t = entry['datetime']
			times.add(t)

			low = int(entry['frequency']) + self.args['offset_freq']
			high = low + 0.5
			step = 0.5

			if self.args['low_freq'] is not None and high < self.args['low_freq']:
				continue
			if self.args['high_freq'] is not None and self.args['high_freq'] < low:
				continue
			if self.args['begin_time'] is not None and self.date_parse(t) < self.args['begin_time']:
				continue
			if self.args['end_time'] is not None and self.date_parse(t) > self.args['end_time']:
				break

			columns = list(self.frange(low, high, step))
			start_col, stop_col = self.slice_columns(columns, self.args['low_freq'], self.args['high_freq'], low,
													 high)
			if not columns:
				continue
			f_key = (columns[start_col], columns[stop_col], step)
			zs = [entry['dbi']]
			if f_key not in f_cache:
				freq2 = list(self.frange(*f_key))[:len(zs)]
				freqs.update(freq2)
				f_cache.add(f_key)

			if not self.args['db_limit']:
				zs = self.floatify(zs)
				min_z = min(min_z, min(zs))
				max_z = max(max_z, max(zs))

			if start is None:
				start = self.date_parse(t)
			stop = self.date_parse(t)
			if self.args['head_time'] is not None and self.args['end_time'] is None:
				self.args['end_time'] = start + self.args['head_time']

		if not self.args['db_limit']:
			self.args['db_limit'] = (min_z, max_z)

		if self.args['tail_time'] is not None:
			times = [t for t in times if self.date_parse(t) >= (stop - self.args['tail_time'])]
			start = self.date_parse(min(times))

		freqs = list(sorted(list(freqs)))
		times = list(sorted(list(times)))
		labels = list(sorted(list(labels)))

		if len(labels) == 1:
			delta = (max(freqs) - min(freqs)) / (len(freqs) / 500.0)
			delta = round(delta / 10 ** int(math.log10(delta))) * 10 ** int(math.log10(delta))
			delta = int(delta)
			lower = int(math.ceil(min(freqs) / delta) * delta)
			labels = list(range(lower, int(max(freqs)), delta))

		height = len(times)
		pix_height = height
		if self.args['compress']:
			if self.args['compress'] > height:
				self.args['compress'] = 0
			if 0 < self.args['compress'] < 1:
				self.args['compress'] *= height
			if self.args['compress']:
				self.args['compress'] = -1 / self.args['compress']
				pix_height = self.time_compression(height, self.args['compress'])

		self.args['freqs'] = freqs
		self.args['times'] = times
		self.args['labels'] = labels
		self.args['pix_height'] = pix_height
		self.args['start_stop'] = (start, stop)
		self.args['pixel_bandwidth'] = step

	def charolastra_palette(self):
		p = []
		for i in range(1024):
			g = i / 1023.0
			c = colorsys.hsv_to_rgb(0.65 - (g - 0.08), 1, 0.2 + g)
			p.append((int(c[0] * 256), int(c[1] * 256), int(c[2] * 256)))
		return p

	def push_pixels(self):
		if self.args['nolabels']:
			self.args['tape_height'] = -1
			self.args['tape_pt'] = 0

		width = len(self.args['freqs'])
		rgb = self.rgb_fn(self.args['palette'](), self.args['db_limit'][0], self.args['db_limit'][1])

		img_array = np.zeros((width, self.args['tape_height'] + self.args['pix_height'] + 1, 3), dtype=np.uint8)

		height = len(self.args['times'])
		for t, zs in self.collate_row(width):
			y = self.args['times'].index(t)
			if not self.args['compress']:
				img_array[:, y + self.args['tape_height'] + 1, :] = [rgb(z) for z in zs]
				continue
			y = self.args['pix_height'] - self.time_compression(height - y, self.args['compress'])
			if old_y is None:
				old_y = y
			if old_y != y:
				img_array[:, old_y + self.args['tape_height'] + 1, :] = [rgb(avg / tally) for avg in average]
				tally = 0
				average = np.zeros(width)
			old_y = y
			average += zs
			tally += 1

		return img_array

if __name__ == '__main__':
	hmap = Heatmap()

	sdr_data = [{'datetime': '2024-02-22 15:41:19.593666', 'dbi': -57.2, 'frequency': 2250.5},
				{'datetime': '2024-02-22 15:41:19.593666', 'dbi': -57.84, 'frequency': 2251.0},
				{'datetime': '2024-02-22 15:41:19.593666', 'dbi': -70.05, 'frequency': 2251.5},
				{'datetime': '2024-02-22 15:41:19.593666', 'dbi': -57.99, 'frequency': 2252.0},
				{'datetime': '2024-02-22 15:41:19.593666', 'dbi': -56.07, 'frequency': 2252.5},
				{'datetime': '2024-02-22 15:41:19.593666', 'dbi': -65.99, 'frequency': 2253.0},
				{'datetime': '2024-02-22 15:41:19.593666', 'dbi': -71.87, 'frequency': 2253.5},
				{'datetime': '2024-02-22 15:41:19.593666', 'dbi': -63.26, 'frequency': 2254.0},
				{'datetime': '2024-02-22 15:41:19.593666', 'dbi': -53.32, 'frequency': 2254.5},
				{'datetime': '2024-02-22 15:41:19.593666', 'dbi': -55.43, 'frequency': 2255.0},
				{'datetime': '2024-02-22 15:41:19.593666', 'dbi': -53.71, 'frequency': 2255.5}]
	
	hmap.set_sdr_data(sdr_data)
	hmap.summarize_pass()
	img = hmap.push_pixels()
