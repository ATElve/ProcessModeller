# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/heinz/1_Gits/ProcessModeller/OntologyGenerator_v07.git/src/ui_equations.ui'
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

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(771, 423)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Consolas"))
        Form.setFont(font)
        Form.setToolTip(_fromUtf8(""))
        self.groupEquationEditor = QtGui.QGroupBox(Form)
        self.groupEquationEditor.setGeometry(QtCore.QRect(10, 140, 741, 271))
        self.groupEquationEditor.setObjectName(_fromUtf8("groupEquationEditor"))
        self.lineNewVariable = QtGui.QLineEdit(self.groupEquationEditor)
        self.lineNewVariable.setGeometry(QtCore.QRect(11, 50, 181, 27))
        self.lineNewVariable.setObjectName(_fromUtf8("lineNewVariable"))
        self.label = QtGui.QLabel(self.groupEquationEditor)
        self.label.setGeometry(QtCore.QRect(200, 50, 16, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.lineExpression = QtGui.QLineEdit(self.groupEquationEditor)
        self.lineExpression.setGeometry(QtCore.QRect(220, 50, 511, 27))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Consolas"))
        self.lineExpression.setFont(font)
        self.lineExpression.setObjectName(_fromUtf8("lineExpression"))
        self.pushAccept = QtGui.QPushButton(self.groupEquationEditor)
        self.pushAccept.setGeometry(QtCore.QRect(480, 10, 85, 28))
        self.pushAccept.setMinimumSize(QtCore.QSize(85, 0))
        self.pushAccept.setMaximumSize(QtCore.QSize(85, 16777215))
        self.pushAccept.setStyleSheet(_fromUtf8("background-color: rgb(0, 0, 255);\n"
"color :rgb(255, 255, 255)"))
        self.pushAccept.setObjectName(_fromUtf8("pushAccept"))
        self.pushDeleteEquation = QtGui.QPushButton(self.groupEquationEditor)
        self.pushDeleteEquation.setGeometry(QtCore.QRect(570, 10, 85, 28))
        self.pushDeleteEquation.setMinimumSize(QtCore.QSize(85, 0))
        self.pushDeleteEquation.setMaximumSize(QtCore.QSize(85, 16777215))
        self.pushDeleteEquation.setStyleSheet(_fromUtf8("background-color: rgb(255, 17, 0);\n"
"color:rgb(255, 255, 255)"))
        self.pushDeleteEquation.setObjectName(_fromUtf8("pushDeleteEquation"))
        self.textBrowser = QtGui.QTextBrowser(self.groupEquationEditor)
        self.textBrowser.setGeometry(QtCore.QRect(10, 90, 721, 161))
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))
        self.labelQuestion = QtGui.QLabel(Form)
        self.labelQuestion.setGeometry(QtCore.QRect(1080, -470, 41, 41))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.labelQuestion.setFont(font)
        self.labelQuestion.setAutoFillBackground(False)
        self.labelQuestion.setStyleSheet(_fromUtf8("background-color: rgb(255, 17, 0);"))
        self.labelQuestion.setAlignment(QtCore.Qt.AlignCenter)
        self.labelQuestion.setObjectName(_fromUtf8("labelQuestion"))
        self.labelNetwork = QtGui.QLabel(Form)
        self.labelNetwork.setGeometry(QtCore.QRect(20, 10, 741, 41))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.labelNetwork.setFont(font)
        self.labelNetwork.setObjectName(_fromUtf8("labelNetwork"))
        self.pushResetInterface = QtGui.QPushButton(Form)
        self.pushResetInterface.setGeometry(QtCore.QRect(571, 70, 127, 28))
        self.pushResetInterface.setObjectName(_fromUtf8("pushResetInterface"))
        self.pushCancel = QtGui.QPushButton(Form)
        self.pushCancel.setGeometry(QtCore.QRect(480, 70, 85, 28))
        self.pushCancel.setObjectName(_fromUtf8("pushCancel"))
        self.pushShowIndices = QtGui.QPushButton(Form)
        self.pushShowIndices.setGeometry(QtCore.QRect(480, 100, 191, 28))
        self.pushShowIndices.setObjectName(_fromUtf8("pushShowIndices"))
        self.pushResetInterface.raise_()
        self.labelNetwork.raise_()
        self.groupEquationEditor.raise_()
        self.labelQuestion.raise_()
        self.pushCancel.raise_()
        self.pushShowIndices.raise_()

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.groupEquationEditor.setToolTip(_translate("Form", "Equation editor", None))
        self.groupEquationEditor.setTitle(_translate("Form", "Equation Editor:  Variable := Expression", None))
        self.lineNewVariable.setToolTip(_translate("Form", "variable field", None))
        self.label.setText(_translate("Form", ":=", None))
        self.lineExpression.setToolTip(_translate("Form", "equation editor field -- press return when finished", None))
        self.pushAccept.setToolTip(_translate("Form", "puts things in place and closes equation editor", None))
        self.pushAccept.setText(_translate("Form", "accept", None))
        self.pushDeleteEquation.setText(_translate("Form", "delete", None))
        self.labelQuestion.setToolTip(_translate("Form", "Variable equation editor\n"
"Generates new variables and equations\n"
"Resulting bipartite graph (variable|equation) must be complete before ontology can be used\n"
"predefined variables: t, dt, t0", None))
        self.labelQuestion.setText(_translate("Form", "?", None))
        self.labelNetwork.setText(_translate("Form", "TextLabel", None))
        self.pushResetInterface.setToolTip(_translate("Form", "reset closes equation editor clears alias table", None))
        self.pushResetInterface.setText(_translate("Form", "reset interface", None))
        self.pushCancel.setToolTip(_translate("Form", "reset closes equation editor clears alias table", None))
        self.pushCancel.setText(_translate("Form", "cancel", None))
        self.pushShowIndices.setText(_translate("Form", "variables & indices", None))

