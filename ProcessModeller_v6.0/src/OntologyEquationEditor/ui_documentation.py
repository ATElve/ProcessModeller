# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/heinz/1_Gits/ProcessModeller/OntologyGenerator_v07.git/src/ui_documentation.ui'
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

class Ui_DocumentationDialog(object):
    def setupUi(self, DocumentationDialog):
        DocumentationDialog.setObjectName(_fromUtf8("DocumentationDialog"))
        DocumentationDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        DocumentationDialog.resize(736, 68)
        DocumentationDialog.setModal(False)
        self.groupDocumentation = QtGui.QGroupBox(DocumentationDialog)
        self.groupDocumentation.setGeometry(QtCore.QRect(7, 5, 630, 50))
        self.groupDocumentation.setObjectName(_fromUtf8("groupDocumentation"))
        self.lineDocumentation = QtGui.QLineEdit(self.groupDocumentation)
        self.lineDocumentation.setGeometry(QtCore.QRect(60, 20, 561, 27))
        self.lineDocumentation.setText(_fromUtf8(""))
        self.lineDocumentation.setObjectName(_fromUtf8("lineDocumentation"))
        self.pushCancle = QtGui.QPushButton(DocumentationDialog)
        self.pushCancle.setGeometry(QtCore.QRect(640, 30, 85, 27))
        self.pushCancle.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushCancle.setObjectName(_fromUtf8("pushCancle"))

        self.retranslateUi(DocumentationDialog)
        QtCore.QMetaObject.connectSlotsByName(DocumentationDialog)

    def retranslateUi(self, DocumentationDialog):
        self.groupDocumentation.setTitle(_translate("DocumentationDialog", "documentation", None))
        self.lineDocumentation.setPlaceholderText(_translate("DocumentationDialog", "describe variable", None))
        self.pushCancle.setText(_translate("DocumentationDialog", "cancel", None))

