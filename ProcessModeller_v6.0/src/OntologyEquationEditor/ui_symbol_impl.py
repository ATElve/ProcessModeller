
"""
===============================================================================
 GUI resource -- handles symbol dialogue for physical variable
===============================================================================

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2015. 03. 01"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"




from PyQt4 import QtCore, QtGui
from OntologyEquationEditor.ui_symbol import Ui_SymbolDialog
from OntologyEquationEditor.resources import setValidator
# from OntologyEquations.resources import NEW_VAR
import copy


ALLREADY_DEFINED = 'already defined -- give new variable'


class UI_SymbolDialog(QtGui.QDialog):
  """
  dialog for a variable
  any new variable will also gnerate a new equation

  state controlled
  """

  finished = QtCore.pyqtSignal()
  renamed_symbol = QtCore.pyqtSignal(str)

  def __init__(self, variables, equations, phys_var):
    '''
    constructs a dialog window based on QDialog
    @param title:     title string: indicates the tree's nature
    @param phys_var: physical variable
    '''

    self.variables = variables
    self.equations = equations
    self.phys_var = phys_var
    self.variable_list = variables.getVariableList()
    # set up dialog window with new title
    QtGui.QDialog.__init__(self)
    self.ui = Ui_SymbolDialog()
    self.ui.setupUi(self)
    self.setWindowTitle('edit variable symbol')
    self.MSG = self.ui.MSG.setPlainText
    self.MSG("provide variable symbol")
    self.validator = setValidator(self.ui.lineSymbol)
    self.setSymbol(phys_var.symbol)
    self.state_OK = False
    self.hide()

  def setSymbol(self, symbol):
    self.ui.groupSymbol.show()
    self.ui.lineSymbol.setText(symbol)
    self.ui.pushCancle.show()

  def on_lineSymbol_textChanged(self,text):
    # a = self.validator.validate(text, 0)
    # state = a[0]
    # print("validator %s"%state)
    if str(text) in self.variables.getVariableList():           # symbol OK ?
      self.MSG("already defined")
      self.state_OK = False
      return
    if  len(str(text)) == 0:
      self.MSG("provide new variable name")
      self.state_OK = False
      return

    self.MSG("OK")
    self.state_OK = True


  def on_lineSymbol_editingFinished(self):
    new_symbol = str(self.ui.lineSymbol.text())
    if self.state_OK:
      old_symbol = copy.copy(self.phys_var.symbol)
      self.variables.renameVariable(old_symbol, new_symbol)
      self.finished.emit()
      self.close()
    else:
      self.MSG("Invalid, provide variable symbol or cancle")

  def on_pushCancle_pressed(self):
    self.close()
