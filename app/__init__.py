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
import pickle
import os

from PySide import QtCore, QtGui
from PySide.QtCore import Signal

import tree as t
import graphicScene as gs
import propertyWidgets as pw

import icons as I

APP = u'pyElecLum'
MAJOR = 0
MINOR = 5
BUILD = 2
VERSION = u'{}.{}.{}'.format(MAJOR, MINOR, BUILD)
APP_VERSION = u'{} {}'.format(APP, VERSION)

DESKTOP_PATH = os.path.expanduser(u'~/Desktop/')

"""
Les class
"""

class DocumentModel(QtCore.QObject):
    documentChanged = Signal()
    
    def __init__(self, parent = None):
        super(DocumentModel, self).__init__()
        self.parent = parent
        self._new()
        
    def new(self):
        if not self.edited:
            self._new()
            self.documentChanged.emit()
        
    def _new(self):
        self.armoire = t.Armoire()
        initalDepart = t.Depart(self.armoire, u'Départ 1')
        self.fileName = None
        self._edited = False
        
    def open(self):
        if not self.edited:
            fileName, selectedFilter = QtGui.QFileDialog.getOpenFileName(self.parent, u'Ouvrir...', DESKTOP_PATH, u'Fichier PyElecLum (*.elc)')
            if fileName is not u'':
                self.fileName = fileName
                self._open(self.fileName)
                self.edited = False
                self.documentChanged.emit()
    
    def openFile(self, file):
        if not self.edited:
            fileName = file.toLocalFile()
            self._open(fileName)
            self.fileName = fileName
            self.edited = False
            self.documentChanged.emit()
        
    def _open(self, fileName):
        file = open(fileName, 'rb')
        unpickler = pickle.Unpickler(file)
        self.armoire = unpickler.load()
        file.close()
    
    def save(self):
        if self.fileName is not None:
            self._save(self.fileName)
            self.edited = False
            self.documentChanged.emit()
            return True
        else:
            fileName, selectedFilter = QtGui.QFileDialog.getSaveFileName(self.parent, u'Enregistrer...', DESKTOP_PATH, u'Fichier PyElecLum (*.elc)')
            if fileName is not u'':
                self.fileName = fileName
                self._save(self.fileName)
                self.edited = False
                self.documentChanged.emit()
                return True
            else:
                return False
        
    def save_as(self):
        fileName, selectedFilter = QtGui.QFileDialog.getSaveFileName(self.parent, u'Enregistrer sous...', DESKTOP_PATH, u'Fichier PyElecLum (*.elc)')
        if fileName is not u'':
                self.fileName = fileName
                self._save(self.fileName)
                self.edited = False
                self.documentChanged.emit()
        
    def _save(self, fileName):
        file = open(fileName,'wb') # In binary format
        pickler = pickle.Pickler(file, pickle.HIGHEST_PROTOCOL)
        pickler.dump(self.armoire)
        file.close()
    
    def addDepart(self):
        nouveauDepart = t.Depart(self.armoire, u'Nouveau départ')
        self.documentChanged.emit()
    
    def supprDepart(self, depart):
        self.armoire.remove(depart)
    
    def edit(self):
        self.edited = True
    
    @property
    def edited(self):
        if self._edited:
            ret = QtGui.QMessageBox.information(self.parent, u'Le fichier a été modifié',
                                                u'Voulez-vous sauvegarder le fichier avant de la fermer ? ',
                                                QtGui.QMessageBox.Save |
                                                QtGui.QMessageBox.Discard |
                                                QtGui.QMessageBox.Cancel,
                                                QtGui.QMessageBox.Save)
            if ret == QtGui.QMessageBox.Save:
                return not self.save()
            elif ret == QtGui.QMessageBox.Discard:
                return False
            else:
                return True
        else:
            return False
    
    @edited.setter
    def edited(self, value):
        self._edited = value


class MainWindow(QtGui.QMainWindow):
    fileDropped = Signal(QtCore.QUrl)
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(None)
        self.showMaximized()
        self.setDocumentMode(True)
        self.setAcceptDrops(True)
        self._fullscreen = False
        
        self.graphicTab = QtGui.QTabWidget(self)
        self.graphicTab.setTabsClosable(True)
        self.graphicTab.tabCloseRequested.connect(self.supprDepart)
        
        self.setCentralWidget(self.graphicTab)
        
        self.document = DocumentModel(self)
        self.document.documentChanged.connect(self.initUi)
        self.fileDropped.connect(self.document.openFile)
        
        self.initToolBar()
        self.initDock()
        
        self.initUi()
    
    def initTitle(self):
        name = u''
        edited = u''
        if self.document.fileName is None:
            name = u'Nouveau fichier'
        else:
            # other, name = os.path.split(self.document.fileName)
            name = os.path.abspath(self.document.fileName)
        if self.document._edited:
            edited = u'*'
        title = u'{}{} - {}'.format(edited, name, APP_VERSION)
        self.setWindowTitle(title)
    
    def initUi(self):
        self.initTitle()
        self.graphicTab.clear()
        for depart in self.document.armoire:
            graphicView = gs.DepartView(self)
            scene = gs.DepartScene(self, depart)
            scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
            scene.edited.connect(self.document.edit)
            scene.edited.connect(self.propertyChange)
            graphicView.setScene(scene)
            graphicView.centerOn(0,0)
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
        
        addDepartAction = QtGui.QAction(QtGui.QIcon(I.ADD_DEP_32), u'Nouveau départ', self)
        addDepartAction.setShortcut(u'Ctrl+Shift+C')
        addDepartAction.setStatusTip(u'Créer un nouveau départ sur l\'armoire')
        addDepartAction.triggered.connect(self.addDepart)
        
        redrawAction = QtGui.QAction(QtGui.QIcon(I.ZOOM_REFR_32), u'Rafraichir', self)
        redrawAction.setShortcut(u'Ctrl+R')
        redrawAction.setStatusTip(u'Rafraichir la zone graphique')
        redrawAction.triggered.connect(self.redraw)
        
        zoomResetAction = QtGui.QAction(QtGui.QIcon(I.ZOOM_FIT_32), u'Réinitialiser', self)
        zoomResetAction.setShortcut(u'R')
        zoomResetAction.setStatusTip(u'Réinitialiser la vue')
        zoomResetAction.triggered.connect(self.zoomReset)
        
        fullScreenAction = QtGui.QAction(QtGui.QIcon(I.FULLSCREEN_32), u'Plein écran', self)
        fullScreenAction.setShortcut(u'F11')
        fullScreenAction.setStatusTip(u'Afficher en plein écran')
        fullScreenAction.triggered.connect(self.fullScreen)
        
        
        ## La barre de menu
        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu(u'&Fichier')
        fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addSeparator()
        fileMenu.addAction(saveAction)
        fileMenu.addAction(saveAsAction)
        
        editMenu = menubar.addMenu(u'&Edition')
        editMenu.addAction(addDepartAction)
        
        displayMenu = menubar.addMenu(u'&Affichage')
        displayMenu.addAction(fullScreenAction)
        displayMenu.addSeparator()
        displayMenu.addAction(redrawAction)
        displayMenu.addAction(zoomResetAction)
        
        ## La barre outils
        toolbar = self.addToolBar(u'Fichier')
        toolbar.setIconSize(QtCore.QSize(32, 32))
        toolbar.addAction(newAction)
        toolbar.addAction(openAction)
        toolbar.addAction(saveAction)
        toolbar.addAction(saveAsAction)
        toolbar.addSeparator()
        
        toolbar = self.addToolBar(u'Edition')
        toolbar.setIconSize(QtCore.QSize(32, 32))
        toolbar.addAction(addDepartAction)
        toolbar.addSeparator()

    def initDock(self):
        self.propertyDockWidget = pw.EditPanel(u'Propriétés', self)
        self.propertyDockWidget.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.propertyDockWidget)
        self.propertyDockWidget.valueChanged.connect(self.document.edit)
        self.propertyDockWidget.valueChanged.connect(self.propertyChange)
        
    def propertyChange(self):
        self.graphicTab.currentWidget().scene().update()
        self.initTitle()
    
    def selectedItemChange(self):
        items = self.graphicTab.currentWidget().scene().selectedItems()
        item = None
        if len(items) > 0:
            item, = items
        self.propertyDockWidget.setItem(item)
        
    def redraw(self):
        print u'Redraw'
        self.graphicTab.currentWidget().scene().redraw_()
        
    def zoomReset(self):
        self.graphicTab.currentWidget().zoomReset()

    def addDepart(self):
        self.document.addDepart()
    
    def supprDepart(self, index):
        ret = QtGui.QMessageBox.information(self, u'Supprimer un départ',
                                                u'Voulez-vous vraiment supprimer le départ ? ',
                                                QtGui.QMessageBox.Yes |
                                                QtGui.QMessageBox.Cancel,
                                                QtGui.QMessageBox.Cancel)
        if ret == QtGui.QMessageBox.Yes:
            depart = self.graphicTab.widget(index).scene().depart
            self.document.supprDepart(depart)
            self.graphicTab.removeTab(index)
        
    def fullScreen(self):
        self._fullscreen = not self._fullscreen
        if self._fullscreen:
            self.showFullScreen()
        else:
            self.showMaximized()
            
    def dragEnterEvent(self, event):
        event.accept()
        
    def dragMoveEvent(self, event):
        event.accept()
    
    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            for url in event.mimeData().urls():
                self.fileDropped.emit(url)
        else:
            event.ignore()

    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    locale = QtCore.QLocale.system().name()
    translator = QtCore.QTranslator()
    translator.load(u"qt_" + locale, QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))
    app.installTranslator(translator)

    win = MainWindow()
    win.showMaximized()

    sys.exit(app.exec_())    