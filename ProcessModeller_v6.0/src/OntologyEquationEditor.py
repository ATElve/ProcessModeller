#!/usr/bin/python3.5
# encoding: utf-8
#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 APP for editing the equations
===============================================================================


"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2009. 04. 17"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"


# __docformat__ = "restructuredtext en"

from PyQt4 import QtGui
from OntologyEquationEditor.ui_ontology_design_impl import UiOntologyDesign
import sys
import os


cwd = os.getcwd()
sys.path.append(cwd)

if __name__ == '__main__':
  a = QtGui.QApplication(sys.argv)
  a.setWindowIcon(QtGui.QIcon("./Common/icons/ontology.svg"))
  w = UiOntologyDesign()
  w.show()
  r = a.exec_()
  sys.exit(r)
