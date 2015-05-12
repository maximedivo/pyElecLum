#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = u'Maxime DIVO'
__copyright__ = u'Copyright 2015, Maxime DIVO'
__credits__ = [u'Maxime DIVO']

__license__ = u'GPL v3'
__version__ = u'0.0.1'
__maintainer__ = u'Maxime DIVO'
__email__ = u'maxime.divo@gmail.com'
__status__ = u'Development'

import sys

from PySide import QtCore, QtGui

import Tree as t
import graphicScene as gs
import propertyWidgets as pw

import Icons as I


"""
Les class
"""

class DocumentModel(object):
    
    def __init__(self):
        self.armoire = t.Armoire()
        initalDepart = t.Depart(self.armoire, u'Départ 1')
        
    def new(self):
        pass
        
    def open(self):
        pass
    
    def save(self):
        pass
        
    def save_as(self):
        pass
        
    def add_depart(self):
        nouveauDepart = t.Depart(self.armoire, u'Nouveau départ')

        
class MainWindow(QtGui.QMainWindow):
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(None)
        
        self.document = DocumentModel()
        
        self.initToolBar()
        self.initDock()
        
        self.graphicTab = QtGui.QTabWidget(self)
        self.setCentralWidget(self.graphicTab)
        
        for depart in self.document.armoire:
            graphicView = QtGui.QGraphicsView(self)
            scene = gs.DepartScene(self, depart)
            scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
            graphicView.setScene(scene)
            self.graphicTab.addTab(graphicView, QtGui.QIcon(I.DEP_32), depart.mnemonique)
            scene.selectionChanged.connect(self.selectedItemChange)
            
    def initToolBar(self):
        
        ## Les actions
        newAction = QtGui.QAction(QtGui.QIcon(I.FILE_32), u'Nouveau', self)
        newAction.setShortcut(u'Ctrl+N')
        newAction.setStatusTip(u'Créer un nouveau fichier')
        newAction.triggered.connect(self.document.new)

        openAction = QtGui.QAction(QtGui.QIcon(I.OPEN_32), u'Ouvrir', self)
        openAction.setShortcut(u'Ctrl+O')
        openAction.setStatusTip(u'Ouvrir un fichier')
        openAction.triggered.connect(self.document.open)

        saveAction = QtGui.QAction(QtGui.QIcon(I.DISK_32), u'Enregistrer', self)
        saveAction.setShortcut(u'Ctrl+S')
        saveAction.setStatusTip(u'Enregistrer le fichier')
        saveAction.triggered.connect(self.document.save)

        saveAsAction = QtGui.QAction(QtGui.QIcon(I.DISKS_32), u'Enregistrer sous...', self)
        saveAsAction.setShortcut(u'Ctrl+Shift+S')
        saveAsAction.setStatusTip(u'Enregistrer le fichier sous...')
        saveAsAction.triggered.connect(self.document.save_as)
        
        
        addDepartAction = QtGui.QAction(QtGui.QIcon(I.ADD_DEP_32), u'Créer un départ', self)
        addDepartAction.setShortcut(u'Ctrl+Shift+S')
        addDepartAction.setStatusTip(u'Créer un nouveau départ sur l\'armoire')
        addDepartAction.triggered.connect(self.document.add_depart)
        
        
        ## La barre de menu
        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu(u'&Fichier')
        fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addSeparator()
        fileMenu.addAction(saveAction)
        fileMenu.addAction(saveAsAction)
        
        ## La barre outils
        toolbar = self.addToolBar(u'Fichier')
        toolbar.setIconSize(QtCore.QSize(32, 32))
        toolbar.addAction(newAction)
        toolbar.addAction(openAction)
        toolbar.addAction(saveAction)
        toolbar.addAction(saveAsAction)
        toolbar.addSeparator()

    def initDock(self):
        self.propertyDockWidget = pw.EditPanel(u'Propriétés', self)
        self.propertyDockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.propertyDockWidget)
        self.propertyDockWidget.valueChanged.connect(self.propertyChange)
        
    def propertyChange(self):
        self.graphicTab.currentWidget().scene().update()
    
    def selectedItemChange(self):
        items = self.graphicTab.currentWidget().scene().selectedItems()
        item = None
        if len(items) > 0:
            item, = items
        self.propertyDockWidget.setItem(item)
    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    locale = QtCore.QLocale.system().name()
    translator = QtCore.QTranslator()
    translator.load(u"qt_" + locale, QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))
    app.installTranslator(translator)

    win = MainWindow()
    win.showMaximized()

    sys.exit(app.exec_())    