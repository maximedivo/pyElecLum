#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = u'Maxime DIVO'
__copyright__ = u'Copyright 2015, Maxime DIVO'
__credits__ = [u'Maxime DIVO']

__license__ = u'GPL v3'
__version__ = u'0.1.1'
__maintainer__ = u'Maxime DIVO'
__email__ = u'maxime.divo@gmail.com'
__status__ = u'Development'

import sys

from PySide import QtCore, QtGui
from PySide.QtCore import Signal

import tree as t
import graphicScene as gs
import icons as I

class TypeDialog(QtGui.QDialog):

    def __init__(self, parent):
        super(TypeDialog, self).__init__(parent)
        self.setWindowTitle(u'Sélection...')
        
        mainLayout = QtGui.QVBoxLayout(self)
        splitter = QtGui.QSplitter(self)
        mainLayout.addWidget(splitter)
        
        self.treeview = QtGui.QTreeWidget(self)
        splitter.addWidget(self.treeview)
        
        rightWidget = QtGui.QWidget(splitter)
        rightLayout = QtGui.QVBoxLayout(rightWidget)
        
        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok |
                                           QtGui.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        rightLayout.addWidget(buttonBox)
        
        rightWidget.setLayout(rightLayout)
        
    def loadTree(self):
        pass
        
    def accept(self):
        print u'Done !'
        super(TypeDialog, self).accept()