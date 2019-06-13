#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 Ontology design facility
===============================================================================

This program is part of the ProcessModelling suite

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2014. 08. 09"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import os
import subprocess
from collections import OrderedDict
from copy import copy
from copy import deepcopy

import pydotplus.graphviz as GV  # python3 -m pip install pydotplus
from jinja2 import Environment  # sudo apt-get install python-jinja2
from jinja2 import FileSystemLoader
# ubuntu18.04 sudo apt-get install python3-pydotplus
from PyQt4 import QtCore
from PyQt4.QtGui import QMainWindow

from Common.common_resources import CONNECTION_NETWORK_SEPARATOR
from Common.common_resources import getIcon
from Common.common_resources import getOntologyName
from Common.common_resources import invertDict
from Common.common_resources import makeTreeView
from Common.ontology_container import OntologyContainer
from Common.resource_initialisation import DIRECTORIES
from Common.resource_initialisation import FILES
from Common.ui_text_browser_popup_impl import UI_FileDisplayWindow
from OntologyEquationEditor.resources import EMPTY_EQ
from OntologyEquationEditor.resources import ENABLED_COLUMNS
from OntologyEquationEditor.resources import EQUATION_TYPE
from OntologyEquationEditor.resources import LANGUAGES
from OntologyEquationEditor.resources import NEW_EQ
from OntologyEquationEditor.resources import NEW_VAR
from OntologyEquationEditor.resources import TEMPLATES
from OntologyEquationEditor.tpg import LexicalError
from OntologyEquationEditor.tpg import SemanticError
from OntologyEquationEditor.tpg import SyntacticError
from OntologyEquationEditor.tpg import WrongToken
from OntologyEquationEditor.ui_aliastableindices_impl import UI_AliasTableIndices
from OntologyEquationEditor.ui_aliastablevariables_impl import UI_AliasTableVariables
from OntologyEquationEditor.ui_equations_impl import UI_Equations
from OntologyEquationEditor.ui_ontology_design import Ui_OntologyDesigner
from OntologyEquationEditor.ui_variabletable_impl import UI_VariableTableDialog
from OntologyEquationEditor.variable_framework import Equations
from OntologyEquationEditor.variable_framework import Expression
from OntologyEquationEditor.variable_framework import IndexStructureError
from OntologyEquationEditor.variable_framework import Indices
from OntologyEquationEditor.variable_framework import UnitError
from OntologyEquationEditor.variable_framework import Units
from OntologyEquationEditor.variable_framework import VarError
from OntologyEquationEditor.variable_framework import Variables

# RULE: fixed wired for initialisation -- needs to be more generic
INITIALVARIABLE_TYPES = {
      "initialise" : ["state", "frame"],
      "connections": ["constant", "transposition"]
      }

CHOOSE_NETWORK = "choose network"
CHOOSE_INTER_CONNECTION = "choose INTER connection"
CHOOSE_INTRA_CONNECTION = "choose INTRA connection"


class EditorError(Exception):
  """
  Exception reporting
  """

  def __init__(self, msg):
    self.msg = msg


class UiOntologyDesign(QMainWindow):
  """
  Main window for the ontology design:
  """

  def __init__(self):
    """
    The editor has  the structure of a wizard,  thus goes through several steps
    to define the ontology.
    - get the base ontology that provides the bootstrap procedure.
    - construct the index sets that are used in the definition of the different
      mathematical objects
    - start building the ontology by defining the state variables
    """

    # set up dialog window with new title
    QMainWindow.__init__(self)
    self.ui = Ui_OntologyDesigner()
    self.ui.setupUi(self)
    # self.ui.pushBack.setIcon(getIcon('^'))
    self.ui.pushWrite.setIcon(getIcon('->'))
    self.setWindowTitle("OntologyFoundationEditor Design")
    # self.ui.combo_01_OntologySubject.show()
    self.radio = [
          self.ui.radioVariables,
          self.ui.radioVariablesAliases,
          self.ui.radioIndicesAliases,
          self.ui.radioCompile]
    [i.hide() for i in self.radio]

    self.ui.groupFiles.hide()
    self.ui.groupVariables.hide()
    # self.ui.groupCompile.hide()

    assert os.path.exists(DIRECTORIES["ontology_repository"])

    self.ontology_name = getOntologyName()
    if not self.ontology_name:
      os._exit(-1)

    ### set up editor =================================================
    self.current_network = None  # holds the current ontology space name
    self.current_variable_type = None
    self.edit_what = None
    self.state = None  # holds this programs state
    self.variables = Variables()
    self.equations = Equations()
    self.equations.linkVariables(self.variables)
    self.variables.linkEquations(self.equations)  # for renaming variables
    self.indices = Indices()
    self.variables.linkIndices(self.indices)  # for renaming variables
    self.aliases_defined = False

    # get ontology
    location = DIRECTORIES["ontology_location"]%str(self.ontology_name)
    self.ontology_container = OntologyContainer(self.ontology_name)
    self.ui.groupOntology.setTitle("ontology : %s"%self.ontology_name)
    # works only for colour and background not font size and font style
    # style = "QGroupBox:title {color: rgb(1, 130, 153);}" # not supported: font-size: 48pt;  background-color:
    # yellow; font-style: italic}"
    # self.ui.groupOntology.setStyleSheet(style)

    self.rules = self.ontology_container.rules
    self.ontology_in_hiearchy = self.ontology_container.ontology_in_hiearchy
    self.ontology_in_hiearchy_inverse = invertDict(self.ontology_container.ontology_in_hiearchy)
    self.networks = self.ontology_container.networks
    self.interconnection_nws = self.ontology_container.interconnection_network_dictionary
    self.intraconnection_nws = self.ontology_container.intraconnection_network_dictionary
    self.variable_types_on_networks = self.ontology_container.variable_types_on_networks
    self.variable_types_on_networks_per_component = self.ontology_container.variable_types_on_networks_per_component
    self.converting_tokens = self.ontology_container.converting_tokens

    # # setup variable indexing
    for nw in self.networks:
      variable_types = self.variable_types_on_networks[nw]
      self.variables.setTypes(variable_types, nw)
      those_who_have_it = self.ontology_container.heirs_list[nw]
      self.variables.setThoseWhoInherit(those_who_have_it, nw)

    for nw in self.ontology_container.interfaces:  # ADDED:
      variable_types = self.ontology_container.interfaces[nw]["internal_variable_classes"]
      self.variables.setTypes(variable_types, nw)
      self.variables.setThoseWhoInherit([nw], nw)

    # get variables, indices and equations or initialise
    variables = self.ontology_container.readVariables()  # variables

    lock_file = FILES["lock_file"]%self.ontology_name

    if os.path.exists(lock_file):
      os.remove(lock_file)

    # there are variables defined in the second stage of the ontology generation
    for v in variables:
      if not self.variables.existSymbol(v):
        variables[v]["symbol"] = v
        if "units" not in variables[v]:
          variables[v]["units"] = Units(ALL=[])
        else:
          variables[v]["units"] = Units(ALL=variables[v]["units"])
        self.variables.addVariable(**variables[v])

    indices = self.ontology_container.readIndices()  # indices
    self.indices.initialise(indices)

    equations = self.ontology_container.readEquations()  # equations
    for e in equations:
      self.equations.addEquation(equation_ID=str(e), **equations[e])
    self.state = "edit"

    # setup for next GUI-phase
    [i.show() for i in self.radio]

    makeTreeView(self.ui.treeWidget, self.ontology_container.ontology_tree)
    self.ui.combo_InterConnectionNetwork.clear()
    self.ui.combo_IntraConnectionNetwork.clear()
    inter_connection_list = []
    intra_connection_list = []
    [inter_connection_list.append(cnw) for cnw in self.interconnection_nws]
    [intra_connection_list.append(cnw) for cnw in self.intraconnection_nws]
    # >>>>>>> 118d9b882be97532535d731bd5de3bfbc3f8451e
    self.ui.combo_InterConnectionNetwork.addItems(sorted(inter_connection_list))
    self.ui.combo_IntraConnectionNetwork.addItems(sorted(intra_connection_list))

    if self.state != "initialise":
      self.ui.combo_InterConnectionNetwork.show()
      self.ui.combo_IntraConnectionNetwork.show()

    self.ui.groupFiles.hide()
    self.ui.groupEdit.hide()
    self.ontology_location = location
    self.__makeAliasDictionary()
    self.variables.reindex()
    return

  def on_pushInfo_pressed(self):
    msg_popup = UI_FileDisplayWindow(FILES["info_ontology_design_editor"])
    msg_popup.exec_()

  def on_radioVariables_pressed(self):
    self.__hideTable()
    self.ui.groupVariables.show()
    self.__writeMessage("edit variables/equations")

  def on_radioVariablesAliases_pressed(self):
    self.__hideTable()
    self.__writeMessage("edit alias table")
    self.ui.groupVariables.hide()
    self.__setupVariablesAliasTable()

  def on_radioIndicesAliases_pressed(self):
    self.__hideTable()
    self.__writeMessage("edit alias table")
    self.ui.groupVariables.hide()
    self.__setupIndicesAliasTable()

  def on_radioCompile_pressed(self):
    for l in LANGUAGES["code_generation"]:
      try:
        self.__compile(l)
      except (EditorError) as error:
        self.__writeMessage(error.msg)

    self.__compile("latex")
    self.__writeMessage("finished latex document")

  def on_radioGraph_clicked(self):
    self.__hideTable()
    self.ui.combo_EditVariableTypes.clear()
    self.ui.combo_EditVariableTypes.addItems(
          self.ontology_container.ontology_tree[self.current_network]["behaviour"]["graph"])

  def on_radioNode_clicked(self):
    self.__hideTable()
    self.ui.combo_EditVariableTypes.clear()
    self.ui.combo_EditVariableTypes.addItems(
          self.ontology_container.ontology_tree[self.current_network]["behaviour"]["node"])

  def on_radioArc_clicked(self):
    self.__hideTable()
    self.ui.combo_EditVariableTypes.clear()
    self.ui.combo_EditVariableTypes.addItems(
          self.ontology_container.ontology_tree[self.current_network]["behaviour"]["arc"])

  def on_treeWidget_clicked(self, index):  # state network_selected
    self.current_network = self.ui.treeWidget.currentItem().name
    print("current network selected: ", self.current_network)
    self.__setupEdit("networks")

  @QtCore.pyqtSlot(str)
  def on_combo_InterConnectionNetwork_activated(self, choice):
    self.__hideTable()
    self.current_network = str(choice)
    self.state = "inter_connections"
    self.__setupEdit("interface")

  @QtCore.pyqtSlot(str)
  def on_combo_IntraConnectionNetwork_activated(self, choice):
    self.__hideTable()
    self.current_network = str(choice)
    self.state = "intra_connections"
    self.__setupEdit("intraface")

  @QtCore.pyqtSlot(int)
  def on_tabWidget_currentChanged(self, which):
    print("changed tab")
    self.ui.combo_EditVariableTypes.hide()

  def __setupEdit(self, what):
    """

    @param nw: either a network or a connection network
    @return: None
    """

    self.__hideTable()

    nw = self.current_network

    if what == "interface":
      vars_types_on_network_variable = self.ontology_container.interfaces[nw]["internal_variable_classes"]
      self.ui.combo_EditVariableTypes.clear()
      self.ui.combo_EditVariableTypes.addItems(vars_types_on_network_variable)
      network_variable = nw
      network_expression = self.ontology_container.interfaces[nw]["left_network"]
      vars_types_on_network_expression = self.ontology_container.interfaces[nw]["left_variable_classes"]
    elif what in "intraface":
      network_variable = self.intraconnection_nws[nw]["right"]
      network_expression = self.intraconnection_nws[nw]["left"]
      vars_types_on_network_variable = self.ontology_container.variable_types_on_networks[network_variable]
      self.ui.combo_EditVariableTypes.clear()
      self.ui.combo_EditVariableTypes.addItems(vars_types_on_network_variable)
      vars_types_on_network_expression = self.ontology_container.variable_types_on_networks[network_expression]
    else:
      self.ui.radioNode.toggle()
      self.on_radioNode_clicked()
      network_variable = nw
      network_expression = nw
      vars_types_on_network_variable = self.ontology_container.variable_types_on_networks[network_variable]
      vars_types_on_network_expression = self.ontology_container.variable_types_on_networks[network_expression]

    self.ui_eq = UI_Equations(self.variables, self.equations, self.indices,
                              network_variable, network_expression,
                              vars_types_on_network_variable, vars_types_on_network_expression
                              )
    self.ui_eq.update_space_information.connect(self.__updateVariableTable)

    self.ui.combo_EditVariableTypes.show()
    self.ui.groupFiles.show()
    self.ui.groupEdit.show()
    self.ui.pushWrite.show()

  def __hideTable(self):
    if "table_variables" in self.__dir__():
      self.table_variables.hide()

  @QtCore.pyqtSlot(str)
  def on_combo_EditVariableTypes_activated(self, selection):
    selection = str(selection)
    if selection == "choose":
      return

    self.current_variable_type = selection
    self.ui.groupEdit.show()
    self.__setupVariableTable(selection)
    self.table_variables.show()

    self.ui.combo_EditVariableTypes.show()
    self.ui.groupFiles.show()
    self.ui.pushWrite.show()
    self.ui.groupEdit.show()

  def on_pushWrite_pressed(self):
    self.ontology_container.writeVariablesEquations(self.variables, "variable", exclude=["symbol", "indices"])
    self.ontology_container.writeVariablesEquations(self.equations, "equation", exclude=["equation_ID"])
    self.ontology_container.writeIndex(self.indices, ["index", "block_index"])
    self.state = 'edit'

    for l in LANGUAGES["code_generation"]:
      try:
        self.__compile(l)
      except (EditorError) as error:
        self.__writeMessage(error.msg)

    if len(self.equations) > 0:
      self.__compile("latex")

  def __compile(self, language):
    # TODO: identify equation types: differential, integration and constant
    f_name = os.path.join(self.ontology_location, language + '.code')
    # buffer = []
    f = open(f_name, 'w')
    var_list = self.variables.getVariableList()
    expression = Expression(self.variables,
                            self.indices,
                            language=language)

    for variable_symbol in var_list:
      v = self.variables[variable_symbol]
      if not hasattr(v, "compiled"):
        v.compiled = {}
      if v.symbol != NEW_VAR:
        v.compiled[language] = str(expression(variable_symbol))  # !!! result is an object
        indices = []
        for index in v.index_structures:
          if index in self.indices:
            indices.append(self.indices[index]["aliases"][language])
        if language in LANGUAGES['code_generation']:
          print('variable : ', v.compiled[language],
                ' : ', v.doc,
                ' : ', v.type,
                ' : ', v.units,
                ' : ', indices,
                file=f)

        else:
          v.units_latex = v.units.prettyPrint()
          print('variable gugus : ', v.compiled[language], ':: ', v.doc, file=f)
          print('writing units in language %s:'%language, v.units_latex)

    for e in self.equations:
      # print("next equation", e)
      expr = self.equations[e].rhs

      variable_symbol = self.equations[e].lhs
      if expr not in [EMPTY_EQ, NEW_EQ]:
        try:
          res = expression(expr)
        except (SemanticError,
                SyntacticError,
                LexicalError,
                WrongToken,
                UnitError,
                IndexStructureError,
                VarError,
                ) as _m:
          print('checked expression failed %s -- %s'%(variable_symbol, _m))

        lhs = self.variables[variable_symbol].compiled[language]
        print("equation %s:"%e, '\t', lhs, '= ', res, file=f)
        # buffer.append(str(res))
        # put away the compiled equations for latex only
        self.equations[e].latex = str(res)
        self.equations[e].number = e
        self.equations[e].lhs_compiled = lhs
        self.equations[e].equation_type = res.equation_type

    f.close()
    self.__writeMessage("Wrote {} output".format(language))
    if language == "latex":
      self.__makeLatexDocument()

  def __makeLatexDocument(self):
    # latex
    #
    print('=============================================== make latex ================================================')
    language = "latex"
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))

    vars = OrderedDict()

    # for nw in all_networks:
    # networks = list(self.variable_types_on_networks_per_component.keys())
    networks = copy(self.ontology_container.networks)
    # networks.extend(self.ontology_container.interfaces)
    for nw in networks:
      ontology_behaviour = self.ontology_container.ontology_tree[nw]["behaviour"]
      vars[nw] = OrderedDict()
      for comp in ontology_behaviour: #self.variable_types_on_networks_per_component[nw]:
        for t in ontology_behaviour[comp] : # self.variable_types_on_networks_per_component[nw][comp]:
          for s in self.variables:
            if (self.variables[s].network == nw) and (self.variables[s].type == t):
              vars[nw][s] = self.variables[s]

    for inw in self.ontology_container.interfaces:
      vars[inw] = OrderedDict()
      for s in self.variables:
        if self.variables[s].network == inw:
          vars[inw][s] = self.variables[s]




    # main.tex

    networks.extend(self.ontology_container.interfaces)
    names = []
    for nw in networks:
      names.append(str(nw).replace(CONNECTION_NETWORK_SEPARATOR, '--'))

    j2_env = Environment(loader=FileSystemLoader(THIS_DIR), trim_blocks=True)
    s = j2_env.get_template(FILES["latex_template_main"]).render(ontology=names) #self.networks)
    f_name = FILES["latex_main"] % self.ontology_name
    f = open(f_name, 'w')
    f.write(s)
    f.close()


    for nw in networks:
      # v = OrderedDict(sorted(vars[nw].items(), key=lambda t: t[1].symbol))
      v = vars[nw]
      j2_env = Environment(loader=FileSystemLoader(THIS_DIR), trim_blocks=True)
      s = j2_env.get_template(FILES["latex_template_variables"]).render(variables=v)
      name = str(nw).replace(CONNECTION_NETWORK_SEPARATOR, '--')
      f_name = FILES["latex_variables"]%(
            self.ontology_location, name)
      # 'variables_' + name + '.tex')
      f = open(f_name, 'w')
      f.write(s)
      f.close()

    eqs = {}
    for e_type in EQUATION_TYPE:  # split into equation types
      eqs[e_type] = OrderedDict()

    for e in self.equations:
      eq = self.equations[e]
      this_eq_type = eq.equation_type
      # print("equation %s is of type %s" % (eq.number, this_eq_type))
      eqs[this_eq_type][e] = deepcopy(eq)

    for e_type in EQUATION_TYPE:
      j2_env = Environment(loader=FileSystemLoader(THIS_DIR), trim_blocks=True)
      s = j2_env.get_template(FILES["latex_template_equations"]). \
        render(equations=eqs[e_type], variables=self.variables)
      f_name = FILES["latex_equations"]%(self.ontology_location, str(e_type))
      f = open(f_name, 'w')
      f.write(s)
      f.close()

    # self.__makeDotGraphs()

    location = DIRECTORIES["latex_main_location"] % self.ontology_location
    f_name = FILES["latex_shell_var_equ_doc_command_exec"] % self.ontology_location

    # print(f_name)


    args = ['sh', f_name, location]
    # print('ARGS: ', args)
    make_it = subprocess.Popen(
          args,
          # start_new_session=True,
          # stdout=subprocess.PIPE,
          # stderr=subprocess.PIPE
          )
    out, error = make_it.communicate()
    self.__writeMessage("Wrote {} output".format(language))

  def __getCompiledIndexList(self, variable_symbol, language):
    v = self.variables[variable_symbol]
    ind = []
    if v.index_structures:  # index structure is part of the variable def
      for i in v.index_structures:
        index = self.indices.compileIndex(i, language)
        ind.append(index)
    else:
      ind = ''
    return ind

  def __makeDotGraphs(self):
    # http://www.graphviz.org/doc/info/colors.html

    vt_colour = ['white', 'yellow', 'darkolivegreen1', 'salmon', 'tan',
                 'tomato', 'cyan', 'green', 'grey',
                 'lightcyan', 'lightcyan1', 'lightcyan2',
                 'lightcyan3', 'lightcyan4',
                 ]

    nodes = []
    edges = []
    nw_count = 0
    dot_graph = {}
    s_nw_vt = "%s___%s"

    vt_colours = {}
    var_types = set()
    for nw in self.networks:
      [var_types.add(vt)
       for vt in self.ontology_container.variable_types_on_networks[nw]]

    var_types = list(var_types)
    for i in range(len(var_types)):
      vt_colours[var_types[i]] = vt_colour[i]

    for nw in self.networks:
      dot_graph[nw] = GV.Dot(graph_name=nw, label=nw,
                             # suppress_disconnected=True,
                             rankdir='TD')

      vt_cluster = {}
      vt_count = 0
      for vt in self.ontology_container.variable_types_on_networks[nw]:
        vt_cluster[vt] = GV.Cluster(graph_name=s_nw_vt%(nw, vt),
                                    suppress_disconnected=False,
                                    label=vt,
                                    rankdir='TD')
        for v in self.variables.getVariablesIndexedType(vt, nw):
          v_name = str(v)  # s_v%(nw_count,v)
          v_node = GV.Node(name=v_name,
                           style='filled',
                           fillcolor=vt_colours[vt],
                           penwidth=3,
                           fontsize=12)
          nodes.append(v)
          vt_cluster[vt].add_node(v_node)
        for e in self.equations:
          v_s = self.equations[e].lhs
          if self.equations[e].network == nw:
            if self.variables[v_s].type == vt:
              e_name = str(e)  # s_e%(nw_count,e)
              e_node = GV.Node(name=e_name,
                               shape='box',
                               style='filled',
                               fillcolor='pink',
                               fontsize=12)
              nodes.append(e)
              vt_cluster[vt].add_node(e_node)
              for l in self.equations[e].incidence_list:
                v_name = str(l)
                e_name = str(e)
                edge = GV.Edge(src=v_name, dst=e_name,
                               splines='ortho')
                edges.append((l, e))
                dot_graph[nw].add_edge(edge)
              v_name = str(v_s)
              e_name = str(e)
              edge = GV.Edge(src=e_name, dst=v_name,
                             splines='ortho')
              vt_cluster[vt].add_edge(edge)
        vt_count += 1
        dot_graph[nw].add_subgraph(vt_cluster[vt])
      nw_count += 1
      f_name = FILES["ontology_graphs_ps"]%(self.ontology_location, nw)

      try:
        dot_graph[nw].write_ps(f_name, )  # prog='fdp')
        f_name2 = DIRECTORIES["ontology_graphs_dot"]%(self.ontology_location, nw)
        dot_graph[nw].write(f_name2, format='raw')
      except:
        print("cannot generate dot graph", f_name)

    print("ferdig med det - no of colours %s - %s"%(nw_count, vt_count))

  def update_tables(self):
    variable_type = self.current_variable_type
    print(">>> udating table :", variable_type)
    self.tables["variables"][variable_type].reset_table()
    self.ui_eq.variable_table.reset_table()

  def finished_edit_table(self, what):
    print("finished editing table : ", what)
    self.__makeAliasDictionary()  # check if all variables are defined
    self.ui.groupEdit.show()
    self.ui.groupFiles.show()
    self.ui.pushWrite.show()
    try:
      self.table_aliases_i.close()
      self.table_aliases_v.close()
    except:
      pass

  def closeEvent(self, event):
    self.close_children(event)
    self.close()

  def close_children(self, event):
    try:
      self.table_variables.close()
    except:
      pass
    try:
      self.table_aliases_v.close()
    except:
      pass
    try:
      self.table_aliases_i.close()
    except:
      pass
    try:
      self.ui_eq.closeEvent(event)
    except:
      pass

  def initialiseAndWriteIndices(self):

    list_of_objects = ["node", "arc"]
    for nw in self.networks:
      for item in list_of_objects:
        rind = self.ontology_container.makeRawIndex(item, nw)
        self.indices.add(rind["symbol"], **rind)

      for token in self.ontology_container.tokens_on_networks[nw]:
        for typed_token in self.ontology_container.token_typedtoken_on_networks[nw][token]:
          rind = self.ontology_container.makeRawIndex(typed_token, nw)
          self.indices.add(rind["symbol"], **rind)
          for item in list_of_objects:
            outer = copy(item)
            inner = copy(typed_token)
            symbol = TEMPLATES['block_index']%(outer, inner)
            rblk = self.ontology_container.makeRawBlockIndex(symbol, outer, inner, nw)
            self.indices.add(rblk["symbol"], **rblk)
          if typed_token in self.converting_tokens:
            symbol = "%s_conversion"%(typed_token)
            crind = self.ontology_container.makeRawIndex(symbol, nw)
            self.indices.add(crind["symbol"], **crind)
            item = "node"
            outer = item
            inner = symbol
            symbol = TEMPLATES['block_index']%(outer, inner)
            rblk = self.ontology_container.makeRawBlockIndex(symbol, outer, inner, nw)
            self.indices.add(rblk["symbol"], **rblk)
    for index in self.indices:
      for l in LANGUAGES['aliasing']:
        self.indices[index]["aliases"][l] = self.indices[index]["symbol"]

    self.ontology_container.writeIndex(self.indices, ["index", "block_index"])

  def initialiseVariableSpace(self):
    for v in self.ontology_container.instantiation:
      kvariables = deepcopy(self.ontology_container.instantiation[v])
      kvariables["units"] = Units(ALL=kvariables["units"])
      for l in LANGUAGES['compile']:
        kvariables["aliases"][l] = kvariables["symbol"]
      self.variables.addVariable(**kvariables)
    return

  def __setupVariableTable(self, choice):
    if self.current_network in self.interconnection_nws:
      network_variable = self.current_network #self.interconnection_nws[self.current_network]["right"]
      network_expression = network_variable #self.interconnection_nws[self.current_network]["left"]
    elif self.current_network in self.intraconnection_nws:
      network_variable = self.intraconnection_nws[self.current_network]["right"]
      network_expression = self.intraconnection_nws[self.current_network]["left"]
    else:
      network_variable = self.current_network
      network_expression = self.current_network
    self.table_variables = UI_VariableTableDialog("edit",
                                                  self.variables,
                                                  self.equations,
                                                  self.indices,
                                                  network_variable,
                                                  network_expression,
                                                  choice,
                                                  choice in self.rules["has-port-variables"],
                                                  mode='inherit'
                                                  )
    for choice in choice:
      try:
        enabled_columns = ENABLED_COLUMNS[self.state][choice]
      except:
        enabled_columns = ENABLED_COLUMNS[self.state]["others"]
      self.table_variables.enable_column_selection(enabled_columns)

    self.ui_eq.def_given_variable.connect(self.table_variables.defineGivenVariable)
    self.table_variables.completed.connect(self.finished_edit_table)
    self.table_variables.new_variable.connect(self.ui_eq.setupNewVariable)
    self.table_variables.new_equation.connect(self.ui_eq.setupNewEquation)

  def __updateVariableTable(self):
    self.table_variables.close()
    self.__setupVariableTable(self.current_variable_type)
    self.table_variables.show()

  def __setupVariablesAliasTable(self):
    self.__makeAliasDictionary()

    variables = self.variables.getVariableList()
    self.table_aliases_v = UI_AliasTableVariables(variables, self.aliases_v)
    self.table_aliases_v.completed.connect(self.__updateAliases_Variables)
    self.table_aliases_v.completed.connect(self.finished_edit_table)
    self.table_aliases_v.show()

  def __setupIndicesAliasTable(self):
    print("gotten here")
    self.table_aliases_i = UI_AliasTableIndices(self.indices)  # , self.aliases_i)
    self.table_aliases_i.completed.connect(self.__updateAliases_Indices)
    self.table_aliases_i.completed.connect(self.finished_edit_table)
    self.table_aliases_i.show()

  def __makeAliasDictionary(self):
    self.aliases_v = {}
    self.aliases_defined = True
    self.ui.radioCompile.show()
    for v in self.variables:
      self.aliases_v[v] = dict(self.variables[v].aliases)
      for language in LANGUAGES["compile"]:
        if language not in self.aliases_v[v]:
          self.aliases_v[v][language] = v
      for l in self.aliases_v[v]:
        if NEW_VAR in self.aliases_v[v][l]:
          self.aliases_defined = False
    if self.aliases_defined:
      self.ui.radioCompile.show()
    else:
      self.ui.radioCompile.hide()

  def __writeMessage(self, message):
    self.ui.msgWindow.clear()
    self.ui.msgWindow.setText(message)

  def __updateAliases_Variables(self):
    print("update", self.aliases_v)
    for v in self.variables:
      self.variables[v].aliases = self.aliases_v[v]
    # self.indices.compile()

  def __updateAliases_Indices(self):
    print("updating indices")
    self.indices.compile()
    self.ontology_container.writeIndex(self.indices, ["index", "block_index"])
