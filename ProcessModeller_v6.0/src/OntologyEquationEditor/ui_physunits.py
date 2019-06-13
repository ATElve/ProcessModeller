# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/heinz/1_Gits/ProcessModeller/OntologyGenerator_v07.git/src/ui_physunits.ui'
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

class Ui_PysUnitsDialog(object):
    def setupUi(self, PysUnitsDialog):
        PysUnitsDialog.setObjectName(_fromUtf8("PysUnitsDialog"))
        PysUnitsDialog.resize(650, 167)
        self.layoutWidget = QtGui.QWidget(PysUnitsDialog)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 20, 611, 100))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.gridlayout = QtGui.QGridLayout(self.layoutWidget)
        self.gridlayout.setMargin(2)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.spinBoxTime = QtGui.QSpinBox(self.layoutWidget)
        self.spinBoxTime.setAccessibleDescription(_fromUtf8(""))
        self.spinBoxTime.setMinimum(-99)
        self.spinBoxTime.setObjectName(_fromUtf8("spinBoxTime"))
        self.gridlayout.addWidget(self.spinBoxTime, 0, 0, 1, 1)
        self.label_4 = QtGui.QLabel(self.layoutWidget)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridlayout.addWidget(self.label_4, 0, 1, 1, 1)
        self.spinBoxLength = QtGui.QSpinBox(self.layoutWidget)
        self.spinBoxLength.setMinimum(-99)
        self.spinBoxLength.setObjectName(_fromUtf8("spinBoxLength"))
        self.gridlayout.addWidget(self.spinBoxLength, 0, 2, 1, 1)
        self.label_5 = QtGui.QLabel(self.layoutWidget)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridlayout.addWidget(self.label_5, 0, 3, 1, 1)
        self.spinBoxTemperature = QtGui.QSpinBox(self.layoutWidget)
        self.spinBoxTemperature.setMinimum(-99)
        self.spinBoxTemperature.setObjectName(_fromUtf8("spinBoxTemperature"))
        self.gridlayout.addWidget(self.spinBoxTemperature, 0, 4, 1, 1)
        self.label_8 = QtGui.QLabel(self.layoutWidget)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridlayout.addWidget(self.label_8, 0, 5, 1, 1)
        self.spinBoxAmount = QtGui.QSpinBox(self.layoutWidget)
        self.spinBoxAmount.setMinimum(-99)
        self.spinBoxAmount.setObjectName(_fromUtf8("spinBoxAmount"))
        self.gridlayout.addWidget(self.spinBoxAmount, 1, 2, 1, 1)
        self.label_6 = QtGui.QLabel(self.layoutWidget)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridlayout.addWidget(self.label_6, 1, 3, 1, 1)
        self.spinBoxCurrent = QtGui.QSpinBox(self.layoutWidget)
        self.spinBoxCurrent.setMinimum(-99)
        self.spinBoxCurrent.setObjectName(_fromUtf8("spinBoxCurrent"))
        self.gridlayout.addWidget(self.spinBoxCurrent, 1, 4, 1, 1)
        self.label_9 = QtGui.QLabel(self.layoutWidget)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridlayout.addWidget(self.label_9, 1, 5, 1, 1)
        self.spinBoxMass = QtGui.QSpinBox(self.layoutWidget)
        self.spinBoxMass.setMinimum(-99)
        self.spinBoxMass.setObjectName(_fromUtf8("spinBoxMass"))
        self.gridlayout.addWidget(self.spinBoxMass, 2, 2, 1, 1)
        self.label_7 = QtGui.QLabel(self.layoutWidget)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridlayout.addWidget(self.label_7, 2, 3, 1, 1)
        self.spinBoxLight = QtGui.QSpinBox(self.layoutWidget)
        self.spinBoxLight.setMinimum(-99)
        self.spinBoxLight.setObjectName(_fromUtf8("spinBoxLight"))
        self.gridlayout.addWidget(self.spinBoxLight, 2, 4, 1, 1)
        self.label_10 = QtGui.QLabel(self.layoutWidget)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.gridlayout.addWidget(self.label_10, 2, 5, 1, 1)
        self.pushOK = QtGui.QPushButton(PysUnitsDialog)
        self.pushOK.setGeometry(QtCore.QRect(530, 130, 97, 27))
        self.pushOK.setObjectName(_fromUtf8("pushOK"))

        self.retranslateUi(PysUnitsDialog)
        QtCore.QMetaObject.connectSlotsByName(PysUnitsDialog)

    def retranslateUi(self, PysUnitsDialog):
        PysUnitsDialog.setWindowTitle(_translate("PysUnitsDialog", "Dialog", None))
        self.label_4.setText(_translate("PysUnitsDialog", "time [s]", None))
        self.label_5.setText(_translate("PysUnitsDialog", "length [m]", None))
        self.label_8.setText(_translate("PysUnitsDialog", "temperature [K]", None))
        self.label_6.setText(_translate("PysUnitsDialog", "amount [mol]", None))
        self.label_9.setText(_translate("PysUnitsDialog", "current [A]", None))
        self.label_7.setText(_translate("PysUnitsDialog", "mass [kg]", None))
        self.label_10.setText(_translate("PysUnitsDialog", "light [cd]", None))
        self.pushOK.setText(_translate("PysUnitsDialog", "OK", None))

