# from PIL import Image, ImageDraw, ImageFont
# from collections import defaultdict
# from itertools import *
import math, colorsys, datetime
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
		r,g,b,x,y = ('000:255:255:025:150').split(":")
		args['rgbxy'] = (int(r), int(g), int(b), int(x), int(y))
		args['nolabels'] = True
		self.args = args

	def set_sdr_data(self, sdr_data):
		self.args['db_limit'] = None # otherwise error accumulating
		# print(sdr_data)
		# sdr_data.reverse() # no need to pyqtgraph
		# print("reverse\n", sdr_data)
		self.sdr_data = sdr_data

	def frange(self, start, stop, step):
		i = 0
		while (i*step + start <= stop):
			yield i*step + start
			i += 1

	def floatify(self, zs):
		# nix errors with -inf, windows errors with -1.#J
		zs2 = []
		previous = 0  # awkward for single-column rows
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
		if '-' not in s:
			return datetime.datetime.fromtimestamp(int(s))
		return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

	def time_compression(self, y, decay):
		return int(round((1/decay)*math.exp(y*decay) - 1/decay))

	def slice_columns(self, columns, low_freq, high_freq, low, high):
		start_col = 0
		stop_col  = len(columns)
		if low_freq  is not None and low <= low_freq  <= high:
			start_col = sum(f<low_freq   for f in columns)
		if high_freq is not None and low <= high_freq <= high:
			stop_col  = sum(f<=high_freq for f in columns)
		return start_col, stop_col-1

	def summarize_pass(self):
		"pumps a bunch of data back into the args construct"
		freqs = set()
		f_cache = set()
		times = set()
		labels = set()
		min_z = 0
		max_z = -100
		start, stop = None, None

		for line in self.sdr_data:
			# ! line = [s.strip() for s in line.strip().split(',')]
			#line = [line[0], line[1]] + [float(s) for s in line[2:] if s]
			# ! line = [s for s in line if s]

			low  = int(line[2]) + self.args['offset_freq']
			high = int(line[3]) + self.args['offset_freq']
			step = float(line[4])
			t = line[0] + ' ' + line[1]
			if '-' not in line[0]:
				t = line[0]

			if self.args['low_freq']  is not None and high < self.args['low_freq']:
				continue
			if self.args['high_freq'] is not None and self.args['high_freq'] < low:
				continue
			if self.args['begin_time'] is not None and self.date_parse(t) < self.args['begin_time']:
				continue
			if self.args['end_time'] is not None and self.date_parse(t) > self.args['end_time']:
				break
			times.add(t)


			columns = list(self.frange(low, high, step))
			start_col, stop_col = self.slice_columns(columns, self.args['low_freq'], self.args['high_freq'], low, high)
			f_key = (columns[start_col], columns[stop_col], step)
			zs = line[6+start_col:6+stop_col+1]
			if not zs:
				continue
			if f_key not in f_cache:
				freq2 = list(self.frange(*f_key))[:len(zs)]
				freqs.update(freq2)
				#freqs.add(f_key[1])  # high
				#labels.add(f_key[0])  # low
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
		# print(f'{times=}')

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
			delta = round(delta / 10**int(math.log10(delta))) * 10**int(math.log10(delta))
			delta = int(delta)
			lower = int(math.ceil(min(freqs) / delta) * delta)
			labels = list(range(lower, int(max(freqs)), delta))

		height = len(times)
		pix_height = height
		print(f"{pix_height=}")
		if self.args['compress']:
			if self.args['compress'] > height:
				self.args['compress'] = 0
				print("Image too short, disabling time compression")
			if 0 < self.args['compress'] < 1:
				self.args['compress'] *= height
			if self.args['compress']:
				self.args['compress'] = -1 / self.args['compress']
				pix_height = self.time_compression(height, self.args['compress'])

		print("x: %i, y: %i, z: (%f, %f)" % (len(freqs), pix_height, self.args['db_limit'][0], self.args['db_limit'][1]))
		self.args['freqs'] = freqs
		self.args['times'] = times
		self.args['labels'] = labels
		self.args['pix_height'] = pix_height
		self.args['start_stop'] = (start, stop)
		self.args['pixel_bandwidth'] = step


	def default_palette(self):
		return [(i, i, 50) for i in range(256)]


	def charolastra_palette(self):
		p = []
		for i in range(1024):
			g = i / 1023.0
			c = colorsys.hsv_to_rgb(0.65-(g-0.08), 1, 0.2+g)
			p.append((int(c[0]*256), int(c[1]*256), int(c[2]*256)))
		return p



	def custom_palette(self):
		if self.args['rgbxy']:
			r,g,b,x,y = self.args['rgbxy']
		else:
			# Default: BRIGHT_YELLOW with Deep Contrast
			r=255; g=255; b=0; x=15; y=140;    
		p = []
		for i in range(x):
			p.append((0,0,0)) 
		for i in range(x,y):
			rp = int(float(r*(i-x))/(float(y-x)))
			gp = int(float(g*(i-x))/(float(y-x)))
			bp = int(float(b*(i-x))/(float(y-x)))
			p.append((rp, gp, bp))
		for i in range(y,256):
			p.append((r,g,b))
		return p

	def rgb_fn(self, palette, min_z, max_z):
		"palette is a list of tuples, returns a function of z"
		def rgb_inner(z):
			tone = (z - min_z) / (max_z - min_z)
			tone_scaled = int(tone * (len(palette)-1))
			return palette[tone_scaled]
		return rgb_inner
		

	def collate_row(self, x_size):
		# this is more fragile than the old code
		# sensitive to timestamps that are out of order
		old_t = None
		row = [0.0] * x_size
		print("collate_row()")
		for line in self.sdr_data:
			# ! line = [s.strip() for s in line.strip().split(',')]
			#line = [line[0], line[1]] + [float(s) for s in line[2:] if s]
			# ! line = [s for s in line if s]
			t = line[0] + ' ' + line[1]
			if '-' not in line[0]:
				t = line[0]
			if t not in self.args['times']:
				continue  # happens with live files and time cropping
			if old_t is None:
				old_t = t
			low = int(line[2]) + self.args['offset_freq']
			high = int(line[3]) + self.args['offset_freq']
			step = float(line[4])
			columns = list(self.frange(low, high, step))
			start_col, stop_col = self.slice_columns(columns, self.args['low_freq'], self.args['high_freq'], low, high)
			if self.args['low_freq'] and columns[stop_col] < self.args['low_freq']:
				continue
			if self.args['high_freq'] and columns[start_col] > self.args['high_freq']:
				continue
			start_freq = columns[start_col]
			if self.args['low_freq']:
				start_freq = max(self.args['low_freq'], start_freq)
			# sometimes fails?  skip or abort?
			x_start = self.args['freqs'].index(start_freq)
			zs = self.floatify(line[6+start_col:6+stop_col+1])
			if t != old_t:
				yield old_t, row
				row = [0.0] * x_size
			old_t = t
			for i in range(len(zs)):
				x = x_start + i
				if x >= x_size:
					continue
				row[x] = zs[i]
		yield old_t, row

	
	def push_pixels(self): 
		if self.args['nolabels']:
			self.args['tape_height'] = -1
			self.args['tape_pt'] = 0

		width = len(self.args['freqs'])
		rgb = self.rgb_fn(self.args['palette'](), self.args['db_limit'][0], self.args['db_limit'][1])

		# Створити порожній масив для зберігання значень пікселів
		img_array = np.zeros((width, self.args['tape_height'] + self.args['pix_height'] + 1, 3), dtype=np.uint8)

		height = len(self.args['times'])
		for t, zs in self.collate_row(width):
			y = self.args['times'].index(t)
			if not self.args['compress']:
				img_array[:, y+self.args['tape_height']+1, :] = [rgb(z) for z in zs]
				continue
			y = self.args['pix_height'] - self.time_compression(height - y, self.args['compress'])
			if old_y is None:
				old_y = y
			if old_y != y:
				img_array[:, old_y+self.args['tape_height']+1, :] = [rgb(avg/tally) for avg in average]
				tally = 0
				average = np.zeros(width)
			old_y = y
			average += zs
			tally += 1

		# Повертаємо масив NumPy, представляючи зображення
		return img_array



def read_lines_from_file(filename, start_line, num_lines):
	lines = []
	with open(filename, 'r') as file:
		# Пропустити перші (start_line - 1) рядків
		for _ in range(start_line - 1):
			next(file)
		# Прочитати наступні num_lines рядків
		for _ in range(num_lines):
			line = file.readline().strip()
			if not line:
				break
			lines.append(line)
	return lines


if __name__ == '__main__':
	hmap = Heatmap()
		
	sdr_data = read_lines_from_file('sdr_data.csv', 0, 50)
	
	hmap.set_sdr_data(sdr_data)
	hmap.summarize_pass()
	print("drawing")
	img = hmap.push_pixels()
	print("labeling")
	hmap.del_create_labels(img)
	print("saving")
	img.save("to1.png")
