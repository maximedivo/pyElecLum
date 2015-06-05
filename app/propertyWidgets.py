#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = u'Maxime DIVO'
__copyright__ = u'Copyright 2015, Maxime DIVO'
__credits__ = [u'Maxime DIVO']

__license__ = u'GPL v3'
__version__ = u'0.2.3'
__maintainer__ = u'Maxime DIVO'
__email__ = u'maxime.divo@gmail.com'
__status__ = u'Development'

import sys
import copy

from PySide import QtCore, QtGui
from PySide.QtCore import Signal

import tree as t
import graphicScene as gs
import typeDialogs as td
import icons as I

PANEL_WIDTH = 450

class OuvrageWidget(QtGui.QWidget):
    ouvrageChanged = Signal()
    
    def __init__(self, parent, ouvrage):
        super(OuvrageWidget, self).__init__(parent)
        
        self.ouvrage = ouvrage
        
        self.mainLayout = QtGui.QVBoxLayout(self)
        formLayout = QtGui.QFormLayout(self)
        self.mnemonique = QtGui.QLineEdit(self)
        
        formLayout.addRow(u'Mnemonique', self.mnemonique)
        
        ouvrageGroup = QtGui.QGroupBox(u'Ouvrage')
        ouvrageGroup.setLayout(formLayout)
        self.mainLayout.addWidget(ouvrageGroup)
        
        self.recepteursTab = QtGui.QTabWidget(self)
        
        self.addReceptBtn = QtGui.QPushButton(u'Ajouter', self)
        self.supprReceptBtn = QtGui.QPushButton(u'Supprimer', self)
        btnReceptLayout = QtGui.QHBoxLayout(self)
        btnReceptLayout.addWidget(self.addReceptBtn)
        btnReceptLayout.addWidget(self.supprReceptBtn)
        
        recepteursLayout = QtGui.QVBoxLayout(self)
        recepteursLayout.addWidget(self.recepteursTab)
        recepteursLayout.addLayout(btnReceptLayout)
        recepteursGroup = QtGui.QGroupBox(u'Récepteurs')
        recepteursGroup.setLayout(recepteursLayout)
        self.mainLayout.addWidget(recepteursGroup)
        self.mainLayout.addStretch()
        
        self.update()
        
        self.mnemonique.textChanged.connect(self.mnemoniqueChange)
        self.addReceptBtn.clicked.connect(self.addReceptClick)
        self.supprReceptBtn.clicked.connect(self.supprReceptClick)
    
    def update(self):
        self.mnemonique.setText(self.ouvrage.mnemonique)
        self.recepteursTab.clear()
        for recept in self.ouvrage.recepteurs:
            recepteurWidget = RecepteurWidget(self, recept)
            self.recepteursTab.addTab(recepteurWidget, QtGui.QIcon(I.DEP_32), recept.mnemonique)
            recepteurWidget.recepteurChanged.connect(self.recepteurChange)
        if  self.recepteursTab.count() == 0:
             self.supprReceptBtn.setEnabled(False)
        else:
            self.supprReceptBtn.setEnabled(True)

    def recepteurChange(self):
        self.ouvrageChanged.emit()
    
    def mnemoniqueChange(self, value):
        if self.ouvrage is not None:
            self.ouvrage.mnemonique = value
            self.ouvrageChanged.emit()
            
    def addReceptClick(self):
        recept = t.Recepteur(self.ouvrage)
        if self.recepteursTab.currentWidget() is not None:
            recept = copy.copy(self.recepteursTab.currentWidget().recepteur)
        recept.mnemonique = gs.INDICE[len(self.ouvrage.recepteurs)]
        self.ouvrage.recepteurs.append(recept)    
        self.update()
        self.ouvrageChanged.emit()
        
    def supprReceptClick(self):
        recept = self.recepteursTab.currentWidget().recepteur
        self.ouvrage.recepteurs.remove(recept)
        self.update()
        self.ouvrageChanged.emit()


class RecepteurWidget(QtGui.QWidget):
    recepteurChanged = Signal()
    
    def __init__(self, parent, recepteur):
        super(RecepteurWidget, self).__init__(parent)
        
        self.recepteur = recepteur
        
        self.type = QtGui.QLineEdit(self)
        self.type.setReadOnly(True)
        self.typeBtn = QtGui.QPushButton(QtGui.QIcon(I.OPEN_DB_32), u'...', self)
        typeHBox = QtGui.QHBoxLayout()
        typeHBox.addWidget(self.type)
        typeHBox.addWidget(self.typeBtn)
        
        self.phase = QtGui.QComboBox(self)
        conducteurs = self.recepteur.parent.phases
        if conducteurs[t.PH1]:
            self.phase.addItem(u'Mono - Ph1-N', t.PH1)
        if conducteurs[t.PH2]:
            self.phase.addItem(u'Mono - Ph2-N', t.PH2)
        if conducteurs[t.PH3]:
            self.phase.addItem(u'Mono - Ph3-N', t.PH3)
        
        self.typeGroup = QtGui.QGroupBox(u'Type personalisé', self)
        self.typeGroup.setCheckable(True)
                
        self.ib = QtGui.QDoubleSpinBox(self)
        self.ib.setSuffix(u'A')
        self.ib.setSingleStep(.01)
        self.ib.setDecimals(2)
        self.ib.setMinimum(0.)
        self.ia = QtGui.QDoubleSpinBox(self)
        self.ia.setSuffix(u'A')
        self.ia.setSingleStep(.01)
        self.ia.setDecimals(2)
        self.ia.setMinimum(0.)
        self.cos = QtGui.QDoubleSpinBox(self)
        self.cos.setSingleStep(.05)
        self.cos.setDecimals(2)
        self.cos.setMinimum(0.)
        self.cos.setMaximum(1.)
        
        typeFormLayout = QtGui.QFormLayout(self)
        typeFormLayout.addRow(u'Ib', self.ib)
        typeFormLayout.addRow(u'Ia (Allumage)', self.ia)
        typeFormLayout.addRow(u'Cos phi', self.cos)
        self.typeGroup.setLayout(typeFormLayout)
                
        formLayout = QtGui.QFormLayout(self)
        formLayout.addRow(u'Type', typeHBox)
        formLayout.addRow(u'Phase', self.phase)
        formLayout.addRow(self.typeGroup)
        
        self.setLayout(formLayout)
        
        self.update()
        
        self.typeBtn.clicked.connect(self.typeSelect)
        self.type.textChanged.connect(self.typeChange)
        self.phase.currentIndexChanged.connect(self.phaseChange)
        self.ib.valueChanged.connect(self.ibChange)
        self.ia.valueChanged.connect(self.iaChange)
        self.cos.valueChanged.connect(self.cosChange)
        self.typeGroup.toggled.connect(self.customType)
        
    def update(self):
        self.type.setText(self.recepteur.type)
        self.type.setReadOnly(not self.recepteur.custom)
        self.typeBtn.setEnabled(not self.recepteur.custom)
        if self.recepteur.custom:
            self.type.setStyleSheet(u'QLineEdit{background: white;}')
        else:
            self.type.setStyleSheet(u'QLineEdit{background: #dfe4f4;}')
        self.typeGroup.setChecked(self.recepteur.custom)
        self.phase.setCurrentIndex(self.phase.findData(self.recepteur.ph))
        self.ib.setValue(self.recepteur.ib)
        self.ia.setValue(self.recepteur.ia)
        self.cos.setValue(self.recepteur.cosfi)

    def typeSelect(self):
        typeDialog = td.TypeDialog(self)
        typeDialog.exec_()
        self.recepteurChanged.emit()
        self.update
    
    def customType(self, checked):
        self.type.setReadOnly(not checked)
        self.typeBtn.setEnabled(not checked)
        if checked:
            self.type.setStyleSheet(u'QLineEdit{background: white;}')
        else:
            self.type.setStyleSheet(u'QLineEdit{background: #dfe4f4;}')
        self.recepteur.custom = checked
    
    def typeChange(self, value):
        self.recepteur.type = value
        self.recepteurChanged.emit()
        
    def phaseChange(self, index):
        value = self.phase.itemData(index)
        self.recepteur.ph = value
        self.recepteurChanged.emit()
        
    def ibChange(self, value):
        self.recepteur.ib = value
        self.recepteurChanged.emit()
        
    def iaChange(self, value):
        self.recepteur.ia = value
        self.recepteurChanged.emit()
        
    def cosChange(self, value):
        self.recepteur.cosfi = value
        self.recepteurChanged.emit()


class ConducteurWidget(QtGui.QWidget):
    conducteurChanged = Signal()
    
    def __init__(self, parent, conducteur):
        super(ConducteurWidget, self).__init__(parent)
        
        self.conducteur = conducteur
        
        self.mainLayout = QtGui.QVBoxLayout(self)
        
        self.mnemonique = QtGui.QLineEdit(self)
        
        self.longueur = QtGui.QDoubleSpinBox(self)
        self.longueur.setSuffix(u'm')
        self.longueur.setMinimum(0.)
        self.longueur.setSingleStep(.5)
        self.longueur.setDecimals(1)
        
        self.type = QtGui.QLineEdit(self)
        self.type.setReadOnly(True)
        self.typeBtn = QtGui.QPushButton(QtGui.QIcon(I.OPEN_DB_32), u'...', self)
        typeHBox = QtGui.QHBoxLayout()
        typeHBox.addWidget(self.type)
        typeHBox.addWidget(self.typeBtn)
        
        self.typeGroup = QtGui.QGroupBox(u'Type personalisé', self)
        self.typeGroup.setCheckable(True)
                
        self.matiere = QtGui.QComboBox(self)
        self.matiere.addItem(QtGui.QIcon(I.CUIVRE_16), u'Cuivre', t.CUIVRE)
        self.matiere.addItem(QtGui.QIcon(I.ALUMINIUM_16), u'Aluminium', t.ALUMINIUM)
        self.isolant = QtGui.QComboBox(self)
        self.isolant.addItem(u'PVC', True)
        self.isolant.addItem(u'PR', False)
        
        typeFormLayout = QtGui.QFormLayout(self)
        typeFormLayout.addRow(u'Matière de l\'âme', self.matiere)
        typeFormLayout.addRow(u'Isolant', self.isolant)
        self.typeGroup.setLayout(typeFormLayout)
        
        self.pose = QtGui.QComboBox(self)
        self.pose.addItem(u'Sous foureau', 1)
        self.pose.addItem(u'Pleine terre', 2)
        self.pose.addItem(u'Aérien', 3)
        
        self.section = QtGui.QDoubleSpinBox(self)
        self.section.setSuffix(u'mm²')
        self.section.setMinimum(0.1)
        self.section.setSingleStep(1)
        self.section.setDecimals(1)
        
        self.hasPE = QtGui.QCheckBox(u'Conducteur de protection intégré', self)
        
        self.composition = QtGui.QComboBox(self)
        conducteurs = self.conducteur.parent.parent.phases
        if all(conducteurs):
            self.composition.addItem(u'Tri - 3Ph+N', list([True,True,True,True]))
        if conducteurs[t.PH1]:
            self.composition.addItem(u'Mono - Ph1+N', list([True,False,False,True]))
        if conducteurs[t.PH2]:
            self.composition.addItem(u'Mono - Ph2+N', list([False,True,False,True]))
        if conducteurs[t.PH3]:
            self.composition.addItem(u'Mono - Ph3+N', list([False,False,True,True]))
        
        formLayout = QtGui.QFormLayout(self)
        formLayout.addRow(u'Mnemonique', self.mnemonique)
        formLayout.addRow(u'Longueur', self.longueur)
        formLayout.addRow(u'Type', typeHBox)
        formLayout.addRow(self.typeGroup)
        formLayout.addRow(u'Mode de pose', self.pose)
        formLayout.addRow(u'Section', self.section)
        formLayout.addRow(self.hasPE)
        formLayout.addRow(u'Phases', self.composition)
        
        ouvrageGroup = QtGui.QGroupBox(u'Conducteur')
        ouvrageGroup.setLayout(formLayout)
        self.mainLayout.addWidget(ouvrageGroup)
        self.mainLayout.addStretch()
        
        self.update()
        
        self.typeBtn.clicked.connect(self.typeSelect)
        self.mnemonique.textChanged.connect(self.mnemoniqueChange)
        self.type.textChanged.connect(self.typeChange)
        self.longueur.valueChanged.connect(self.longueurChange)
        self.matiere.currentIndexChanged.connect(self.matiereChange)
        self.isolant.currentIndexChanged.connect(self.isolantChange)
        self.hasPE.clicked.connect(self.peChange)
        self.section.valueChanged.connect(self.sectionChange)
        self.composition.currentIndexChanged.connect(self.phaseChange)
        self.typeGroup.toggled.connect(self.customType)
        
    def update(self):
        self.mnemonique.setText(self.conducteur.mnemonique)
        self.type.setText(self.conducteur.famille)
        self.type.setReadOnly(not self.conducteur.custom)
        self.typeBtn.setEnabled(not self.conducteur.custom)
        if self.conducteur.custom:
            self.type.setStyleSheet(u'QLineEdit{background: white;}')
        else:
            self.type.setStyleSheet(u'QLineEdit{background: #dfe4f4;}')
        self.typeGroup.setChecked(self.conducteur.custom)
        self.longueur.setValue(self.conducteur.longueur)
        self.matiere.setCurrentIndex(self.matiere.findData(self.conducteur.rho0))
        self.isolant.setCurrentIndex(self.isolant.findData(self.conducteur.is_isolant_pvc))
        self.hasPE.setChecked(self.conducteur.conducteurs[t.PE])
        self.section.setValue(self.conducteur.s[t.PH1])
        conducteurs = self.conducteur.conducteurs[0:4]
        if all(conducteurs):
            self.composition.setCurrentIndex(self.composition.findData(list([True,True,True,True])))
        elif conducteurs[t.PH1]:
            self.composition.setCurrentIndex(self.composition.findData(list([True,False,False,True])))
        elif conducteurs[t.PH2]:
            self.composition.setCurrentIndex(self.composition.findData(list([False,True,False,True])))
        elif conducteurs[t.PH3]:
            self.composition.setCurrentIndex(self.composition.findData(list([False,False,True,True])))
    
    def typeSelect(self):
        #***
        self.conducteurChanged.emit()
        self.update
    
    def customType(self, checked):
        self.type.setReadOnly(not checked)
        self.typeBtn.setEnabled(not checked)
        if checked:
            self.type.setStyleSheet(u'QLineEdit{background: white;}')
        else:
            self.type.setStyleSheet(u'QLineEdit{background: #dfe4f4;}')
        self.conducteur.custom = checked
        
    def mnemoniqueChange(self, value):
        self.conducteur.mnemonique = value
        self.conducteurChanged.emit()
        
    def typeChange(self, value):
        self.conducteur.famille = value
        self.conducteurChanged.emit()

    def longueurChange(self, value):
        self.conducteur.longueur = value
        self.conducteurChanged.emit()
           
    def matiereChange(self, index):
        self.conducteur.rho0 = self.matiere.itemData(index)
        self.conducteurChanged.emit()
            
    def isolantChange(self, index):
        self.conducteur.is_isolant_pvc = self.isolant.itemData(index)
        self.conducteurChanged.emit()
           
    def sectionChange(self, value):
        self.conducteur.s[t.PH1] = value
        self.conducteur.s[t.PH2] = value
        self.conducteur.s[t.PH3] = value
        self.conducteur.s[t.N] = value
        self.conducteur.s[t.PE] = value
        self.conducteurChanged.emit()
        
    def peChange(self):
        value = self.hasPE.isChecked()
        self.conducteur.conducteurs[t.PE] = value
        self.conducteurChanged.emit()
           
    def phaseChange(self, index):
        value = self.composition.itemData(index)
        self.conducteur.conducteurs[0:4] = value
        if not all(value):
            tree = self.conducteur.parent.tree
            currentOvrage = self.conducteur.parent
            phase = 0
            if value[t.PH1]:
                phase = t.PH1
            elif value[t.PH2]:
                phase = t.PH2
            elif value[t.PH3]:
                phase = t.PH3
            for recept in currentOvrage.recepteurs:
                    recept.ph = phase
            for child in tree.childs_of(currentOvrage):
                child.conducteur.conducteurs[0:4] = value
                for recept in child.recepteurs:
                    recept.ph = phase
        self.conducteurChanged.emit()


class OuvragePanel(QtGui.QTabWidget):
    ouvrageChanged = Signal()
    
    def __init__(self, parent, ouvrage):
        super(OuvragePanel, self).__init__(parent)
        
        self.ouvrageWidget = OuvrageWidget(self, ouvrage)
        
        self.addTab(self.ouvrageWidget, QtGui.QIcon(I.EDIT_32), u'Edition')

        self.ouvrageWidget.ouvrageChanged.connect(self.valueChange)
    
    def size(self):
        return QtCore.QSize(PANEL_WIDTH,100)
    
    def valueChange(self):
        self.ouvrageChanged.emit()


class ConducteurPanel(QtGui.QTabWidget):
    conducteurChanged = Signal()
    
    def __init__(self, parent, conducteur):
        super(ConducteurPanel, self).__init__(parent)
        
        self.conducteurWidget = ConducteurWidget(self, conducteur)
        
        self.addTab(self.conducteurWidget, QtGui.QIcon(I.EDIT_32), u'Edition')

        self.conducteurWidget.conducteurChanged.connect(self.valueChange)
    
    def size(self):
        return QtCore.QSize(PANEL_WIDTH,100)
    
    def valueChange(self):
        self.conducteurChanged.emit()


class DepartPanel(QtGui.QTabWidget):
    departChanged = Signal()
    
    def __init__(self, parent, depart):
        super(DepartPanel, self).__init__(parent)
        
        #self.departWidget = DepartWidget(self, depart)
        self.departWidget = QtGui.QWidget(self)
        
        self.addTab(self.departWidget, QtGui.QIcon(I.EDIT_32), u'Edition')
        #self.departWidget.conducteurChanged.connect(self.valueChange)
    
    def size(self):
        return QtCore.QSize(PANEL_WIDTH,100)
    
    def valueChange(self):
        self.departChanged.emit()

        
class EditPanel(QtGui.QDockWidget):
    valueChanged = Signal()
    
    def __init__(self, title, parent):
        super(EditPanel, self).__init__(title, parent)
        
        self.defaultWidget = QtGui.QLabel(u'Selectionnez un élément')
        self.defaultWidget.setMinimumSize(QtCore.QSize(PANEL_WIDTH,100))
        self.defaultWidget.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.setWidget(self.defaultWidget)
    
    def setItem(self, item):
        if isinstance(item, gs.OuvrageItem):
            widget = OuvragePanel(self, item.ouvrage)
            self.setWidget(widget)
            widget.ouvrageChanged.connect(self.itemChange)
        elif isinstance(item, gs.CableItem):
            widget = ConducteurPanel(self, item.conducteur)
            self.setWidget(widget)
            widget.conducteurChanged.connect(self.itemChange)
        elif isinstance(item, gs.DepartItem):
            widget = DepartPanel(self, item.depart)
            self.setWidget(widget)
            widget.departChanged.connect(self.itemChange)
        else:
            self.setWidget(self.defaultWidget)
    
    def itemChange(self):
        self.valueChanged.emit()