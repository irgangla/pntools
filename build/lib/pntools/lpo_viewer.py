#!/usr/bin/python3
# -*- coding_ utf-8 -*-

""" This program implements a viewer for the LPO data structure.

"""

import sys
import math
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QAction, qApp, QFileDialog, QTabWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
import partialorder

class LpoWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        
        self.lpo = None

    def initUI(self):
        self.setMinimumSize(100, 100)

    def showLpo(self, lpo_to_show):
        print("Show lpo", lpo_to_show.name)
        self.lpo = lpo_to_show
        self.updateSize()
        self.repaint()
        self.setToolTip(lpo_to_show.name)

    def updateSize(self):
        size = [50, 50]
        
        for id, event in self.lpo.events.items():
            if event.position[0] > size[0]:
                size[0] = event.position[0]
            if event.position[1] > size[1]:
                size[1] = event.position[1]

        self.setMinimumSize(size[0] + 50, size[1] + 50)
        self.resize(size[0] + 50, size[1] + 50)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        if self.lpo != None:
            self.drawLpo(qp)
        qp.end()

    def drawLpo(self, qp):
        for arc in self.lpo.arcs:
            if arc.user_drawn == True:
                self.drawArc(qp, arc)

        for id, event in self.lpo.events.items():
            self.drawEvent(qp, event)

    def setEventPen(self, qp):
        qp.setPen(QPen(QColor(0, 0, 0), 2, Qt.SolidLine))
        qp.setBrush(QColor(180, 180, 180))

        font = QFont('Serif', 7, QFont.Light)
        qp.setFont(font)
        
        qp.setRenderHint(QPainter.HighQualityAntialiasing)

    def drawEvent(self, qp, event):
        self.setEventPen(qp)
        
        qp.drawRect(event.position[0] - 10, event.position[1] - 10, 20, 20)
        metrics = qp.fontMetrics()
        fw = metrics.width(event.label)
        fh = metrics.height()
        qp.drawText(event.position[0] - fw / 2, event.position[1] + 12 + fh , event.label)

    def setArcPen(self, qp):
        qp.setPen(QPen(QColor(0, 0, 0), 2, Qt.SolidLine))
        
        qp.setRenderHint(QPainter.HighQualityAntialiasing)

    def setTipPen(self, qp):
        qp.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
        qp.setBrush(QColor(0, 0, 0))

        qp.setRenderHint(QPainter.HighQualityAntialiasing)

    def drawArc(self, qp, arc):
        self.setArcPen(qp)
        
        start_event = self.lpo.events[arc.source]
        end_event = self.lpo.events[arc.target]

        intersections = self.calculateIntersections(start_event, end_event)

        start = start_event.position[0] + intersections[0][0], start_event.position[1] + intersections[0][1]
        end = end_event.position[0] + intersections[1][0], end_event.position[1] + intersections[1][1]
        
        qp.drawLine(start[0], start[1], end[0], end[1])

        tip = self.calculateTip(start_event, end_event)

        self.setTipPen(qp)
       
        qp.drawPolygon(QPoint(end[0], end[1]),
                       QPoint(end[0] + tip[0][0], end[1] + tip[0][1]),
                       QPoint(end[0] + tip[1][0], end[1] + tip[1][1]))


    def calculateTip(self, start, end):
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

    def calculateIntersections(self, start, end):
        vector = float(end.position[0] - start.position[0]), float(end.position[1] - start.position[1])

        fact = 10 / math.fabs(vector[0])
        start_vector = vector[0] * fact, vector[1] * fact
        if start_vector[1] > 10:
            fact = 10 / math.fabs(vector[1])
            start_vector = vector[0] * fact, vector[1] * fact

        fact = 10 / math.fabs(vector[0])
        end_vector = -vector[0] * fact, -vector[1] * fact
        if end_vector[1] > 10:
            fact = 10 / math.fabs(vector[1])
            end_vector = -vector[0] * fact, -vector[1] * fact

        return start_vector, end_vector
        
class LpoViewer(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        openAction = QAction('&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Load LPO from XML file')
        openAction.triggered.connect(self.openLpo)

        closeAction = QAction('&Close', self)
        closeAction.setShortcut('Ctrl+C')
        closeAction.setStatusTip('Close selected tab')
        closeAction.triggered.connect(self.closeLpo)
        
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+X')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.closeApp)
                
        menubar = self.menuBar()
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(openAction)
        filemenu.addAction(closeAction)
        filemenu.addAction(exitAction)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.statusBar()
                
        self.setGeometry(500, 500, 200, 200)
        self.setWindowTitle("Lpo Viewer")
        self.show()

    def showLpo(self, lpo):
        view = LpoWidget()

        index = self.tabs.addTab(view, lpo.name)
        self.tabs.setCurrentIndex(index)
        
        view.showLpo(lpo)
        
        self.statusBar().showMessage(lpo.name)

    def closeLpo(self):
        index = self.tabs.currentIndex()
        self.tabs.removeTab(index)

    def openLpo(self):
        fname = QFileDialog.getOpenFileName(self, 'Open LPO')
        print("Open LPO", fname[0])
        parsed_lpos = lpoparser.parse_lpo_file(fname[0])
        print(parsed_lpos[0])
        self.showLpo(parsed_lpos[0])        

    def closeApp(self):
        self.hide()
        qApp.quit()
        sys.exit(0)
        
        

if __name__ == "__main__":
    lpos = partialorder.parse_lpo_file(sys.argv[1])
    print(lpos[0])
        
    app = QApplication(sys.argv)
    
    viewer = LpoViewer()
    viewer.showLpo(lpos[0])

    sys.exit(app.exec_())

    
    


            

    
        

