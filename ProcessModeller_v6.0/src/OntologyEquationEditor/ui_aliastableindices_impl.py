
"""
===============================================================================
 GUI resource -- handles the table for the indices
===============================================================================

Major change in that only a symbol is set for each base index set
matlab was chosen as being the root symbol container
The other aliases are generated via compilation.

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2012. 04. 09"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"



MAX_HEIGHT = 800

from PyQt4 import QtGui, QtCore
from OntologyEquationEditor.ui_aliastable import Ui_AliasTable
from OntologyEquationEditor.resources import LANGUAGES


class UI_AliasTableIndices(QtGui.QWidget):
  '''
  classdocs
  '''

  completed = QtCore.pyqtSignal(str)

  def __init__(self, indices):
    '''
    Constructor
    '''
    QtGui.QWidget.__init__(self)
    self.indices = indices
    self.languages = LANGUAGES['aliasing']
    self.ui = Ui_AliasTable()
    self.ui.setupUi(self)
    self.setup()
    self.ui.tableWidget.itemChanged.connect(self.rename)

  def setup(self):

    a = self.ui.tableWidget
    a.clear()
    a.setRowCount(0)
    item = QtGui.QTableWidgetItem()
    item.setText("symbol")
    a.setHorizontalHeaderItem(0, item)
    col = 0
    a.setColumnCount(col + 1)
    item = QtGui.QTableWidgetItem()
    item.setText("symbol")
    a.setHorizontalHeaderItem(col, item)

    self.keep_symbol = {}
    for symbol in self.indices:
      if self.indices[symbol]["type"] == "index":
        row = a.rowCount()
        a.setRowCount(row+1)
        self.keep_symbol[row] = symbol #self.indices[symbol]["symbol"]  # not row+1 !
        item = QtGui.QTableWidgetItem()
        item.setText(str(symbol))
        a.setVerticalHeaderItem(row,item)
        item = QtGui.QTableWidgetItem()
        item.setText(self.indices[symbol]["aliases"][LANGUAGES["internal_code"]])
        a.setItem(row,col,item)
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

  def rename(self, item):
    symbol = self.keep_symbol[item.row()]
    self.indices[symbol]["symbol"] = str(item.text())
    self.indices.compile()
    self.__resize()

  def on_pushFinished_pressed(self):
    self.completed.emit("alias indices")
    self.hide()
