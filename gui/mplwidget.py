# ------------------------------------------------- -----
# -------------------- mplwidget.py --------------------
# -------------------------------------------------- ----
from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure


class MplWidget(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.canvas = FigureCanvasQTAgg(Figure(tight_layout={'pad': 0.1}))
        #self.toolbar = NavigationToolbar(self.canvas, self)
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        #vertical_layout.addWidget(self.toolbar)
        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.axes.tick_params(axis='both', which='major', labelsize=5)
        self.canvas.axes.tick_params(axis='both', which='minor', labelsize=1)
        self.canvas.axes.xaxis.label.set_size(5)
        self.canvas.axes.yaxis.label.set_size(5)

        self.setLayout(vertical_layout)
