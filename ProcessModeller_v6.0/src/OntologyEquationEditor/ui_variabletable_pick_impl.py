#!/usr/local/bin/python3
# encoding: utf-8
"""
@summary:      An editor for designing ontologies in my context
@contact:      heinz.preisig@chemeng.ntnu.no
@requires:     Python 3 or higher
@since:        29.08.15
@version:      0.1
@change:       Aug 29, 2015
@author:       Preisig, Heinz A
@copyright:    2014 Preisig, Heinz A  All rights reserved.
"""

__author__ = 'Preisig, Heinz A'

MAX_HEIGHT = 800

from PyQt4 import QtCore, QtGui

# from OntologyEquations.resources import CONSTANT
from OntologyEquationEditor.resources import TOOLTIPS
# from Common.ui_two_list_selector_impl import UI_TwoListSelector
from OntologyEquationEditor.ui_variabletable import Ui_Dialog


class UI_VariableTablePick(QtGui.QDialog):
  """
  dialog for a variable
  emits a signal on completion
  """

  completed = QtCore.pyqtSignal(str)
  picked = QtCore.pyqtSignal(str)
  new_variable = QtCore.pyqtSignal(str)
  new_equation = QtCore.pyqtSignal(str,str)
  deleted_symbol = QtCore.pyqtSignal(str)

  def __init__(self,
               title,
               variables,
               network,
               enabled_types=['ALL'],
               hide_vars=[],
               hide_columns=[]):
    """
    constructs a dialog window based on QDialog for picking variables
    @param title:     title string: indicates the tree's nature
    @param variables: physical variable.
    @network_variable:      network type
    @my_types:      type of variables being processed

    control is done through the interface and additional functions:
    - enable_pick_contents : true or false
    - enable_seclection : rows and columns

    signals:
    - picked : returns selected item text
    - completed : button finished has been pressed
    -
    """

    self.title = title
    self.variables = variables
    self.network = network
    self.enabled_variable_types = enabled_types
    self.variable_list = []
    self.variable_types = variables.types
    # self.disabled_variables = disabled_variables
    self.pick_contents = "picking"
    self.hide_vars = hide_vars
    self.hide_columns = hide_columns

    # set up dialog window with new title
    QtGui.QDialog.__init__(self)
    self.ui = Ui_Dialog()
    self.setWindowTitle(title)
    self.ui.setupUi(self)
    # self.ui.labelNetwork.setText(network_variable + "  " + title)
    self.ui.labelNetwork.setText(title)

    self.setToolTips('select')

    self.reset_table()
    self.hide()

  def reset_table(self):
    self.ui.tableVariable.clearContents()
    self.ui.tableVariable.setRowCount(0)
    self.__fillTable()
    self.update()

  def setToolTips(self, mode):
    rows = self.ui.tableVariable.rowCount()
    cols = self.ui.tableVariable.columnCount()
    for c in range(cols):
      c_item = self.ui.tableVariable.horizontalHeaderItem(c)
      c_t = c_item.text()
      for r in range(rows):
        try:
          r_item = self.ui.tableVariable.item(r, c)
          r_item.setToolTip(TOOLTIPS[mode][c_t])
        except:
          # print(' could not set tool tips row %s, column %s ,c_t : %s'%(rows,cols,c_t))
          pass

  def __fillTable(self, ):
    nw = self.network
    tab = self.ui.tableVariable
    tab.clearContents()
    rowCount = 0
    for i in self.enabled_variable_types:
      variable_set = self.variables.getVariablesIndexedType(i, nw)
      if i not in self.variables.indexedvariables[nw]:
        print("here it goes wrong")
      for v in self.variables.indexedvariables[nw][i]:
        variable_set.add(v)
      variable_list = list(variable_set)
      variable_list.sort()
      if not variable_list:
        if not self.pick_contents:
          self.__addQtTableItem(tab, i, rowCount, 0)
          rowCount += 1
      else:
        for symbol in variable_list:
          if symbol not in self.hide_vars:
            v = self.variables[symbol]
            t = v.type
            if t == i:
              self.__addQtTableItem(tab, i, rowCount, 0)
              self.__addQtTableItem(tab, symbol, rowCount, 1)
              self.__addQtTableItem(tab, v.doc, rowCount, 2)
              self.__addQtTableItem(tab, str(v.units), rowCount, 3)
              self.__addQtTableItem(tab, str(v.index_structures), rowCount, 4)
              _l = len(v.equation_list)
              self.__addQtTableItem(tab, str(_l), rowCount, 5)
              self.__addQtTableItem(tab, 'x', rowCount, 6)
              rowCount += 1

    for c in self.hide_columns:
      self.ui.tableVariable.hideColumn(c)

    # fitting window
    tab.resizeColumnsToContents()
    tab.resizeRowsToContents()
    t = self.__tabSizeHint()
    tab.resize(t)
    x = t.width() + tab.x() + 12
    y = tab.y() + tab.height() + 12
    s = QtCore.QSize(x, y)
    self.resize(s)

  def __tabSizeHint(self):
    tab = self.ui.tableVariable
    width = 0
    for i in range(tab.columnCount()):
      width += tab.columnWidth(i)
    width += tab.verticalHeader().sizeHint().width()
    width += tab.verticalScrollBar().sizeHint().width()
    width += tab.frameWidth() * 2

    height = 0
    for i in range(tab.rowCount()):
      height += tab.rowHeight(i)
    height += tab.horizontalHeader().sizeHint().height()
    height += tab.horizontalScrollBar().sizeHint().width()
    height += tab.frameWidth() * 2

    return QtCore.QSize(width, min(height,MAX_HEIGHT))

  @staticmethod
  def __addQtTableItem(tab, s, row, col):
    item = QtGui.QTableWidgetItem(s)
    tab.setRowCount(row + 1)
    tab.setItem(row, col, item)


  def on_tableVariable_itemClicked(self, item):

    r = int(item.row())
    item = self.ui.tableVariable.item
    self.selected_variable_type = str(item(r, 0).text())

    # picking only
    self.selected_variable_symbol = str(item(r, 1).text())
    if self.pick_contents:
      self.picked.emit(self.selected_variable_symbol)
      return


  def on_pushFinished_pressed(self):
    self.close()

  def closeEvent(self, event):
    self.close()
