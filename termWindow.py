# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'termWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class UiMainWindowTerm(object):
    def setup_term_ui(self, _TermWindow, _chosen_device):
        _TermWindow.setObjectName("TermWindow")
        _TermWindow.resize(1301, 601)
        self.centralwidget = QtWidgets.QWidget(_TermWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.terminalEntry = QtWidgets.QListWidget(self.centralwidget)
        self.terminalEntry.setGeometry(QtCore.QRect(0, 30, 1301, 571))
        self.terminalEntry.setStyleSheet("")
        self.terminalEntry.setObjectName("terminalEntry")
        self.terminal = QtWidgets.QLineEdit(self.centralwidget)
        self.terminal.setGeometry(QtCore.QRect(0, 0, 1301, 31))
        self.terminal.setObjectName("terminal")
        self.terminal.setPlaceholderText("terminal")
        _TermWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(_TermWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1301, 26))
        self.menubar.setObjectName("menubar")
        _TermWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(_TermWindow)
        self.statusbar.setObjectName("statusbar")
        _TermWindow.setStatusBar(self.statusbar)


        self.retranslate_term_ui(_TermWindow)
        QtCore.QMetaObject.connectSlotsByName(_TermWindow)

    def retranslate_term_ui(self, _TermWindow):
        _translate = QtCore.QCoreApplication.translate
        _TermWindow.setWindowTitle(_translate("TermWindow", "TermWindow"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    TermWindow = QtWidgets.QMainWindow()
    ui = UiMainWindowTerm()
    ui.setup_term_ui(TermWindow)
    TermWindow.show()
    sys.exit(app.exec_())