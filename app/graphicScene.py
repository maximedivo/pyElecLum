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
import copy

from PySide import QtCore, QtGui

import tree as t
import icons as I

INDICE = [u'A', u'B', u'C', u'D', u'E', u'F', u'G', u'H', u'I', u'J', u'K', u'L', u'M', \
          u'N', u'O', u'P', u'Q', u'R', u'S', u'T', u'U', u'V', u'W', u'X', u'Y', u'Z']

Z_IN_MAX = 10
Z_OUT_MAX = -10
Z_FACTOR = 1.075

class Node(QtGui.QGraphicsItem):
    Type = QtGui.QGraphicsItem.UserType + 1
    edited = QtCore.Signal()
    
    def __init__(self, x, y):
        QtGui.QGraphicsItem.__init__(self)

        #self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        #self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
        self.setCacheMode(self.DeviceCoordinateCache)
        self.setAcceptHoverEvents(True)
        self.setZValue(1)
        self.setPos(x,y)
       
    def update(self, rect=QtCore.QRectF()):
        self.setToolTip(self.getToolTip())
        QtGui.QGraphicsItem.update(self, rect)
    
    def shape(self):
        path = QtGui.QPainterPath()
        path.addRect(self.boundingRect())
        return path
    
    def hoverEnterEvent(self, event):
        print u'Node hover'
        self.update()
        event.accept()
        QtGui.QGraphicsItem.hoverEnterEvent(self, event)
    
    def mousePressEvent(self, event):
        self.update()
        print "Node pressed"
        event.accept()
        QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.update()
        print "Node released"
        event.accept()
        QtGui.QGraphicsItem.mouseReleaseEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        self.update()
        print "Node double click"
        event.accept()
        QtGui.QGraphicsItem.mouseDoubleClickEvent(self, event)

    def paint(self, painter, option, widget):
        if self.isSelected():
            painter.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
            painter.setPen(QtGui.QPen(QtCore.Qt.red, 1, s=QtCore.Qt.DashLine))
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
            newOuvrage.conducteur = copy.copy(self.ouvrage.conducteur)
            newOuvrage.conducteur.conducteurs = copy.copy(self.ouvrage.conducteur.conducteurs)
            newOuvrage.conducteur.s = copy.copy(self.ouvrage.conducteur.s)
            newOuvrage.conducteur.mnemonique = u'c{0}'.format(self.ouvrage.tree.nb)
            newOuvrage.recepteurs = list()
            for recept in self.ouvrage.recepteurs :
                newOuvrage.recepteurs.append(copy.copy(recept))
            self.ouvrage.tree.append(newOuvrage)
            self.scene().edit()
            # self.scene().redraw_()
        elif selectedAction == supprAction:
            parent = self.ouvrage.parent
            for child in self.ouvrage.tree.direct_childs_of(self.ouvrage):
                child.parent = parent
            self.ouvrage.parent = None
            self.ouvrage.tree.remove(self.ouvrage)
            self.scene().edit()
            # self.scene().redraw_()
        
    def boundingRect(self):
        dchar = len(self.ouvrage.mnemonique) * 7 + 5
        nb_recept = len(self.ouvrage.recepteurs)
        dx = 20
        x0 = -(nb_recept - 1) * dx / 2
        if nb_recept > 0:
            return QtCore.QRectF(-11 + x0, -11, 21 - x0 * nb_recept + dchar, 21)
        else:
            return QtCore.QRectF(-11, -11, 21 + dchar, 21)

    def paint(self, painter, option, widget):
        
        gradient = QtGui.QRadialGradient(0, 0, 22)
        color = QtCore.Qt.black
        gradient.setColorAt(1, QtGui.QColor(255, 128, 0, 255))
        painter.setBrush(QtGui.QBrush(gradient))
        painter.setPen(QtGui.QPen(color, 1))
        
        nb_recept = len(self.ouvrage.recepteurs)
        dx = 20
        x0 = -(nb_recept - 1) * dx / 2
        
        if nb_recept == 0:
            gradient.setColorAt(1, QtGui.QColor(128, 128, 128, 255))
            painter.setBrush(QtGui.QBrush(gradient))
            painter.drawRect(-6, -6, 12, 12)
            painter.setFont(QtGui.QFont(u'Verdana', 8))
            painter.drawText(QtCore.QPointF(15 , 0), self.ouvrage.mnemonique)
        else:
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
        tooltip = u'<b>{}</b><br/>'.format(self.ouvrage.mnemonique)
        tooltip += u'<b>DU%b:</b> {0:.2f}%, {1:.2f}%, {2:.2f}%<br/>'.format(self.ouvrage.dub[t.PH1]/2.30, self.ouvrage.dub[t.PH2]/2.30, self.ouvrage.dub[t.PH3]/2.30)
        tooltip += u'<b>DU%a:</b> {0:.2f}%, {1:.2f}%, {2:.2f}%<br/>'.format(self.ouvrage.dua[t.PH1]/2.30, self.ouvrage.dua[t.PH2]/2.30, self.ouvrage.dua[t.PH3]/2.30)
        tooltip += u'<b>Ikmin:</b> {0:.3f}kA<br/>'.format(self.ouvrage.ikmin)
        tooltip += u'<b>Rcph-n:</b> {0:.2f}m\u03A9<br/><b>Xcph-n:</b> {1:.2f}m\u03A9'.format(self.ouvrage.source.rs + self.ouvrage.rcphn(self.ouvrage.tree.protection.rho), self.ouvrage.source.xs + self.ouvrage.xcphn())
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
            newOuvrage.conducteur.mnemonique = u'c{0}'.format(self.depart.nb)
            self.depart.append(newOuvrage)
            self.scene().edit()
            # self.scene().redraw_() 
            
    def boundingRect(self):
        dchar = len(self.depart.mnemonique) * 6
        return QtCore.QRectF(-20, -30, 40 + dchar, 60)

    def paint(self, painter, option, widget):
        color = QtCore.Qt.black
        if not self.depart.is_conforme():
            color = QtCore.Qt.red
        painter.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
        painter.setPen(QtGui.QPen(color, 1))

        painter.drawLine(QtCore.QLineF(0, -30, 0, -10))
        painter.drawLine(QtCore.QLineF(0, 30, 0, 10))
        painter.drawLine(QtCore.QLineF(0, 10, -10, -10))
        
        painter.setFont(QtGui.QFont(u'Verdana', 8))
        painter.drawText(QtCore.QPointF(15,0), self.depart.mnemonique)
        painter.drawText(QtCore.QPointF(15,15), u'{0}{1:.0f}A'.format(self.courbe(), self.depart.protection.inom))
        
        if self.depart.protection.type == t.FUSIBLE:
            painter.drawLine(QtCore.QLineF(-5, -10, 5, -10))

            painter.drawLine(QtCore.QLineF(0, 5, -5, -5))
            painter.drawLine(QtCore.QLineF(-5, -5, -9, -3))
            painter.drawLine(QtCore.QLineF(-9, -3, -4, 7))
            painter.drawLine(QtCore.QLineF(-4, 7, 0, 5))
        elif self.depart.protection.type == t.DISJONCTEUR:
            painter.drawLine(QtCore.QLineF(-3, -7, 3, -13))
            painter.drawLine(QtCore.QLineF(-3, -13, 3, -7))
            if self.depart.protection.is_diff :
                painter.drawEllipse(-10, 15, 20, 10)
                painter.drawLine(QtCore.QLineF(-10, 20, -20, 20))
                painter.drawLine(QtCore.QLineF(-20, 20, -20, 0))
                painter.drawLine(QtCore.QLineF(-20, 0, -5, 0))
                painter.drawText(QtCore.QPointF(15,30), u'{0:.0f}mA'.format(self.depart.protection.idn * 1000))
        
        super(DepartItem, self).paint(painter, option, widget)
    
    def getToolTip(self):
        tooltip = u'<b>{}</b><br/>'.format(self.depart.mnemonique)
        tooltip += u'<b>IB:</b> {0:.2f}A, {1:.2f}A, {2:.2f}A<br/>'.format(self.depart.ib[t.PH1], self.depart.ib[t.PH2], self.depart.ib[t.PH3])
        tooltip += u'<b>IA:</b> {0:.2f}A, {1:.2f}A, {2:.2f}A<br/>'.format(self.depart.ia[t.PH1], self.depart.ia[t.PH2], self.depart.ia[t.PH3])
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
        # self.setCacheMode(self.DeviceCoordinateCache)
        self.setAcceptHoverEvents(True)
        self.setZValue(0)

        self.parent = parent
        self.child = child
        
        self.conducteur = conducteur

    def boundingRect(self):
        pt1 = QtCore.QPointF(min(self.parent.parentSlot().x(), self.child.childSlot().x()) - 10, min(self.parent.parentSlot().y(), self.child.childSlot().y()) - 5)
        pt2 = QtCore.QPointF(max(self.parent.parentSlot().x(), self.child.childSlot().x()) + 75, max(self.parent.parentSlot().y(), self.child.childSlot().y()) + 5)
        return QtCore.QRectF(pt1, pt2)
    
    def shape(self):
        path = QtGui.QPainterPath()
        
        ptInt = self.parent.parentSlot() - self.child.childSlot()
        ptInt.setX(0)
        ptInt += self.child.childSlot()
        path.addRect(QtCore.QRectF(self.parent.parentSlot(), ptInt).adjusted(-10,-5,15,5))
        path.addRect(QtCore.QRectF(ptInt, self.child.childSlot()).adjusted(-10,-5,15,5))
                     
        return path
    
    def hoverEnterEvent(self, event):
        self.update()
        event.accept()
        QtGui.QGraphicsItem.hoverEnterEvent(self, event)
    
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
        if self.isSelected():
            pen = painter.pen()
            pen.setStyle(QtCore.Qt.DotLine)
            painter.setPen(pen)
        painter.drawLine(self.parent.parentSlot(), ptInt)
        painter.drawLine(ptInt, self.child.childSlot())
        
        y_step = 6
        pt0 = ptInt + (self.child.childSlot() - ptInt) / 2
        
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
        painter.setBrush(QtGui.QBrush(QtCore.Qt.black))
        painter.setFont(QtGui.QFont(u'Verdana', 7, italic=True))
        painter.drawText(pt0 + QtCore.QPointF(15,-8), u'{0}'.format(self.conducteur.famille))
        painter.drawText(pt0 + QtCore.QPointF(15,0), u'{0}'.format(self.conducteur.descr))
        painter.drawText(pt0 + QtCore.QPointF(15,8), u'{0:.1f}m'.format(self.conducteur.longueur))
        
        pt0.setY(pt0.y() - (y_step * self.conducteur.nb_conduc) / 2)
        for conduc, is_ in enumerate(self.conducteur.conducteurs):
            if is_:
                pt1 = pt0 + QtCore.QPointF(-5, 3)
                pt2 = pt0 + QtCore.QPointF(5, -3)
                painter.drawLine(pt1, pt2)
                if conduc == t.N:
                    painter.drawEllipse(QtCore.QRectF(pt2 + QtCore.QPointF(0, -3), pt2 + QtCore.QPointF(3, 0)))
                elif conduc == t.PE:
                    painter.drawLine(pt2 + QtCore.QPointF(1, -3), pt2 + QtCore.QPointF(1, 3))
                else:
                    painter.setFont(QtGui.QFont(u'Verdana', 5, italic=False))
                    pta = pt2 + QtCore.QPointF(2, 0)

                    painter.drawText(pta, u'{0}'.format(conduc+1))
                pt0 += QtCore.QPointF(0, y_step)
        
    def getToolTip(self):
        tooltip = u'<b>{}</b><br/>'.format(self.conducteur.mnemonique)
        tooltip += u'<b>IB:</b> {0:.2f}A, {1:.2f}A, {2:.2f}A<br/>'.format(self.conducteur.ib[t.PH1], self.conducteur.ib[t.PH2], self.conducteur.ib[t.PH3])
        tooltip += u'<b>IA:</b> {0:.2f}A, {1:.2f}A, {2:.2f}A<br/>'.format(self.conducteur.ia[t.PH1], self.conducteur.ia[t.PH2], self.conducteur.ia[t.PH3])
        if self.conducteur.is_conforme():
            tooltip += u'<font color="green"><b>Conforme</b></font>'
        else:
            tooltip += u'<font color="red"><b>Non Conforme</b></font>'
        return tooltip
        

class DepartScene(QtGui.QGraphicsScene):
    edited = QtCore.Signal()
    
    def __init__(self, parent, depart):
        QtGui.QGraphicsScene.__init__(self, parent)
        self._depart = depart
        self.redraw_()
    
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
    
    def edit(self):
        self.edited.emit()
        self.redraw_()
    
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


class DepartView(QtGui.QGraphicsView):

    def __init__(self, parent):
        QtGui.QGraphicsView.__init__(self, parent)
        self.setRenderHints(QtGui.QPainter.Antialiasing|QtGui.QPainter.TextAntialiasing|QtGui.QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)
        
        # self.setTransformationAnchor(QtGui.QGraphicsView.NoAnchor)
        # self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setSceneRect(-5000, -5000, 20000, 20000) 
        
        
        self.zoom = 0
        
        self.pan = False
        self.lastPos = QtCore.QPoint()

    def setScene(self, scene):
        QtGui.QGraphicsView.setScene(self, scene)
        self.centerOn(0,0)

    def resizeEvent(self, event):
        self.centerOn(0,0)
        
    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.MidButton:
            self.zoomReset()
            event.accept()
        else:
            QtGui.QGraphicsView.mouseDoubleClickEvent(self, event)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            #Debug print "Move start"
            self.lastPos = event.pos()
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            self.setTransformationAnchor(QtGui.QGraphicsView.NoAnchor)
            self.pan = True
            event.accept()
        QtGui.QGraphicsView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.pan:
            delta = (event.pos() - self.lastPos) / (Z_FACTOR ** self.zoom)
            self.translate(delta.x(), delta.y())
            self.lastPos = event.pos()
            event.accept()
        QtGui.QGraphicsView.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            #Debug print "Move end"
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.setTransformationAnchor(QtGui.QGraphicsView.AnchorViewCenter)
            self.pan = False
            event.accept()
        QtGui.QGraphicsView.mouseReleaseEvent(self, event)

    def wheelEvent(self, event):
        if event.modifiers() == QtCore.Qt.ControlModifier:
            self.zoom += event.delta() / 120
            if self.zoom >= Z_OUT_MAX and self.zoom <= Z_IN_MAX:
                #Debug print u'Wheel Z={0} f={1}'.format(self.zoom, self.facteur)
                self.resetTransform()
                self.scale(self.facteur, self.facteur)
                event.accept()
            else:
                if self.zoom > 0:
                    self.zoom = Z_IN_MAX
                else:
                    self.zoom = Z_OUT_MAX
                event.ignore()
        else:
            QtGui.QGraphicsView.wheelEvent(self, event)

    def zoomReset(self):
        self.resetTransform()
        self.zoom = 0
        self.centerOn(0,0)

    @property
    def facteur(self):
        return Z_FACTOR ** self.zoom

        
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
