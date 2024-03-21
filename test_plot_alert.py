import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox
import pyqtgraph as pg


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")

        self.button_open_graph = QPushButton("Open Graph Window")
        self.button_open_graph.clicked.connect(self.open_graph_window)

        self.button_show_alert = QPushButton("Show Alert")
        self.button_show_alert.clicked.connect(self.show_alert)

        layout = QVBoxLayout()
        layout.addWidget(self.button_open_graph)
        layout.addWidget(self.button_show_alert)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_graph_window(self):
        self.second_window = SecondWindow()
        self.second_window.show()

    def show_alert(self):
        alert = QMessageBox()
        alert.setWindowTitle("Alert")
        alert.setText("This is an alert message!")
        alert.setStandardButtons(QMessageBox.Ok)
        alert.exec_()


class SecondWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph Window")

        self.graph_widget = pg.PlotWidget()
        self.plot()

        layout = QVBoxLayout()
        layout.addWidget(self.graph_widget)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def plot(self):
        x = [1, 2, 3, 4, 5]
        y = [1, 4, 9, 16, 25]
        self.graph_widget.plot(x, y, pen='r')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
