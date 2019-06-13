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

from PyQt4 import QtCore
from PyQt4 import QtGui

from Common.qt_resources import NO
from Common.qt_resources import YES
from Common.common_resources import CONNECTION_NETWORK_SEPARATOR
from Common.record_definitions import RecordVariable
from OntologyEquationEditor.resources import ENABLED_COLUMNS
from OntologyEquationEditor.resources import LANGUAGES
# from OntologyEquations.resources import CONSTANT
from OntologyEquationEditor.resources import NEW_VAR
from OntologyEquationEditor.resources import TOOLTIPS
from OntologyEquationEditor.ui_documentation_impl import UI_DocumentationDialog
from OntologyEquationEditor.ui_physunits_impl import UI_PhysUnitsDialog
# from Common.ui_two_list_selector_impl import UI_TwoListSelector
from Common.ui_radio_selector_w_sroll_impl import UI_RadioSelector
from OntologyEquationEditor.ui_symbol_impl import UI_SymbolDialog
from OntologyEquationEditor.ui_variabletable import Ui_Dialog
from OntologyEquationEditor.variable_framework import generateIndexSeq
from OntologyEquationEditor.variable_framework import simulateDeletion
from OntologyEquationEditor.variable_framework import Units


class UI_VariableTableDialog(QtGui.QDialog):
  """
  dialog for a variable
  emits a signal on completion
  """

  completed = QtCore.pyqtSignal(str)
  picked = QtCore.pyqtSignal(str)
  new_variable = QtCore.pyqtSignal(str)
  new_equation = QtCore.pyqtSignal(str, str)
  deleted_symbol = QtCore.pyqtSignal(str)

  def __init__(self,
               title,
               variables,
               equations,
               indices,
               network_variable,
               network_expression,
               choice,
               has_port_variables,
               disabled_variables=[],
               mode='inherit',
               hide=[]):
    """
    constructs a dialog window based on QDialog
    @param title:     title string: indicates the tree's nature
    @param variables: physical variable.
    @network_variable:      network type
    @my_types:      type of variables being processed

    control is done through the interface and additional functions:
    - enable_pick_contents : true or false
    - enable_selection : rows and columns

    signals:
    - picked : returns selected item text
    - completed : button finished has been pressed
    -
    """

    self.title = title
    self.variables = variables
    self.equations = equations
    self.indices = indices
    self.network_variable = network_variable
    self.network_expression = network_expression
    # self.enabled_variable_types = enabled_types
    # TODO enable all variable types (default)
    self.choice = choice
    self.variable_list = []  # variables.getVariableList()
    self.variable_types = variables.types
    self.disabled_variables = disabled_variables
    self.has_port_variables = has_port_variables
    self.mode = mode
    self.hide_vars = hide

    # set up dialog window with new title
    QtGui.QDialog.__init__(self)
    self.ui = Ui_Dialog()
    self.setWindowTitle(title)
    self.ui.setupUi(self)
    # self.ui.labelNetwork.setText(network_variable + "  " + title)
    self.ui.labelNetwork.setText(title)
    self.reset_table()
    self.hide()

  def show(self):
    self.reset_table()
    QtGui.QDialog.show(self)
    self.raise_()
    self.setToolTips('edit')

  def hideColumn(self, c):
    self.ui.tableVariable.hideColumn(c)

  def reset_table(self):
    self.ui.tableVariable.clearContents()
    self.ui.tableVariable.setRowCount(0)
    self.__fillTable()
    self.update()

  def enable_column_selection(self, columns):
    self.enabled_columns = columns

  def protect_variable_type(self, variable_types):  #TODO may be useful
    self.protected_variable_types = variable_types

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

  def __fillTable(self):
    nw = self.network_variable
    tab = self.ui.tableVariable
    tab.clearContents()
    rowCount = 0
    added_variables = []
    # for i in self.enabled_variable_types:
    i = self.choice
    variable_set = set()
    if self.mode == 'inherit':
      # TODO: this is a decision if all variables that are accessible or only those for this network are made visible
      variable_set = self.variables.getVariablesIndexedType(i, nw)
      try:
        for v in self.variables.indexedvariables[nw][i]:
          variable_set.add(v)
      except:
        print(">>> got here again")
    else:
      try:
        variable_set = self.variables.getVariablesForTypeAndNetwork(i, nw)
      except:
        variable_set = set()
    variable_list = list(variable_set)
    variable_list.sort()
    if not variable_list:
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
            added_variables.append(symbol)

    self.variable_list = added_variables
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

    return QtCore.QSize(width, min(height, MAX_HEIGHT))

  @staticmethod
  def __addQtTableItem(tab, s, row, col):
    item = QtGui.QTableWidgetItem(s)
    tab.setRowCount(row + 1)
    tab.setItem(row, col, item)

  def __showDeleteDialog(self):
    var_symbol = self.selected_variable_symbol
    msg = "deleting variable : %s" % var_symbol
    var = self.variables[var_symbol]
    print(var)
    d_vars, d_equs = simulateDeletion(self.variables, self.equations, var)
    msg += "\n\nand consequently \n...variables:%s \n...equations %s" % (d_vars, d_equs)
    self.deleting = d_vars, d_equs

    reply = QtGui.QMessageBox.question(self, 'choose', msg, YES, NO)  # QtGui.QMessageBox.Yes, QtGui.QMessageBox.No )
    print("reply :", reply)
    if reply == YES:
      print("yes")
      self.__deleteVariable()
      self.reset_table()

  def __deleteVariable(self):
    d_vars, d_equs = self.deleting
    print("going to delete: \n...variables:%s \n...equations %s" % (d_vars, d_equs))
    for id in d_equs:
      self.equations.removeEquation(id)
    for s in d_vars:
      self.variables.removeVariable(s)

    self.variables.reindex()
    # self.deleted_symbol.emit()
    self.__fillTable()

  def __showNewVariableDialog(self):
    msg = 'new port variable ?'
    if self.has_port_variables:
      reply = QtGui.QMessageBox.question(self, 'choose', msg, YES, NO)  # QtGui.QMessageBox.Yes, QtGui.QMessageBox.No )
    # print("reply :", reply)
    else:
      reply = NO

    if reply == YES:
      print("yes")
      self.defineGivenVariable()
    elif reply == NO:
      print("no")
      self.__defineNewVarWithEquation()
    else:
      print("none")
    self.reset_table()

  def __defineNewVarWithEquation(self):
    self.new_variable.emit(self.selected_variable_type)

  ### table handling
  def on_tableVariable_itemClicked(self, item):

    c = int(item.column())
    r = int(item.row())
    item = self.ui.tableVariable.item
    self.selected_variable_type = str(item(r, 0).text())

    if c == 0:
      self.__showNewVariableDialog()
      return

    # picking only
    self.selected_variable_symbol = str(item(r, 1).text())

    # get out if not desired
    if self.selected_variable_symbol in self.disabled_variables:
      return

    # do not allow chaning of units and index sets once in use or is defined via equation
    v = self.variables[self.selected_variable_symbol]
    l = len(v.equation_list)
    IIM = self.equations.inverseIncidenceMatrix()
    if IIM[v.symbol] or (l != 0):
      if 3 in self.enabled_columns:
        self.enabled_columns.remove(3)
      if 4 in self.enabled_columns:
        self.enabled_columns.remove(4)
    else:
      if 3 not in self.enabled_columns:
        self.enabled_columns += [3]
      if 4 not in self.enabled_columns:
        self.enabled_columns += [4]

    if c not in self.enabled_columns:
      return

    # execute requested command
    if c == 1:
      # print('clicked 1 - symbol ', self.selected_variable_symbol)
      self.__changeSymbol(v)
    elif c == 2:
      # print('clicked 2 - description ', v.doc)
      self.__changeDocumentation(v)
    elif c == 3:
      # print('clicked 3 - units ', v.units)
      self.__changeUnits(v)
    elif c == 4:
      # print('clicked 4 - indexing ', v.index_structures)
      self.__changeIndexing(v)
    elif c == 5:
      # print('clicked 5 - equations ', selected_number_of_equations)
      self.new_equation.emit(self.selected_variable_symbol,
                             self.selected_variable_type)
    elif c == 6:
      # print('clicked 6 - delete ')
      self.__showDeleteDialog()
    return

  def defineGivenVariable(self):
    kvariables = RecordVariable()  # deepcopy(STRUCTURES_Vars_Equs["variable"])
    symbol = NEW_VAR
    kvariables["symbol"] = symbol
    kvariables["type"] = self.selected_variable_type
    kvariables["network"] = self.network_variable
    kvariables["units"] = Units()
    kvariables["aliases"] = {}
    for l in LANGUAGES['compile']:
      kvariables["aliases"][l] = symbol  # .append((l, symbol))
    self.variables.addVariable(**kvariables)
    self.reset_table()

    enabled_columns = ENABLED_COLUMNS["edit"]["constant"]
    self.enable_column_selection(enabled_columns)

  def __changeSymbol(self, phys_var):
    self.ui_symbol = UI_SymbolDialog(self.variables, self.equations, phys_var)
    self.ui_symbol.finished.connect(self.reset_table)
    self.ui_symbol.show()

  def __changeUnits(self, phys_var):
    self.ui_units = UI_PhysUnitsDialog('new physical units', phys_var)
    self.ui_units.finished.connect(self.reset_table)
    self.ui_units.show()

  def __changeDocumentation(self, phys_var):
    self.ui_documentation = UI_DocumentationDialog(phys_var)
    self.ui_documentation.finished.connect(self.reset_table)
    self.ui_documentation.show()

  def __changeIndexing(self, phys_var):
    self.phys_var = phys_var
    if CONNECTION_NETWORK_SEPARATOR in phys_var.network:
      index_structs = ["node", "arc"]                                    # RULE: connection networks have nodes and arcs
    else:
      index_structs = self.indices.getIndexListPerNetwork(self.network_variable)
    self.ui_selector = UI_RadioSelector(index_structs,
                                        phys_var.index_structures)
    self.ui_selector.newSelection.connect(self.__gotNewIndexStrucList)
    # self.ui_selector = UI_TwoListSelector()        # changed to radio selector
    # self.ui_selector.populateLists(index_structs, phys_var.index_structures)
    self.ui_selector.show()

  def __gotNewIndexStrucList(self, strucs_list):
    indexing_sets = generateIndexSeq(strucs_list, self.indices.getIndexListUnsorted())
    self.phys_var.index_structures = indexing_sets
    self.reset_table()

  def on_pushFinished_pressed(self):
    # self.completed.emit("variables")
    if NEW_VAR in self.variables.getVariableList():
      self.variables.removeVariable(NEW_VAR)

    self.completed.emit("variables")
    # self.ui_selector.hide()
    self.close()

  def closeEvent(self, event):
    if NEW_VAR in self.variables.getVariableList():
      self.variables.removeVariable(NEW_VAR)
    try:
      self.ui_symbol.close()
    except:
      pass
    self.close()
