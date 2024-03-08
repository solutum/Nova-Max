# https://github.com/davesmotleyprojects/RTL_SpectrumSweeper

# import os
import sys
# import time
# import subprocess
import datetime
import platform
from collections import defaultdict

import numpy as np
import tkinter as tk
# from tkinter import ttk
import PIL.Image as Image

# import matplotlib as mpl
import matplotlib.pyplot as plt
# import matplotlib.image as mpimg
# import matplotlib.gridspec as gridspec
# import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import style

from heatmap import Heatmap


# cmd_str = "RTL_SpectrumSweeper -a 75 -s 15 --palette custom -i 3s -e 60m -g 28 -f 88M:108M:5k test.csv"  
cmd_str = "RTL_SpectrumSweeper -a 101 -s 101 --palette charolastra -c 25% -i 3s -g 28 -f 88M:108M:10k test.csv"         
#cmd_str = "RTL_SpectrumSweeper -a 101 -s 101 --palette custom --rgbxy 0:255:255:25:150 -c 25% -i 3s -e 60m -g 28 -f 88M:108M:10k test.csv"   
#cmd_str = "RTL_SpectrumSweeper -a 151 -s 201 -o -125000000 --ratio 5:4 --palette custom --rgbxy 0:255:255:25:150 -i 3s -g 28 -f 132000k:132200k:100 test.csv"    
# cmd_str = "RTL_SpectrumSweeper -a 151 -s 201 -o -125000000 --ratio 6:2 --palette custom -i 3s -g 28 -f 132000k:132200k:100 test.csv"    
#cmd_str = "RTL_SpectrumSweeper -a 200 -s 100 -i 3s -e 60m -g 28 -f 88M:108M:5k test.csv" 

print("\n" + cmd_str)
sys.argv = cmd_str.split()


"""############################################################################

	Global Variables

############################################################################"""

class global_vars:
	
	def __init__(self):
		self.csv_data = []

		self.heatmap = Heatmap()

		self.csv_sdr_data_filename = "sdr_data.csv" # .csv
		self.csv_data_counter = 0
		self.waterfall_vertical_size = 1
		self.waterfall_max_vertical_size = 69

		self.sweeptime = 3.0

		self.animation_interval = 500 # 1000 - 1 sec

		self.opt_str = ""
		self.rtl_str = ""
		self.hmp_str = ""
		
		# self.stop = 101       # 0 = autostop disabled
							# 1 = autostop when window filled
							# N = autostop when N sweeps completed
		self.aspect = 70     # 0 = stretch/shrink window to fill display
							# 1 = force image aspect ratio to window
							# N = force waterfall to N pixel height
		self.offset = 0
		
		self.trace_color = "#FFFF00"

		self.ready = False
		self.done = False
		
		self.csv_path = ""
		self.old_csv_size = 0

		self.root = None
		# self.scrn_width_in = root.winfo_screenmmwidth() / 25.4
		# self.scrn_height_in = root.winfo_screenmmheight() / 25.4

		self.combined_image = None
		self.tmax = 0.0

		self.fig_title = ""
		self.rows = [6,2]
		self.fig = None
		self.ax1 = None
		self.ax2 = None

		self.ax1_w = 0
		self.ax1_h = 0
		self.ax2_w = 0
		self.ax2_h = 0

		self.rtl_proc = None

		self.anim = None 
		self.anim_intvl = self.sweeptime * 1000

		self.x_vals = []
		self.y_vals = []
		
		
g = global_vars()
		


def initialize_plot():
	print("\nInitializing plot... ", end='', flush=True)
	
	try:
		   
		g.root = tk.Tk()
		g.root.title("Nova Max v0.1")
		g.root.geometry("1200x800")

		# Вертикальний блок з простою формою
		input_frame = tk.Frame(g.root)
		input_frame.pack(side=tk.LEFT, fill=tk.BOTH)

		# Текстове поле
		text_entry = tk.Entry(input_frame)
		text_entry.pack()

		# Кнопка
		button = tk.Button(input_frame, text="_btn_")
		button.pack()


		# Один графік з двома підграфіками (Axes)
		g.fig = plt.figure(figsize=(5, 8), dpi=100)
		g.ax1 = g.fig.add_subplot(211)
		g.ax2 = g.fig.add_subplot(212)
	
		"""if (platform.system() == "Windows"):
			plt.rcParams["figure.figsize"] = [scrn_width_in, scrn_height_in*0.9]
			gs = gridspec.GridSpec(g.rows[0], 1, figure=g.fig)
		else:
			gs = gridspec.GridSpec(g.rows[0], 1)"""
			
		#g.ax1 = g.fig.add_subplot(gs[0:g.rows[1],0])
		#g.ax2 = g.fig.add_subplot(gs[(g.rows[0]-g.rows[1]):,0])
		
		# print("\n{}, {}, {}" .format(g.rows, g.rows[0], g.rows[1]))
		"""g.ax1 = g.fig.add_subplot(gs[0:g.rows[1],0])
		g.ax2 = g.fig.add_subplot(gs[g.rows[1]:g.rows[0],0])"""
		#g.ax1 = g.fig.add_subplot(gs[0:1,0])
		#g.ax2 = g.fig.add_subplot(gs[1:3,0])


		g.ax1.margins(0)
		g.ax2.margins(0)
		g.ax1.set_facecolor('#000000')
		g.ax2.set_facecolor('#000000')
		g.ax1.set_aspect('auto')
		g.ax2.set_aspect('auto')
		# g.fig.canvas.draw() # !

		
		bbox = g.ax2.get_window_extent().transformed(g.fig.dpi_scale_trans.inverted())
		g.ax2_w, g.ax2_h = int(bbox.width*g.fig.dpi), int(bbox.height*g.fig.dpi)
		bgnd = Image.new("RGB",(g.ax2_w,g.ax2_h),'#000000') 
		g.ax2.imshow(bgnd)
		
		#print("ax2 window size: width={}, height={}" .format(g.ax2_w, g.ax2_h))
		#print("bgnd2 image size: width={}, height={}" .format(bg2.size[0],bg2.size[1]))
		
		
		# This is the same code that gets executed by the animation
		# g.ax1.clear()
		# g.ax1.plot(g.x_vals, g.y_vals, color='yellow', linewidth=0.75) 
		# y_min = min(g.y_vals); y_max = max(g.y_vals)
		# y_diff = y_max-y_min; y_margin = y_diff *0.10
		# g.ax1.set_ylim([min(g.y_vals)-y_margin, max(g.y_vals)+y_margin])
		# g.ax1.set_xlim([g.x_vals[0], g.x_vals[-1]])
		"""g.ax1.tick_params(axis='both', labelsize=8)
		g.ax1.set_title("Title", fontsize=12)
		g.ax1.set_xlabel("Frequency (MHz)", fontsize=10)
		g.ax1.set_ylabel("Power (dB)", fontsize=10)"""
		# g.fig.canvas.draw() # !

		# Відображення фігури Matplotlib у вікні Tkinter
		g.fig.canvas = FigureCanvasTkAgg(g.fig, g.root)
		# g.fig.canvas.draw()
		g.fig.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH)

		# Запуск головного циклу подій Tkinter
				
		print("done")
		
	except Exception as e:
		
		print("\nException occurred in initialize_plot")
		print(e)


def animation_poll():
	print(f"\nanimation_poll(i): {datetime.datetime.now()}")

	try:

		g.csv_data = read_lines_from_file(g.csv_sdr_data_filename, g.csv_data_counter, g.waterfall_vertical_size)
		g.csv_data_counter += 1
		if g.waterfall_vertical_size < g.waterfall_max_vertical_size:
			g.waterfall_vertical_size += 1

		print(f'waterfall_vertical_size = {g.waterfall_vertical_size}')

		update_waterfall()

		try:
			g.ax2.imshow(g.combined_image)
			g.ax2.set_aspect('auto')
			g.ax2.tick_params(axis='both', labelsize=3)
			g.ax2.set_xlabel("FFT Bins (N)", fontsize=5)
			g.ax2.set_ylabel("Spectrum Sweeps (N)", fontsize=5)
			# g.fig.canvas.draw()
		except Exception as e:
			print(f'Error: {e}')

		flatten_data_for_spectrum()

		try:
			g.ax1.clear()
			g.ax1.plot(g.x_vals, g.y_vals, color=g.trace_color, linewidth=0.75) 
			y_min = min(g.y_vals); y_max = max(g.y_vals)
			print("{:0.1f}, {:0.1f}" .format(y_min, y_max))
			y_diff = y_max-y_min; y_margin = y_diff *0.10
			g.ax1.set_ylim([min(g.y_vals)-y_margin, max(g.y_vals)+y_margin])
			g.ax1.set_xlim([g.x_vals[0], g.x_vals[-1]])
			g.ax1.tick_params(axis='both', labelsize=3)
			# g.ax1.set_title("Title", fontsize=10)
			g.ax1.set_xlabel("Frequency (MHz)", fontsize=5)
			g.ax1.set_ylabel("Power (dB)", fontsize=5)
			
		except Exception as e:
			# print("\nException occurred in animation_poll")
			print(e)

		plt.tight_layout()
		g.fig.canvas.draw()
		
		print(f"Finished animation poll at {datetime.datetime.now()}")

		
		"""if g.done:
			print("\nauto-stop criteria was met.")
			# stop the animation polling. 
			g.anim.event_source.stop()
			# g.rtl_proc.terminate()
			print("The rtl_power subprocess was terminated.")"""

		# time.sleep(3)		

	except Exception as e:
		
		print("\nException occurred in animation_poll")
		print(e)
		

	
def update_waterfall():
	print("update_waterfall():")
	# return False
	
	try:

		g.heatmap.set_sdr_data(g.csv_data)
		g.heatmap.summarize_pass()
		img = g.heatmap.push_pixels()
		w1, h1 = img.size


		if ((g.aspect-h1) > 0):
			bg2 = Image.new("RGB",(w1,g.aspect-h1),'#000000') 
			w,h = bg2.size
			#print("bgnd2 image size: width={}, height={}" .format(w,h))
			g.combined_image = np.concatenate((img, bg2), axis = 0)
			w,h = g.combined_image.shape[1], g.combined_image.shape[0]
			#print("combined image size: width={}, height={}" .format(w,h))
			g.tmax = h
		else:
			#print("using unmodified heatmap image")
			g.combined_image = img
			g.tmax = h1

		return False
		
		fstr = ("{}.png" .format(g.filename))
		print("opening: {}" .format(fstr))
		img1 = Image.open(fstr)
		#print("opened image file")
		w1,h1 = img1.size
		print("image size: width={}, height={}" .format(w1,h1))
		print("ax2 window size: width={}, height={}" .format(g.ax2_w, g.ax2_h))
		
		wpcnt = (g.ax2_w / float(w1))   
		h2size = int((float(g.ax2_h)/float(wpcnt))-h1)
		
		print("wpcnt={}, h2size={}" .format(wpcnt, h2size))
		print("Remaining window size = {}" .format(h2size))
		
		
		'''
		self.stop = 0       # 0 = autostop disabled
							# 1 = autostop when window filled
							# N = autostop when N sweeps completed
		self.aspect = 0     # 0 = stretch/shrink window to fill display
							# 1 = force image aspect ratio to window
							# N = force waterfall to N pixel height
		'''
		
		
		# if g.stop == 0 (disabled)
		if (0 == g.stop):
			pass # do nothing
	
		# if g.stop == 1 (stop when window filled)
		elif (1 == g.stop):
			print("auto-stopping in {} sweeps" .format(h2size))
			# and the window is full
			if (h2size <= 0):
				g.done = True  
		
		# if g.stop == N (stop after N sweeps)
		else:
			# and the waterfal is more than N pixels high
			print(f"auto-stopping in {(g.stop-h1)} sweeps. {h1} >= g.stop : '{g.stop}'")
			if (h1 >= g.stop):
				g.done = True
			

		if (0 == g.aspect):
			#print("using unmodified heatmap image")
			g.combined_image = img1
			g.tmax = h1
				
		elif ((1 == g.aspect) and (h2size > 0)):
			bg2 = Image.new("RGB",(w1,h2size),'#000000') 
			w,h = bg2.size
			#print("bgnd2 image size: width={}, height={}" .format(w,h))
			g.combined_image = np.concatenate((img1, bg2), axis = 0)
			w,h = g.combined_image.shape[1], g.combined_image.shape[0]
			#print("combined image size: width={}, height={}" .format(w,h))
			g.tmax = h 
		
		else:
			if ((g.aspect-h1) > 0):
				bg2 = Image.new("RGB",(w1,g.aspect-h1),'#000000') 
				w,h = bg2.size
				#print("bgnd2 image size: width={}, height={}" .format(w,h))
				g.combined_image = np.concatenate((img1, bg2), axis = 0)
				w,h = g.combined_image.shape[1], g.combined_image.shape[0]
				#print("combined image size: width={}, height={}" .format(w,h))
				g.tmax = h
			else:
				#print("using unmodified heatmap image")
				g.combined_image = img1
				g.tmax = h1

		#print("done")
		
	except Exception as e:
		
		print("\nException occurred in update_waterfall")
		print(e)
	

def frange(start, stop, step):
	i = 0
	f = start
	while f <= stop:
		f = start + step*i
		yield f
		i += 1


def flatten_data_for_spectrum():
	print("flatten_data_for_spectrum()")

	g.x_vals = []; g.y_vals = [];

	sums = defaultdict(float)
	counts = defaultdict(int)

	# for line in g.csv_data:
	line = g.csv_data[0] # GET only 1st row
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
		# print(','.join([str(f), str(ave[f])]))

		g.x_vals.append(float(f))
		g.y_vals.append(float(ave[f]))
		g.x_vals[-1] += g.offset
		g.x_vals[-1] /= 1000000.0
	

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

def animate_periodically():
	animation_poll()  # Викликаємо функцію анімації
	g.root.after(g.animation_interval, animate_periodically)  # Повторюємо через 1000 мс (1 с)

def main():
	
	try:
		initialize_plot()

	
		# g.anim = animation.FuncAnimation(g.fig, animation_poll, interval=g.anim_intvl)
		"""g.anim = animation.FuncAnimation(g.fig, animation_poll, interval=1000)
		plt.tight_layout()"""
		
		print("\nRunning... ", end='', flush=True)
		# plt.show()

		animate_periodically()

		g.root.mainloop()
		# time.sleep(40)
		print("done")
		
	except Exception as e:		
		print(f"\nException occurred in main\n{e}")
	
	finally:
		
		print("\nrtl_scan Finished!")


if __name__ == '__main__':
	main()
