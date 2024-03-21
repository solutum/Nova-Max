# https://www.pythonguis.com/tutorials/pyside6-embed-pyqtgraph-custom-widgets/
import sys
import json
from pprint import pprint
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtCore import pyqtSignal, QObject, QDir
# https://build-system.fman.io/qt-designer-download

from components.SocketConnection import SocketConnection
from components.Logger import Logger
from components.OutputCommand import OutputCommand
from components.EventHandler import EventHandler
from windows.MainWindow import MainWindow
from windows.PlotWindow import PlotWindow


class Signals(QObject):
	show_alert = pyqtSignal(str, str)
	show_plot_window = pyqtSignal()


class NovaApp(MainWindow):
	
	WIN_TITLE = "Nova max v0.1"
	# DEBUG_DEFAULT_IP = "192.168.88.51"
	DEFAULT_PORT = "12345"
	NUM_OF_RANGES = 5  # count of ranges in window-form
	MAIN_FREQ = 900  # config in "SCAN_RANGES" (need for on_save_btn())

	def __init__(self):
		super().__init__()
		self.sdr_config = dict()

		self.signals = Signals()
		# self.signals.about_to_close.connect(self.about_to_close)
		self.signals.show_alert.connect(self.show_alert)
		self.signals.show_plot_window.connect(self.show_plot_window)

		self.plot = PlotWindow("2250-2440 MHz   -30.0 dB")

		self.need_to_show_save_msg = False

		self.socketConnection = SocketConnection()
		self.outputCommand = OutputCommand(self.socketConnection)

		EventHandler.add_event(
			EventHandler.EVENT_ON_CONNECTION_SUCCESS, self.on_connection_success
		)
		EventHandler.add_event(EventHandler.EVENT_ON_GET_CONFIGS, self.on_get_configs)
		EventHandler.add_event(
			EventHandler.EVENT_ON_SCAN_RANGE_DATA, self.on_scan_range_data
		)
		# EventHandler.add_event(EventHandler.EVENT_ON_GET_ERROR, self.on_error)


	# ! ################
	def on_scan_range_data(self, data):
		pprint(data)
		self.plot.update_plot(data['signals']['all'])
		if self.need_to_show_save_msg:
			# self.logger.log_message(f"on_save_btn. Config was saved.")
			# self.show_alert("Alert", "Config was saved.")
			self.signals.show_alert.emit("Alert", "Config was saved.")
			self.need_to_show_save_msg = False
			self.set_connected_status_label("Connected", "green")

	def closeEvent(self, event):
		self.log_window.close()
		if hasattr(self, 'plot'):
			self.plot.close()
		self.socketConnection.thread_stop_listening()
		# sys.exit(0)
	
	def on_connection_success(self, data):
		self.outputCommand.get_configs()

	def on_get_configs(self, data):
		print(f"\non_get_configs =\n{data}\n")
		self.sdr_config = data
		pprint(data["SCAN_RANGES"])
		self.update_form_configs(data["SCAN_RANGES"])


	def on_status_change(self, is_ok_status, message):
		if is_ok_status:
			self.set_connected_status_label(message, "green")
			self.form_enabled_status(True)
			
			# self.show_plot_window()
			# self.signals.show_plot_window.emit()

			self.on_get_config_btn()
		else:
			self.need_to_show_save_msg = False
			self.set_connected_status_label(message, "red")
			self.form_enabled_status(False)


	# def cb_open_log_window(self):
	# 	self.logging_window.show()
	# 	self.logger.log_message("Log window opened.")

	
	def show_plot_window(self):
		try:
			
			self.plot.show()
			# self.plot.start_animation()
		except Exception as e:
			print(e)


	def config_file_prase(self, file_data):
		json_data = json.loads(file_data)
		pprint(json_data)
		if (
			"BIN_WIDTH" in json_data
			and "SORT_REVERSE" in json_data
			and len(json_data["SCAN_RANGES"]) > 0
		):
			# update existing config var
			self.on_get_configs(json_data)
		else:
			self.show_alert("Alert", "Wrong json config file!")


	# ############# BTN ################
	def on_connect_btn(self):
		host = self.get_form_val('address_entry')
		port = self.__class__.DEFAULT_PORT
		# print(host, port)

		self.set_connected_status_label("Trying to connect ...")
		connection_status = self.socketConnection.thread_start_listening(
			host, port, self.on_status_change
		)

	def on_get_config_btn(self):
		# self.setFocus()
		print("on_get_config_btn()")
		self.outputCommand.get_configs()

	def on_import_config_btn(self):
		# on_configs_file_prase
		print("on_import_config_btn()")
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		file_name, _ = QFileDialog.getOpenFileName(self, "Виберіть файл", QDir.homePath(), "JSON files (*.json);;All files (*.*)", options=options)
		if file_name:
			with open(file_name, 'r') as file:
				file_content = file.read()
				self.config_file_prase(file_content)
		

	def on_reset_btn(self):
		# self.setFocus()
		print("on_reset_btn.")
		self.outputCommand.reset_configs()
		self.on_get_config_btn()


	def on_save_btn(self):
		# self.setFocus()
		print("on_save_btn():")

		# self.sdr_config
		ranges = []
		for n in range(0, self.__class__.NUM_OF_RANGES):
			start_entry_value = self.get_form_val(f'start_entries_{n}')
			end_entry_value = self.get_form_val(f'end_entries_{n}')
			threshold_entry_value = self.get_form_val(f'threshold_entries_{n}')

			if start_entry_value and end_entry_value and threshold_entry_value:
				try:
					start = int(start_entry_value)
					end = int(end_entry_value)
					threshold = float(threshold_entry_value)
					if start > 0 and end > 0 and threshold < 0:
						ranges.append(
							{
								"start": start,
								"end": end,
								"main_freq": self.__class__.MAIN_FREQ,
								"threshold": threshold,
							}
						)
					else:
						raise ValueError
				except ValueError:
					print("Entry correct data")

		updated_config = self.sdr_config

		updated_config["SCAN_RANGES"] = ranges
		# pprint(updated_config)

		self.outputCommand.save_configs(updated_config)

		self.need_to_show_save_msg = True
		self.set_connected_status_label("Trying to save new config ...")
	# ##################################


if __name__ == "__main__":
	app = QApplication([])
	nova_app = NovaApp()
	sys.exit(app.exec_())
