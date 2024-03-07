from PIL import Image, ImageDraw, ImageFont
import os, sys, gzip, math, argparse, colorsys, datetime
from collections import defaultdict
from itertools import *


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
		args['palette'] = self.custom_palette
		r,g,b,x,y = ('000:255:255:025:150').split(":")
		args['rgbxy'] = (int(r), int(g), int(b), int(x), int(y))
		args['nolabels'] = True
		self.args = args

	def set_sdr_data(self, sdr_data):
		self.args['db_limit'] = None # oterwise error accumulating
		self.sdr_data = sdr_data

	def frange(self, start, stop, step):
		i = 0
		while (i*step + start <= stop):
			yield i*step + start
			i += 1

	def min_filter(self, row):
		size = 3
		result = []
		for i in range(size):
			here = row[i]
			near = row[0:i] + row[i+1:size]
			if here > min(near):
				result.append(here)
				continue
			result.append(min(near))
		for i in range(size-1, len(row)):
			here = row[i]
			near = row[i-(size-1):i]
			if here > min(near):
				result.append(here)
				continue
			result.append(min(near))
		return result

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

	def freq_parse(self, s):
		suffix = 1
		if s.lower().endswith('k'):
			suffix = 1e3
		if s.lower().endswith('m'):
			suffix = 1e6
		if s.lower().endswith('g'):
			suffix = 1e9
		if suffix != 1:
			s = s[:-1]
		return float(s) * suffix

	def duration_parse(self, s):
		suffix = 1
		if s.lower().endswith('s'):
			suffix = 1
		if s.lower().endswith('m'):
			suffix = 60
		if s.lower().endswith('h'):
			suffix = 60 * 60
		if s.lower().endswith('d'):
			suffix = 24 * 60 * 60
		if suffix != 1 or s.lower().endswith('s'):
			s = s[:-1]
		return float(s) * suffix

	def date_parse(self, s):
		if '-' not in s:
			return datetime.datetime.fromtimestamp(int(s))
		return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')


	def gzip_wrap(self, path):
		"hides silly CRC errors"
		iterator = gzip.open(path, 'rb')
		running = True
		while running:
			try:
				line = next(iterator)
				if type(line) == bytes:
					line = line.decode('utf-8')
				yield line
			except IOError:
				running = False

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
			line = [s.strip() for s in line.strip().split(',')]
			#line = [line[0], line[1]] + [float(s) for s in line[2:] if s]
			line = [s for s in line if s]

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
		print(f'{times=}')

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

	def extended_palette(self):
		p = [(0,0,50)]
		for i in range(1, 256):
			p.append((i, i-1, 50))
			p.append((i-1, i, 50))
			p.append((i, i, 50))
		return p

	def charolastra_palette(self):
		p = []
		for i in range(1024):
			g = i / 1023.0
			c = colorsys.hsv_to_rgb(0.65-(g-0.08), 1, 0.2+g)
			p.append((int(c[0]*256), int(c[1]*256), int(c[2]*256)))
		return p

	def twente_palette(self):
		p = []
		for i in range(20, 100, 2):
			p.append((0, 0, i))
		for i in range(256):
			g = i / 255.0
			p.append((int(g*255), 0, int(g*155)+100))
		for i in range(256):
			p.append((255, i, 255))
		# intentionally blow out the highs
		for i in range(100):
			p.append((255, 255, 255))
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
			line = [s.strip() for s in line.strip().split(',')]
			#line = [line[0], line[1]] + [float(s) for s in line[2:] if s]
			line = [s for s in line if s]
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

	def new_push_pixels(self):
		if self.args['nolabels']:
			self.args['tape_height'] = -1
			self.args['tape_pt'] = 0
		"returns PIL img"
		width = len(self.args['freqs'])
		rgb = self.rgb_fn(self.args['palette'](), self.args['db_limit'][0], self.args['db_limit'][1])
		img = Image.new("RGB", (width, self.args['tape_height'] + self.args['pix_height'] + 1))
		pix = img.load()
		x_size = img.size[0]
		average = [0.0] * width
		tally = 0
		old_y = None
		height = len(self.args['times'])
		for y, (t, zs) in enumerate(self.collate_row(x_size)):
			if not self.args['compress']:
				for x in range(len(zs)):
					pix[x, self.args['pix_height'] - 1 - y] = rgb(zs[x])
				continue
			# ugh
			y = self.args['pix_height'] - self.time_compression(height - y, self.args['compress'])
			if old_y is None:
				old_y = y
			if old_y != y:
				for x in range(len(average)):
					pix[x, self.args['pix_height'] - 1 - old_y] = rgb(average[x] / tally)
				tally = 0
				average = [0.0] * width
			old_y = y
			for x in range(len(zs)):
				average[x] += zs[x]
			tally += 1

		return img
	
	def push_pixels(self): # ORIGINAL
		if self.args['nolabels']:
			self.args['tape_height'] = -1
			self.args['tape_pt'] = 0
		"returns PIL img"
		width = len(self.args['freqs'])
		rgb = self.rgb_fn(self.args['palette'](), self.args['db_limit'][0], self.args['db_limit'][1])
		img = Image.new("RGB", (width, self.args['tape_height'] + self.args['pix_height'] + 1))
		pix = img.load()
		x_size = img.size[0]
		average = [0.0] * width
		tally = 0
		old_y = None
		height = len(self.args['times'])
		for t, zs in self.collate_row(x_size):
			y = self.args['times'].index(t)
			if not self.args['compress']:
				for x in range(len(zs)):
					pix[x,y+self.args['tape_height']+1] = rgb(zs[x])
				continue
			# ugh
			y = self.args['pix_height'] - self.time_compression(height - y, self.args['compress'])
			if old_y is None:
				old_y = y
			if old_y != y:
				for x in range(len(average)):
					pix[x,old_y+self.args['tape_height']+1] = rgb(average[x]/tally)
				tally = 0
				average = [0.0] * width
			old_y = y
			for x in range(len(zs)):
				average[x] += zs[x]
			tally += 1
		img = img.transpose(Image.FLIP_TOP_BOTTOM)
		return img


	def closest_index(self, n, m_list, interpolate=False):
		"assumes sorted m_list, returns two points for interpolate"
		i = len(m_list) // 2
		jump = len(m_list) // 2
		while jump > 1:
			i_down = i - jump
			i_here = i
			i_up =   i + jump
			if i_down < 0:
				i_down = i
			if i_up >= len(m_list):
				i_up = i
			e_down = abs(m_list[i_down] - n)
			e_here = abs(m_list[i_here] - n)
			e_up   = abs(m_list[i_up]   - n)
			e_best = min([e_down, e_here, e_up])
			if e_down == e_best:
				i = i_down
			if e_up == e_best:
				i = i_up
			if e_here == e_best:
				i = i_here
			jump = jump // 2
		if not interpolate:
			return i
		if n < m_list[i] and i > 0:
			return i-1, i
		if n > m_list[i] and i < len(m_list)-1:
			return i, i+1
		return i, i

	def word_aa(self, label, pt, fg_color, bg_color):
		f = ImageFont.truetype("Vera.ttf", pt*3)
		s = f.getsize(label)
		s = (s[0], pt*3 + 3)  # getsize lies, manually compute
		w_img = Image.new("RGB", s, bg_color)
		w_draw = ImageDraw.Draw(w_img)
		w_draw.text((0, 0), label, font=f, fill=fg_color)
		return w_img.resize((s[0]//3, s[1]//3), Image.ANTIALIAS)

	def blend(self, percent, c1, c2):
		"c1 and c2 are RGB tuples"
		# probably isn't gamma correct
		r = c1[0] * percent + c2[0] * (1 - percent)
		g = c1[1] * percent + c2[1] * (1 - percent)
		b = c1[2] * percent + c2[2] * (1 - percent)
		c3 = map(int, map(round, [r,g,b]))
		return tuple(c3)

	def tape_lines(self, draw, freqs, interval, y1, y2, used=set()):
		min_f = min(freqs)
		max_f = max(freqs)
		"returns the number of lines"
		low_f = (min_f // interval) * interval
		high_f = (1 + max_f // interval) * interval
		hits = 0
		blur = lambda p: self.blend(p, (255, 255, 0), (0, 0, 0))
		for i in range(int(low_f), int(high_f), int(interval)):
			if not (min_f < i < max_f):
				continue
			hits += 1
			if i in used:
				continue
			x1,x2 = self.closest_index(i, self.args['freqs'], interpolate=True)
			if x1 == x2:
				draw.line([x1,y1,x1,y2], fill='black')
			else:
				percent = (i - self.args['freqs'][x1]) / float(self.args['freqs'][x2] - self.args['freqs'][x1])
				draw.line([x1,y1,x1,y2], fill=blur(percent))
				draw.line([x2,y1,x2,y2], fill=blur(1-percent))
			used.add(i)
		return hits

	def tape_text(self, img, freqs, interval, y, used=set()):
		min_f = min(freqs)
		max_f = max(freqs)
		low_f = (min_f // interval) * interval
		high_f = (1 + max_f // interval) * interval
		for i in range(int(low_f), int(high_f), int(interval)):
			if i in used:
				continue
			if not (min_f < i < max_f):
				continue
			x = self.closest_index(i, freqs)
			s = str(i)
			if interval >= 1e6:
				s = '%iM' % (i/1e6)
			elif interval > 1000:
				s = '%ik' % ((i/1e3) % 1000)
				if s.startswith('0'):
					s = '%iM' % (i/1e6)
			else:
				s = '%i' % (i%1000)
				if s.startswith('0'):
					s = '%ik' % ((i/1e3) % 1000)
				if s.startswith('0'):
					s = '%iM' % (i/1e6)
			w = self.word_aa(s, self.args['tape_pt'], 'black', 'yellow')
			img.paste(w, (x - w.size[0]//2, y))
			used.add(i)

	def shadow_text(self, draw, x, y, s, font, fg_color='white', bg_color='black'):
		draw.text((x+1, y+1), s, font=font, fill=bg_color)
		draw.text((x, y), s, font=font, fill=fg_color)

	def create_labels(self, img):
		if(self.args['nolabels']):
			return
		draw = ImageDraw.Draw(img)
		font = ImageFont.load_default()
		pixel_bandwidth = self.args['pixel_bandwidth']

		draw.rectangle([0,0,img.size[0],self.args['tape_height']], fill='yellow')
		min_freq = min(self.args['freqs'])
		max_freq = max(self.args['freqs'])
		delta = max_freq - min_freq
		width = len(self.args['freqs'])
		height = len(self.args['times'])
		label_base = 9

		for i in range(label_base, 0, -1):
			interval = int(10**i)
			low_f = (min_freq // interval) * interval
			high_f = (1 + max_freq // interval) * interval
			hits = len(range(int(low_f), int(high_f), interval))
			if hits >= 4:
				label_base = i
				break
		label_base = 10**label_base

		for scale,y in [(1,10), (5,15), (10,19), (50,22), (100,24), (500, 25)]:
			hits = self.tape_lines(draw, self.args['freqs'], label_base/scale, y, self.args['tape_height'])
			pixels_per_hit = width / hits
			if pixels_per_hit > 50:
				self.tape_text(img, self.args['freqs'], label_base/scale, y-self.args['tape_pt'])
			if pixels_per_hit < 10:
				break

		start, stop = self.args['start_stop']
		duration = stop - start
		duration = duration.days * 24*60*60 + duration.seconds + 30
		pixel_height = duration / len(self.args['times'])
		hours = int(duration / 3600)
		minutes = int((duration - 3600*hours) / 60)

		if self.args['time_tick']:
			label_format = "%H:%M:%S"
			if self.args['time_tick'] % (60*60*24) == 0:
				label_format = "%Y-%m-%d"
			elif self.args['time_tick'] % 60 == 0:
				label_format = "%H:%M"
			label_next = datetime.datetime(start.year, start.month, start.day, start.hour)
			tick_delta = datetime.timedelta(seconds = self.args['time_tick'])
			while label_next < start:
				label_next += tick_delta
			last_y = -100
			full_height = self.args['pix_height']
			for y,t in enumerate(self.args['times']):
				label_time = self.date_parse(t)
				if label_time < label_next:
					continue
				if self.args['compress']:
					y = full_height - self.time_compression(height - y, self.args['compress'])
				if y - last_y > 15:
					self.shadow_text(draw, 2, y+self.args['tape_height'], label_next.strftime(label_format), font)
					last_y = y
				label_next += tick_delta

		margin = 2
		if self.args['time_tick']:
			margin = 60
		self.shadow_text(draw, margin, img.size[1] - 45, 'Duration: %i:%02i' % (hours, minutes), font)
		self.shadow_text(draw, margin, img.size[1] - 35, 'Range: %.2fMHz - %.2fMHz' % (min_freq/1e6, (max_freq+pixel_bandwidth)/1e6), font)
		self.shadow_text(draw, margin, img.size[1] - 25, 'Pixel: %.2fHz x %is' % (pixel_bandwidth, int(round(pixel_height))), font)
		self.shadow_text(draw, margin,  img.size[1] - 15, 'Started: {0}'.format(start), font)
	# bin size


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
	hmap.create_labels(img)
	print("saving")
	img.save("to1.png")
