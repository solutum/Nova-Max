# import json

class OutputCommand:

	__instance = None

	def __init__(self, socket_connection) -> None:
		self.socket_connection = socket_connection

		OutputCommand.__instance = self
		pass

	@staticmethod
	def get_instance():
		return OutputCommand.__instance

	def get_configs(self):
		print("OutputCommand.get_configs.")

		self.__send_data("get_configs")

	def save_configs(self, data):
		print("OutputCommand.save_configs.")

		# self.__send_data("set_configs", json.loads(data))
		self.__send_data("set_configs", data)

	def reset_configs(self):
		print("OutputCommand.reset_configs.")

		self.__send_data("reset_configs")

	def __send_data(self, cmd, data = {}):
		cmd_data = {
			"cmd": cmd,
			"data": data
		}

		try:
			print(f'{cmd_data=}')
			self.socket_connection.send_client(cmd_data)
		except Exception as e:
			print(f"OutputCommand.__send_data. Send socker error: {e}")