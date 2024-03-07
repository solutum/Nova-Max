import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Створення основного вікна Tkinter
root = tk.Tk()
root.title("Графіки з Tkinter та Matplotlib")
root.geometry("800x600")

# Створення рамки для лівого вертикального блоку з кнопками
button_frame = ttk.Frame(root, width=200, height=600)
button_frame.pack(side="left", fill="y")

# Додавання кнопок в лівий блок
button1 = ttk.Button(button_frame, text="Графік 1")
button1.pack(pady=10)
button2 = ttk.Button(button_frame, text="Графік 2")
button2.pack(pady=10)

# Створення рамки для правого блоку з графіками
plot_frame = ttk.Frame(root)
plot_frame.pack(side="right", fill="both", expand=True)

# Створення фігури Matplotlib
fig, axes = plt.subplots(2, 1)

# Побудова прикладних графіків
x = [1, 2, 3, 4, 5]
y1 = [10, 20, 15, 25, 30]
y2 = [5, 8, 12, 10, 15]

axes[0].plot(x, y1)
axes[0].set_title("Графік 1")
axes[0].set_xlabel("X-ось")
axes[0].set_ylabel("Y-ось")

axes[1].plot(x, y2)
axes[1].set_title("Графік 2")
axes[1].set_xlabel("X-ось")
axes[1].set_ylabel("Y-ось")

# Відображення фігури Matplotlib у вікні Tkinter
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.draw()
canvas.get_tk_widget().pack(fill="both", expand=True)

# Запуск головного циклу подій Tkinter
root.mainloop()
