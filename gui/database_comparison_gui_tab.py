
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
import matplotlib.pyplot as plt
import numpy as np
from PyQt5 import QtCore, uic, QtGui
from PyQt5.QtGui import QIcon, QPixmap
import transistordatabase as tdb


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        uic.loadUi('pre-work_2.ui', self)
        _translate = QtCore.QCoreApplication.translate
        # self.setWindowIcon(QIcon('Images\\logo.png'))
        self.setWindowTitle(_translate("MainWindow", "transistordatabase"))
        trans_list = tdb.print_TDB()
        app.aboutToQuit.connect(self.closeEvent)
        self.comboBoxTransOne.addItems(trans_list)
        self.comboBoxTransTwo.addItems(trans_list)
        self.comboBoxTransThree.addItems(trans_list)
        self.comboBoxTransOne.setCurrentIndex(2)
        self.comboBoxTransTwo.setCurrentIndex(4)
        self.comboBoxTransThree.setCurrentIndex(11)
        self.comboBoxTransOne.currentTextChanged.connect(self.populate_transistors)
        self.comboBoxTransTwo.currentTextChanged.connect(self.populate_transistors)
        self.comboBoxTransThree.currentTextChanged.connect(self.populate_transistors)
        self.populate_graphs(trans_list)
        self.comboBoxTransOne.setStyleSheet("background-color: rgb(245, 34, 34) ; color: rgb(133, 10, 5);")
        self.comboBoxTransTwo.setStyleSheet("background-color: rgb(34, 245, 34) ; color: rgb(4, 112, 13);")
        self.comboBoxTransThree.setStyleSheet("background-color: rgb(80, 85, 242) ; color: rgb(15, 4, 112);")
        #.setPalette(QPalette(blue))
#        self.simulateBtn.clicked.connect(self.simulate)


    def populate_transistors(self, selectedTrans):
        transistor = tdb.load({'name': selectedTrans})

        print("hello")

    def populate_graphs(self, collection):
        transistor_one = tdb.load({'name': collection[2]})
        transistor_two = tdb.load({'name': collection[4]})
        transistor_three = tdb.load({'name': collection[11]})
        channel_collection = {}
        energy_on_collection = {}
        energy_off_collection = {}
        diode_channel_collection = {}
        diode_energy_rr_collection = {}
        output_imp_collection = {}
        self.mplWidgetOne.canvas.axes.clear()
        sc = {}
        for index, transistor in enumerate([transistor_one, transistor_two, transistor_three]):
            # Switch channel and loss energy collection
            for channel in transistor.switch.channel:
                if channel.t_j == 125:
                    channel_collection[index+1] = channel.graph_v_i
            for e_on in transistor.switch.e_on:
                if e_on.dataset_type == 'graph_i_e' and e_on.v_supply == 600 and e_on.v_g == 15:
                    if transistor.manufacturer.lower() == 'cree' and e_on.t_j == 25:
                        energy_on_collection[index+1] = e_on.graph_i_e
                    elif e_on.t_j == 125:
                        energy_on_collection[index + 1] = e_on.graph_i_e
            for e_off in transistor.switch.e_off:
                if e_off.dataset_type == 'graph_i_e' and e_off.v_supply == 600:
                    if transistor.manufacturer.lower() == 'cree' and e_off.t_j == 25 and e_off.v_g == -4:
                        energy_off_collection[index+1] = e_off.graph_i_e
                    elif e_off.t_j == 125 and e_off.v_g == -15:
                        energy_off_collection[index + 1] = e_off.graph_i_e
            # Diode channel and loss energy collection
            for channel in transistor.diode.channel:
                if channel.t_j == 125:
                    diode_channel_collection[index + 1] = channel.graph_v_i
            for e_rr in transistor.diode.e_rr:
                if e_rr.dataset_type == 'graph_i_e' and e_rr.v_supply == 600 and e_rr.v_g == 15:
                    if transistor.manufacturer.lower() == 'cree' and e_rr.t_j == 25:
                        diode_energy_rr_collection[index + 1] = e_rr.graph_i_e
                    elif e_rr.t_j == 125:
                        diode_energy_rr_collection[index + 1] = e_rr.graph_i_e
            # Switch impedance curve collection
            output_imp_collection[index + 1] = transistor.switch.thermal_foster.graph_t_rthjc

        # Graphs starts from here
        color = {1: "red", 2: "green", 3: "blue"}
        labels = {1: transistor_one.name, 2: transistor_two.name, 3: transistor_three.name}
        for key, value in channel_collection.items():
            collection = value.tolist()
            self.mplWidgetOne.canvas.axes.plot(collection[0], collection[1], label=labels[key], color=color[key])
        x_label = 'Voltage [V]'
        y_label = 'Current [A]'
        self.mplWidgetOne.canvas.axes.set_xlabel(x_label)
        self.mplWidgetOne.canvas.axes.set_ylabel(y_label)

        for key, value in diode_channel_collection.items():
            collection = value.tolist()
            self.mplWidgetFour.canvas.axes.plot(collection[0], collection[1], label=labels[key], color=color[key])
        x_label = 'Voltage [V]'
        y_label = 'Current [A]'
        self.mplWidgetFour.canvas.axes.set_xlabel(x_label)
        self.mplWidgetFour.canvas.axes.set_ylabel(y_label)

        for key, value in energy_on_collection.items():
            collection = value.tolist()
            self.mplWidgetTwo.canvas.axes.plot(collection[0], collection[1], label=labels[key], color=color[key])
        x_label = 'Current [A]'
        y_label = 'Energy [J]'
        self.mplWidgetTwo.canvas.axes.set_xlabel(x_label)
        self.mplWidgetTwo.canvas.axes.set_ylabel(y_label)

        for key, value in energy_off_collection.items():
            collection = value.tolist()
            self.mplWidgetThree.canvas.axes.plot(collection[0], collection[1], label=labels[key], color=color[key])
        x_label = 'Current [A]'
        y_label = 'Energy [J]'
        self.mplWidgetThree.canvas.axes.set_xlabel(x_label)
        self.mplWidgetThree.canvas.axes.set_ylabel(y_label)

        for key, value in diode_energy_rr_collection.items():
            collection = value.tolist()
            self.mplWidgetFive.canvas.axes.plot(collection[0], collection[1], label=labels[key], color=color[key])
        x_label = 'Current [A]'
        y_label = 'Energy [J]'
        self.mplWidgetFive.canvas.axes.set_xlabel(x_label)
        self.mplWidgetFive.canvas.axes.set_ylabel(y_label)

        for key, value in output_imp_collection.items():
            collection = value.tolist()
            self.mplWidgetSix.canvas.axes.loglog(collection[0], collection[1], label=labels[key], color=color[key])
        x_label = 'time [s]'
        y_label = 'Energy [J]'
        self.mplWidgetSix.canvas.axes.set_xlabel(x_label)
        self.mplWidgetSix.canvas.axes.set_ylabel(y_label)

        self.mplWidgetOne.canvas.axes.legend(loc=2, prop={'size': 6})
        self.mplWidgetTwo.canvas.axes.legend(loc=2, prop={'size': 6})
        self.mplWidgetThree.canvas.axes.legend(loc=2, prop={'size': 6})
        self.mplWidgetFour.canvas.axes.legend(loc=2, prop={'size': 6})
        self.mplWidgetFive.canvas.axes.legend(loc=2, prop={'size': 6})
        self.mplWidgetSix.canvas.axes.legend(loc=2, prop={'size': 6})
        self.mplWidgetOne.canvas.axes.grid()
        self.mplWidgetTwo.canvas.axes.grid()
        self.mplWidgetThree.canvas.axes.grid()
        self.mplWidgetFour.canvas.axes.grid()
        self.mplWidgetFive.canvas.axes.grid()
        self.mplWidgetSix.canvas.axes.grid()
        self.mplWidgetOne.canvas.figure.set_visible(True)
        self.mplWidgetTwo.canvas.figure.set_visible(True)
        self.mplWidgetThree.canvas.figure.set_visible(True)
        self.mplWidgetFour.canvas.figure.set_visible(True)
        self.mplWidgetFive.canvas.figure.set_visible(True)
        self.mplWidgetSix.canvas.figure.set_visible(True)
        self.mplWidgetOne.canvas.draw()
        self.mplWidgetTwo.canvas.draw()
        self.mplWidgetThree.canvas.draw()
        self.mplWidgetFour.canvas.draw()
        self.mplWidgetFive.canvas.draw()
        self.mplWidgetSix.canvas.draw()


        markers = ['o', 'd', 's']

    def validate_choices(self):
        print("Hello")

if __name__ == "__main__":
    # transistor = tdb.load({'name': 'Fuji_2MBI300XBE120-50'})
    # transistor.plot_energy_data()
    # transistor.switch.e_on[1].graph_i_e = np.delete(transistor.switch.e_on[1].graph_i_e, [28, 29], axis=1)
    # transistor.save(overwrite=True)
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    mainWindow = MainWindow()
    mainWindow.show()
    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window....')