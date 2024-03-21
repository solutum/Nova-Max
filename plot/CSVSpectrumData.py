from collections import defaultdict


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