# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/heinz/1_Gits/OntologyGenerator_v07/src/ui_aliastable.ui'
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

class Ui_AliasTable(object):
    def setupUi(self, AliasTable):
        AliasTable.setObjectName(_fromUtf8("AliasTable"))
        AliasTable.resize(592, 919)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AliasTable.sizePolicy().hasHeightForWidth())
        AliasTable.setSizePolicy(sizePolicy)
        self.tableWidget = QtGui.QTableWidget(AliasTable)
        self.tableWidget.setGeometry(QtCore.QRect(10, 40, 571, 861))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setSizeIncrement(QtCore.QSize(1, 1))
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.pushFinished = QtGui.QPushButton(AliasTable)
        self.pushFinished.setGeometry(QtCore.QRect(10, 10, 97, 27))
        self.pushFinished.setObjectName(_fromUtf8("pushFinished"))

        self.retranslateUi(AliasTable)
        QtCore.QMetaObject.connectSlotsByName(AliasTable)

    def retranslateUi(self, AliasTable):
        AliasTable.setWindowTitle(_translate("AliasTable", "Form", None))
        self.pushFinished.setText(_translate("AliasTable", "finished", None))

