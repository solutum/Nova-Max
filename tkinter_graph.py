# https://github.com/davesmotleyprojects/RTL_SpectrumSweeper

from collections import defaultdict
import datetime
import numpy as np
import tkinter as tk
import PIL.Image as Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from plot.heatmap import Heatmap
from utils import read_lines_from_file


class GlobalVars:
	
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
		
		
g = GlobalVars()
		

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
	



		g.ax1.margins(0)
		g.ax2.margins(0)
		g.ax1.set_facecolor('#000000')
		g.ax2.set_facecolor('#000000')
		g.ax1.set_aspect('auto')
		g.ax2.set_aspect('auto')

		bbox = g.ax2.get_window_extent().transformed(g.fig.dpi_scale_trans.inverted())
		g.ax2_w, g.ax2_h = int(bbox.width*g.fig.dpi), int(bbox.height*g.fig.dpi)
		bgnd = Image.new("RGB",(g.ax2_w,g.ax2_h),'#000000') 
		g.ax2.imshow(bgnd)

		# Відображення фігури Matplotlib у вікні Tkinter
		g.fig.canvas = FigureCanvasTkAgg(g.fig, g.root)
		# g.fig.canvas.draw()
		g.fig.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH)

		# Запуск головного циклу подій Tkinter
				
		print("done")
		
	except Exception as e:		
		print(f"\nException occurred in initialize_plot: {e}")


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

	except Exception as e:
		print(f"\nException occurred in animation_poll: {e}")

	
def update_waterfall():
	print("update_waterfall():")
	
	try:
		g.heatmap.set_sdr_data(g.csv_data)
		g.heatmap.summarize_pass()
		img = g.heatmap.push_pixels()
		w1, h1 = img.size


		if ((g.aspect-h1) > 0):
			bg2 = Image.new("RGB",(w1,g.aspect-h1),'#000000') 
			w,h = bg2.size
			g.combined_image = np.concatenate((img, bg2), axis = 0)
			w,h = g.combined_image.shape[1], g.combined_image.shape[0]
			#print("combined image size: width={}, height={}" .format(w,h))
			g.tmax = h
		else:
			#print("using unmodified heatmap image")
			g.combined_image = img
			g.tmax = h1

		return False
		
	except Exception as e:
		print(f"\nException occurred in update_waterfall: {e}")
	

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
