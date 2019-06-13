"""
===============================================================================
 Resources for the equation editor
===============================================================================


"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2012. 03. 221"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

# import os as OS
from PyQt4 import QtCore
from PyQt4 import QtGui

UNITARY_RETAIN_UNITS = ["abs", "+", "-", "min", "max"]
UNITARY_INVERSE_UNITS = ["inv"]
UNITARY_NO_UNITS = ["exp", "log", "ln", "sqrt", "^", "sin", "cos", "tan",
                    "asin", "acos", "atan"]
UNITARY_LOOSE_UNITS = ["sign"]

# INDENT = "    "
# LF = "\n"
NEW = "_new_"
NEW_EQ = NEW  # ..................... for new equation
EMPTY_EQ = "_empty_"  # ..............for no equation
PORT = "port"  # .....................for variables that are to be defined
UNDEF_EQ_NO = "Exxx"  # ..............for no equation defined
CONSTANT = "constant"
NEW_VAR = NEW
TEMP_VARIABLE = "temporary"
LAYER_DELIMITER = "_"
VAR_REG_EXPR = QtCore.QRegExp("[a-zA-Z_]\w*")
BLOCK_INDEX_SEPARATOR = " & "

TOOLTIPS = {}
TOOLTIPS["select"] = {}
TOOLTIPS["select"]["type"] = "click to for new variable"
TOOLTIPS["select"]["symbol"] = "click to change symbol"
TOOLTIPS["select"]["description"] = "click to change description"
TOOLTIPS["select"]["units"] = "click to change units"
TOOLTIPS["select"]["indices"] = "click to change indices"
TOOLTIPS["select"]["eqs"] = "click to get list of equations"
TOOLTIPS["select"]["del"] = "no action"

TOOLTIPS["edit"] = {}
TOOLTIPS["edit"]["type"] = "click for new variable"
TOOLTIPS["edit"]["symbol"] = "click to modify symbol"
TOOLTIPS["edit"]["description"] = "modify description"
TOOLTIPS["edit"]["units"] = "time, lenth, amount, mass, temp, current, light\nmay only be modified for _new_ variable"
TOOLTIPS["edit"]["indices"] = "may only be modified for _new_ variable"
TOOLTIPS["edit"]["eqs"] = "add equation"
TOOLTIPS["edit"]["variable"] = "no action"
TOOLTIPS["edit"]["del"] = "delete"

# ------------
TEMPLATES = {}

# used in compile space
TEMPLATES["temp_variable"] = "temp_%s"

# used in physvars
TEMPLATES["Equation_definition_delimiter"] = ":="
TEMPLATES["block_index"] = "%s" + BLOCK_INDEX_SEPARATOR + "%s"
TEMPLATES["conversion"] = "%s_conversion"
TEMPLATES["sub_index"] = "%s_%s"

EQUATION_TYPE = ["instantiate", "select", "generic", "network", "constant"]
# table control

# columns are
# 0 type --> new variable
# 1 symbol
# 2 description / documentation
# 3 units
# 4 indices
# 5 equations
# 6 delete

ENABLED_COLUMNS = {}  # TODO: remove hard wiring
ENABLED_COLUMNS["initialise"] = {}
ENABLED_COLUMNS["initialise"]["constant"] = [0, 1, 2, 3, 4, 5]
ENABLED_COLUMNS["initialise"]["state"] = [1, 2, 3, ]
ENABLED_COLUMNS["initialise"]["frame"] = [1, 2, 3, ]
ENABLED_COLUMNS["initialise"]["network"] = [1, 2, 4]
ENABLED_COLUMNS["initialise"]["others"] = []

ENABLED_COLUMNS["edit"] = {}
ENABLED_COLUMNS["edit"]["constant"] = [0, 1, 2, 3, 4, 5, 6]
ENABLED_COLUMNS["edit"]["others"] = [0, 1, 2, 4, 5, 6]
ENABLED_COLUMNS["edit"]["state"] = [1, 2, 3, 4, 5]
ENABLED_COLUMNS["edit"]["frame"] = [1, 2, 3, 4, 5]
ENABLED_COLUMNS["edit"]["network"] = [1, 2, 4, 6]

ENABLED_COLUMNS["inter_connections"] = {}
ENABLED_COLUMNS["inter_connections"]["constant"] = [0, 1, 2, 3, 4, 5, 6]
ENABLED_COLUMNS["inter_connections"]["transposition"] = [0, 1, 2, 5, 6]
ENABLED_COLUMNS["inter_connections"]["others"] = [0, 1, 2, 3, 4, 5, 6]
ENABLED_COLUMNS["inter_connections"]["state"] = [0, 1, 2, 3, 4, 5]

ENABLED_COLUMNS["intra_connections"] = {}
ENABLED_COLUMNS["intra_connections"]["constant"] = [0, 1, 2, 3, 4, 5, 6]
ENABLED_COLUMNS["intra_connections"]["transposition"] = [0, 1, 2, 5, 6]
ENABLED_COLUMNS["intra_connections"]["others"] = [0, 1, 2, 3, 4, 5, 6]
ENABLED_COLUMNS["intra_connections"]["state"] = [0, 1, 2, 3, 4, 5]

# code generation in abstract syntax

ONEPLACETEMPLATE = []
TWOPLACETEMPLATE = ["+", "-",
                    "^",
                    ".",
                    ":",
                    "diff",
                    "Diff",
                    ]
THREPLACETEMPLATE = ["|", "interval"]
FOURPLACETEMPLATE = ["integral"]
CODE = {}

## Languages
LANGUAGES = {}
# LANGUAGES["output"] = ["matlab", "latex"]
LANGUAGES["internal_code"] = "internal_code"
LANGUAGES["internals"] = [LANGUAGES["internal_code"], "rename"]
LANGUAGES["code_generation"] = ["python", "cpp", "matlab"]
LANGUAGES["documentation"] = ["latex"]
# LANGUAGES["compile"] = [LANGUAGES["internal_code"]] +  LANGUAGES["code_generation"] + LANGUAGES["documentation"]
LANGUAGES["compile"] = LANGUAGES["code_generation"] + LANGUAGES["documentation"]
LANGUAGES["aliasing"] =[LANGUAGES["internal_code"]] + LANGUAGES["code_generation"] + LANGUAGES["documentation"]
# LANGUAGES["aliasing"] = LANGUAGES["code_generation"] + LANGUAGES["documentation"]
LANGUAGES["index_roots_symbol"] = ["matlab"] #[LANGUAGES["internal_code"]]  # used in alias table GUI
LANGUAGES["rename"] = "rename"
LANGUAGES["matrix_form"] = ["matlab", "python", "cpp"]

###########    Core representation -- our language
internal = LANGUAGES["internal_code"]
CODE[internal] = {}
CODE[internal]["+"] = "%s + %s"
CODE[internal]["-"] = "%s - %s"

CODE[internal]["^"] = "%s^{%s}"  # power
CODE[internal][":"] = "%s : %s"  # Khatri-Rao product
CODE[internal]["."] = "%s . %s"  # expand product
CODE[internal]["|"] = "%s |%s| %s"  # reduce product
CODE[internal]["block_reduce"] = "%s |%s in %s| %s"  # reduce product
CODE[internal]["diff"] = "diff(%s,%s)"
CODE[internal]["Diff"] = "Diff(%s,%s)"
# CODE[internal]["integral"] = "integral( %s, %s )"
CODE[internal]["integral"] = "integral({integrand!s} :: {differential!s} in [{lower!s},{upper!s} ])"
CODE[internal]["interval"] = "interval(%s in [%s , %s])"
CODE[internal]["UFunc"] = "%s(%s)"
CODE[internal]["root"] = "root(%s,%s)"
# CODE[internal]["select"] = "select(%s,%s,%s)"
CODE[internal]["set"] = "set(%s)"
CODE[internal]["()"] = "(%s)"
CODE[internal]["index"] = "%s"
CODE[internal]["block_index.delimiter"] = " & "
CODE[internal]["block_index"] = "%s" + CODE[internal]["block_index.delimiter"] + "%s"
CODE[internal]["sub_index.delimiter"] = "_"
CODE[internal]["sub_index"] = "%s" + CODE[internal]["sub_index.delimiter"] + "%s"
CODE[internal]["comment"] = ""
CODE[internal]["max"] = "max(%s, %s)"
CODE[internal]["min"] = "min(%s, %s)"
CODE[internal]["prod"] = "prod({}, {}, {}, {})"
CODE[internal]["obj"] = "{}"

CODE["matlab"] = {}
CODE["matlab"]["+"] = "%s + %s"
CODE["matlab"]["-"] = "%s - %s"
CODE["matlab"]["^"] = "%s ** (%s)"
CODE["matlab"][":"] = "KhatriRaoProduct(%s, %s)"  # ..................Khatri-Rao product
CODE["matlab"]["."] = "expandproduct(%s, %s)"  # .....................expand product
CODE["matlab"]["."] = "%s .* %s"  # ..................................expand product
# CODE["matlab"]["|"] = "reduceproduct(%s, %s, %s)"  # reduce product
CODE["matlab"]["|"] = "%s * %s"  # ...................................reduce product
CODE["matlab"]["diff"] = "diff(%s,%s)"
CODE["matlab"]["Diff"] = "Diff(%s,%s)"
# CODE["matlab"]["integral"] = "integral(%s,%s)"
CODE["matlab"]["integral"] = "integral({integrand!s},{differential!s}," \
                             "{lower!s},{upper!s})"
CODE["matlab"]["interval"] = "interval(%s, %s , %s)"
CODE["matlab"]["UFunc"] = "%s(%s)"
CODE["matlab"]["root"] = "root(%s,%s)"
# CODE["matlab"]["select"] = "select(%s,%s,%s)"
CODE["matlab"]["set"] = "sett(%s)"
CODE["matlab"]["()"] = "(%s)"
CODE["matlab"]["index"] = "%s"
CODE["matlab"]["block_index.delimiter"] = "_x_"
CODE["matlab"]["block_index"] = "%s" + CODE["matlab"]["block_index.delimiter"] + "%s"
CODE["matlab"]["sub_index.delimiter"] = "_"
CODE["matlab"]["sub_index"] = "%s" + CODE["matlab"]["sub_index.delimiter"] + "%s"
CODE["matlab"]["transpose"] = "( %s )' "
CODE["matlab"]["block_reduce"] = "blockReduce(%s,%s,%s,%s)"
CODE["matlab"]["matrix_reduce"] = "matrixProduct(%s,%s,%s,%s)"
CODE["matlab"]["comment"] = "%"
CODE["matlab"]["max"] = "max(%s, %s)"
CODE["matlab"]["min"] = "min(%s, %s)"
CODE["matlab"]["prod"] = "blockProduct({}, {}, {}, {})"
CODE["matlab"]["khatri_rao_matrix"] = "khatriRao(%s, %s, %s, %s)"
CODE["matlab"]["obj"] = "{}"

CODE["python"] = {}
CODE["python"]["array"] = "np.array(%s)"
CODE["python"]["list"] = "np.array"
CODE["python"]["+"] = "np.add(%s, %s)"
CODE["python"]["-"] = "np.subtract(%s, %s)"
CODE["python"]["^"] = "np.power(%s, %s)"
CODE["python"][":"] = "khatriRao(%s, %s)"  # .......................Khatri-Rao product
CODE["python"]["."] = "np.multiply(%s, %s)"  # .....................expand product
CODE["python"]["|"] = "np.dot(%s, %s)"  # ..........................reduce product
CODE["python"]["diff"] = "diff(%s, %s)"
CODE["python"]["Diff"] = "Diff(%s, %s)"
CODE["python"]["integral"] = "integral({integrand!s},{differential!s}," \
                             "{lower!s},{upper!s})"
CODE["python"]["interval"] = "interval(%s, %s, %s)"
CODE["python"]["UFunc"] = "%s(%s)"
CODE["python"]["root"] = "root(%s, %s)"
# CODE["python"]["select"] = "select(%s, %s, %s)"
CODE["python"]["set"] = "np.ones(np.shape(%s))"
CODE["python"]["()"] = "(%s)"
CODE["python"]["index"] = "%s"
CODE["python"]["block_index.delimiter"] = "_x_"
CODE["python"]["block_index"] = "%s" + CODE["python"]["block_index.delimiter"] + "%s"
CODE["python"]["sub_index.delimiter"] = "_"
CODE["python"]["sub_index"] = "%s" + CODE["python"]["sub_index.delimiter"] + "%s"
CODE["python"]["transpose"] = "np.transpose(%s)"
CODE["python"]["block_reduce"] = "blockReduce(%s, %s, %s, %s)"
CODE["python"]["matrix_reduce"] = "matrixProduct(%s, %s, %s, %s)"
CODE["python"]["khatri_rao_matrix"] = "khatriRao(%s, %s, %s, %s)"
CODE["python"]["comment"] = "#"
CODE["python"]["sign"] = "np.sign(%s)"
CODE["python"]["inv"] = "np.reciprocal(%s)"
CODE["python"]["sqrt"] = "np.sqrt(%s)"
CODE["python"]["exp"] = "np.exp(%s)"
CODE["python"]["ln"] = "np.log(%s)"
CODE["python"]["log"] = "np.log10(%s)"
CODE["python"]["neg"] = "np.negative(%s)"
CODE["python"]["abs"] = "np.abs(%s )"  # .........................not fabs complex numbers
CODE["python"]["sin"] = "np.sin(%s)"
CODE["python"]["asin"] = "np.arcsin(%s)"
CODE["python"]["tan"] = "np.tan(%s)"
CODE["python"]["atan"] = "np.arctan(%s)"
CODE["python"]["cos"] = "np.cos(%s)"
CODE["python"]["acos"] = "np.arccos(%s)"
CODE["python"]["max"] = "np.fmax(%s, %s)"
CODE["python"]["min"] = "np.fmin(%s, %s)"
CODE["python"]["prod"] = "blockProduct({}, {}, {}, {})"
CODE["python"]["obj"] = "self.{}"

CODE["cpp"] = {}
CODE["cpp"]["array"] = "np.array(%s)"
CODE["cpp"]["list"] = "liste(%s)"
CODE["cpp"]["+"] = "np.add(%s, %s)"
CODE["cpp"]["-"] = "np.subtract(%s, %s)"
CODE["cpp"]["^"] = "np.power(%s, %s)"
CODE["cpp"][":"] = "khatriRao(%s, %s)"  # ........................Khatri-Rao product
CODE["cpp"]["."] = "ganger(%s, %s)"  # ...........................expand product
CODE["cpp"]["|"] = "np.dot(%s, %s)"  # ...........................reduce product
CODE["cpp"]["diff"] = "diff(%s, %s)"
CODE["cpp"]["Diff"] = "Diff(%s, %s)"
CODE["cpp"]["integral"] = "integral({integrand!s},{differential!s}," \
                          "{lower!s},{upper!s})"
CODE["cpp"]["interval"] = "interval(%s, %s, %s)"
CODE["cpp"]["UFunc"] = "%s(%s)"
CODE["cpp"]["root"] = "root(%s, %s)"
# CODE["cpp"]["select"] = "select(%s, %s, %s)"
CODE["cpp"]["set"] = "np.ones(np.shape(%s))"
CODE["cpp"]["()"] = "(%s)"
CODE["cpp"]["index"] = "%s"
CODE["cpp"]["block_index.delimiter"] = "_x_"
CODE["cpp"]["block_index"] = "%s" + CODE["cpp"]["block_index.delimiter"] + "%s"
CODE["cpp"]["sub_index.delimiter"] = "_"
CODE["cpp"]["sub_index"] = "%s" + CODE["cpp"]["sub_index.delimiter"] + "%s"
CODE["cpp"]["transpose"] = "np.transpose(%s)"
CODE["cpp"]["block_reduce"] = "blockReduce(%s, %s, %s, %s)"
CODE["cpp"]["matrix_reduce"] = "matrixProduct(%s, %s, %s, %s)"
CODE["cpp"]["khatri_rao_matrix"] = "khatriRao(%s, %s, %s, %s)"
CODE["cpp"]["comment"] = "#"
CODE["cpp"]["sign"] = "np.sign(%s)"
CODE["cpp"]["inv"] = "np.reciprocal(%s)"
CODE["cpp"]["sqrt"] = "np.sqrt(%s)"
CODE["cpp"]["exp"] = "np.exp(%s)"
CODE["cpp"]["ln"] = "np.log(%s)"
CODE["cpp"]["log"] = "np.log10(%s)"
CODE["cpp"]["neg"] = "np.negative(%s)"
CODE["cpp"]["abs"] = "np.abs(%s )"  # not fabs complex numbrs
CODE["cpp"]["sin"] = "np.sin(%s)"
CODE["cpp"]["asin"] = "np.arcsin(%s)"
CODE["cpp"]["tan"] = "np.tan(%s)"
CODE["cpp"]["atan"] = "np.arctan(%s)"
CODE["cpp"]["cos"] = "np.cos(%s)"
CODE["cpp"]["acos"] = "np.arccos(%s)"
CODE["cpp"]["max"] = "np.fmax(%s, %s)"
CODE["cpp"]["min"] = "np.fmin(%s, %s)"
CODE["cpp"]["prod"] = "blockProduct(%s, %s, %s)"

# CODE["python_numpy"] = {}
# CODE["python_numpy"]["+"] = "%s + %s"
# CODE["python_numpy"]["-"] = "%s - %s"
# CODE["python_numpy"]["^"] = "%s ** (%s)"
# CODE["python_numpy"][":"] = "KhatriRaoProduct(%s, %s)"  # Khatri-Rao product
# CODE["python_numpy"]["."] = "expandproduct(%s, %s)"  # expand product
# CODE["python_numpy"]["|"] = "reduceproduct(%s, %s, %s)"  # reduce product
# CODE["python_numpy"]["|"] = "reduceproduct%s , %s"  # reduce product
# CODE["python_numpy"]["diff"] = "diff(%s,%s)"
# CODE["python_numpy"]["Diff"] = "Diff(%s,%s)"
# CODE["python_numpy"]["integral"] = "integral(%s,%s)"
# CODE["python_numpy"]["integral"] = "integral({integrand!s},{differential!s}," \
#                             "{lower!s},{upper!s})"
# CODE["python_numpy"]["interval"] = "interval(%s, %s , %s)"
# CODE["python_numpy"]["UFunc"] = "%s(%s)"
# CODE["python_numpy"]["root"] = "root(%s,%s)"
# CODE["python_numpy"]["select"] = "select(%s,%s,%s)"
# CODE["python_numpy"]["set"] = "sett(%s)"
# CODE["python_numpy"]["()"] = "(%s)"
# CODE["python_numpy"]["index"] = "%s"
# CODE["python_numpy"]["block_index.delimiter"] = "_x_"
# CODE["python_numpy"]["block_index"] = "%s" + CODE["python_numpy"]["block_index.delimiter"] + "%s"
# CODE["python_numpy"]["sub_index.delimiter"] = "_"
# CODE["python_numpy"]["sub_index"] = "%s" + CODE["python_numpy"]["sub_index.delimiter"] + "%s"
# CODE["python_numpy"]["transpose"] = "transpose( %s ) "
# CODE["python_numpy"]["block_reduce"] = "blockReduce(%s,%s,%s,%s)"
# CODE["python_numpy"]["matrix_reduce"] = "matrixProduct(%s,%s,%s,%s)"
# CODE["python_numpy"]["comment"] = "#"

CODE["latex"] = {}
CODE["latex"]["+"] = "%s  + %s"
CODE["latex"]["-"] = "%s  - %s"
CODE["latex"]["^"] = "%s^{%s}"  # power
CODE["latex"][":"] = "%s \, {\odot} \, %s"  # .........................Khatri-Rao product
CODE["latex"]["."] = "(%s) \, . \, (%s)"  # ...............................expand product
CODE["latex"]["|"] = "%s \stackrel{%s}{\,\star\,} %s"  # ..............reduce product
CODE["latex"]["diff"] = "\ParDiff{%s}{%s}"
CODE["latex"]["Diff"] = "\TotDiff{%s}{%s}"
CODE["latex"]["block_reduce"] = "%s \stackrel{%s \, \in \, %s}{\,\star\,} %s"
# CODE["latex"]["integral"] = "\int \, %s d%s"
# CODE["latex"]["integral"] = "integral({integrand!s},{differential!s}," \
#                              "{lower!s},{upper!s})"
CODE["latex"]["integral"] = "\int_{{ {lower!s} }}^{{ {upper!s} }} \, {integrand!s} \enskip d\,{differential!s}"
CODE["latex"]["interval"] = r"%s \in \left[ {%s} , {%s} \right] "
CODE["latex"]["UFunc"] = r"%s\left(%s\right)"
CODE["latex"]["root"] = r"root\left( %s, %s \right)"
# CODE["latex"]["select"] = r"S\left(%s,%s \rightarrow %s\right)"
CODE["latex"]["set"] = "set(%s)"
CODE["latex"]["equation"] = "%s = %s"
CODE["latex"]["()"] = r"\left(%s \right)"
CODE["latex"]["max"] = r"\mathbf{max}\left( %s, %s \right)"
CODE["latex"]["min"] = r"\mathbf{min}\left( %s, %s \right)"
CODE["latex"]["prod"] = r"\displaystyle \prod_{{ {2} \in {3} }} {0}"
#
CODE["latex"]["index"] = "{\cal{%s}}"
CODE["latex"]["block_index.delimiter"] = " "
# CODE["latex"]["block_index"] = "{"+ CODE["latex"]["index"] + \
#                                 CODE["latex"]["block_index.delimiter"] + \
#                                 CODE["latex"]["index"] + "}"
# CODE["latex"]["sub_index.delimiter"] = "^"
# CODE["latex"]["sub_index"] = "{"+ CODE["latex"]["index"] + \
#                                 CODE["latex"]["sub_index.delimiter"] + \
#                                 "%s" + "}"
CODE["latex"]["block_index"] = "{%s" + \
                               CODE["latex"]["block_index.delimiter"] + \
                               "%s}"
CODE["latex"]["sub_index.delimiter"] = "^"
CODE["latex"]["sub_index"] = "{%s" + \
                             CODE["latex"]["sub_index.delimiter"] + \
                             "{%s}" + "}"

CODE[LANGUAGES["rename"]] = CODE[internal]

FILE_EXTENSIONS = {}
FILE_EXTENSIONS["python"] = ".py"
FILE_EXTENSIONS["json"] = ".json"
FILE_EXTENSIONS["latex"] = ".tex"
FILE_EXTENSIONS["matlab"] = ".m"
FILE_EXTENSIONS["cpp"] = ".cpp"
FILE_EXTENSIONS["str"] = ".txt"

LOAD_FILE = "Load file"
SAVE_AS = "Save as"


def setValidator(lineEdit):
  validator = QtGui.QRegExpValidator(VAR_REG_EXPR, lineEdit)
  lineEdit.setValidator(validator)
  return validator
