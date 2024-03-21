from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDesktopWidget

from windows.LogWindow import LogWindow
from components.Logger import Logger
from utils import get_my_local_ip, get_server_ip_from_local_ip

class MainWindow(QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()

		self.log_window = LogWindow()
		self.logger = Logger(self.log_window)

		self.create_window()


	def create_window(self):
		# https://build-system.fman.io/qt-designer-download
		loadUi("window.ui", self)

		my_local_ip = get_my_local_ip()

		self.setWindowTitle(self.WIN_TITLE + "   |   Local IP: " + my_local_ip)
		if hasattr(self, 'DEBUG_DEFAULT_IP'):
			self.address_entry.setText(self.DEBUG_DEFAULT_IP)
		else:
			self.address_entry.setText(get_server_ip_from_local_ip(my_local_ip))

		self.menu_show_log.triggered.connect(self.on_menu_show_log)
		self.menu_show_help.triggered.connect(self.on_menu_show_help)
	
		self.connect_btn.clicked.connect(self.on_connect_btn)
		self.import_config_btn.clicked.connect(self.on_import_config_btn)
		self.get_config_btn.clicked.connect(self.on_get_config_btn)
		self.reset_btn.clicked.connect(self.on_reset_btn)
		self.save_btn.clicked.connect(self.on_save_btn)

		self.show()

	
	def set_connected_status_label(self, text, color='default'):
		if color == 'red':
			self.connected_status_label.setStyleSheet("color: red")
		elif color == 'green':
			self.connected_status_label.setStyleSheet("color: green")
		else :
			self.connected_status_label.setStyleSheet("")

		self.connected_status_label.setText(str(text))


	def get_form_val(self, field_name):
		return getattr(self, field_name).text()
	
	def set_form_val(self, field_name, value):
		return getattr(self, field_name).setText(str(value))


	def on_menu_show_log(self):
		self.log_window.show()

	def on_menu_show_help(self):
		instructions = """Довідка:

1. тут
2. коротка
3. інструкція
4. ...
5. ...

...

CONTACT_INFO
"""
		self.show_alert("Help", instructions)


	def update_form_configs(self, scan_ranges):
		# clear all fields
		for n in range(0, self.__class__.NUM_OF_RANGES):
			self.set_form_val(f'start_entries_{n}', '')
			self.set_form_val(f'end_entries_{n}', '')
			self.set_form_val(f'threshold_entries_{n}', '')
		# set new values
		for n, data in enumerate(scan_ranges):
			self.set_form_val(f'start_entries_{n}', data['start'])
			self.set_form_val(f'end_entries_{n}', data['end'])
			self.set_form_val(f'threshold_entries_{n}', data['threshold'])


	def form_enabled_status(self, enabled):
		for n in range(0, self.__class__.NUM_OF_RANGES):
			getattr(self, f'start_entries_{n}').setEnabled(enabled)
			getattr(self, f'end_entries_{n}').setEnabled(enabled)
			getattr(self, f'threshold_entries_{n}').setEnabled(enabled)

		self.get_config_btn.setEnabled(enabled)
		self.import_config_btn.setEnabled(enabled)
		self.reset_btn.setEnabled(enabled)
		self.save_btn.setEnabled(enabled)



	
	def show_alert(self, title, message):
		alert = QMessageBox()
		alert.setWindowTitle(title)
		alert.setText(str(message))
		alert.setStandardButtons(QMessageBox.Ok)

		alert.setStyleSheet("QMessageBox {width: 200px; height: 300px;}")
		alert.setFixedSize(200, 300)
		
		alert.exec_()
