import sys
import weakref
import math
from PySide import QtCore, QtGui



### 
class Edge(QtGui.QGraphicsItem):
    Type = QtGui.QGraphicsItem.UserType + 2

    def __init__(self, sourceNode, destNode):
        QtGui.QGraphicsItem.__init__(self)
        #
        self.sourcePoint = QtCore.QPointF()
        self.destPoint = QtCore.QPointF()
        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)
        self.source = weakref.ref(sourceNode)
        self.dest = weakref.ref(destNode)
        self.source().addEdge(self)
        self.dest().addEdge(self)
        self.set_index()
        self.adjust()

    def type(self):
        return Edge.Type

    def sourceNode(self):
        return self.source()

    def setSourceNode(self, node):
        self.source = weakref.ref(node)
        self.adjust()

    def destNode(self):
        return self.dest()

    def setDestNode(self, node):
        self.dest = weakref.ref(node)
        self.adjust()

    def set_index(self):
        self.setToolTip(self.source().label)

    def adjust(self):
        # do we have a line to draw ?
        if  self.source() and self.dest():
            line = QtCore.QLineF(self.mapFromItem(self.source(), 0, 0), self.mapFromItem(self.dest(), 0, 0))
            length = line.length()
            if length > 20:
                edgeOffset = QtCore.QPointF((line.dx() * 10) / length, (line.dy() * 10) / length)
                self.prepareGeometryChange()
                self.sourcePoint = line.p1() + edgeOffset
                self.destPoint   = line.p2() - edgeOffset
            else: # want to make sure line not drawn
                self.prepareGeometryChange()
                self.sourcePoint = self.destPoint 

    def boundingRect(self):
        # do we have a line to draw ?
        if not self.source() or not self.dest():
            return QtCore.QRectF()
        else:
            extra = 1
            return QtCore.QRectF(self.sourcePoint,
                                 QtCore.QSizeF(self.destPoint.x() - self.sourcePoint.x(),
                                               self.destPoint.y() - self.sourcePoint.y())).normalized().adjusted(-extra, -extra, extra, extra)

    def paint(self, painter, option, widget):
        if self.source() and self.dest():
            # Draw the line itself.
            line = QtCore.QLineF(self.sourcePoint, self.destPoint)
            if line.length() > 0.0:
                painter.setPen(QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
                painter.drawLine(line)

###
class Node(QtGui.QGraphicsItem):
    Type = QtGui.QGraphicsItem.UserType + 1

    def __init__(self, graphWidget, time, temp, pos):
        QtGui.QGraphicsItem.__init__(self)

        self.graph = weakref.ref(graphWidget)
        self.edgeList = []
        self.set_index(pos)
        self.newPos = QtCore.QPointF()
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(self.DeviceCoordinateCache)
        self.setZValue(-1)
        #
        self.temp = temp
        self.time = time
        x,y = self.map_temptime_to_pos()
        self.setPos(x,y)
        self.marker = False


    def type(self):
        return Node.Type

    def addEdge(self, edge):
        self.edgeList.append(weakref.ref(edge))

    def set_index(self, index):
        self.index = index
        self.label = "Step %d" % index
        self.setToolTip(self.label)

    def get_prev_edge(self):
        index = 1000
        edge = False
        for e in self.edgeList:
            sn = e().source().index
            dn = e().dest().index
            if sn < index:
                index = sn
                edge = e
            if dn < index:
                index = dn
                edge = e
        return edge

    def get_next_edge(self):
        index = -1
        edge = False
        for e in self.edgeList:
            sn = e().source().index
            dn = e().dest().index
            if sn > index:
                index = sn
                edge = e
            if dn > index:
                index = dn
                edge = e
        return edge

    def map_temptime_to_pos(self):
        x = self.time * self.graph().graph_width_ratio
        y = self.graph().size[3] - self.temp * self.graph().graph_height_ratio
        return (x,y)

    def boundingRect(self):
        adjust = 2.0
        return QtCore.QRectF(-10 - adjust, -10 - adjust,
                             22 + adjust, 23 + adjust)

    def paint(self, painter, option, widget):
        painter.drawLine(QtCore.QLineF(6,-40,6,-2))
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.lightGray)
        painter.drawEllipse(-10, -10, 20, 20)
        gradient = QtGui.QRadialGradient(0, 0, 22)
        if option.state & QtGui.QStyle.State_Sunken: # selected
            gradient.setColorAt(0, QtGui.QColor(QtCore.Qt.darkGreen).lighter(120))
        else:
            gradient.setColorAt(1, QtCore.Qt.blue)
        painter.setBrush(QtGui.QBrush(gradient))
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 0))
        painter.drawEllipse(-6, -6, 12, 12)


    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            for edge in self.edgeList:
                edge().adjust()
        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def mousePressEvent(self, event):
        if not self.graph().inhibit_edit:
            self.update()
            print "Node pressed"
            QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        if not self.graph().inhibit_edit:
            self.update()
            print "Node released"
            #
            QtGui.QGraphicsItem.mouseReleaseEvent(self, event)



###
class GraphWidget(QtGui.QGraphicsView):
    def __init__(self):
        QtGui.QGraphicsView.__init__(self)
        self.size = (-30, 30, 600, 400)
        #
        scene = QtGui.QGraphicsScene(self)
        scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        scene.setSceneRect(self.size[0],self.size[1],self.size[2],self.size[3])
        self.setScene(scene)
        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        #
        self.maxtemp = 300
        self.maxtime = 160
        self.nodecount = 0
        self.calc_upper_limits()
        #
        self.scale(0.8, 0.8)
        self.setMinimumSize(600, 400)
        self.setWindowTitle(self.tr("Elastic Nodes"))
        self.inhibit_edit = False

    def calc_upper_limits(self):
        self.toptemp = (self.maxtemp / 100 + 1) * 100
        self.toptime = (int(self.maxtime) / 30 + 1) * 30
        self.graph_width_ratio = float(self.size[2]) /self.toptime
        self.graph_height_ratio = float(self.size[3]) / self.toptemp

    def add_node(self, time, temp, marker=False, pos=-1):
        self.nodecount += 1
        scene = self.scene()
        # Insert Node into scene
        node = Node(self, time, temp, self.nodecount)
        scene.addItem(node)
        # Insert new edges
        nodes = self.get_ordered_nodes()
        if len(nodes) > 1:
            e = Edge(nodes[-2], node)
            scene.addItem(e)
        # cleanup edge tooltips
        for n in self.get_ordered_nodes():
            edges = n.edgeList
            for e in edges:
                e().set_index()

    def get_ordered_nodes(self):
        nodes = [item for item in self.scene().items() if isinstance(item, Node)]
        nodes.sort(key=lambda n: n.index)
        return nodes

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Plus:
            self.scaleView(1.2)
        elif key == QtCore.Qt.Key_Minus:
            self.scaleView(1 / 1.2)
        else:
            QtGui.QGraphicsView.keyPressEvent(self, event)

    def mousePressEvent(self, event):
        print "GraphWidget mouse"
        QtGui.QGraphicsView.mousePressEvent(self, event)

    def wheelEvent(self, event):
        self.scaleView(math.pow(2.0, -event.delta() / 240.0))

    def scaleView(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
        if factor < 0.07 or factor > 100:
            return
        self.scale(scaleFactor, scaleFactor)

    def drawBackground(self, painter, rect):
        sceneRect = self.sceneRect()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    widget = GraphWidget()
    widget.add_node(0,    25)
    widget.add_node(30,  100)
    widget.add_node(120,  100)
    widget.add_node(60,  200)
    widget.show()
    sys.exit(app.exec_())
