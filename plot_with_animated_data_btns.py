import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Графіки та керування")
        self.setGeometry(100, 100, 600, 400)
        self.setFixedSize(600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QGridLayout()
        self.central_widget.setLayout(self.layout)

        self.control_widget = QWidget()
        self.control_layout = QVBoxLayout()
        self.control_layout.setSpacing(5)
        self.control_widget.setLayout(self.control_layout)

        self.row1_layout = QHBoxLayout()
        self.control_layout.addLayout(self.row1_layout)
        self.label1 = QLabel("Server Address:")
        self.row1_layout.addWidget(self.label1)
        self.textbox1 = QLineEdit()
        self.textbox1.setFixedSize(135, 25)
        self.row1_layout.addWidget(self.textbox1)
        self.button1 = QPushButton("Connect")
        self.button1.setFixedWidth(110)
        self.row1_layout.addWidget(self.button1)

        self.row2_layout = QHBoxLayout()
        self.control_layout.addLayout(self.row2_layout)
        self.label2 = QLabel("Status:")
        self.row2_layout.addWidget(self.label2)
        self.label3 = QLabel("Text")
        self.row2_layout.addWidget(self.label3)

        self.row3_layout = QHBoxLayout()
        self.row3_layout.setSpacing(10)
        self.control_layout.addLayout(self.row3_layout)
        self.label4 = QLabel("Start:")
        self.row3_layout.addWidget(self.label4)
        self.textbox2 = QLineEdit()
        self.textbox2.setFixedSize(50, 25)
        self.row3_layout.addWidget(self.textbox2)
        self.label9 = QLabel("End:")
        self.row3_layout.addWidget(self.label9)
        self.textbox8 = QLineEdit()
        self.textbox8.setFixedSize(50, 25)
        self.row3_layout.addWidget(self.textbox8)
        self.label14 = QLabel("Threshold:")
        self.row3_layout.addWidget(self.label14)
        self.textbox13 = QLineEdit()
        self.textbox13.setFixedSize(50, 25)
        self.row3_layout.addWidget(self.textbox13)

        self.row4_layout = QHBoxLayout()
        self.control_layout.addLayout(self.row4_layout)
        self.label5 = QLabel("Start:")
        self.row4_layout.addWidget(self.label5)
        self.textbox3 = QLineEdit()
        self.textbox3.setFixedSize(50, 25)
        self.row4_layout.addWidget(self.textbox3)
        self.label10 = QLabel("End:")
        self.row4_layout.addWidget(self.label10)
        self.textbox9 = QLineEdit()
        self.textbox9.setFixedSize(50, 25)
        self.row4_layout.addWidget(self.textbox9)
        self.label15 = QLabel("Threshold:")
        self.row4_layout.addWidget(self.label15)
        self.textbox14 = QLineEdit()
        self.textbox14.setFixedSize(50, 25)
        self.row4_layout.addWidget(self.textbox14)
        self.label33 = QLabel("dB")
        self.row4_layout.addWidget(self.label33)

        self.row8_layout = QHBoxLayout()
        self.row8_layout.setSpacing(5)
        self.control_layout.addLayout(self.row8_layout)
        self.button2 = QPushButton("Get Config From Analyzer")
        self.row8_layout.addWidget(self.button2)
        self.button3 = QPushButton("Import Config From File")
        self.row8_layout.addWidget(self.button3)
        self.button4 = QPushButton("Reset Config")
        self.row8_layout.addWidget(self.button4)

        self.row9_layout = QHBoxLayout()
        self.control_layout.addLayout(self.row9_layout)
        self.button5 = QPushButton("Save Config")
        self.button5.setFixedHeight(29)
        self.row9_layout.addWidget(self.button5)

        self.control_wrapper = QWidget()
        self.control_wrapper.setLayout(QHBoxLayout())
        self.control_wrapper.layout().addWidget(self.control_widget)
        self.control_wrapper.setFixedWidth(540)
        self.control_wrapper.setFixedHeight(400)
        self.control_wrapper.setContentsMargins(0, 0, 0, 0)

        self.layout.addWidget(self.control_wrapper, 0, 0, 10, 1)

        self.update_plots()

    def update_plots(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
