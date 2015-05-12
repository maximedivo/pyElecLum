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

import Tree as t
import graphicScene as gs
import Icons as I

class OuvrageWidget(QtGui.QWidget):
    ouvrageChanged = Signal()
    
    def __init__(self, parent, ouvrage):
        super(OuvrageWidget, self).__init__(parent)
        
        self.ouvrage = ouvrage
        
        self.mainLayout = QtGui.QVBoxLayout(self)
        
        formLayout = QtGui.QFormLayout(self)
        self.mnemonique = QtGui.QLineEdit(self)
        self.mnemonique.setText(ouvrage.mnemonique)
        formLayout.addRow(u'Mnemonique', self.mnemonique)
        
        ouvrageGroup = QtGui.QGroupBox(u'Ouvrage')
        ouvrageGroup.setLayout(formLayout)
        self.mainLayout.addWidget(ouvrageGroup)
        
        self.mnemonique.textChanged.connect(self.mnemoniqueChange)
        
    def mnemoniqueChange(self, value):
        if self.ouvrage is not None:
            self.ouvrage.mnemonique = value
            self.ouvrageChanged.emit()

            
class RecepteursWidget(QtGui.QWidget):
    recepteursChanged = Signal()
    
    def __init__(self, parent, recepteurs):
        super(RecepteursWidget, self).__init__(parent)
        
        self.recepteurs = recepteurs
        
        self.mainLayout = QtGui.QVBoxLayout(self)
        
        self.listWidget = QtGui.QListWidget(self)
        for recept in self.recepteurs:
            item = QtGui.QListWidgetItem()
            item.setData(0, recept.mnemonique)
            item.setData(1, recept)
            self.listWidget.addItem(item)
        
        listLayout = QtGui.QVBoxLayout(self)
        listLayout.addWidget(self.listWidget)
        
        recepteursGroup = QtGui.QGroupBox(u'Récepteurs')
        recepteursGroup.setLayout(listLayout)
        self.mainLayout.addWidget(recepteursGroup)
        
        self.recepteurWidget = RecepteurWidget(self)
        self.mainLayout.addWidget(self.recepteurWidget)
        
        self.listWidget.currentItemChanged.connect(self.itemSelect)
        self.recepteurWidget.recepteurChanged.connect(self.recepteurChange)
    
    def itemSelect(self, item):
        recept = item.data(1)
        self.recepteurWidget.setRecepteur(recept)
        
    def recepteurChange(self):
        self.recepteursChanged.emit()
   
   
class RecepteurWidget(QtGui.QGroupBox):
    recepteurChanged = Signal()
    
    def __init__(self, parent, recepteur=None):
        super(RecepteurWidget, self).__init__(u'Edition', parent)
        
        self.mnemonique = QtGui.QLineEdit(self)
        self.type = QtGui.QLineEdit(self)
        self.phase = QtGui.QSpinBox(self)
        self.phase.setPrefix(u'Phase N°')
        self.phase.setMinimum(1)
        self.phase.setMaximum(3)
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
        
        formLayout = QtGui.QFormLayout(self)
        formLayout.addRow(u'Mnemonique', self.mnemonique)
        formLayout.addRow(u'Type', self.type)
        formLayout.addRow(u'Phase', self.phase)
        formLayout.addRow(u'Ib', self.ib)
        formLayout.addRow(u'Ia (Allumage)', self.ia)
        formLayout.addRow(u'Cos phi', self.cos)
        
        self.setLayout(formLayout)
           
        self.mnemonique.textChanged.connect(self.mnemoniqueChange)
        self.type.textChanged.connect(self.typeChange)
        self.phase.valueChanged.connect(self.phaseChange)
        self.ib.valueChanged.connect(self.ibChange)
        self.ia.valueChanged.connect(self.iaChange)
        self.cos.valueChanged.connect(self.cosChange)
        
        self.setRecepteur(recepteur)
        
    def setRecepteur(self, value):
        self.recepteur = value
        
        if self.recepteur is not None:
            self.mnemonique.setText(self.recepteur.mnemonique)
            self.type.setText(self.recepteur.type)
            self.phase.setValue(self.recepteur.ph + 1)
            self.ib.setValue(self.recepteur.ib)
            self.ia.setValue(self.recepteur.ia)
            self.cos.setValue(self.recepteur.cosfi)
            
            self.mnemonique.setEnabled(True)
            self.type.setEnabled(True)
            self.phase.setEnabled(True)
            self.ib.setEnabled(True)
            self.ia.setEnabled(True)
            self.cos.setEnabled(True)
        else:
            self.mnemonique.setEnabled(False)
            self.type.setEnabled(False)
            self.phase.setEnabled(False)
            self.ib.setEnabled(False)
            self.ia.setEnabled(False)
            self.cos.setEnabled(False)
    
    def mnemoniqueChange(self, value):
        self.recepteur.mnemonique = value
        self.recepteurChanged.emit()
        
    def typeChange(self, value):
        self.recepteur.type = value
        self.recepteurChanged.emit()
        
    def phaseChange(self, value):
        self.recepteur.ph = value - 1
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
        self.typeBtn = QtGui.QPushButton(u'...', self)
        typeHBox = QtGui.QHBoxLayout()
        typeHBox.addWidget(self.type)
        typeHBox.addWidget(self.typeBtn)
        
        self.typeGroup = QtGui.QGroupBox(u'Type personalisé', self)
        
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
        self.section.setMinimum(0.)
        self.section.setSingleStep(1)
        self.section.setDecimals(1)
        
        self.hasPE = QtGui.QCheckBox(u'Conducteur de protection intégré', self)
        
        formLayout = QtGui.QFormLayout(self)
        formLayout.addRow(u'Mnemonique', self.mnemonique)
        formLayout.addRow(u'Longueur', self.longueur)
        formLayout.addRow(u'Type', typeHBox)
        formLayout.addRow(self.typeGroup)
        formLayout.addRow(u'Mode de pose', self.pose)
        formLayout.addRow(u'Section', self.section)
        formLayout.addRow(self.hasPE)
        
        ouvrageGroup = QtGui.QGroupBox(u'Conducteur amont')
        ouvrageGroup.setLayout(formLayout)
        self.mainLayout.addWidget(ouvrageGroup)
        
        self.mnemonique.setText(self.conducteur.mnemonique)
        self.type.setText(self.conducteur.famille)
        self.longueur.setValue(self.conducteur.longueur)
        self.matiere.setCurrentIndex(self.matiere.findData(self.conducteur.rho0))
        self.isolant.setCurrentIndex(self.isolant.findData(self.conducteur.is_isolant_pvc))
        self.hasPE.setChecked(self.conducteur.conducteurs[t.PE])
        self.section.setValue(self.conducteur.s[t.PH1])
        
        self.mnemonique.textChanged.connect(self.mnemoniqueChange)
        self.type.textChanged.connect(self.typeChange)
        self.longueur.valueChanged.connect(self.longueurChange)
        self.matiere.currentIndexChanged.connect(self.matiereChange)
        self.isolant.currentIndexChanged.connect(self.isolantChange)
        self.hasPE.clicked.connect(self.peChange)
        self.section.valueChanged.connect(self.sectionChange)
        
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
           
    def phaseChange(self, value):
        self.conducteur.count_ph = value
        self.conducteurChanged.emit()
        
    
class OuvragePanel(QtGui.QTabWidget):
    ouvrageChanged = Signal()
    
    def __init__(self, parent, ouvrage):
        super(OuvragePanel, self).__init__(parent)
        
        self.ouvrageWidget = OuvrageWidget(self, ouvrage)
        self.recepteursWidget = RecepteursWidget(self, ouvrage.recepteurs)
        
        self.addTab(self.ouvrageWidget, QtGui.QIcon(I.DEP_32), u'Ouvrage')
        self.addTab(self.recepteursWidget, QtGui.QIcon(I.DEP_32), u'Récepteurs')

        self.ouvrageWidget.ouvrageChanged.connect(self.valueChange)
        self.recepteursWidget.recepteursChanged.connect(self.valueChange)
        
    def valueChange(self):
        self.ouvrageChanged.emit()


class EditPanel(QtGui.QDockWidget):
    valueChanged = Signal()
    
    def __init__(self, title, parent):
        super(EditPanel, self).__init__(title, parent)
        
        self.defaultWidget = QtGui.QLabel(u'Selectionnez un élément')
        self.setWidget(self.defaultWidget)
        
    def setItem(self, item):
        if isinstance(item, gs.OuvrageItem):
            widget = OuvragePanel(self, item.ouvrage)
            self.setWidget(widget)
            widget.ouvrageChanged.connect(self.itemChange)
        elif isinstance(item, gs.CableItem):
            widget = ConducteurWidget(self, item.conducteur)
            self.setWidget(widget)
            widget.conducteurChanged.connect(self.itemChange)
        else:
            self.setWidget(self.defaultWidget)
    
    def itemChange(self):
        self.valueChanged.emit()