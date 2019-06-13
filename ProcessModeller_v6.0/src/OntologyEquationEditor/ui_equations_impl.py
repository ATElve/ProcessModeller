#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 GUI defining equations
===============================================================================

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2012. 03. 21"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"




from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot

# from Debugging import message_logging
from OntologyEquationEditor.variable_framework import VarError
from OntologyEquationEditor.variable_framework import UnitError
from OntologyEquationEditor.variable_framework import IndexStructureError
from OntologyEquationEditor.variable_framework import Expression
# from OntologyEquationEditor.variable_framework import Units



# from Common.common_resources import STRUCTURES_Vars_Equs
from Common.record_definitions import RecordVariable, RecordEquation

from OntologyEquationEditor.resources import TEMPLATES
from OntologyEquationEditor.resources import NEW_EQ, UNDEF_EQ_NO
from OntologyEquationEditor.resources import NEW_VAR
from OntologyEquationEditor.resources import LANGUAGES
from OntologyEquationEditor.resources import TWOPLACETEMPLATE
from OntologyEquationEditor.resources import THREPLACETEMPLATE
from OntologyEquationEditor.resources import FOURPLACETEMPLATE
from OntologyEquationEditor.resources import UNITARY_RETAIN_UNITS
from OntologyEquationEditor.resources import UNITARY_INVERSE_UNITS
from OntologyEquationEditor.resources import UNITARY_NO_UNITS
from OntologyEquationEditor.resources import CODE
from OntologyEquationEditor.resources import CONSTANT
from OntologyEquationEditor.resources import PORT
# from OntologyEquationEditor.resources import NETWORK_SEPARATOR
from OntologyEquationEditor.resources import setValidator

from OntologyEquationEditor.ui_variabletable_pick_impl import UI_VariableTablePick

from OntologyEquationEditor.tpg import SemanticError, SyntacticError, LexicalError, WrongToken
from OntologyEquationEditor.ui_variabletable_impl import UI_VariableTableDialog
from OntologyEquationEditor.ui_equations import Ui_Form
from Common.single_list_selector_impl import   SingleListSelector
import copy


LF = '\n'

internal = LANGUAGES["internal_code"]



class UI_Equations(QtGui.QWidget):
  """
  user interface for the equation definition
  """

  update_space_information = QtCore.pyqtSignal()
  def_given_variable = QtCore.pyqtSignal()

  def __init__(self, variables, equations, indices,
               network_for_variable, network_for_expression,
               variable_types_variable,
               variable_types_expression,
               enabled_variable_types = []
               ):
    """
    Constructor
    """
    QtGui.QWidget.__init__(self)
    self.ui = Ui_Form()
    self.ui.setupUi(self)
    self.hide()
    self.variables = variables
    self.equations = equations
    self.indices = indices
    self.variable_list = variables.getVariableList()
    self.index_list = indices.getIndexList()
    self.network_for_variable = network_for_variable
    self.network_for_expression = network_for_expression
    self.actual_network_for_expression = network_for_expression        # may change if equation is edited
    self.variable_types_variable = variable_types_variable
    self.variable_types_expression = variable_types_expression
    self.enabled_variable_types = enabled_variable_types

    # TODO: equation editing -- control when to allow editing of an equation. Currently it is not controlled over the
    #  network d.h. if one has defined a equation on macro as a second equation whilst the first was defined on
    # physical, then the equation can be edited on physical even though it remains (now) on the macro layer.




    self.ui.labelNetwork.setText(network_for_variable)

    # print("define variable for network <%s> from variables from network <%s>" %(network_variable,network_expression))
    self.__makePickVariableTable()

# TODO: not nice needs fixing
    _l = []
    for i in TWOPLACETEMPLATE:
      _l.append(CODE[internal][i] % ('a', 'b'))

    _l.append(CODE[internal]['|'] % ('a', "index", 'b'))
    _l.append(CODE[internal]['interval'] % ('x', 'xl', 'xu'))
    _l.append(CODE[internal]['integral'].format(integrand='var',
                                             differential='t',
                                             lower='l',
                                             upper='u'))
    for i in UNITARY_NO_UNITS:
      _l.append('%s(no units)' % i)
    for i in UNITARY_RETAIN_UNITS+UNITARY_INVERSE_UNITS:
      _l.append('%s(with units)' % i)

    _l.append(CODE[internal]['root'] % ('expression','var'))

    self.operator_table = SingleListSelector(thelist=_l)
    self.operator_table.hide()
    self.operator_table.newSelection.connect(self.__insertSnipp)

    self.resetEquationInterface()
    self.MSG = self.ui.textBrowser.setText
    self.appendMSG = self.ui.textBrowser.append
    self.MSG("ready")
    self.hide()

  def __makePickVariableTable(self):

    self.variable_tables = {}

    if self.network_for_variable != self.network_for_expression:
      vars = {self.network_for_variable  : self.variable_types_variable,
              self.network_for_expression: self.variable_types_expression}
    else:
      vars = {self.network_for_expression: self.variable_types_expression}
    networks = set([self.network_for_variable, self.network_for_expression])
    for nw in networks:
      self.variable_tables[nw] = UI_VariableTablePick('Pick variable symbol \nnetwork %s' % nw,
                                                      self.variables,
                                                      nw,
                                                      enabled_types=vars[nw],
                                                      hide_vars=[NEW_VAR],
                                                      hide_columns=[0, 3, 5, 6]
                                                      )
      self.variable_tables[nw].hide()
      self.variable_tables[nw].picked.connect(self.__insertSnipp)

  def closeEvent(self, event):
    try:
      self.ui_equationselector.close()
    except:
      pass
    try:
      self.ui_indices.close()
    except:
      pass
    # for nw in self.variable_tables:
    try:
      [self.variable_tables[nw].close() for nw in self.variable_tables]
    except:
      pass
    try:
      self.operator_table.close()
    except:
      pass
    self.close()

  def __insertSnipp(self, text):
    # TODO: fix templates
    try:
      starting, ending = self.text_range
    except:
      starting, ending = 0, 0
    t = str(self.ui.lineExpression.text())
    s = t[0:starting] + text + t[ending:]
    self.ui.lineExpression.setText(s)
    self.ui.lineExpression.setFocus(True)
    self.show()
    # self.ui.lineExpression.cursorWordBackward(False)
    # self.ui.lineExpression.cursorWordForward(False)

  def resetEquationInterface(self):
    self.__makePickVariableTable()
    self.ui_indices = SingleListSelector(self.index_list)
    self.ui_indices.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    # self.ui_indices.hideButtons()
    self.ui_indices.newSelection.connect(self.__insertSnipp)
    self.hide()
    self.ui.lineExpression.clear()
    self.ui.lineNewVariable.clear()
    # reg_ex =QtCore.QRegExp("[a-zA-Z_]\w*")
    # validator = QtGui.QRegExpValidator(VAR_REG_EXPR, self.ui.lineNewVariable)
    # self.ui.lineNewVariable.setValidator(validator)
    setValidator(self.ui.lineNewVariable)
    self.ui.pushAccept.hide()
    self.ui.groupEquationEditor.hide()
    self.ui_indices.hide()
    self.selected_variable_type = None
    self.selected_variable_symbol = ''
    self.update()

  def setupNewVariable(self, variable_type):
    variable_type = str(variable_type)
    print("setup new variable: %s" % variable_type)
    self.resetEquationInterface()
    self.selected_variable_type = variable_type
    self.ui.groupEquationEditor.show()
    self.ui.lineExpression.hide()
    self.status_new_variable = True
    self.status_rename_var = False
    self.status_edit_expr = True
    self.status_new_equation = True
    self.ui.pushDeleteEquation.hide()
    self.ui.lineNewVariable.setReadOnly(False)
    self.show()
    self.MSG("new variable")

  @pyqtSlot(str, str)
  def setupNewEquation(self, variable_symbol, variable_type):
    variable_symbol = str(variable_symbol)
    self.selected_variable_type = variable_type
    self.setupEquationList(variable_symbol)
    self.ui.groupEquationEditor.show()
    self.status_new_variable = False
    self.ui.pushAccept.hide()
    if variable_symbol == NEW_VAR:
      self.status_rename_var = True
      self.ui.lineNewVariable.setReadOnly(False)
      self.ui.lineExpression.hide()
    else:
      self.status_rename_var = False
      self.ui.lineNewVariable.setReadOnly(True)
      self.ui.lineExpression.show()
    self.status_edit_expr = True
    self.status_new_equation = True
    self.ui.pushDeleteEquation.hide()
    self.MSG("new equation")

  def on_lineNewVariable_returnPressed(self):
    symbol = str(self.ui.lineNewVariable.text())
    if self.variables.existSymbol(symbol):
      self.MSG("variable already defined")
      return
    else:
      if not self.variables.checkVariableCompiles(symbol):
        self.MSG("illegal syntax in symbol %s"%symbol)
        self.ui.lineNewVariable.setText("")
        return
      self.MSG("variable symbol OK")
      self.ui.lineExpression.show()
      self.ui.lineExpression.setFocus()

  def on_lineExpression_returnPressed(self):
    text = str(self.ui.lineExpression.text())
    if self.__checkExpression():
      self.ui.pushAccept.show()
    else:
      self.ui.pushAccept.hide()

  def on_lineExpression_cursorPositionChanged(self, old, new):
    starting = new
    ending = new
    if self.ui.lineExpression.hasSelectedText():
      text = str(self.ui.lineExpression.selectedText())
      starting = self.ui.lineExpression.selectionStart()
      ending = starting + len(text)
    # LOGGER.info('pos: %s,%s' % (starting, ending))
    self.text_range = starting, ending

  def on_lineExpression_textChanged(self, text):
    self.ui.pushAccept.hide()
    self.ui.pushDeleteEquation.hide()

  def on_lineNewVariable_textChanged(self, text):
    self.ui.pushAccept.hide()
    if str(text) in self.variable_list:
      self.MSG("already defined variable")
    else:
      self.MSG("OK")

  def __checkExpression(self):
    s = str(self.ui.lineExpression.text())
    # print('sssss: ', s)
    self.expr = s.strip()
    # print('expression: ', self.expr)
    # print('self.variable: ', self.variables)
    # print('self.indices: ', self.indices)
    try:
      expression = Expression(self.variables, self.indices)
      self.checked_var = expression(self.expr)
      print('self.checked_var:  ', self.checked_var)


      if "PhysicalVariable" in str(self.checked_var.__class__): # RULE: copy of variable is not allowed
        self.MSG('cannot be a copy of a variable')
        return False

      self.checked_var.incidence_list = expression.space.getIncidenceList()
      print('variable from expression', self.checked_var, 'are :', self.checked_var.incidence_list)
      for var in self.checked_var.incidence_list:
        no_variable = False
        for nw in self.variable_tables:
          if var not in self.variable_tables[nw].variable_list:
            # self.MSG('variable <%s> is not in the list of %s'%(var, self.variable_tables[nw].variable_list))
            self.MSG('modified expression OK\n index struct: %s\n units :%s\n units: %s'
                     %(self.checked_var.index_structures, self.checked_var.units, str(self.checked_var.units.prettyPrint())))
            no_variable = True
          else:
            no_variable = False
        if no_variable:
          return no_variable

      if self.status_new_variable or self.status_rename_var:
        # LOGGER.info('checked new_variable expression')
        self.MSG('expression OK')
        self.MSG('modified expression OK\n units :%s\n index struct: %s'
                 %(self.checked_var.units, self.checked_var.index_structures))
        return True
      else:
        # LOGGER.info('checked modified expression')
        self.MSG('modified expression OK\n units :%s\n index struct: %s'
                 %(self.checked_var.units, self.checked_var.index_structures))
        symbol = str(self.ui.lineNewVariable.text())
        current_var = self.variables[symbol]
        if current_var.compatible(self.checked_var):
          return True
        else:
          self.appendMSG(' - but Not compatible variable \n>> %s \n>> %s'
                         %(current_var,self.checked_var))
          return False
    except (VarError,
            SemanticError,
            SyntacticError,
            LexicalError,
            WrongToken,
            UnitError,
            IndexStructureError
            ) as _m:
      self.MSG('checked expression failed %s -- %s' % (self.expr, _m))
      return False

      # ## Buttons

  def on_pushCheckExpression_pressed(self):
    # LOGGER.info('checking')
    if self.__checkExpression():
      self.MSG('Expression OK %s' % self.expr)
      self.ui.pushAccept.show()

  def on_pushDeleteEquation_pressed(self):
    v = self.selected_variable
    self.delete_variable = False
    self.equations.removeEquation(self.current_eq_ID) # remove IT
    v.removeEquation(self.current_eq_ID)              # remove from variable def
    self.update_space_information.emit()
    self.close()

  def on_pushAccept_pressed(self):
    symbol = str(self.ui.lineNewVariable.text())
    if self.status_new_variable:
      kvariables = RecordVariable() #copy.deepcopy(STRUCTURES_Vars_Equs["variable"])
      kvariables["symbol"] = symbol
      kvariables["type"] = self.selected_variable_type
      kvariables["network"] = self.network_for_variable
      kvariables["index_structures"] = self.checked_var.index_structures
      kvariables["units"] = copy.deepcopy(self.checked_var.units)
      for l in LANGUAGES['compile']:
        kvariables["aliases"][l] = symbol #.append((l, symbol))
      self.variables.addVariable(**kvariables)


    if self.status_new_equation:
      kequations = RecordEquation() # copy.deepcopy(STRUCTURES_Vars_Equs["equation"])
      kequations["lhs"] = symbol
      kequations["rhs"] = str(self.ui.lineExpression.text())
      kequations["incidence_list"] = self.checked_var.incidence_list
      kequations["network"] = self.network_for_variable #self.network_for_expression
      kequations["equation_ID"] = None  # generate a new one
      equation_ID = self.equations.addEquation(**kequations)
      self.variables[symbol].addEquation(equation_ID)


    else:
      eq = self.equations[self.current_eq_ID]
      eq.lhs = symbol
      eq.rhs = str(self.ui.lineExpression.text())
      eq.incidence_list = self.checked_var.incidence_list
      eq.layer = self.actual_network_for_expression

    self.update_space_information.emit()  # TODO fix - not active

    self.ui.groupEquationEditor.hide()
    self.resetEquationInterface()

    self.ui_indices.close()
    # for nw in self.variable_tables:
    [self.variable_tables[nw].close() for nw in self.variable_tables ]
    self.operator_table.close()

    self.hide()
    self.close()

  @staticmethod
  def __printDelete():
    print('going to delete')

  def __setupEditAndDelete(self):
    # TODO: set tooltips

    self.ui.pushDeleteEquation.hide()
    if self.current_alternative != NEW_EQ:
      e = copy.copy(self.equations[self.current_eq_ID])
      self.current_expression = e.rhs
      self.actual_network_for_expression = e.network
      v = self.variables[self.selected_variable_symbol]
      if len(v.equation_list) > 1:
        self.ui.pushDeleteEquation.show()
      self.ui.lineExpression.setText(e.rhs)
    else:
      e = RecordEquation() #copy.deepcopy(STRUCTURES_Vars_Equs["equation"])
      e["name"] = self.selected_variable.doc
      e["rhs"] = NEW_EQ  # No name on equation
      self.ui.lineExpression.setText(e["rhs"])
      self.current_equation_name = e["name"]

    self.ui.lineNewVariable.setText(self.selected_variable_symbol)
    self.ui.groupEquationEditor.show()
    self.status_edit_expr = True
    self.show()

  def setupEquationList(self, variable_symbol):
    v = self.variables[variable_symbol]
    self.selected_variable = v
    self.selected_variable_symbol = variable_symbol
    equation_list = v.equation_list
    print('got dictionary')
    _list = [UNDEF_EQ_NO + TEMPLATES['Equation_definition_delimiter'] + NEW_EQ]
    for alterntative in equation_list:
      equ = self.equations[alterntative]
      _list.append(alterntative + TEMPLATES['Equation_definition_delimiter']
                   + equ.rhs)
    self.ui_equationselector = SingleListSelector(_list)
    self.ui_equationselector.show()
    self.ui_equationselector.newSelection.connect(self.__selectedEquation)

  def __selectedEquation(self, entry):
    print('got it', entry)
    # TODO: fix overlap of syntax - equations and operator
    eq_no, eq_string = entry.split(TEMPLATES['Equation_definition_delimiter'])
    self.current_eq_ID = eq_no
    self.current_alternative = eq_string
    self.status_new_equation = (eq_string == NEW_EQ)
    if eq_string == PORT:
      self.__defGivenVariable()
      return
    print('this is a new equation ?', eq_string, '   ',
          self.status_new_equation)
    self.__setupEditEquation()

  def __setupEditEquation(self):
    self.__setupEditAndDelete()
    # self.ui_indices.show()
    # only show if there is more than one equation
    # TODO: rule for constants --> document
    # TODO: this could be contradicing port variables
    v = self.selected_variable
    if self.selected_variable_type == CONSTANT:
      min_l = 0
    else:
      min_l = 1
    if len(v.equation_list) > min_l:
      self.ui.pushDeleteEquation.show()
    # [self.variable_tables[nw].show()  for nw in self.variable_tables]
    # self.operator_table.show()
    self.show()

  def __defGivenVariable(self):
    self.def_given_variable.emit()


  def on_pushShowIndices_pressed(self):
    self.ui_indices.show()
    [self.variable_tables[nw].show()  for nw in self.variable_tables]
    self.operator_table.show()

  def on_pushResetInterface_pressed(self):
    self.resetEquationInterface()

  def on_pushCancel_pressed(self):
    self.resetEquationInterface()
    self.close()
