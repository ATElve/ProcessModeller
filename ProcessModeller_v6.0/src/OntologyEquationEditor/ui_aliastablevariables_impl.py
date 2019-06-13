
"""
===============================================================================
 GUI resource -- handles the table for the variables
===============================================================================

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2016. 08. 15"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"



from PyQt4 import QtGui, QtCore
from OntologyEquationEditor.ui_aliastable import Ui_AliasTable
from OntologyEquationEditor.resources import LANGUAGES

MAX_HEIGHT = 800


class UI_AliasTableVariables(QtGui.QWidget):
  '''
  classdocs
  '''

  completed = QtCore.pyqtSignal(str)

  def __init__(self, variables, aliases):
    '''
    Constructor
    '''
    QtGui.QWidget.__init__(self)
    self.aliases = aliases
    self.all_variables = variables
    self.languages = LANGUAGES['aliasing']
    self.ui = Ui_AliasTable()
    self.ui.setupUi(self)
    # self.ui.tableWidget.setRowCount(0)
    # self.hide()
    self.setup()
    self.ui.tableWidget.itemChanged.connect(self.rename)
  #
  # def reset_table(self, aliases, all_variables):

  def setup(self):

    aliases = self.aliases
    all_variables = self.all_variables
    a = self.ui.tableWidget
    a.clear()
    a.setRowCount(0)
    item = QtGui.QTableWidgetItem()
    item.setText("symbol")
    a.setHorizontalHeaderItem(0, item)
    col = 0
    for l in self.languages:
      a.setColumnCount(col + 1)
      item = QtGui.QTableWidgetItem()
      item.setText(l)
      a.setHorizontalHeaderItem(col, item)
      col += 1
    for what in all_variables:
      row = a.rowCount()
      a.setRowCount(row + 1)
      item = QtGui.QTableWidgetItem()
      item.setText(str(what))
      a.setVerticalHeaderItem(row, item)
      col = 0
      for l in self.languages:
        try:
          s = aliases[what][l]
        except:
          s = what
        item = QtGui.QTableWidgetItem()
        item.setText(s)
        a.setItem(row, col, item)
        col += 1
    self.__resize()

  def __resize(self):
    tab = self.ui.tableWidget
    tab.resizeColumnsToContents()
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
    tab = self.ui.tableWidget
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

  # def on_tableWidget_itemChanged(self, item):
  def rename(self, item):
    lang = self.languages[int(item.column())]
    token = self.all_variables[int(item.row())]
    self.aliases[token][lang] = str(item.text())
    self.__resize()

  # def show(self):
  #   self.reset_table(self.aliases, self.all_variables)
  #   QtGui.QDialog.show(self)

  def on_pushFinished_pressed(self):
    self.completed.emit("alias variables")
    self.close()
