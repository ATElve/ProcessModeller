
"""
===============================================================================
 THE variable framework
===============================================================================

Translate  between global  representation  and local  representation.  Could be
extended  to do  the compilation  job as  well removing it  from  the  phys var
package.


Section Abstract Syntax
=======================

The  module  generates  variables  and  equations  building  on  the classes of
"physvars" the physical variables module.

The   variables   and    equations   are   stored   in   the   variable   space
(class physvars.VariableSpace).  Each  variable  may  be  given  by alternative
equations. Alternatives are coded into the variable name by adding a __V## thus
two underlines and an integer number.


 Equation / variable factory
 Generates two dictionaries and a list:
 EQUATIONS: a dictionary  of equations with  the key being the defined variable
            if the equation is implicit a new zero variable is to be defined.

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2012. 04. 23"
__since__ = "2014. 10. 07"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"


# TODO: think about removing the compilation from the physvar package

import OntologyEquationEditor.resources as resources
from Common.common_resources import CONNECTION_NETWORK_SEPARATOR
from Common.common_resources import STRUCTURES_Vars_Equs


from collections import OrderedDict
from jinja2 import Environment
from jinja2 import FileSystemLoader

from OntologyEquationEditor.resources import LANGUAGES
from OntologyEquationEditor.tpg import VerboseParser, SemanticError, tpg
from OntologyEquationEditor.tpg import SyntacticError, LexicalError, WrongToken

import copy
import os


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
j2_env = Environment(loader=FileSystemLoader(THIS_DIR), trim_blocks=True)
internal = LANGUAGES["internal_code"]


def stringBinaryOperation(language, operation, left, right,
                          index = None, indices = None):
  """
  :param language: current output language
  :param operation: what binary operation
  :param left: left argument (object)
  :param right: right argument (object)
  :param index: index (object)
  :param index_compiled for reduced product (string)
  :param global_list: the global ordered list of indices
  :return: code string

  Operation: fills in the templates stored in resources.
  Special case is  the reduction product.  If  the output is  a matrix-oriented
  language,  then  one  needs  to  implement  the implicit  rules of the matrix
  multiplication. Let A and B be two two-dimensional objects with the indexsets
  a,b and c. Thus we write Aab |a| Bac, thus reduce the two objects over a then
  the result is Cbc. Thus in matrix notation using the prime for transposition:

  Aab |a| Bac -->   (Aab)' *  Bac     = Cbc    1,2 |1| 1,3 = 2,3
  Aab |a| Bac -->  ((Aab)' *  Bac)'   = Ccb    1,2 |1| 1,3 = 3,2     # BUG HERE
  Aab |b| Bbc -->    Aab   *  Bbc     = Cac    1,2 |2| 2,3 = 1,3
  Aac |a| Bab -->  ((Aac)' *  Bab)'   = Cbc    1,3 |1| 1,2 = 2,3
  Aac |c| Bbc -->    Aac   * (Bbc)'   = Cab    1,3 |3| 2,3 = 1,2
  Aa  |a| Bab -->   ((Aa)' *  Bab)'   = Cb     1   |1| 1,2 = 2
  Aab |a| Ba  -->   (Aab)' *  Ba      = Cb     1,2 |1| 1   = 2
  Ab  |b| Bab -->   (Ab    * (Bab)')' = Ca     2   |2| 1,2 = 1
  Aab |b| Bb  -->    Aab   *  Bb      = Ca     1,2 |2| 2   = 1

  Rules:
  - if left  index in position 1  --> transpose left
  - if right index in position 2  --> transpose right
  - if left only one index transpose left and result

  Note:
  - The index results must always be in the original order, here alphabetically
  - The product   Aab |b| Bab --> is forbidden as it results in a Caa, which is
    not permitted.
  - Objects with one dimension only are interpreted as column vectors
  """
  if left.type == resources.TEMP_VARIABLE:
    a = resources.CODE[language]['()'] % left.__str__()
  else:
    a = "%s" % left.__str__()
  if right.type == resources.TEMP_VARIABLE:
    b = resources.CODE[language]['()'] % right.__str__()
  else:
    b = "%s" % right.__str__()
  if index:                                 # If index present >> reduceproduct
    res_index_structure = []                             # Resulting index sets
    index_compiled = indices[index]["aliases"][language] #indices.compileIndex(index, language)
    global_list = list(indices.keys())
    if language in resources.LANGUAGES['matrix_form']:
      try:
        left_transpose = left.index_structures.index(index) == 0
        right_transpose = right.index_structures.index(index) == 1
        left_vector = len(left.index_structures) == 1
        right_vector = len(right.index_structures) == 1
      except:
        print('>>>>>>>>>>>>>>>>>>>>> reduce product -- something goes wrong')
      if left_transpose:
        a = resources.CODE[language]['transpose'] % a
      if right_transpose:
        b = resources.CODE[language]['transpose'] % b
      s = resources.CODE[language][operation] % (a, b)     # index_compiled, b)
      if left_vector:
        if not right_vector:    # vector * matrix --> row  vector --> transpose
          s = resources.CODE[language]['transpose'] % s
      else:
        if right_vector:     # matrix * vector --> column vector --> do nothing
          pass
        else:      # matrix * matrix --> matrix ---> complicated needs analysis
          if left_transpose:
            res_index_structure.append(left.index_structures[1])
          else:
            res_index_structure.append(left.index_structures[0])
          if right_transpose:
            res_index_structure.append(right.index_structures[0])
          else:
            res_index_structure.append(right.index_structures[1])
          if global_list.index(res_index_structure[0]) >  \
             global_list.index(res_index_structure[1]):
            s = resources.CODE[language]['transpose'] % s

    else:
      s = resources.CODE[language][operation] % (a,  index_compiled, b)
  else:
    s = resources.CODE[language][operation] % (a, b)
  return s


def simulateDeletion(variables, equations, var):
  vars_eqs = {}
  for v, variable in variables.items():
    s = copy.copy(variable.symbol)
    vars_eqs[s] = copy.copy(variable.equation_list)
    # if variable.type == 'state':
    #   vars_state.append(variable.symbol)
  equs_incidence = OrderedDict()
  for e in equations:
    id = (copy.copy(equations[e].equation_ID))
    equs_incidence[id] = (copy.copy(equations[id].lhs),
                          copy.copy(equations[id].incidence_list))
  d_vars = set()
  d_equs = set()
  # print(vars_eqs)
  reduceVars(vars_eqs, variables, equs_incidence, d_vars, d_equs, var.symbol)
  return d_vars, d_equs


def reduceVars(vars_eqs, variables, equs, d_vars, d_equs, var_symbol):
  var = variables[var_symbol]
  if var.type != 'state':            # RULE: Cannot delete state variables
    d_vars.add(var_symbol)

  for id in vars_eqs[var_symbol]:
    if id not in d_equs:
      d_equs.add(id)
      if var.type == 'state':
        return                                                        # Way out
      else:
        for i, eq in equs.items():
          if i < id:                    # Only delete down the equation tree...
            continue
          lhs, equs_il = eq
          if var_symbol in equs_il:
            reduceVars(vars_eqs, variables, equs, d_vars, d_equs, lhs)


def generateIndexSeq(seq, origin):
  """
  produces an ordered sequence according to the list origin
  does not check for duplications

  :param seq: unordered
  :param origin: template
  :return: ordered list
  """

  ordered_seq = []
  for o in origin:
    if o in seq:
      ordered_seq.append(o)

  return ordered_seq

# =============================================================================
# error classes
# =============================================================================


class VarError(Exception):
  """
  Exception reporting
  """

  def __init__(self, msg):
    self.msg = msg

  def __str__(self):
    return ">>> %s" % self.msg


class UnitError(VarError):
  """
  variable error with unit exception
  """

  def __init__(self, msg, pre, post):
    self.msg = msg + ' --  pre: %s, post: %s' % (pre, post)


class IndexStructureError(VarError):
  """
  variable error with unit exception
  """

  def __init__(self, msg):
    self.msg = msg


class EquationError(VarError):
  def __init__(self, msg):
    self.msg = msg


class KhatriRaoError(VarError):
  def __init__(self, msg):
    self.msg = msg


class EquationCounter():
  self = 0

  def newID(self):
    self += 1
    return self

  def set(self, ID):
    self = ID


# =============================================================================
# Components of the variable/equation space
# =============================================================================

class Units():
  """
  Defines a container for the SI units
  TODO:could be generated from the ont ology
  """

  def __init__(self, time=0, length=0, amount=0, mass=0,
               temperature=0, current=0, light=0, nil=0, ALL=[]):
    """
    SI - unit container. There are two ways of using it:
      1. define all individual units separately using the keywords
      2. define a vector of all 8 units and pass it through the keyword ALL
    :param time: exponent for time
    :param length: exponent for length
    :param amount: exponent for amount
    :param mass: exponent for mass
    :param temperature: exponent for temperature
    :param current: exponent for current
    :param light: exponent for light
    :param nil:nil         TODO: can be eliminated - probably
    :param ALL: list of the eight exponents
    """
    if ALL == []:
      self.time = time
      self.length = length
      self.amount = amount
      self.mass = mass
      self.temperature = temperature
      self.current = current
      self.light = light
      self.nil = nil
    else:
      self.time = ALL[0]
      self.length = ALL[1]
      self.amount = ALL[2]
      self.mass = ALL[3]
      self.temperature = ALL[4]
      self.current = ALL[5]
      self.light = ALL[6]
      self.nil = ALL[7]

  def isZero(self):
    iszero = True
    d = [self.time, self.length, self.amount, self.mass, self.current,
         self.light]
    for i in d:
      if i != 0:
        iszero = False
    return iszero

  def __add__(self, other):
    """
    Checks if the two unit sets are the same. If not it raises an UnitError
    :param other: the other
    """
    if self.__dict__ == other.__dict__:
      return copy.copy(self)
    else:
      raise UnitError('add - incompatible units', self, other)

  def __mul__(self, other):
    u = [sum(unit) for unit in zip(Units.asList(self), Units.asList(other))]
    return Units(*u)

  def asDictionary(self):
    return self.__dict__

  def prettyPrint(self):
    pri = ''
    if self.mass != 0:
      if self.mass == 1:
        pri += 'kg \,'
      else:
        pri += 'kg^{%s} \,'%self.mass
    if self.length != 0:
      if self.length == 1:
        pri += 'm '
      else:
        pri += 'm^{%s} \,'%self.length
    if self.amount != 0:
      if self.amount == 1:
        pri += 'mol \,'
      else:
        pri += 'mol^{%s} \,'%self.amount
    if self.temperature != 0:
      if self.temperature == 1:
        pri += 'K \,'
      else:
        pri += 'K^{%s} \,'%self.temperature
    if self.current != 0:
      if self.current == 1:
        pri += 'A \,'
      else:
        pri += 'A^{%s} '%self.current
    if self.light != 0:
      if self.light == 1:
        pri += 'cd \,'
      else:
        pri += 'cd^{%s} \,'%self.light
    if self.time != 0:
      if self.time == 1:
        pri += 's \,'
      else:
        pri += 's^{%s} \,'%self.time
    return pri

  def asList(self):
    r = [self.time, self.length, self.amount,
         self.mass, self.temperature, self.current, self.light, self.nil]
    return r

  def __str__(self):
    return str(self.asList())


class Equation():
  def __init__(self, **kwargs):
    self.__dict__ = kwargs


class Equations(OrderedDict):
  """
  Repository for the equation objects.
  Keeps  track of the equation identifiers, which are unique over the life time
  of  the ontology.  The identifier  is the string  version of  an integer.  On
  reading  equations  the counter  value will  be set to  the maximimum  of the
  current value and the value associated with the new equation.
  """
  equation_counter = -1  # counter start
  names = []  # an empty list of names

  def addEquation(self, equation_ID=None, **kwargs):
    """
    input arguments are defined in resources as a dictionary
    @return: equation_ID
    """
    # name = kwargs['name']

    # assert not self.existName(name)
    if not equation_ID:
      self.equation_counter += 1
      equation_ID = str(self.equation_counter)
    elif self.equation_counter < int(equation_ID):  # keep track when reading i
      self.equation_counter = int(equation_ID)

    kwargs["equation_ID"] = equation_ID
    self[equation_ID] = Equation(**kwargs)
    # self.names.append(name)
    return equation_ID

  def removeEquation(self, equation_ID):
    assert equation_ID in self
    r = self.pop(equation_ID)
    return r

  # def existName(self, name):
  #   return name in self.names

  def listIDs(self):
    lst = list(self.keys())
    lst.sort()
    return lst

  def linkVariables(self, variables):
    self.variables = variables

  def inverseIncidenceMatrix(self):
    variable_list = self.variables.getVariableList()
    inverse_incidence_lists = {}
    for v in variable_list:
      inverse_incidence_lists[v] = []
    for e in self:
      for s in self[e].incidence_list:
        inverse_incidence_lists[s].append(e)
    return inverse_incidence_lists

  def equationsWithSymbolV(self, v):
    invIM = self.inverseIncidenceMatrix()
    return invIM[v]


class Indices(OrderedDict):


  def add(self, hashtag, **kwargs):
    """
    used during the build-up of the index containers
    it is adding a new index if it does not exist
    if does exist it checks of it exists for the current network and adds the network if it is a newcommer
    :param hashtag: label for the container
    :param kwargs: data structure of an index
    :return:
    """

    # TODO: the attribute network can be simplified if one uses the ontology_container 's attribute heirs_list
    # print("adding indices", kwargs)
    if hashtag == "species":
      # print(">>> species")
      pass
    if hashtag in self:
      if "network"  in kwargs:
        self[hashtag]["network"].append(kwargs["network"])
    else:
      self[hashtag] = {}
      for i in kwargs:
        self[hashtag][i] = kwargs[i]
      self[hashtag]["network"] = [kwargs["network"]]


  def initialise(self, indices):
    for hashtag in indices:
      self[hashtag] = {}
      for i in indices[hashtag]:
        self[hashtag][i] = copy.copy(indices[hashtag][i])# NOTE: this must copy ! Cannot just be assigned !

  def existIndexStructure(self, symbol):
    return symbol in self

  def getIndexListUnsorted(self):
    lst = list(self.keys())
    return lst

  def getIndexList(self):
    lst = list(self.keys())
    lst.sort()
    return lst

  def getIndexDict(self):
    dict = {}
    for key, item in self.items():
      dict[key] = item
    return dict

  def getIndexListPerNetwork(self, nw):
    lst = []
    for i in self:
      for layer in self[i]["network"]:
        if layer == nw:
         lst.append(i)
    return lst

  def compile(self):
    for i in self:
      self.compileMe(i)

  def compileMe(self, symbol):
    self[symbol]["aliases"] = {}
    # self[symbol]["aliases"] = []
    for language in resources.LANGUAGES['compile']:
      ind = self.compileIndex(symbol, language)
      # self[symbol]["aliases"].append( [language, ind] )
      self[symbol]["aliases"][language] = ind
    self[symbol]["aliases"][LANGUAGES["internal_code"]] = self[symbol]["symbol"]

  def generateIndexSeq(self, seq):
    """
    produces an ordered sequence according to the list origin
    does not check for duplications
    :param seq: unordered
    :param origin: template
    :return: ordered list
    """
    ordered_seq = []
    for o in self.getIndexListUnsorted():
      if o in seq:
        ordered_seq.append(o)
    return ordered_seq

  def compileIndex(self, symbol, language):
    if language in resources.LANGUAGES['internals']:
      return symbol

    i = self[symbol]
    i_type = i["type"]
    if i_type == "block_index":
      outer = self.compileIndex(i["outer"], language)
      inner = self.compileIndex(i["inner"], language)
      ind = resources.CODE[language][i_type] % (outer, inner)
    elif i_type == "index":
      ind = resources.CODE[language][i_type] % i["symbol"] #(i[internal])
    return ind

  def compileIndices(self, ind_list, language):  #TODO can be made obsolete ?
    ind_compiled = []
    for i in ind_list:
      if language in resources.LANGUAGES["compile"]:
        # alias_i_dict = dict(self[i]["aliases"])
        ind = self[i]["aliases"][language]   # alias_i_dict[language]
      else:
        ind = self[i]["symbol"]
      ind_compiled.append(ind)
    return ind_compiled

  # def printLanguage(self, symbol, language):
  #   if language == internal:
  #     return symbol
  #   else:
  #     ind = self[symbol]
  #     indalias = [item for item in ind["aliases"] if item[0] == language][0]
  #     return(indalias[1])


class Variables(OrderedDict):
  types = OrderedDict()
  indexedvariables_inherited = OrderedDict()         # indexing is "cumulative"
  indexedvariables = OrderedDict()                             # not cumulative
  those_who_inherit = OrderedDict()

  def addVariable(self, **kwargs):

    symbol = kwargs["symbol"]
    v_t = kwargs["type"]
    nw = kwargs["network"]
    if not self.existSymbol(symbol):
      self[symbol] = PhysicalVariable(**kwargs)
      if CONNECTION_NETWORK_SEPARATOR in nw:
        if nw not in self.those_who_inherit.keys():
          self.those_who_inherit[nw] = [nw]
      for nw_i in self.those_who_inherit[nw]:   # inherit to the lower networks
        if CONNECTION_NETWORK_SEPARATOR in nw_i:
          if v_t in ["conversion", "network"]:
            self.indexedvariables_inherited[nw_i][v_t].add(symbol)
        else:
          self.indexedvariables_inherited[nw_i][v_t].add(symbol)
    self.reindex()
    return

  def __addSymbolToIndex(self, lst, symbol, v_t):
    for n in lst:
      # if n not in self.indexedvariables:
      #   self.indexedvariables[n] = {}
      if v_t not in list(self.indexedvariables_inherited[n].keys()):
        self.indexedvariables_inherited[n][v_t] = set()
      self.indexedvariables_inherited[n][v_t].add(symbol)

  def reindex(self):   # TODO:check if connection networks are properly updated
    self.indexedvariables_inherited = OrderedDict()
    self.indexedvariables = OrderedDict()
    for nw in self.types:
      self.setTypes(self.types[nw], nw)
    for symbol in self:
      v_t = self[symbol].type
      nw = self[symbol].network
      for nw_i in self.those_who_inherit[nw]:   # inherit to the lower networks
        if CONNECTION_NETWORK_SEPARATOR in nw_i:
          if v_t in ["conversion", "network"]:
            self.indexedvariables_inherited[nw_i][v_t].add(symbol)
        else:
          self.indexedvariables_inherited[nw_i][v_t].add(symbol)

      self.indexedvariables[nw][v_t].add(symbol)

  def setTypes(self, types, nw):
    self.types[nw] = types
    self.indexedvariables_inherited[nw] = OrderedDict()
    self.indexedvariables[nw] = OrderedDict()
    for v_t in types:
      self.indexedvariables_inherited[nw][v_t] = set()
      self.indexedvariables[nw][v_t] = set()

  def setThoseWhoInherit(self, those_who_inherit, nw):
    self.those_who_inherit[nw] = those_who_inherit

  def getThoseWhoInherit(self, nw):
    return self.those_who_inherit[nw]

  def getVariablesIndexedType(self, vartype, nw):
    if vartype in self.indexedvariables_inherited[nw]:
      return self.indexedvariables_inherited[nw][vartype]
    else:
      return set()

  def linkEquations(self, equations):
    self.equations = equations

  def linkIndices(self, indices):
    self.indices = indices

  def checkVariableCompiles(self, symbol):

    expression = Expression(self,
                            self.indices,
                            language=internal)
    try:
      expression(symbol)
    except (SemanticError,
            SyntacticError,
            LexicalError,
            WrongToken,
            UnitError,
            IndexStructureError
            ) as _m:
      print('checked expression failed %s -- %s' % (symbol, _m))
      return False
    except (VarError):  # that is a new variable
      pass
    return True

  def renameVariable(self, old_symbol, new_symbol):
    """
    strategy:
    1. the symbols in the equations must be changed
       use the compiler for the renaming either
       - add a rename to the alias list --> not nice for storage
       - add but then remove later --> distributed code
       - add to all variables the "new" names implying all the old ones
           except the one being changed, thus a similar mechanism as using
           the aliasing, but in a separate attribute called rename and a
           corresponding switch in the str method of the variable
           triggered by the language
    2. go through all the layers to change the symbol
    """
    for v in self:                         # generate the new symbols attribute
      self[v].new_symbol = copy.copy(self[v].symbol)
    self[old_symbol].new_symbol = new_symbol

    expression = Expression(self,
                            self.indices,
                            language=resources.LANGUAGES['rename'])
    eqs = self.equations.equationsWithSymbolV(old_symbol)
    for e in eqs:
      s = expression(self.equations[e].rhs)
      self.equations[e].rhs = str(s)
      ls = self.equations[e].incidence_list
      c = ls.count(old_symbol)
      for i in range(c):
        ls[ls.index(old_symbol)] = new_symbol

    eqs = self[old_symbol].equation_list
    for e in eqs:
      self.equations[e].lhs = new_symbol

    layer_list = list(self.indexedvariables_inherited.keys())
    for nw in layer_list:
      variable_type_list = list(self.indexedvariables_inherited[nw].keys())
      for v_t in variable_type_list:
        if old_symbol in self.indexedvariables_inherited[nw][v_t]:
          self.indexedvariables_inherited[nw][v_t].remove(old_symbol)
          self.indexedvariables_inherited[nw][v_t].add(new_symbol)
    nw = self[old_symbol].network
    v_t = self[old_symbol].type
    self.indexedvariables[nw][v_t].remove(old_symbol)
    self.indexedvariables[nw][v_t].add(new_symbol)
    self.change_key(old_symbol, new_symbol)
    self[new_symbol].symbol = new_symbol

    # fix aliases
    _d = dict(self[new_symbol].aliases)
    for i in _d:
      if _d[i] == resources.NEW_VAR:
        _d[i] = new_symbol
    self[new_symbol].aliases = list( _d.items() )
    return True

  def change_key(self, old, new):
    for i in range(len(self)):
      k, v = self.popitem(False)
      if old == k:                           # self[new if old == k else k] = v
        self[new] = v
        self[new].symbol = v
      else:
        self[k] = v

  def removeVariable(self, symbol):
    self.pop(symbol)
    self.reindex()

  def removeEquationFromVariable(self, symbol, eq_id):
    print(self[symbol])

  def existSymbol(self, symbol):
    return symbol in list(self.keys())

  def getVariableList(self):
    lst = list(self.keys())
    lst.sort()
    return lst

  def getVariableTypes(self, nw):
    return self.types[nw]

  def getVariablesForTypeAndNetwork(self, vartype, nw):
    return self.indexedvariables[nw][vartype]


class CompileSpace:
  """
  Used for compilation
  - Transfers language across to the variables and access to the variables
  - Constructs an incidence list for the compiled expression
  - Constructs names for the temporary variables
  """
  counter = 0

  def __init__(self, variables, indices, language=internal):
    '''
    Access to variables and language definition
    @param variables: variable ordered dictionary (access by symbol)
    @param language: target language string
    '''
    self.language = language                         # sets the target language
    self.variables = variables
    self.indices = indices
    self.eq_variable_incidence_list = []

  def getVariable(self, symbol):
    '''
    gets the variable "symbol" from the variable oredered dictionary and
    sets the appropriate language
    @param symbol: variable's symbol
    @return: v : the variable object
    '''
    # print("get variable", symbol)
    if symbol in self.variables:
      v = self.variables[symbol]
      v.language = self.language
      v.indices = self.indices
      self.eq_variable_incidence_list.append(symbol)
    else:
      raise VarError('no such variable %s' % symbol)
    return v

  def newTemp(self):
    '''
    defines the symbol for a new temporary variable
    @return: symbol for the temporary variable
    '''
    symbol = resources.TEMPLATES['temp_variable'] % self.counter
    self.counter += 1
    return symbol

  def getIncidenceList(self):
    '''
    provides the incidence list collected during the compilation
    @return:
    '''
    incidence_set = set(self.eq_variable_incidence_list)
    incidence_list = list(incidence_set)
    incidence_list.sort()
    return incidence_list


class PhysicalVariable():
  """
  Variables are  the base object in  the physical variable construct they have:
    - a symbol, an ID, which is unique within the global set of variables
    - a doc (string)
    - a list of uniquely named index structures
  """

  def __init__(self, **kwargs):
    # symbol= '', variable_type='',
    #            layer=None, doc='', index_structures=[], units=Units()):
    """

    @param symbol: an identifier for symbolic representation also serves as key
                   for  the variable dictionary thus this must be a unique name
                   in the set of variables.
    @param variable_type: variable type
    @param layer: ontology layer
    @param doc: a document string
    @param index_structures: list of index structures
    @param units: the units object
    @return:
    """
    # print(kwargs)
    self.__dict__ = kwargs

  def addEquation(self, equation_ID):
    self.equation_list.append(str(equation_ID))

  def removeEquation(self, equation_ID):
    self.equation_list.remove(equation_ID)

  def compatible(self, other):
    # print('compatible test:')
    for item in STRUCTURES_Vars_Equs['variable_compatible']:
      s = str(self.__dict__[item])
      o = str(other.__dict__[item])
      if s != o:
        print( "compatible problem item %s : %s != %s" % (item, s, o) )
        return False
    return True

  def __str__(self):

    if "language" not in self.__dir__():                    # default is string
      self.language = internal

    if self.language not in resources.LANGUAGES['compile']:  # use language temp
      return self.symbol
    else:

      if self.language == resources.LANGUAGES["rename"]:        # kept internally
        s = self.new_symbol
      elif self.language == internal:                               # no translation  #TODO could just translate
        s = str(self.symbol)
      else:
        alias_dict = dict(self.aliases)        # translation into target language
        var = alias_dict[self.language]

        ind = []
        for i in self.index_structures:
          if i in self.indices:
            ind.append(self.indices[i]["aliases"][self.language])


        temp = "template_variable.%s" % self.language
        s = j2_env.get_template(temp).render(var=var, ind=ind)

      return s



###############################################################################
#                                  OPERATORS                                  #
###############################################################################

class Operator(PhysicalVariable):
  def __init__(self, space, equation_type="generic"):
    PhysicalVariable.__init__(self)
    self.symbol = space.newTemp
    self.space = space
    self.type = resources.TEMP_VARIABLE
    self.equation_type = equation_type


class UnitOperator(Operator):
  def __init__(self, op, space):
    Operator.__init__(self, space)
    self.op = op

  # def expressionAsString(self):
  #   language = self.space.language
  #   return 'IDIOT'

  def __str__(self):
    return self.asString()


class BinaryOperator(Operator):
  """
  Binary operator
  operator:
  + | - :: units must fit, index structures must fit

  @param op: string:: the operator
  @param a: variable:: left one
  @param b: variable:: right one
  """

  def __init__(self, op, a, b, space):
    Operator.__init__(self, space)
    self.op = op
    self.a = a
    self.b = b

  def __str__(self):
    s = stringBinaryOperation(self.space.language, self.op, self.a, self.b)
    return s


class Add(BinaryOperator):
  def __init__(self, op, a, b, space):
    """
    Binary operator
    operator:
    + | - :: units must fit, index structures must fit

    @param op: string:: the operator
    @param a: variable:: left one
    @param b: variable:: right one
    """

    BinaryOperator.__init__(self, op, a, b, space)

    self.units = a.units + b.units            # consistence check done in class

    if a.index_structures == b.index_structures:            # strictly the same
      self.index_structures = a.index_structures

    else:
      print(' issue')
      print(self.space.indices.keys())
      raise IndexStructureError('add incompatible index structures %s'
                                % resources.CODE[self.space.language][op] % (
                                  a.index_structures, b.index_structures))


class KhatriRao(BinaryOperator):
  def __init__(self, op, a, b, space):
    """
    Binary operator
    operator:
    + | - :: units must fit, index structures must fit
    *     :: Khatri-Rao product
    # .index. :: matrix product reducing over the index

    @param op: string:: the operator
    @param a: variable:: left one
    @param b: variable:: right one

    This is not an universal Khatri-Rao product.  This version is limited to be
    on practical form and to be useable in current indices

    The cases are
     1: N,A : NS,AS  --> NS,AS
     2: N,A : AS,NS  --> AS,NS
     3: N   : NS     --> NS
     4: N   : NS,AS  --> NS,AS
     5: A   : NS,AS  --> NS,AS

    pattern
     6: S   : NS  --> NS  does not make sense not block operation

    """

    BinaryOperator.__init__(self, op, a, b, space)

    self.units = a.units * b.units

    # pattern recognition
    a_len = len(a.index_structures)
    b_len = len(b.index_structures)

    error = True

    if (a_len == 2) and (b_len == 2):                           # pattern 1 & 2
      b_outer = [0, 1]
      for j in [0, 1]:
        if '&' not in b.index_structures[j]:
          error = True
        else:
          b_outer[j], dummy = b.index_structures[j].split('&')
          b_outer[j] = b_outer[j].strip()
          if (a.index_structures[0] == b_outer[0]) and (
                    a.index_structures[1] == b_outer[1]) \
                  or (a.index_structures[0] == b_outer[1]) and (
                            a.index_structures[1] == b_outer[0]):
            error = False
    #
    elif (a_len == 1) and (b_len == 1):                             # pattern 3
      # order of the two operands must be observed
      try:
        b_outer, dummy = b.index_structures[0].split('&')
      except:
        raise KhatriRaoError('not an allowed sequence - product set must be'
                             'in the second operand')
      b_outer = b_outer.strip()
      if b_outer == a.index_structures[0]:
        error = False

    elif (a_len == 1) and (b_len == 2):                        # pattern 3 or 4
      b_outer = [0, 1]
      for j in [0, 1]:
        if '&' not in b.index_structures[j]:
          error = True
        else:
          b_outer[j], dummy = b.index_structures[j].split('&')
          b_outer[j] = b_outer[j].strip()
          if (a.index_structures[0] == b_outer[0]) \
                  or (a.index_structures[0] == b_outer[1]):
            error = False

    if error:
      raise IndexStructureError(
        "Khatri Rao Index error %s.index: %s, %s.index: %s"
        % (a.symbol, a.index_structures, b.symbol, b.index_structures))
    else:
      self.index_structures = b.index_structures
      self.index = a.index_structures

  def __str__(self):                                # Str version of the object
    language = self.space.language
    if (language not in resources.LANGUAGES['matrix_form']):
      s = resources.CODE[language][':'] % (self.a, self.b)
    else:                                                   # If in matrix form
      indaa = []
      for index in self.a.index_structures:
        indaa.append(self.space.indices[index]["aliases"][language])

      indba = []
      for index in self.b.index_structures:
        indba.append(self.space.indices[index]["aliases"][language])
      # index = self.space.indices.getIndexDict()            #TODO : fix index handling --> alias_dict
      # inda = [index[ind]["aliases"] for ind in self.index]
      # indb = [index[ind]["aliases"] for ind in self.index_structures]
      #
      # # Bad system. This line get the indx sets written out in language to list
      # indaa = [resources.CODE[language]["index"] % (al[1])
      #          for als in inda for al in als if al[0] == language]
      # indba = [resources.CODE[language]["index"] % (al[1])
      #          for als in indb for al in als if al[0] == language]
      indaaa = "[" + ", ".join(indaa) + "]"  # Writing index to a single string
      indbaa = "[" + ", ".join(indba) + "]"  # Writing index to a single string

      try:
        s = resources.CODE[language]['khatri_rao_matrix'] % (self.a, indaaa,
                                                             self.b, indbaa)
      except:
        print(">>>>failed")
    return s


class ReduceProduct(BinaryOperator):
  def __init__(self, op, a, b, index, space):
    """
    Binary operator
    operator:
    .index. :: matrix product reducing over the index

    @param op: string:: the operator
    @param a: variable:: left one
    @param b: variable:: right one
    @param prec: precedence
    """

    BinaryOperator.__init__(self, op, a, b, space)
    self.index = index
    self.units = a.units * b.units
    index = index.strip(' ')
    s_index_a = set(a.index_structures)
    s_index_b = set(b.index_structures)
    s_index = set([index])            # Conversion to set from a list of stings
    s_index_reduce = s_index_a.intersection(s_index_b)
    s_index_remain = s_index_a.symmetric_difference(s_index_b)

    # RULE: Not allowed to have same index sets
    if not s_index_remain and len(s_index_a) > 1:
      error_message = "Index error: a.index: {}, b.index: {} are equal"
      raise IndexStructureError(error_message.format(a.index_structures,
                                                     b.index_structures))
    # first case is a standard reduction
    # a(N) *N* b(N,A) --> c(A)            >>> case 1
    # a(A) *A* b(N,A) --> c(N)            >>> case 1
    indices = self.space.indices
    if s_index.intersection(s_index_reduce):
      keptIndexes = s_index.symmetric_difference(s_index_reduce)
      self.index_structures = indices.generateIndexSeq(list(s_index_remain
                                                            | keptIndexes))
    else:                                                                  # Sp
      raise IndexStructureError("Index error a.index: %s, b.index: %s"
                                % (a.index_structures, b.index_structures))

  def __str__(self):
    s = stringBinaryOperation(self.space.language, self.op,
                              self.a, self.b,
                              index = self.index,
                              indices = self.space.indices
                              )
    return s


class ReduceBlockProduct(BinaryOperator):
  def __init__(self, op, a, b, index, productindex, space):
    """
    Binary operator
    operator:
    .index. :: matrix product reducing over the index

    @param op: string:: the operator
    @param a: variable:: left one
    @param b: variable:: right one
    @param prec: precedence
    """

    BinaryOperator.__init__(self, op, a, b, space)
    self.units = a.units * b.units

    self.index = index.strip(' ')
    self.org_indx = productindex.strip(' ')

    s_index_a = set(a.index_structures)
    s_index_b = set(b.index_structures)
    s_index_big = set([self.org_indx])  # Conversion to set from list of stings
    s_index = set([self.index])

    s_index_reduce = s_index_a.intersection(s_index_b)   # Reduction dimensions
    s_index_remain = s_index_a.symmetric_difference(s_index_b)
    if s_index_big.intersection(s_index_reduce):    # Need identical index sets
      red = set(self.org_indx.split(resources.BLOCK_INDEX_SEPARATOR)) ^ s_index
      s_indices = s_index_remain | s_index_big ^ s_index_reduce | red  # ^ symd
      self.index_structures = generateIndexSeq( list(s_indices),
                                                self.space.indices )
    else:
      raise IndexStructureError("Index error a.index: %s, b.index: %s"
                                % (a.index_structures, b.index_structures))

  def __str__(self):
    language = self.space.language
    ind_all = self.space.indices
    # ind = [el[0] for el in ind_all[self.index]["aliases"]].index(language)
    red_index = ind_all[self.index]["aliases"][language] # ind_all[self.index]["aliases"][ind][1]
    org_index = ind_all[self.org_indx]["aliases"][language] # ind_all[self.org_indx]["aliases"][ind][1]
    # red_index = self.space.indices.compileIndex(self.index, language)
    # org_index = self.space.indices.compileIndex(self.org_indx, language)
    # print('HELLO: ', ind_all[self.index]["aliases"])
    s = resources.CODE[language]['block_reduce'] \
        % (self.a, red_index, org_index, self.b)
    return s


class ExpandProduct(BinaryOperator):
  def __init__(self, op, a, b, space):
    """
    Binary operator
    operator:
    .index. :: matrix product expanding over the index

    @param op: string:: the operator
    @param a: variable:: left one
    @param b: variable:: right one
    @param space: the storage space for variable and equations

    for  matrix  output  this maps into a  .*  product.  Only issue is to align
    dimensions
    a(A) . b(A,B) --> c(A,B)   a .* b
    a(B) . b(A,B) --> c(A,B)   (a .* b)'
    """
    BinaryOperator.__init__(self, op, a, b, space)

    self.aind = copy.copy(a.index_structures)
    self.bind = copy.copy(b.index_structures)
    self.doc = 'EXPAND '          # EXPAND TEMPLATES[op] % (a.symbol, b.symbol)
    self.units = a.units * b.units

    _s = copy.copy(
      a.index_structures)       # that was a tricky one indeed -- needs copying
    _s.extend(b.index_structures)
    __s = set(_s) - {'nil'}

    self.index_structures = generateIndexSeq(list(__s), self.space.indices)

  def __str__(self):
    language = self.space.language
    if (language not in resources.LANGUAGES['matrix_form']):
      s = resources.CODE[language]['.'] % (self.a, self.b)
    else:
      s = self.expandMatrix(language)                   # Calculating the stuff
    return s

  def expandMatrix(self, language):
    """
    :param language: current output language
    :return: code string

    Operation: fills in the templates stored in resources.  Special case is the
    expansion product.  If the output is  a matrix-oriented language,  then one
    needs to implement the implicit rules of matrix multiplication. Let A and B
    be two two-dimensional objects with the index sets a,b and c. Thus we write
    Aab . Bac, thus reduce the two objects over a then the result is Cbc.  Thus
    in matrix notation  using the prime for transposition:

    Aa  . Ba  := Ca
    A   . Ba  := Ca
    Aa  . B   := Ca
    Aa  . Bab := Cab
    Ab  . Bab := Cab
    Aab . Ba  := Cab
    Aab . Bb  := Cab --> Transpose B
    Aab . Bab := Cab

    Rules
    if left  index in position 1  --> transpose left
    if right index in position 2  --> transpose right
    if left only one index transpose left and result


    Note:
    - The  index   results   must  always  be  in  the  original  order,   here
      alphabetically.
    - The product   Aab |b| Bab -->  is forbidden as it results in a Caa, which
      is not permitted.
    - Objects with one dimension only are interpreted as column vectors


    """
    if self.a.type == resources.TEMP_VARIABLE:
      aa = resources.CODE[language]['()'] % self.a.__str__()
    else:
      aa = "%s" % self.a.__str__()
    if self.b.type == resources.TEMP_VARIABLE:
      bb = resources.CODE[language]['()'] % self.b.__str__()
    else:
      bb = "%s" % self.b.__str__()

    if self.aind == self.bind or self.aind == [] or self.bind == []:
      pass           # Nothing really needs to happen, this is the default case
    elif self.aind[0] != self.bind[0]:
      # SOMETHING ELSE NEEDS TO HAPPEN
      if len(self.aind) > len(self.bind):
        bb = resources.CODE[language]['transpose'] % bb
      elif len(self.aind) < len(self.bind):
        aa = resources.CODE[language]['transpose'] % aa
    return resources.CODE[language]['.'] % (aa, bb)


class Power(BinaryOperator):
  def __init__(self, op, a, b, space):
    """
    Binary operator
    operator:
    ^  :: the exponent,b

    Index structure of a propagates but not of b

    @param op: string:: the operator
    @param a: variable:: left one
    @param b: variable:: right one
    @param prec: precedence
    """
    # TODO: what happens with the index sets -- currently the ones of a
    BinaryOperator.__init__(self, op, a, b, space)

    # self.doc = resources.TEMPLATES[op] % (a, b)

    # units of both basis and  exponent must be zero
    if (not a.units.isZero()) or (not b.units.isZero()):
      raise UnitError('units of basis and exponent must be zero',
                      a.units, b.units)
    else:
      self.units = a.units

    # rule for index structures
    self.index_structures = a.index_structures

  def __str__(self):
    language = self.space.language
    if isinstance(self.b, PhysicalVariable):
      return stringBinaryOperation(language, '^', self.a, self.b)
    else:
      k = self.a.__str__()
      s = resources.CODE[language]['^'] % (k, self.b)
      return s


class BlockProduct(Operator):
  def __init__(self, op, a, index, productindex, space):
    """
    Unitary operator
    operator:
    prod :: no units

    """

    Operator.__init__(self, space)

    self.op = op
    self.a = copy.copy(a)
    self.units = a.units                      # consistence check done in class
    for unit in self.units.asList():
      if unit != 0:
        raise UnitError('Units of {} are not zero!'.format(self.a), self.units,
                        self.units)
    #
    # rule for index structures

    self.index = index.strip(' ')
    self.org_indx = productindex.strip(' ')

    if self.index not in self.space.indices.keys():
      raise IndexStructureError(" {} not recognized ".format(index))
    elif self.org_indx not in self.space.indices.keys():
      raise IndexStructureError(" {} not recognized ".format(productindex))

    # s_index_a = set(a.index_structures)
    s_index_big = set([self.org_indx])  # Conversion to set from list of stings
    s_index = set([self.index])

    # if s_index_big.intersection(s_index_big):       # Need identical index sets
    red = set(self.org_indx.split(resources.BLOCK_INDEX_SEPARATOR)) ^ s_index
    s_ind = set(self.a.index_structures) - s_index_big
    s_indices = s_ind | red  # ^ symd
    self.index_structures = generateIndexSeq( list(s_indices),
                                              self.space.indices )

  def __str__(self):
    language = self.space.language
    str_ind = self.space.indices[self.index]["aliases"][language] #.printLanguage(self.index, language)
    str_out = self.space.indices[self.index]["aliases"][language] #.printLanguage(self.org_indx, language)
    var_ind = self.a.index_structures
    ind = [self.space.indices[ind]["aliases"] for ind in var_ind]
    # Bad system. This line get the indx sets written out in language to list
    inda = [resources.CODE[language]["index"] % (al[1])
            for als in ind for al in als if al[0] == language]
    indaa = "[" + ", ".join(inda) + "]"  # Writing index to a single string
    s = resources.CODE[language]['prod'].format(self.a, indaa, str_ind, str_out)
    return s


class MaxMin(BinaryOperator):
  def __init__(self, op, a, b, space):
    """
    Binary operator
    operator:
    max | min :: units must fit, index structures must fit

    @param op: string:: the operator
    @param a: variable:: left one
    @param b: variable:: right one
    """

    BinaryOperator.__init__(self, op, a, b, space)
    self.op = op
    self.a = copy.copy(a)
    self.b = copy.copy(b)
    self.units = a.units + b.units            # consistence check done in class

    # rule for index structures
    if a.index_structures == b.index_structures:            # strictly the same
      self.index_structures = a.index_structures

    else:
      print(' issue')
      print(self.space.indices.keys())
      raise IndexStructureError('comparing incompatible index structures %s'
                                % resources.CODE[self.space.language][op] % (
                                  a.index_structures, b.index_structures))

  def __str__(self):
    language = self.space.language
    s = resources.CODE[language][self.op] % (self.a, self.b)
    return s


class Implicit(Operator):
  def __init__(self, fct, arg, var_to_solve, space):
    """
    implicite equations with the syntax:   root( <expr> , <variable_solve_for>)
    <variable_solve_for> must correspond to lhs of the equation
    :param fct: 'root'
    :param arg: expression
    :param var_to_solve: must correspond to lhs of the equation
    :param space: variable space
    """

    Operator.__init__(self, space)

    self.args = arg
    self.fct = fct
    self.var_to_solve = var_to_solve

    self.doc = fct

    # get variable defined as lhs - must appear on the rhs
    # if variable exists -- no worries
    # if not then things are difficult  x = ax for example:
    # what should be the units ? no hands on them neither the indexing.
    # one could have a look at  :  space.eq_variable_incidence_list   and check
    # if the var_to_solve   is in there

    if var_to_solve.symbol not in space.eq_variable_incidence_list:
      # TODO: this searches only one level down...
      self.msg = 'warning >>> variable %s not in incidence list' % var_to_solve

    self.units = var_to_solve.units
    self.index_structures = arg.index_structures

  def __str__(self):
    language = self.space.language
    return resources.CODE[language]['root'] % (self.args, self.var_to_solve)


class UFunc(Operator):
  def __init__(self, fct, arg, space):
    """
    Unitary functions such as sin cos etc.
    arguments may be an expression, but must have no units
    @param symbol: symbol representing
    @param fct: function name
    TODO: needs some work here such as variable name generated etc
    """
    Operator.__init__(self, space)

    self.args = arg
    self.fct = fct
    # print(">>>> got Ufunc")
    if fct in resources.UNITARY_RETAIN_UNITS:
      self.units = copy.deepcopy(arg.units)
    elif fct in resources.UNITARY_INVERSE_UNITS:
      _units = Units.asList(arg.units)
      _u = [-1 * _units[i] for i in range(len(_units))]
      self.units = Units(ALL=_u)
    elif fct in resources.UNITARY_NO_UNITS:
      for i in arg.units.asList():               # TODO: check if this is right
        if i != 0:
          raise UnitError('%s expression must have no units'
                          % fct, arg, '-')
      self.units = arg.units
    elif fct in resources.UNITARY_LOOSE_UNITS:
      self.units = Units()
    else:
      raise VarError('there is no unitary function : %s' % fct)

    self.index_structures = arg.index_structures

  def __str__(self):
    language = self.space.language
    try:                   # HACK: Check if unitary function exists in language
      s = resources.CODE[language][self.fct] % (self.args)
    except:
      s = resources.CODE[language]['UFunc'] % (self.fct, self.args)
    return s


class Selection(Operator):                                      # TODO: Unused?
  def __init__(self, arg, org_ind, sel_index, space ):
    """
    org_ind must be  of type index  and  must correspond with  the super set in
    sel_index
    """
    if "super" not in space.indices[sel_index]:
      raise IndexStructureError("forbidden substitution")
      return
    if org_ind != space.indices[sel_index]["super"]:
      raise IndexStructureError(" selection %s is not a subset of %s "
                                % (space.indices[sel_index]["super"], org_ind))
      return
    Operator.__init__(self, space, equation_type="select")
    self.arg = arg
    self.units = arg.units
    self.orig_index = org_ind
    self.sel_index = sel_index
    index_structures = copy.deepcopy(arg.index_structures)

    changed = False
    for i in range(len(index_structures)):
      ind = index_structures[i].replace(" ", "")
      if "&" in ind:
        c = ind.split("&")
        for j in range(len(c)):
          if c[j] == org_ind:
            c[j] = sel_index
            changed = True
        if changed:
          index_structures[i] = resources.TEMPLATES['block_index']\
                                     % (c[0], c[1])
      else:
        if ind == org_ind:
          index_structures[i] = sel_index
          changed = True
    if not changed:
      raise IndexStructureError("no such index %s in structures %s"
                                % (org_ind, arg.index_structures))
    else:         # added because of a suspicious error -- may not be necessary
      self.index_structures = generateIndexSeq(index_structures,
                                               self.space.indices)

  def __str__(self):

    language = self.space.language
    # s = resources.CODE[language]['UFunc'] % (self.fct, self.args)
    # indices = self.space.indices


    ind = self.space.indices.compileIndices([self.orig_index, self.sel_index],
                                            language)

    s = resources.CODE[language]['select'] % (self.arg, ind[0], ind[1])
    return s


class Instantiate(Operator):

  def __init__(self, var,  space):
    """
    Symbolically instantiate a variable
    @param var: variable
    @param space: compile space
    """
    Operator.__init__(self, space, equation_type="instantiate")
    self.arg = var
    self.index_structures = var.index_structures
    self.index_structures = generateIndexSeq(var.index_structures,
                                             self.space.indices)
    self.units = var.units

  def __str__(self):
    self.language = self.space.language
    s = resources.CODE[self.language]['set'] % (self.arg)
    return s


class Interval(Operator):

  def __init__(self, x, xl, xu, space):
    Operator.__init__(self, space)
    self.x = x
    self.xl = xl
    self.xu = xu

    self.units = xl.units + xu.units          # consistence check done in class

    # TODO: use the internal class for this. Rule for index sets.
    xxl = x.index_structures == xl.index_structures
    xxu = x.index_structures == xu.index_structures
    if xxl and xxu:                                         # Strictly the same
      self.index_structures = x.index_structures
    else:
      print(' issue')
      print(self.space.indices.keys())
      raise IndexStructureError(
        'interval -- incompatible index structures %s != %s != %s'
        % (x.index_structures, xl.index_structures, xu.index_structures)
        )

  def __str__(self):
    language = self.space.language
    s = resources.CODE[language]['interval'] % (self.x, self.xl, self.xu)
    return s


class Integral(Operator):
  def __init__(self, y, x, xl, xu, space):
    """
    implements an integral definition
    @param y: derivative
    @param x: integration variable
    @param xl: lower limit of integration variable
    @param xu: upper limit of integration variable
    """
    Operator.__init__(self, space)
    self.y = y
    self.x = x
    self.xl = xl
    self.xu = xu

    units = y.units * x.units               # consistence check done in class
    # rule for index structures
    # TODO: use the internal class for this. Rule for index sets.

    # Not correct

    xxl = x.index_structures == xl.index_structures
    xxu = x.index_structures == xu.index_structures
    if x.index_structures == []:
      self.index_structures = y.index_structures
    elif xxl and xxu:                                       # Strictly the same
      self.index_structures = x.index_structures
    else:

      raise IndexStructureError(
            'interval -- incompatible index structures %s != %s != %s' %
             (x.index_structures, xl.index_structures, xu.index_structures))

    xunits = Units.asList(x.units)
    yunits = Units.asList(y.units)
    units = [xunits[i] + yunits[i] for i in range(len(yunits))]

    self.units = Units(ALL=units)

  def __str__(self):
    language = self.space.language
    # s = resources.CODE[language]['integral']%(self.y, self.x)
    s = resources.CODE[language]['integral'].format(integrand=self.y,
                                                    differential=self.x,
                                                    lower=self.xl,
                                                    upper=self.xu)
    return s


class TotDifferential(Operator):
  def __init__(self, x, y, space):
    """
    implements partial differential definition
    @param x: dx
    @param y: dy
    """

    Operator.__init__(self, space)
    self.x = x
    self.y = y

    xunits = Units.asList(x.units)
    yunits = Units.asList(y.units)
    units = [xu - yu for xu, yu in zip(xunits, yunits)]
    self.units = Units(ALL=units)

    indexSet = (set(x.index_structures) | set(y.index_structures)) - {'nil'}
    for structure in filter(lambda sett: '&' in sett, indexSet):
      structures = structure.split(' & ')
      for struc in structures:
        if struc in indexSet:
          indexSet = indexSet - {struc}

    self.index_structures = list(indexSet)

  def __str__(self):
    return resources.CODE[self.space.language]['Diff'] % (self.x, self.y)


class ParDifferential(Operator):
  def __init__(self, x, y, space):
    """
    implements partial differential definition
    @param x: dx
    @param y: dy
    """
    Operator.__init__(self, space)
    self.x = x
    self.y = y

    xunits = Units.asList(x.units)
    yunits = Units.asList(y.units)
    units = [xu - yu for xu, yu in zip(xunits, yunits)]
    self.units = Units(ALL=units)

    indexSet = (set(x.index_structures) | set(y.index_structures)) - {'nil'}
    for structure in filter(lambda sett: '&' in sett, indexSet):
      structures = structure.split(' & ')
      for struc in structures:
        if struc in indexSet:
          indexSet = indexSet - {struc}

    self.index_structures = list(indexSet)

  def __str__(self):
    return resources.CODE[self.space.language]['diff'] % (self.x, self.y)


class Expression(VerboseParser):
  r"""
  token UFunc       : '\b(inv|sqrt|exp|log|ln|sin|cos|tan|asin|acos|atan|sign|neg|abs)\b';
  token Root        : '\b(root)\b';
  token MaxMin      : '\b(max|min)\b';
  token Left        : '\<';
  token Right       : '\>';
  token IN          : '\b(in)\b';
  token Integral    : '\b(integral)\b';
  token Instantiate : '\b(set)\b';
  token Prod        : '\b(prod)\b';
  token Interval    : '\b(interval)\b';
  separator spaces  : '\s+' ;
  token VarID       : '[a-zA-Z_]\w*';
  token fixID       : '[a-zA-Z_]\w*';
  token sum         : '[+-]'; # plus minus
  token power       : '\^';   # power
  token dot         : '\.';   # expand product
  token DL          : '\|';   # reduce product
  token KR          : ':';    # Khatri Rao product
  token real        :'(\d+\.\d*|\d*\.\d+)([eE][-+]?\d+)?|\d+[eE][-+]?\d+'$float
  token integer     :'\d+';

  START/e -> EXPR/e
      |Instantiate/f
       '\(' ATOM/dx  '\)'                        $e=Instantiate(dx, self.space)
  ;
  EXPR/e -> TERM/e( sum/op TERM/t                     $e=Add(op,e,t,self.space)
      )*
  ;
  TERM/t -> FACT/t (
       dot/op FACT/f                        $t=ExpandProduct(op,t,f,self.space)
      |KR/op FACT/f                             $t=KhatriRao(op,t,f,self.space)
      |DL/op INDID/i IN INDID/j DL FACT/f
                                  $t=ReduceBlockProduct(op,t,f,i,j, self.space)
      |DL/op INDID/i DL FACT/f            $t=ReduceProduct(op,t,f,i,self.space)
      )*
  ;
  FACT/f -> SATOM/f
      ( power/op '{' (SINTEGER/e|SATOM/e) '}'      $f=Power('^',f,e,self.space)
      )?
  ;
  SATOM/ss -> sum/zz     ATOM/a                    $ss = UFunc(zz,a,self.space)
      | ATOM/a                                                          $ss = a
  ;
  SINTEGER/ss -> sum/zz     integer/a                                $ss = zz+a
      | integer/a                                                       $ss = a
  ;
  INDID/i -> (VarID/j '&' VarID/k)                           $i = j + ' & ' + k
      |  VarID/l DL (VarID/j '&' VarID/k)               $i = l + DL + ' & ' + k
      |  VarID/l                                                         $i = l
  ;
  ATOM/a ->
       Func/fu                                                          $a = fu
      | '\(' EXPR/a '\)'
      | VARID/a
  ;
  VARID/a -> VarID/s                               $a=self.space.getVariable(s)
  ;
  Func/fu -> UFunc/s '\(' EXPR/a '\)'               $fu=UFunc(s,a,  self.space)
      | Integral/f
        '\(' EXPR/dx '::'
          VARID/s IN '\['VARID/ll ',' VARID/ul '\]'
       '\)'                                $fu=Integral(dx,s,ll,ul, self.space)
      | Root/s '\(' EXPR/a ',' VARID/u '\)'     $fu=Implicit(s,a,u, self.space)
      | Prod/ss '\(' EXPR/a ',' INDID/i IN INDID/j '\)'
                                    $fu = BlockProduct(ss, a, i, j, self.space)
      | MaxMin/fmm '\(' EXPR/amm ',' EXPR/bmm '\)'
                                          $fu=MaxMin(fmm, amm, bmm, self.space)
      |  'Diff'/f
       '\(' EXPR/x ',' EXPR/y '\)'         $fu=TotDifferential(x,y, self.space)
      | 'diff'/f
       '\(' EXPR/x ',' EXPR/y '\)'         $fu=ParDifferential(x,y, self.space)
      | Interval/f
        '\(' EXPR/a IN '\['VARID/ll ',' VARID/ul '\]' '\)'
                                            $fu=Interval(a, ll, ul, self.space)
  ;
  """

  verbose = 0

  def __init__(self, variables, indices, language=internal):
    '''
    Object to compile expression
    @param variables: an ordered dictionary of variable objects
    @param language: string defining the chosen target language
    '''
    self.space = CompileSpace(variables, indices, language)
    # print("expression language:", self.space.language)
    VerboseParser.__init__(self)
    self.space.eq_variable_incidence_list = []


if __name__ == '__main__':
    orig = ['a', 'c', 'd', 'b']
    se = ['a', 'c', 'a']
    print(generateIndexSeq(se, orig))
