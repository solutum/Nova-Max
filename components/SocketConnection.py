import threading
import socket
import pickle
import traceback

from components.InputCommand import InputCommand
from components.Logger import Logger


class SocketConnection:
	__instance = None

	def __init__(self):

		self.inputCommand = InputCommand()

		self.logger = Logger.get_instance()

		self.stop_thread_event = threading.Event()
		# ? DEL
		self.socket_thread = threading.Thread(target=self.listen_for_data) # ?

		self.client_socket = None

		self.address_ip = None
		self.address_port = None

		SocketConnection.__instance = self

		pass
		
	@staticmethod
	def get_instance():
		return SocketConnection.__instance

	def thread_event_on(self):
		self.stop_thread_event.set()
		
	def thread_event_off(self):
		self.stop_thread_event.clear()

	def thread_stop_listening(self):
		print("Closing socket connection ...")
		try:
			self.thread_event_on()

			if self.client_socket:
				# Встановлення таймауту на сокеті перед його закриттям
				self.client_socket.settimeout(1)  # Наприклад, 1 секунда

				self.client_socket.close()
				self.client_socket = None
		except Exception as e:
			self.logger.log_message(f"SocketConnection.cb_reset_conection. Exception {e}")


	def thread_start_listening(self, address_ip, address_port, status_callback):
		self.address_ip = address_ip
		self.address_port = address_port
		self.status_callback = status_callback

		self.thread_event_off()

		self.socket_thread = threading.Thread(target=self.listen_for_data)
		self.socket_thread.start()
		
		# return True

	def listen_for_data(self):
		#print("listen_for_data. ")
		self.logger.log_message(f"SocketConnection.listen_for_data.")
		try:
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
				client_socket.settimeout(20)  # Set 20sec timeout
				client_socket.connect((self.address_ip, int(self.address_port)))

				#print("listen_for_data. socket connected")
				self.logger.log_message(f"SocketConnection.listen_for_data. socket connected")

				self.client_socket = client_socket
				self.status_callback(True, "Connected")

				while not self.stop_thread_event.is_set():
					# Read the size of the incoming chunk
					size_bytes = client_socket.recv(4)
					if not size_bytes:
						break

					self.logger.log_message(f"SocketConnection.listen_for_data. socket receive")

					chunk_size = int.from_bytes(size_bytes, 'big')

					# Read the chunk data
					chunk_data = b''
					while len(chunk_data) < chunk_size:
						remaining_size = chunk_size - len(chunk_data)
						chunk_data += client_socket.recv(min(4096, remaining_size))

					#print(datetime.now(), "listen_for_data. Data gets")
					self.logger.log_message(f"SocketConnection.listen_for_data. Data gets")

					# Update charts with the received data
					# print(pickle.loads(chunk_data))
					try:
						data = pickle.loads(chunk_data)

						if 'cmd' not in data:
							raise Exception("Wrong input data format")
						
						# if data['cmd'] == 'scan_range_data':
						# 	self.plot_callback(data['data']['signals']['all'])

						self.inputCommand.parse_input_command(data)
					except Exception as e:
						print(f"Error updating charts: {e}")
						self.logger.log_message(f"SocketConnection.listen_for_data. Error updating charts: {e}")
						traceback.print_exc()
		except TimeoutError:
			print("Timeout occurred while listening for data. Socket thread exiting.")
		except Exception as e:
			self.status_callback(False, str(e))
			print(f"Error listening for data: {e}")
			self.logger.log_message(f"SocketConnection.listen_for_data. Error listening for data: {e}")
			traceback.print_exc()
			raise
		finally:
			#print("Socket thread exiting.")
			pass
			self.logger.log_message(f"SocketConnection.listen_for_data. Socket thread exiting")


	def send_client(self, cmd_data):
		self.client_socket.send(pickle.dumps(cmd_data))