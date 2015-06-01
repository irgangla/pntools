#!/usr/bin/python3
# -*- coding_ utf-8 -*-

""" This program implements a viewer for the LPO data structure.

A LPO is a partial ordered set of events. If two events are ordered
this order is represented by an arrow. If there is an arrow form an
event a to an event b this means event b occurs after event a.

Usage: python lpo_viewer.py [<lpo-file>]
"""

import math # calculation of intersection point (fabs, ...)
import sys # sys.argv
import partialorder # LPO parser and data structure
import os # demo file
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QAction, qApp, QFileDialog, QTabWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QFont

class LpoWidget(QWidget):
    """ This class implements a LPO widget.

    This class use a canvas to draw the Hasse diagram of a LPO.
    """
    
    def __init__(self):
        """ This method creates a new, empty LpoView. """
        super().__init__()
        self.__initUI()
        
        self.__lpo = None

    def __initUI(self):
        """ Set up user interface. """
        self.setMinimumSize(100, 100)

    def showLpo(self, lpo_to_show):
        """ This method show the given LPO in this LpoView. """
        self.__lpo = lpo_to_show
        self.updateSize()
        self.repaint()
        self.setToolTip(lpo_to_show.name)

    def updateSize(self):
        """ Update the size of the widget to fit the size of the LPO. """
        size = [50, 50]
        
        for id, event in self.__lpo.events.items():
            if event.position[0] > size[0]:
                size[0] = event.position[0]
            if event.position[1] > size[1]:
                size[1] = event.position[1]

        self.setMinimumSize(size[0] + 50, size[1] + 50)
        self.resize(size[0] + 50, size[1] + 50)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        if self.__lpo != None:
            self.__drawLpo(qp)
        qp.end()

    def __drawLpo(self, qp):
        """ Draw LPO. """
        for arc in self.__lpo.arcs:
            if arc.user_drawn == True:
                self.__drawArc(qp, arc)

        for id, event in self.__lpo.events.items():
            self.__drawEvent(qp, event)

    def __setEventPen(self, qp):
        """ Set up painter for drawing events. """
        qp.setPen(QPen(QColor(0, 0, 0), 2, Qt.SolidLine))
        qp.setBrush(QColor(180, 180, 180))

        font = QFont('Serif', 7, QFont.Light)
        qp.setFont(font)
        
        qp.setRenderHint(QPainter.HighQualityAntialiasing)

    def __drawEvent(self, qp, event):
        """ Draw the given event. """
        self.__setEventPen(qp)
        
        qp.drawRect(event.position[0] - 10, event.position[1] - 10, 20, 20)
        metrics = qp.fontMetrics()
        fw = metrics.width(event.label)
        fh = metrics.height()
        qp.drawText(event.position[0] - fw / 2, event.position[1] + 12 + fh , event.label)

    def __setArcPen(self, qp):
        """ Set up painter for drawing arcs. """
        qp.setPen(QPen(QColor(0, 0, 0), 2, Qt.SolidLine))
        
        qp.setRenderHint(QPainter.HighQualityAntialiasing)

    def __setTipPen(self, qp):
        """ Set up painter for drawing arc tips. """
        qp.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
        qp.setBrush(QColor(0, 0, 0))

        qp.setRenderHint(QPainter.HighQualityAntialiasing)

    def __drawArc(self, qp, arc):
        """ Draw the given arc. """
        self.__setArcPen(qp)
        
        start_event = self.__lpo.events[arc.source]
        end_event = self.__lpo.events[arc.target]

        intersections = self.__calculateIntersections(start_event, end_event)

        start = start_event.position[0] + intersections[0][0], start_event.position[1] + intersections[0][1]
        end = end_event.position[0] + intersections[1][0], end_event.position[1] + intersections[1][1]
        
        qp.drawLine(start[0], start[1], end[0], end[1])

        tip = self.__calculateTip(start_event, end_event)

        self.__setTipPen(qp)
       
        qp.drawPolygon(QPoint(end[0], end[1]),
                       QPoint(end[0] + tip[0][0], end[1] + tip[0][1]),
                       QPoint(end[0] + tip[1][0], end[1] + tip[1][1]))


    def __calculateTip(self, start, end):
        vector = float(start.position[0] - end.position[0]), float(start.position[1] - end.position[1])
        vector_length = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
        vector_sized = vector[0] * 10 / vector_length, vector[1] * 10 / vector_length

        alpha = 30 * 2 * math.pi / 360

        sin_alpha = math.sin(alpha)
        cos_alpha = math.cos(alpha)

        tip1 = (vector_sized[0] * cos_alpha - vector_sized[1] * sin_alpha,
                vector_sized[0] * sin_alpha + vector_sized[1] * cos_alpha)

        sin_alpha = math.sin(-alpha)
        cos_alpha = math.cos(-alpha)

        tip2 = (vector_sized[0] * cos_alpha - vector_sized[1] * sin_alpha,
                vector_sized[0] * sin_alpha + vector_sized[1] * cos_alpha)

        return tip1, tip2

    def __calculateIntersections(self, start, end):
        """ Calculate intersection point of start and end events with the arc.

        This method calculates two vectors which describe the intersection point of the arc from the
        given start event to the given end event.
        """

        # vector from the center of the start event to the center of the end event
        vector = float(end.position[0] - start.position[0]), float(end.position[1] - start.position[1])
        #calculate a factor to scale the x-component to 10px (half of side length)
        fact = 1
        if vector[0] != 0:
            fact = 10 / math.fabs(vector[0])
        # scale the vector
        start_vector = vector[0] * fact, vector[1] * fact

        # if y-component of vector is larger than 10px or x-component is 0, scale with y-component
        if math.fabs(start_vector[1]) > 10 or vector[0] == 0:
            fact = 10 / math.fabs(vector[1])
            start_vector = vector[0] * fact, vector[1] * fact
        #calculate intersection for arc end
        if vector[0] != 0:
            fact = 10 / math.fabs(vector[0])

        end_vector = -vector[0] * fact, -vector[1] * fact

        if math.fabs(end_vector[1]) > 10 or vector[0] == 0:
            fact = 10 / math.fabs(vector[1])
            end_vector = -vector[0] * fact, -vector[1] * fact

        return start_vector, end_vector
        
class LpoViewer(QMainWindow):
    """ This class implements the window of the Lpo viewer.

    This class implements a menu and tab management for the LpoView.
    """
    
    def __init__(self):
        """ Create new window. """
        super().__init__()
        self.__initUI()

    def __initUI(self):
        """ Set up UI. """
        openAction = QAction('&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Load LPO from XML file')
        openAction.triggered.connect(self.__onOpen)

        closeAction = QAction('&Close', self)
        closeAction.setShortcut('Ctrl+C')
        closeAction.setStatusTip('Close selected tab')
        closeAction.triggered.connect(self.__onClose)
        
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+X')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.__onQuit)
        
        menubar = self.menuBar()
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(openAction)
        filemenu.addAction(closeAction)
        filemenu.addAction(exitAction)

        self.__tabs = QTabWidget()
        self.setCentralWidget(self.__tabs)
        
        self.statusBar()
                
        self.setGeometry(500, 500, 200, 200)
        self.setWindowTitle("Lpo Viewer")
        self.show()

    def openLpo(self, file):
        """ This method shows the LPO contained in the given file as new tab. """
        lpos = partialorder.parse_lpo_file(file)
        self.showLpo(lpos[0])


    def showLpo(self, lpo):
        """ Show the given LPO in a new tab. """
        view = LpoWidget()
        
        index = self.__tabs.addTab(view, lpo.name)
        self.__tabs.setCurrentIndex(index)
        
        view.showLpo(lpo)
        
        self.statusBar().showMessage(lpo.name)

    def __onClose(self):
        index = self.tabs.currentIndex()
        self.tabs.removeTab(index)

    def __onOpen(self):
        fname = QFileDialog.getOpenFileName(self, 'Open LPO')
        parsed_lpos = lpoparser.parse_lpo_file(fname[0])
        self.showLpo(parsed_lpos[0])        

    def __onQuit(self):
        self.hide()
        qApp.quit()
        sys.exit(0)
        
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = LpoViewer()

    if len(sys.argv) > 1: # load LPO if file is given as parameter
        viewer.openLpo(sys.argv[1])

    if os.path.exists("../abcabc.lpo"): # debug/demo file
        viewer.openLpo("../abcabc.lpo")

    sys.exit(app.exec_())

    
    


            

    
        

