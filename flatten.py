import sys
from collections import defaultdict


sums = defaultdict(float)
counts = defaultdict(int)

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

def frange(start, stop, step):
	i = 0
	f = start
	while f <= stop:
		f = start + step*i
		yield f
		i += 1

lines = read_lines_from_file('from.csv', 0, 3)

for line in lines:
	line = line.strip().split(', ')
	low = int(line[2])
	high = int(line[3])
	step = float(line[4])
	weight = int(line[5])
	dbm = [float(d) for d in line[6:]]
	for f,d in zip(frange(low, high, step), dbm):
		sums[f] += d*weight
		counts[f] += weight

ave = defaultdict(float)
for f in sums:
	ave[f] = sums[f] / counts[f]

for f in sorted(ave):
	print(','.join([str(f), str(ave[f])]))
	
"""132000000.0,-55.28900653594771
132000097.66,-55.85134640522876
132000195.32,-55.496575163398695
132000292.98,-55.98321568627451
132000390.64,-54.944797385620916
132000488.3,-55.617581699346395
132000585.96,-55.5604183006536
132000683.62,-54.975686274509805"""
