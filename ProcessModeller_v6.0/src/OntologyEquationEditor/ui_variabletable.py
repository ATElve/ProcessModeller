# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/heinz/1_Gits/ProcessModeller/OntologyGenerator_v07.git/src/ui_variabletable.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(839, 365)
        self.tableVariable = QtGui.QTableWidget(Dialog)
        self.tableVariable.setGeometry(QtCore.QRect(20, 90, 801, 261))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(self.tableVariable.sizePolicy().hasHeightForWidth())
        self.tableVariable.setSizePolicy(sizePolicy)
        self.tableVariable.setMinimumSize(QtCore.QSize(100, 100))
        self.tableVariable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tableVariable.setProperty("showDropIndicator", False)
        self.tableVariable.setDragDropOverwriteMode(False)
        self.tableVariable.setObjectName(_fromUtf8("tableVariable"))
        self.tableVariable.setColumnCount(7)
        self.tableVariable.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableVariable.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableVariable.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableVariable.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableVariable.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.tableVariable.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.tableVariable.setHorizontalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.tableVariable.setHorizontalHeaderItem(6, item)
        self.labelNetwork = QtGui.QLabel(Dialog)
        self.labelNetwork.setGeometry(QtCore.QRect(20, 10, 791, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.labelNetwork.setFont(font)
        self.labelNetwork.setObjectName(_fromUtf8("labelNetwork"))
        self.pushFinished = QtGui.QPushButton(Dialog)
        self.pushFinished.setGeometry(QtCore.QRect(20, 50, 85, 27))
        self.pushFinished.setObjectName(_fromUtf8("pushFinished"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.tableVariable.setToolTip(_translate("Dialog", "variable list", None))
        item = self.tableVariable.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "type", None))
        item.setWhatsThis(_translate("Dialog", "click for new variable", None))
        item = self.tableVariable.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "symbol", None))
        item.setWhatsThis(_translate("Dialog", "click for rename", None))
        item = self.tableVariable.horizontalHeaderItem(2)
        item.setText(_translate("Dialog", "description", None))
        item = self.tableVariable.horizontalHeaderItem(3)
        item.setText(_translate("Dialog", "units", None))
        item = self.tableVariable.horizontalHeaderItem(4)
        item.setText(_translate("Dialog", "indices", None))
        item = self.tableVariable.horizontalHeaderItem(5)
        item.setText(_translate("Dialog", "eqs", None))
        item = self.tableVariable.horizontalHeaderItem(6)
        item.setText(_translate("Dialog", "del", None))
        self.labelNetwork.setText(_translate("Dialog", "TextLabel", None))
        self.pushFinished.setText(_translate("Dialog", "finished", None))

