import tkinter as tk
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

def animate(i):
	# Генеруємо випадкові дані для першого графіку
	num_points = 100
	xs = np.random.rand(num_points)
	ys = np.random.rand(num_points)
	zs = np.random.rand(num_points)

	# Очищаємо перший графік та малюємо нові дані
	ax1.clear()
	ax1.plot(xs, ys, zs)

	# Генеруємо випадкові дані для другого графіку
	xs = np.random.rand(num_points)
	ys = np.random.rand(num_points)
	zs = np.random.rand(num_points)

	# Очищаємо другий графік та малюємо нові дані
	ax2.clear()
	ax2.tick_params(axis='both', labelsize=8)
	ax2.set_xlabel('X Label', fontsize=10)
	ax2.set_ylabel('Y Label', fontsize=10)
	ax2.set_title('Title', fontsize=12)
	ax2.plot(xs, ys, zs)

	# Оновлюємо візуалізацію для першого графіку
	line1.draw()

def animate_periodically():
	animate(0)  # Викликаємо функцію анімації
	root.after(1000, animate_periodically)  # Повторюємо через 1000 мс (1 с)

root = tk.Tk()
root.geometry('800x800')  # Задаємо розмір вікна

# Вертикальний блок з простою формою
input_frame = tk.Frame(root)
input_frame.pack(side=tk.LEFT, fill=tk.BOTH)

# Текстове поле
text_entry = tk.Entry(input_frame)
text_entry.pack()

# Кнопка
button = tk.Button(input_frame, text="Натисни мене")
button.pack()

# Налаштування графіку
style.use('fivethirtyeight')

# Один графік з двома підграфіками (Axes)
fig1 = plt.figure(figsize=(5, 8), dpi=100)
ax1 = fig1.add_subplot(211)
ax2 = fig1.add_subplot(212)

# Зменшуємо розмір шрифту для розмітки осей та інших елементів
ax1.tick_params(axis='both', labelsize=8)
ax1.set_xlabel('X Label', fontsize=10)
ax1.set_ylabel('Y Label', fontsize=10)
ax1.set_title('Title', fontsize=12)

ax2.tick_params(axis='both', labelsize=8)
ax2.set_xlabel('X Label', fontsize=10)
ax2.set_ylabel('Y Label', fontsize=10)
ax2.set_title('Title', fontsize=12)

line1 = FigureCanvasTkAgg(fig1, root)
line1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH)

animate_periodically()

root.mainloop()
