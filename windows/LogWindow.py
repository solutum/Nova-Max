from PyQt5 import QtWidgets


class LogWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Log Window")
		self.resize(800, 600)
		self.log_text_edit = QtWidgets.QPlainTextEdit()
		self.log_text_edit.setReadOnly(True)
		self.setCentralWidget(self.log_text_edit)

	def log_message(self, message):
		pass
		# self.log_text_edit.appendPlainText(message)
		# self.log_text_edit.verticalScrollBar().setValue(self.log_text_edit.verticalScrollBar().maximum())


"""    def show(self):
		self.window.deiconify()

	def cb_hide(self):
		self.window.withdraw()"""