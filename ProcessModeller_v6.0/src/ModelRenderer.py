"""
Author:  Arne Tobias Elve
What:    Start point for code rendering
Started: Date
Reason:
Status:  Production
Contact: arne.t.elve(at)ntnu.no
"""

from PyQt4 import QtGui
from ModelRenderer.Editor.editor_model_renderer_gui_impl import Ui_ModelFactory
# from Common.resource_initialisation import DIRECTORIES
from Common.ontology_container import OntologyContainer
from ModelRenderer.main import ModelRenderer
import sys
import os


cwd = os.getcwd()
sys.path.append(cwd)

if __name__ == '__main__':
  # mode = 'use'
  mode = 'development back-end'
  # mode = 'development front-end'
  if mode == 'development back-end':

    # Selectables:
    ontology_name = 'HEX_02'
    mod_name = 'cc_HEX_single_nodes'
    case_name = 'latest'
    language = 'python'

    ontology = OntologyContainer(ontology_name)
    ontology_location = ontology.onto_path
    # model_loc = '{}/models/{}'.format(ontology_location, mod_name)
    mr = ModelRenderer(ontology, mod_name, case_name)
    mr.setup_system(language)
    mr.generate_output()

  else:
    a = QtGui.QApplication(sys.argv)
    a.setWindowIcon(QtGui.QIcon("./Common/icons/modelfactory.png"))
    w = Ui_ModelFactory()
    w.setWindowTitle('Model Renderer')
    w.show()
    r = a.exec_()
    sys.exit(r)
