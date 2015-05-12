#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = u'Maxime DIVO'
__copyright__ = u'Copyright 2015, Maxime DIVO'
__credits__ = [u'Maxime DIVO']

__license__ = u'GPL v3'
__version__ = u'0.9.1'
__maintainer__ = u'Maxime DIVO'
__email__ = u'maxime.divo@gmail.com'
__status__ = u'Development'

import sys
import math

from PySide import QtCore, QtGui

import Tree as t
import Icons as I

INDICE = [u'A', u'B', u'C', u'D', u'E', u'F', u'G', u'H', u'I', u'J', u'K', u'L', u'M', \
          u'N', u'O', u'P', u'Q', u'R', u'S', u'T', u'U', u'V', u'W', u'X', u'Y', u'Z']


class Node(QtGui.QGraphicsItem):
    Type = QtGui.QGraphicsItem.UserType + 1
    
    def __init__(self, x, y):
        QtGui.QGraphicsItem.__init__(self)

        #self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setCacheMode(self.DeviceCoordinateCache)
        self.setZValue(1)
        self.setPos(x,y)
       
    def update(self, rect=QtCore.QRectF()):
        self.setToolTip(self.getToolTip())
        QtGui.QGraphicsItem.update(self, rect)
    
    def mousePressEvent(self, event):
        self.update()
        print "Node pressed"
        QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.update()
        print "Node released"
        QtGui.QGraphicsItem.mouseReleaseEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        self.update()
        print "Node double click"
        QtGui.QGraphicsItem.mouseDoubleClickEvent(self, event)

    def paint(self, painter, option, widget):
        if self.isSelected ():
            painter.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 0, s=QtCore.Qt.DashLine))
            painter.drawRect(self.boundingRect())

    def _parentSlot(self):
        return QtCore.QPointF(0,0)

    def _childSlot(self):
        return QtCore.QPointF(0,0)

    def parentSlot(self):
        return self._parentSlot() + self.pos()

    def childSlot(self):
        return self._childSlot() + self.pos()

        
class OuvrageItem(Node):

    def __init__(self, ouvrage, x, y):
        super(OuvrageItem, self).__init__(x,y)

        self.ouvrage = ouvrage

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu()
        addAction = menu.addAction(QtGui.QIcon(I.ADD_32), u'Ajouter un ouvrage')
        supprAction = menu.addAction(QtGui.QIcon(I.SUP_32), u'Supprimer l\'ouvrage')
        selectedAction = menu.exec_(event.screenPos())
        if selectedAction == addAction:
            self.ouvrage.tree.nb += 1
            newOuvrage = t.Ouvrage(u'EP{0}'.format(self.ouvrage.tree.nb), self.ouvrage)
            self.ouvrage.tree.append(newOuvrage)
            self.scene().redraw_()
        elif selectedAction == supprAction:
            parent = self.ouvrage.parent
            for child in self.ouvrage.tree.direct_childs_of(self.ouvrage):
                child.parent = parent
            self.ouvrage.parent = None
            self.ouvrage.tree.remove(self.ouvrage)
            self.scene().redraw_()
        
    def boundingRect(self):
        dchar = len(self.ouvrage.mnemonique) * 7 + 5
        nb_recept = len(self.ouvrage.recepteurs)
        dx = 20
        x0 = -(nb_recept - 1) * dx / 2
        return QtCore.QRectF(-10 + x0, -10, 20 - x0 * nb_recept + dchar, 20)

    def paint(self, painter, option, widget):
        
        gradient = QtGui.QRadialGradient(0, 0, 22)
        color = QtCore.Qt.black
        gradient.setColorAt(1, QtGui.QColor(255, 128, 0, 255))
        painter.setBrush(QtGui.QBrush(gradient))
        painter.setPen(QtGui.QPen(color, 1))
        
        nb_recept = len(self.ouvrage.recepteurs)
        dx = 20
        x0 = -(nb_recept - 1) * dx / 2
        
        for id, recept in enumerate(self.ouvrage.recepteurs):
            recept.mnemonique = INDICE[id]
            x = x0 + dx * id
            painter.drawEllipse(-10 + x, -10, 20, 20)
            painter.setFont(QtGui.QFont(u'Verdana', 7))
            painter.drawText(-10 + x, -10, 20, 15, QtCore.Qt.AlignCenter, recept.mnemonique)
            painter.setFont(QtGui.QFont(u'Verdana', 7))
            painter.drawText(-10 + x, 0, 20, 10, QtCore.Qt.AlignCenter, u'L{0}'.format(recept.ph+1))
        
        painter.setFont(QtGui.QFont(u'Verdana', 8))
        painter.drawText(QtCore.QPointF(15 - x0 , 0), self.ouvrage.mnemonique)
        
        super(OuvrageItem, self).paint(painter, option, widget)
    
    def getToolTip(self):
        tooltip = self.ouvrage.mnemonique + u'\n'
        tooltip += u'DU%b: {0:.2f}%, {1:.2f}%, {2:.2f}%\n'.format(self.ouvrage.dub[t.PH1]/2.30, self.ouvrage.dub[t.PH2]/2.30, self.ouvrage.dub[t.PH3]/2.30)
        tooltip += u'DU%a: {0:.2f}%, {1:.2f}%, {2:.2f}%\n'.format(self.ouvrage.dua[t.PH1]/2.30, self.ouvrage.dua[t.PH2]/2.30, self.ouvrage.dua[t.PH3]/2.30)
        tooltip += u'Ikmin: {0:.3f}kA\n'.format(self.ouvrage.ikmin)
        tooltip += u'Rcph-n: {0:.2f}m\u03A9\nXcph-n: {1:.2f}m\u03A9'.format(self.ouvrage.source.rs + self.ouvrage.rcphn(self.ouvrage.tree.protection.rho), self.ouvrage.source.xs + self.ouvrage.xcphn())
        return tooltip
    
    def _parentSlot(self):
        return QtCore.QPointF(0,10)

    def _childSlot(self):
        return QtCore.QPointF(0,-10)


class DepartItem(Node):

    def __init__(self, depart, x, y):
        super(DepartItem, self).__init__(x,y)
        
        self.depart = depart
        
    def courbe(self):
        courbe = self.depart.protection.courbe
        if courbe == t.B:
            return u'B'
        elif courbe == t.C:
            return u'C'
        elif courbe == t.D:
            return u'D'

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu()
        addAction = menu.addAction(QtGui.QIcon(I.ADD_32), u'Ajouter un ouvrage')
        selectedAction = menu.exec_(event.screenPos())
        if selectedAction == addAction:
            self.depart.nb += 1
            newOuvrage = t.Ouvrage(u'EP{0}'.format(self.depart.nb), self.depart)
            self.depart.append(newOuvrage)
            self.scene().redraw_()        
            
    def boundingRect(self):
        dchar = len(self.depart.mnemonique) * 6
        return QtCore.QRectF(-20, -30, 40 + dchar, 60)

    def paint(self, painter, option, widget):
        color = QtCore.Qt.black
        if not self.depart.is_conforme():
            color = QtCore.Qt.red
        painter.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
        painter.setPen(QtGui.QPen(color, 0))

        painter.drawLine(QtCore.QLineF(0, -30, 0, -10))
        painter.drawLine(QtCore.QLineF(0, 30, 0, 10))
        painter.drawLine(QtCore.QLineF(0, 10, 10, -10))
        
        painter.setFont(QtGui.QFont(u'Verdana', 8))
        painter.drawText(QtCore.QPointF(15,0), self.depart.mnemonique)
        painter.drawText(QtCore.QPointF(15,15), u'{0}{1:.0f}A'.format(self.courbe(), self.depart.protection.inom))
        
        if self.depart.protection.type == t.FUSIBLE:
            painter.drawLine(QtCore.QLineF(-5, -10, 5, -10))

            painter.drawLine(QtCore.QLineF(0, 5, 5, -5))
            painter.drawLine(QtCore.QLineF(5, -5, 9, -3))
            painter.drawLine(QtCore.QLineF(9, -3, 4, 7))
            painter.drawLine(QtCore.QLineF(4, 7, 0, 5))
        elif self.depart.protection.type == t.DISJONCTEUR:
            painter.drawLine(QtCore.QLineF(-3, -7, 3, -13))
            painter.drawLine(QtCore.QLineF(-3, -13, 3, -7))
            if self.depart.protection.is_diff :
                painter.drawEllipse(-10, 15, 20, 10)
                painter.drawLine(QtCore.QLineF(-10, 20, -20, 20))
                painter.drawLine(QtCore.QLineF(-20, 20, -20, 0))
                painter.drawLine(QtCore.QLineF(-20, 0, 5, 0))
                painter.drawText(QtCore.QPointF(15,30), u'{0:.0f}mA'.format(self.depart.protection.idn * 1000))
        
        super(DepartItem, self).paint(painter, option, widget)
    
    def getToolTip(self):
        tooltip = self.depart.mnemonique + u'\n'
        tooltip += u'IB: {0:.2f}A, {1:.2f}A, {2:.2f}A\n'.format(self.depart.ib[t.PH1], self.depart.ib[t.PH2], self.depart.ib[t.PH3])
        tooltip += u'IA: {0:.2f}A, {1:.2f}A, {2:.2f}A\n'.format(self.depart.ia[t.PH1], self.depart.ia[t.PH2], self.depart.ia[t.PH3])
        return tooltip
    
    def _parentSlot(self):
        return QtCore.QPointF(0, 30)

    def _childSlot(self):
        return QtCore.QPointF(0, -30)


class CableItem(QtGui.QGraphicsItem):
    Type = QtGui.QGraphicsItem.UserType + 2
    
    def __init__(self, conducteur, parent, child):
        QtGui.QGraphicsItem.__init__(self)
        #self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setCacheMode(self.DeviceCoordinateCache)
        self.setZValue(-1)

        self.parent = parent
        self.child = child
        
        self.conducteur = conducteur

    def boundingRect(self):
        pt1 = QtCore.QPointF(min(self.parent.parentSlot().x(), self.child.childSlot().x()) - 10, min(self.parent.parentSlot().y(), self.child.childSlot().y()) - 5)
        pt2 = QtCore.QPointF(max(self.parent.parentSlot().x(), self.child.childSlot().x()) + 60, max(self.parent.parentSlot().y(), self.child.childSlot().y()) + 5)
        self.update()
        return QtCore.QRectF(pt1, pt2)
    
    def shape(self):
        path = QtGui.QPainterPath()
        
        ptInt = self.parent.parentSlot() - self.child.childSlot()
        ptInt.setX(0)
        ptInt += self.child.childSlot()
        path.addRect(QtCore.QRectF(self.parent.parentSlot(), ptInt).adjusted(-10,-5,15,5))
        path.addRect(QtCore.QRectF(ptInt, self.child.childSlot()).adjusted(-10,-5,15,5))
                     
        return path
    
    def update(self, rect=QtCore.QRectF()):
        self.setToolTip(self.getToolTip())
        QtGui.QGraphicsItem.update(self, rect)
    
    def paint(self, painter, option, widget):
        ptInt = self.parent.parentSlot() - self.child.childSlot()
        ptInt.setX(0)
        ptInt += self.child.childSlot()
        if self.conducteur.is_conforme():
            painter.setPen(QtGui.QPen(QtCore.Qt.darkGreen, 2))
        else:
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 2))
        if self.hasFocus():
            pen = painter.pen()
            pen.setStyle(QtCore.Qt.DotLine)
            painter.setPen(pen)
        painter.drawLine(self.parent.parentSlot(), ptInt)
        painter.drawLine(ptInt, self.child.childSlot())
        
        y_step = 4
        pt0 = ptInt + (self.child.childSlot() - ptInt) / 2
        
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 0))
        painter.setFont(QtGui.QFont(u'Verdana', 7, italic=True))
        painter.drawText(pt0 + QtCore.QPointF(8,-8), u'{0}'.format(self.conducteur.famille))
        painter.drawText(pt0 + QtCore.QPointF(8,0), u'{0}'.format(self.conducteur.descr))
        painter.drawText(pt0 + QtCore.QPointF(8,8), u'{0:.1f}m'.format(self.conducteur.longueur))
        
        pt0.setY(pt0.y() - (y_step * self.conducteur.nb_conduc) / 2)
        for conduc, is_ in enumerate(self.conducteur.conducteurs):
            if is_:
                pt1 = pt0 + QtCore.QPointF(-5, 3)
                pt2 = pt0 + QtCore.QPointF(5, -3)
                painter.drawLine(pt1, pt2)
                if conduc == t.N:
                    painter.drawEllipse(QtCore.QRectF(pt2 + QtCore.QPointF(-1, -1), pt2 + QtCore.QPointF(1, 1)))
                elif conduc == t.PE:
                    painter.drawLine(pt2 + QtCore.QPointF(0, -1), pt2 + QtCore.QPointF(0, 1))
                pt0 += QtCore.QPointF(0, y_step)
        
    def getToolTip(self):
        tooltip = self.conducteur.mnemonique + u'\n'
        tooltip += u'IB: {0:.2f}A, {1:.2f}A, {2:.2f}A\n'.format(self.conducteur.ib[t.PH1], self.conducteur.ib[t.PH2], self.conducteur.ib[t.PH3])
        tooltip += u'IA: {0:.2f}A, {1:.2f}A, {2:.2f}A\n'.format(self.conducteur.ia[t.PH1], self.conducteur.ia[t.PH2], self.conducteur.ia[t.PH3])
        if self.conducteur.is_conforme():
            tooltip += u'Conforme'
        else:
            tooltip += u'Non Conforme'
        return tooltip
        

class DepartScene(QtGui.QGraphicsScene):
    
    def __init__(self, parent, depart):
        QtGui.QGraphicsScene.__init__(self, parent)
        self._depart = depart
        self.redraw_()
    
    '''def update(self, rect=QtCore.QRectF()):
        if isinstance(self._depart, t.Depart):
            print u'Ok'
        QtGui.QGraphicsScene.update(self, rect)'''
    
    def redraw_(self):
        self.clear()
        departItem = DepartItem(self._depart, 0, 0)
        self.addItem(departItem)
        self.ouvrageDraw(departItem, self.depart.root_items)
        
    def ouvrageDraw(self, parentItem, childList):
        x_step = 100
        y_step = 125
        x0 = parentItem.pos().x()
        x_offset = 0
        for child in childList :
            nb_child = child.tree.count_childs_intersecs(child)            
            x = x0 + x_offset
            ouvrage = OuvrageItem(child, x, y_step * (1 + child.level))
            self.addItem(ouvrage)
            self.addItem(CableItem(child.conducteur, parentItem, ouvrage))
            self.ouvrageDraw(ouvrage, self.depart.direct_childs_of(child))
            x_offset += x_step * nb_child + x_step
    
    @property
    def depart(self):
        return self._depart
    
    @depart.setter
    def depart(self, value):
        if isinstance(value, t.Depart):
            self._parent = value
            self.redraw_()
        else:
            raise ValueError(u'Depart must be a <class t.Depart> instance.')

        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    widget = QtGui.QGraphicsView()
    
    commande = t.Armoire()
    t = t.Depart(commande)
    it0 = t.Ouvrage(u'EP1', t)
    t.append(it0)
    last = it0
    ph = 1
    for i in range(8):
        it = t.Ouvrage(u'EP%i'%(i+2), last)
        for recept in it.recepteurs:
            recept.ph = ph
            ph = t.rotation_phase(ph)
        t.append(it)
        last = it
    
    scene = DepartScene(widget, t)
    scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)

    widget.setScene(scene)
    widget.show()
    sys.exit(app.exec_())
