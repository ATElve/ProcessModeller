"""
Author:  Tobias Elve and Andreas Johannesen
What:    The new model factory
Started: 2019-05-20
Reason:  Because the old was outdated
Status:  Production
Contact: arne.t.elve(at)ntnu.no
"""

import os
from time import strftime                                    # Library for time
import copy
import numpy as np

from jinja2 import Environment, FileSystemLoader

from Common.resource_initialisation import FILES, DIRECTORIES
from Common.ontology_container import getData

from OntologyEquationEditor.variable_framework import Expression, Variables, Equations, Indices, Units
from OntologyEquationEditor.resources import CODE              # Code templates

from ModelRenderer.model_framework import Model


class ModelRenderer(object):
  """
  Model renderer

  Reads in following files:
    - ontology: Knowlengde library
    - variables: List of all available variables in the current ontology
    - equations: Dict with all equations available for the current ontology
    - typed tokens: Dict of all typed tokens with reactions an such.
    - indices: Model structure file, raw file, not model specific
    - model file: model file specific with structure
    - cases: load the case compremising three files:
      - nodes
      - arcs
      - globals
      - calculation_sequence

  Render all this information into executable python code
  """

  def __init__(self, ontology, model_name, case_name):
    self.ontology = ontology
    self.case_name = case_name
    # self.ui = ui
    self.onto_name = self.ontology.ontology_name                     # Shortcut
    self.onto_path = self.ontology.onto_path
    self.mod_name = model_name
    self.model_dict = getData(FILES["model_file"] % (self.onto_name,
                                                     self.mod_name))
    self.vars_dict = self.ontology.vars
    self.eqs_dict = self.ontology.eqs
    self.rules = getData(FILES["rules_file"] % (self.onto_name))

    self.typed_tokens_dict = getData(FILES["typed_token_file"] % (self.onto_name))
    self.indices_dict = getData(FILES["indices_file"] % (self.onto_name))
    self.model = Model(self.model_dict, self.typed_tokens_dict, self.ontology)

    self.variables = Variables()
    self.equations = Equations()
    self.equations.linkVariables(self.variables)
    self.variables.linkEquations(self.equations)       # for renaming variables
    self.indices = Indices()
    self.variables.linkIndices(self.indices)           # for renaming variables

    self.init_node_loc = FILES["init_nodes"] % (self.onto_name,
                                                self.mod_name,
                                                self.case_name)
    self.init_node_dict = getData(self.init_node_loc)
    self.init_arc_loc = FILES["init_arcs"] % (self.onto_name,
                                              self.mod_name,
                                              self.case_name)
    self.init_arc_dict = getData(self.init_arc_loc)
    self.init_globals_loc = FILES["init_globals"] % (self.onto_name,
                                                     self.mod_name,
                                                     self.case_name)
    self.init_globals_dict = getData(self.init_globals_loc)
    self.init_globals_loc = FILES["init_globals"] % (self.onto_name,
                                                     self.mod_name,
                                                     self.case_name)
    self.init_globals_dict = getData(self.init_globals_loc)
    self.init_calseq_loc = FILES["calculation_sequence"] % (self.onto_name,
                                                     self.mod_name,
                                                     self.case_name)
    self.init_calseq_dict = getData(self.init_calseq_loc)
    self.variables_init_used_set = set(self.init_calseq_dict['vars'])
    self.calculation_order = self.init_calseq_dict['calculation_order']

    self.var_list = self.get_all_used_variables()

  def generate_output(self):
    """
    Generate the output code
    """
    # initial variables
    self.variables_init = self.gather_variables_initial()
    self.output_initial_variables = self.render_initial_variables()
    self.writeInitials(self.output_initial_variables)

    # network variables
    self.network_main_list = self.gather_network_variables()
    self.output_network_variables = self.render_network_variables()
    self.writeNetworks(self.output_network_variables)

  def setup_system(self, language):
    """
    Input from graphical user interface.
    Frist an foremost used to declare output language and then put together the
    simulation model.
    """
    self.language = language

    for nw in self.ontology.networks:
      variable_types = self.ontology.variable_types_on_networks[nw]
      self.variables.setTypes(variable_types, nw)
      those_who_have_it = self.ontology.heirs_list[nw]
      self.variables.setThoseWhoInherit(those_who_have_it, nw)

    variables = self.ontology.readVariables()
    for v in variables:
      if not self.variables.existSymbol(v):
        variables[v]["symbol"] = v
        variables[v]["units"] = Units(ALL=variables[v]["units"])
        self.variables.addVariable(**variables[v])

    indices = self.ontology.readIndices()                             # indices
    for i in indices:
      self.indices.add(i, **indices[i])

    equations = self.ontology.readEquations()                       # equations
    for e in equations:
      self.equations.addEquation(equation_ID=str(e), **equations[e])

    self.expression = Expression(self.variables, self.indices, language)

    # print(self.equations['0'].__dict__)
    # print(self.expression(self.equations['0'].rhs))

  def get_all_used_variables(self):
    var_list = []
    for eq in self.calculation_order:
      var_list += self.eqs_dict[eq]['incidence_list']
    return var_list

  def gather_variables_initial(self):
    variables_init = {}
    for label in self.variables_init_used_set:

      variables_init[label] = {}
      var = self.vars_dict[label]
      variable_type = var['type']
      if variable_type in self.rules["has-port-variables"]:
        index_sets = [self.model.indices[index_set] for index_set in var['index_structures']]
        if index_sets:
          # print('var: ', label, index_sets)
          for index_set in index_sets:
            if index_set.type == 'block_index':
              # print
              # print(self.indices)
              ind_list = self.indices_dict[index_set.label]['outer']
            elif index_set.label in self.typed_tokens_dict.keys():
              ind_list = 'globals'
            else:

              ind_list = index_set.label
        else:
          ind_list = 'globals'                          # Non indexed variables

      else:
        print('VARIABLE NOT IN CORRECT LIST')    # TODO: remove Already checked
      if ind_list == 'node':
        value = {}
        variables_init[label]['group'] = 'node'
        for node, vars in self.init_node_dict.items():
          value[node] = vars[label]
        variables_init[label]['value'] = value
        # print(self.init_node_dict)
      elif ind_list == 'arc':
        value = {}
        variables_init[label]['group'] = 'arc'
        for arc, vars in self.init_arc_dict.items():
          value[arc] = vars[label]
        variables_init[label]['value'] = value
      elif ind_list == 'globals':
        value = {}
        variables_init[label]['group'] = 'globals'
        variables_init[label]['value'] = self.init_globals_dict[label]
    return variables_init

  def render_initial_variables(self):
    var_output = []
    var_str = '{} = {}'
    for label, variable in self.variables_init.items():
      val = []
      if variable['group'] == 'node':
        for node, value in sorted(variable['value'].items()):
          val.append(value[0])
      elif variable['group'] == 'arc':
        for arc, value in sorted(variable['value'].items()):
          val.append(value[0])
      elif variable['group'] == 'globals':
        if self.variables[label].index_structures:
          val += variable['value'][0]                                    # LIST
        else:
          val = copy.copy(variable['value'][0][0])
      out_put_version = CODE[self.language]["array"] % (val)
      var_output.append(var_str.format(label, out_put_version))
    return var_output

###############################################################################
###############################################################################

  def gather_network_variables(self):
    network_vars = []
    for label, var_dict in self.vars_dict.items():
      if var_dict['type'] == 'network' and var_dict['immutable']:
        network_vars.append(label)
    return network_vars

  def render_network_variables(self):
    output_variables = []
    out_str = '{var} = {list}(\n{val})'
    for label in self.network_main_list:
      var = self.vars_dict[label]
      if var['doc'] == 'incidence matrix':
        token = var['token']
        mechanism = var['transfer_mechanism']
        network = var['network']
        var_obj = self.variables[label]
        if token in self.typed_tokens_dict.keys():
          print('NOT AN INCIDENCE MATRIX')
        else:
          mat = self.makeIncidenceMatrix(var_obj, token, mechanism, network)
          print(mat)
          str_mat = self.matrix_to_string(mat)
          out = out_str.format(var = var['aliases'][self.language],
                               list = CODE[self.language]['list'],
                               val = str_mat)
          output_variables.append(out)
        # mechanism = var['']
    print(output_variables)
    return output_variables

  def size_of_variable(self, variable):
    """
    Calculate size of variable
    """

    component_list = {}
    index_structures = variable.index_structures
    if not index_structures:
      size = 1
    else:
      size = []
      curr_network = self.model.networks[variable.network]
      for ind_set in index_structures:
        length = 0
        curr_ind_obj = self.model.indices[ind_set]
        if curr_ind_obj.type == 'index':
          if ind_set == 'node':
            component_list['node'] = []
            for node in curr_ind_obj.mapping:
              if str(node) in curr_network.nodes:           # HAVE TO BE STRING
                component_list['node'].append(node)
                length += 1
          elif ind_set == 'arc':
            component_list['arc'] = []
            for arc in curr_ind_obj.mapping:
              if str(arc) in curr_network.arcs:
                component_list['arc'].append(arc)
                length += 1
          else:
            print("THIS SHOULD NOT HAPPEN")
            print("THE USAGE OF THIS FUNCTION HAS NOT BEEN IMPLEMENTED")
        else:
          print("LOOK TO BLOCK INDEXES")
        size.append(length)

    return size, component_list

  def matrix_to_string(self, mat, prefix = ''):       # Fixed sign and seprator
    """
    Converts to numpy string
    """
    if self.language == 'python':
      mat_str = np.array2string(mat, prefix = prefix, sign = ' ', separator = ', ')
    else:
      mat_str = str(mat)
    return mat_str

  def makeIncidenceMatrix(self, variable, token, mechanism, network):
    """
    Generate incidence matrix based on variable,  token,  network and mechanism
    of transport.

    Args:
      variable: variable object
      token: transported token
      network: which network
      mechanism: mechanism

    Returns:
      mat: Incidence matrix
    """
    size, cons_list = self.size_of_variable(variable)
    mat = np.zeros(size)
    for i, node_label in enumerate(cons_list['node']):
      for j, arc_label in enumerate(cons_list['arc']):
        arc = self.model.arcs[str(arc_label)]
        if str(node_label) == str(arc.source) and mechanism == arc.mechanism:
          mat[i, j] = -1.
        elif str(node_label) == str(arc.sink) and mechanism == arc.mechanism:
          mat[i, j] = 1.
    return mat

  def writeInitials(self, variables):
    output_dir = DIRECTORIES["output_language"] % (self.onto_name,
                                                   self.mod_name,
                                                   self.case_name,
                                                   self.language)
    if not os.path.exists(output_dir):
      os.mkdir(output_dir)
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    TEMPLATE_DIR = os.path.join(THIS_DIR, 'Templates/')    # Internal placement

    j2_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), trim_blocks=True)
    s = j2_env.get_template('template_initials.py.j2').render(
        date = '{}'.format(strftime("%Y-%m-%d %H:%M:%S")),
        model_name = self.mod_name,
        case_name = self.case_name,
        variables = variables,
        author = os.uname().nodename,
      )
    out_file = FILES["constants_initialized"] % (self.onto_name,
                                                 self.mod_name,
                                                 self.case_name,
                                                 self.language)
    f = open(out_file, 'w+')
    f.write(s)
    f.close()

  def writeNetworks(self, variables):
    """
    write out the network variable file
    """
    output_dir = DIRECTORIES["output_language"] % (self.onto_name,
                                                   self.mod_name,
                                                   self.case_name,
                                                   self.language)
    if not os.path.exists(output_dir):
      os.mkdir(output_dir)
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    TEMPLATE_DIR = os.path.join(THIS_DIR, 'Templates/')    # Internal placement

    j2_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), trim_blocks=True)
    s = j2_env.get_template('template_networks.py.j2').render(
        date = '{}'.format(strftime("%Y-%m-%d %H:%M:%S")),
        model_name = self.mod_name,
        case_name = self.case_name,
        variables = variables,
        author = os.uname().nodename,
      )
    out_file = FILES["networks_variables"] % (self.onto_name,
                                             self.mod_name,
                                             self.case_name,
                                             self.language)
    f = open(out_file, 'w+')
    f.write(s)
    f.close()


  def equation_list_output(self):
    eq_list_output = []
    for eq in self.calculation_order:
      eq_str = self.expression(self.equations[eq].rhs)
      print(eq_str)
