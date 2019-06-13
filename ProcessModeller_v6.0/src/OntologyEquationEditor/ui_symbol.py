# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/heinz/1_Gits/ProcessModeller/OntologyGenerator_v07.git/src/ui_symbol.ui'
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

class Ui_SymbolDialog(object):
    def setupUi(self, SymbolDialog):
        SymbolDialog.setObjectName(_fromUtf8("SymbolDialog"))
        SymbolDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        SymbolDialog.resize(376, 99)
        SymbolDialog.setModal(False)
        self.groupSymbol = QtGui.QGroupBox(SymbolDialog)
        self.groupSymbol.setGeometry(QtCore.QRect(9, 9, 630, 51))
        self.groupSymbol.setObjectName(_fromUtf8("groupSymbol"))
        self.lineSymbol = QtGui.QLineEdit(self.groupSymbol)
        self.lineSymbol.setGeometry(QtCore.QRect(60, 10, 191, 27))
        self.lineSymbol.setText(_fromUtf8(""))
        self.lineSymbol.setObjectName(_fromUtf8("lineSymbol"))
        self.pushCancle = QtGui.QPushButton(self.groupSymbol)
        self.pushCancle.setGeometry(QtCore.QRect(270, 10, 85, 27))
        self.pushCancle.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushCancle.setObjectName(_fromUtf8("pushCancle"))
        self.MSG = QtGui.QPlainTextEdit(SymbolDialog)
        self.MSG.setGeometry(QtCore.QRect(10, 60, 351, 31))
        self.MSG.setObjectName(_fromUtf8("MSG"))

        self.retranslateUi(SymbolDialog)
        QtCore.QMetaObject.connectSlotsByName(SymbolDialog)
        SymbolDialog.setTabOrder(self.lineSymbol, self.pushCancle)

    def retranslateUi(self, SymbolDialog):
        self.groupSymbol.setTitle(_translate("SymbolDialog", "symbol", None))
        self.lineSymbol.setPlaceholderText(_translate("SymbolDialog", "symbol", None))
        self.pushCancle.setText(_translate("SymbolDialog", "cancel", None))

