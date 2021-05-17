# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GUIQT.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
import threading
from os import getcwd, path
from os import mkdir
from random import choice
from shutil import rmtree
from time import sleep

from PyQt5 import QtCore, QtGui, QtWidgets

import computer
import server
import torNetwork
import termWindow


class MyLabel(QtWidgets.QLabel):

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if isinstance(ui.label_dict.get(self), server.Server):
                ui.serverListButton.click()
            else:
                ui.computerListButton.click()
            ui.choose_device(str(ui.label_dict.get(self)))
            ui.listComboBox.setCurrentText(str(ui.label_dict.get(self)))


class UiMainWindow(threading.Thread):
    def __init__(self, tor_network):
        threading.Thread.__init__(self)
        self.ui = termWindow.UiMainWindowTerm()
        self.window = QtWidgets.QMainWindow()
        self.chosen_device = None
        self.label_dict = {}
        self.tor_network = tor_network
        self.server_drop_list = []
        self.computer_drop_list = []
        self.chosen_drag = None

    def setup_ui(self, main_window):

        main_window.setObjectName("MainWindow")
        main_window.resize(1602, 1003)
        main_window.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralwidget = QtWidgets.QWidget(main_window)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 121, 71))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.serverListButton = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.serverListButton.setObjectName("serverListButton")
        self.devicesGroup = QtWidgets.QButtonGroup(main_window)
        self.devicesGroup.setObjectName("devicesGroup")
        self.devicesGroup.addButton(self.serverListButton)
        self.verticalLayout.addWidget(self.serverListButton)
        self.computerListButton = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.computerListButton.setObjectName("computerListButton")
        self.devicesGroup.addButton(self.computerListButton)
        self.verticalLayout.addWidget(self.computerListButton)
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(120, 0, 141, 71))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.listComboBox = QtWidgets.QComboBox(self.verticalLayoutWidget_2)
        self.listComboBox.setObjectName("listComboBox")
        self.verticalLayout_2.addWidget(self.listComboBox)
        self.removeDeviceButton = QtWidgets.QPushButton(self.centralwidget)
        self.removeDeviceButton.setGeometry(QtCore.QRect(0, 70, 261, 81))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.removeDeviceButton.setFont(font)
        self.removeDeviceButton.setObjectName("removeDeviceButton")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(0, 150, 261, 591))
        self.groupBox.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.groupBox.setObjectName("groupBox")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(0, 150, 261, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.nameEdit = QtWidgets.QLineEdit(self.groupBox)
        self.nameEdit.setGeometry(QtCore.QRect(0, 190, 261, 41))
        self.nameEdit.setObjectName("nameEdit")
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(0, 230, 261, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.addressEdit = QtWidgets.QLineEdit(self.groupBox)
        self.addressEdit.setGeometry(QtCore.QRect(0, 270, 261, 41))
        self.addressEdit.setObjectName("addressEdit")
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(0, 30, 261, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_5.setFont(font)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.createServerButton = QtWidgets.QRadioButton(self.groupBox)
        self.createServerButton.setGeometry(QtCore.QRect(0, 70, 261, 41))
        self.createServerButton.setObjectName("createServerButton")
        self.createServerButton.setChecked(True)
        self.createButtonGroup = QtWidgets.QButtonGroup(main_window)
        self.createButtonGroup.setObjectName("createButtonGroup")
        self.createButtonGroup.addButton(self.createServerButton)
        self.createComputerButton = QtWidgets.QRadioButton(self.groupBox)
        self.createComputerButton.setGeometry(QtCore.QRect(0, 110, 261, 41))
        self.createComputerButton.setObjectName("createComputerButton")
        self.createButtonGroup.addButton(self.createComputerButton)
        self.createButton = QtWidgets.QPushButton(self.groupBox)
        self.createButton.setGeometry(QtCore.QRect(0, 350, 261, 61))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.createButton.setFont(font)
        self.createButton.setObjectName("createButton")
        self.randomAddressButton = QtWidgets.QPushButton(self.groupBox)
        self.randomAddressButton.setGeometry(QtCore.QRect(0, 310, 261, 41))
        self.randomAddressButton.setObjectName("randomAddressButton")
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setGeometry(QtCore.QRect(0, 410, 261, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_6.setFont(font)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.onThreadButton = QtWidgets.QRadioButton(self.groupBox)
        self.onThreadButton.setGeometry(QtCore.QRect(0, 450, 261, 41))
        self.onThreadButton.setObjectName("onThreadButton")
        self.threadsGroup = QtWidgets.QButtonGroup(main_window)
        self.threadsGroup.setObjectName("threadsGroup")
        self.threadsGroup.addButton(self.onThreadButton)
        self.offThreadButton = QtWidgets.QRadioButton(self.groupBox)
        self.offThreadButton.setGeometry(QtCore.QRect(0, 490, 261, 41))
        self.offThreadButton.setObjectName("offThreadButton")
        self.threadsGroup.addButton(self.offThreadButton)
        self.stepButton = QtWidgets.QPushButton(self.groupBox)
        self.stepButton.setGeometry(QtCore.QRect(0, 530, 261, 61))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.stepButton.setFont(font)
        self.stepButton.setObjectName("stepButton")
        self.terminalEntry = QtWidgets.QListWidget(self.centralwidget)
        self.terminalEntry.setGeometry(QtCore.QRect(260, 30, 1341, 121))
        self.terminalEntry.setStyleSheet("")
        self.terminalEntry.setObjectName("terminalEntry")
        self.terminal = QtWidgets.QLineEdit(self.centralwidget)
        self.terminal.setGeometry(QtCore.QRect(260, 0, 1251, 31))
        self.terminal.setObjectName("terminal")
        self.terminal.setPlaceholderText("terminal")

        self.terminalWindowButton = QtWidgets.QPushButton(self.centralwidget)
        self.terminalWindowButton.setGeometry(QtCore.QRect(1510, 0, 91, 31))
        self.terminalWindowButton.setMinimumSize(QtCore.QSize(91, 31))
        self.terminalWindowButton.setObjectName("terminalWindowButton")
        main_window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1602, 26))
        self.menubar.setObjectName("menubar")
        main_window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)

        for i in range(300, 1501, 100):
            for j in range(200, 901, 100):
                if (301 < i < 1499) and (201 < j < 899):
                    self.server_drop_list.append((i, j))
                else:
                    self.computer_drop_list.append((i, j))

        self.computerListButton.clicked.connect(lambda: self.clicked_computer_list_button())
        self.serverListButton.clicked.connect(lambda: self.clicked_server_list_button())
        self.randomAddressButton.clicked.connect(lambda: self.set_random_address(tor_network.validate_address(
            torNetwork.random_address())))
        self.createButton.clicked.connect(lambda: self.create_new_device(
            self.nameEdit.text(), self.addressEdit.text(), self.createServerButton.isChecked()))
        self.listComboBox.activated.connect(lambda: self.choose_device(self.listComboBox.currentText()))
        self.terminal.returnPressed.connect(lambda: self.clicked_terminal_enter_button(self.terminal.text()))
        self.terminalWindowButton.clicked.connect(lambda: self.setup_terminal())
        self.onThreadButton.clicked.connect(lambda: self.start_threads())
        self.offThreadButton.clicked.connect(lambda: self.stop_threads())
        self.removeDeviceButton.clicked.connect(lambda: self.remove_device())
        self.stepButton.clicked.connect(lambda: self.step_on_thread())


        self.retranslate_ui(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslate_ui(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.computerListButton.setText(_translate("MainWindow", "Computers\' list"))
        self.serverListButton.setText(_translate("MainWindow", "Servers\' list"))
        self.label.setText(_translate("MainWindow", "Server/Computer List"))
        self.removeDeviceButton.setText(_translate("MainWindow", "Remove chosen device"))
        self.groupBox.setTitle(_translate("MainWindow", "Add new device"))
        self.label_3.setText(_translate("MainWindow", "Name:"))
        self.label_4.setText(_translate("MainWindow", "IP Address:"))
        self.label_5.setText(_translate("MainWindow", "Choose device:"))
        self.createServerButton.setText(_translate("MainWindow", "Server"))
        self.createComputerButton.setText(_translate("MainWindow", "Computer"))
        self.createButton.setText(_translate("MainWindow", "Create new device"))
        self.randomAddressButton.setText(_translate("MainWindow", "Random address"))
        self.label_6.setText(_translate("MainWindow", "Threads"))
        self.onThreadButton.setText(_translate("MainWindow", "ON"))
        self.offThreadButton.setText(_translate("MainWindow", "OFF"))
        self.stepButton.setText(_translate("MainWindow", "STEP"))
        self.terminalWindowButton.setText(_translate("MainWindow", "Window"))

    def clicked_computer_list_button(self):
        self.listComboBox.clear()
        for pc in self.tor_network.computer_list:
            self.listComboBox.addItem(str(pc))
        self.choose_device(self.listComboBox.currentText())

    def clicked_server_list_button(self):
        self.listComboBox.clear()
        for serv in self.tor_network.server_list:
            self.listComboBox.addItem(str(serv))
        self.choose_device(self.listComboBox.currentText())

    def create_new_device(self, name, ip_address, is_server):
        if self.tor_network.allow_name(name) and self.tor_network.allow_address(ip_address):
            new_label = MyLabel(self.centralwidget)
            new_label.setText(ip_address)
            new_label.selectedText()
            if is_server:
                new_srv = server.Server(name, ip_address, self.tor_network)
                self.listComboBox.addItem(str(new_srv))
                position = choice(self.server_drop_list)
                self.server_drop_list.remove(position)
                new_label.setGeometry(QtCore.QRect(position[0], position[1], 70, 70))
                new_label.setPixmap(QtGui.QPixmap("srv.png"))
                new_label.show()
                self.label_dict[new_label] = new_srv
                self.label_dict[new_srv] = new_label
            else:
                new_computer = computer.Computer(name, ip_address, self.tor_network)
                self.listComboBox.addItem(str(new_computer))
                position = choice(self.computer_drop_list)
                self.computer_drop_list.remove(position)
                new_label.setGeometry(QtCore.QRect(position[0], position[1], 82, 74))
                new_label.setPixmap(QtGui.QPixmap("pc.png"))
                new_label.show()
                self.label_dict[new_label] = new_computer
                self.label_dict[new_computer] = new_label

    def set_random_address(self, address):
        self.addressEdit.setText(address)

    def choose_device(self, device_name):
        for host in self.tor_network.server_list + self.tor_network.computer_list:
            if str(host) == device_name:
                if self.chosen_device and self.chosen_device != host:
                    if isinstance(self.chosen_device, server.Server):
                        self.label_dict.get(self.chosen_device).setPixmap(QtGui.QPixmap("srv.png"))
                    else:
                        self.label_dict.get(self.chosen_device).setPixmap(QtGui.QPixmap("pc.png"))
                self.chosen_device = host
                self.load_terminal_entry()
                if isinstance(self.chosen_device, server.Server):
                    for _server in self.tor_network.server_list:
                        self.label_dict.get(_server).setPixmap(QtGui.QPixmap("srv.png"))
                    self.label_dict.get(self.chosen_device).setPixmap(QtGui.QPixmap("srv_chosen.png"))
                else:
                    self.label_dict.get(self.chosen_device).setPixmap(QtGui.QPixmap("pc_chosen.png"))
                break

    def load_terminal_entry(self, general=False):
        try:
            self.terminalEntry.clear()
            if general:
                self.ui.terminalEntry.clear()
            with open(path.join(getcwd(), "logs", "console_" + self.chosen_device.name + ".txt"), "r") as file:
                data = file.readlines()
            for line in data[::-1]:
                self.terminalEntry.addItem(line.removesuffix("\n"))
                if general:
                    self.ui.terminalEntry.addItem(line.removesuffix("\n"))
        except FileNotFoundError:
            pass
        except AttributeError:
            pass

    def clicked_terminal_enter_button(self, command_text, general=False):
        self.chosen_device.log_write("console", self.chosen_device.execute_command(command_text))
        self.terminal.clear()
        self.load_terminal_entry()
        if general:
            self.ui.terminal.clear()
            self.load_terminal_entry(True)

    def setup_terminal(self):
        if self.chosen_device:
            self.ui.setup_term_ui(self.window, self.chosen_device)
            self.window.show()
            self.load_terminal_entry(True)
            self.ui.terminal.returnPressed.connect(lambda: self.clicked_terminal_enter_button(self.ui.terminal.text(),
                                                                                              True))

    def start_threads(self):
        for host in self.tor_network.server_list + self.tor_network.computer_list:
            host.run_event.set()
            host.start()

    def stop_threads(self):
        try:
            for host in self.tor_network.server_list + self.tor_network.computer_list:
                host.run_event.clear()
                host.join()
        except RuntimeError:
            pass

    def step_on_thread(self):
        try:
            for host in self.tor_network.server_list + self.tor_network.computer_list:
                host.connections_timeout_check()
                host.buffer_check()
        except RuntimeError:
            pass

    def generate_default(self):
        self.create_new_device("PC1", "01.02.03.04", False)
        self.create_new_device("PC2", "09.09.09.09", False)
        self.create_new_device("PC3", "04.03.02.01", False)

        self.create_new_device("SRV1", "11.11.11.11", True)
        self.create_new_device("SRV2", "22.22.22.22", True)
        self.create_new_device("SRV3", "33.33.33.33", True)
        self.create_new_device("SRV4", "44.44.44.44", True)
        self.create_new_device("SRV5", "55.55.55.55", True)
        self.create_new_device("SRV6", "66.66.66.66", True)
        self.create_new_device("SRV7", "77.77.77.77", True)

        self.computerListButton.click()
        self.onThreadButton.click()

    def remove_device(self):
        x = self.label_dict.get(self.chosen_device).geometry().x()
        y = self.label_dict.get(self.chosen_device).geometry().y()
        if isinstance(self.chosen_device, server.Server):
            self.server_drop_list.append((x, y))
            self.serverListButton.click()
        else:
            self.computer_drop_list.append((x, y))
            self.computerListButton.click()
        self.label_dict.get(self.chosen_device).setPixmap(QtGui.QPixmap(""))
        self.chosen_device.remove()
        self.chosen_device = None

    def run(self):
        while True:
            # self.load_terminal_entry()
            if isinstance(self.chosen_device, computer.Computer):
                for _server in self.tor_network.server_list:
                    for connection in self.chosen_device.connection_list:
                        if _server in connection.servers:
                            self.label_dict.get(_server).setPixmap(QtGui.QPixmap("srv_used.png"))
                            break
                    else:
                        self.label_dict.get(_server).setPixmap(QtGui.QPixmap("srv.png"))
                for _computer in self.tor_network.computer_list:
                    for connection in self.chosen_device.connection_list:
                        if _computer.ip_address == connection.dest_addr:
                            self.label_dict.get(_computer).setPixmap(QtGui.QPixmap("pc_end.png"))
                            break
                    else:
                        if _computer != self.chosen_device:
                            self.label_dict.get(_computer).setPixmap(QtGui.QPixmap("pc.png"))
            sleep(1)


if __name__ == "__main__":
    import sys

    try:
        rmtree("keys")
    except FileExistsError:
        pass
    try:
        mkdir("keys")
    except FileExistsError:
        pass
    try:
        rmtree("logs")
    except FileNotFoundError:
        pass

    mkdir("logs")

    tor_network = torNetwork.TorNetwork([], [])

    app = QtWidgets.QApplication(sys.argv)
    OnionRouting = QtWidgets.QMainWindow()
    ui = UiMainWindow(tor_network)
    ui.setup_ui(OnionRouting)
    OnionRouting.show()

    ui.generate_default()
    ui.start()
    sys.exit(app.exec_())
