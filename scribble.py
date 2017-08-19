# !/usr/bin/env python
# structured edges, iopl edge detection

#############################################################################
##
## Copyright (C) 2010 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################


# These are only needed for Python v2 but are harmless for Python v3
import sip

sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
from ThreeSweep import ThreeSweep

threesweep = ThreeSweep()

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import qRgb, QImage
import numpy as np


class NotImplementedException:
    pass


gray_color_table = [qRgb(i, i, i) for i in range(256)]


def toQImage(im, copy=False):
    if im is None:
        return QImage()

    if im.dtype == np.uint8:
        if len(im.shape) == 2:
            qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_Indexed8)
            qim.setColorTable(gray_color_table)
            return qim.copy() if copy else qim

        elif len(im.shape) == 3:
            if im.shape[2] == 3:
                qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_RGB888);
                return qim.copy() if copy else qim
            elif im.shape[2] == 4:
                qim = QImage(im.data, im.shape[1], im.shape[0], im.strides[0], QImage.Format_ARGB32);
                return qim.copy() if copy else qim


class ScribbleArea(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ScribbleArea, self).__init__(parent)
        self.tempDrawing = False
        self.setMouseTracking(True)
        self.firstPoint = None
        self.secondPoint = None
        self.thirdPoint = None
        self.contourPoints = []
        self.setAttribute(QtCore.Qt.WA_StaticContents)
        self.modified = False
        self.clicked = False
        self.state = 'Start'
        self.myPenWidth = 5
        self.myPenColor = QtCore.Qt.blue
        self.image = QtGui.QImage()
        self.lastPoint = QtCore.QPoint()
        self.imagePainter = None
        self.edges = None

    def stateUpdate(self, state=None):
        if state == None:
            pass
        else:
            self.state = state
        state = (self.state)
        if state == 'Start':
            pass
        elif self.state == 'FirstSweep':
            self.setPenColor(QtCore.Qt.blue)
            pass
        elif self.state == 'SecondSweep':
            self.setPenColor(QtCore.Qt.red)
            pass
        elif self.state == 'ThirdSweep':
            self.setPenColor(QtCore.Qt.green)
            pass
        self.plotPoint(self.firstPoint)
        self.plotPoint(self.secondPoint)
        self.plotPoint(self.thirdPoint)

    def openImage(self, fileName):
        loadedImage = QtGui.QImage()
        if not loadedImage.load(fileName):
            return False

        newSize = loadedImage.size()
        self.resize(newSize)
        ##newSize = loadedImage.size().expandedTo(self.size())
        ##self.resizeImage(loadedImage, newSize)
        self.image = loadedImage
        self.modified = False
        self.update()
        return True

    def saveImage(self, fileName, fileFormat):
        visibleImage = self.image
        self.resizeImage(visibleImage, self.size())

        if visibleImage.save(fileName, fileFormat):
            self.modified = False
            return True
        else:
            return False

    def setPenColor(self, newColor):
        self.myPenColor = newColor

    def setPenWidth(self, newWidth):
        self.myPenWidth = newWidth

    def clearImage(self):
        self.image.fill(QtGui.qRgb(255, 255, 255))
        self.modified = True
        self.update()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.state == 'Start':
                pass
            elif self.state == 'FirstSweep':
                pass
            elif self.state == 'SecondSweep':
                self.stateUpdate('ThirdSweep')
                self.thirdPoint = event.pos()
                pass
            elif self.state == 'ThirdSweep':
                pass
            self.lastPoint = event.pos()
            self.clicked = True

    def mouseMoveEvent(self, event):
        if (event.buttons() & QtCore.Qt.LeftButton) and self.state == 'ThirdSweep' and self.clicked:
            self.drawLineTo(event.pos())

        if self.state == 'FirstSweep':
            self.drawLineWithColor(self.firstPoint, event.pos(), temp=True)

        if self.state == 'SecondSweep':
            self.drawLineWithColor(self.secondPoint, event.pos(), temp=True)
            distance = (self.firstPoint - self.secondPoint)
            center = (self.firstPoint + self.secondPoint) / 2
            minor = (center - event.pos()).y()
            distance = (distance.x()) ** 2 + (distance.y()) ** 2
            distance = distance ** 0.5
            self.imagePainter.drawEllipse(center, distance / 2, minor)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.state == 'ThirdSweep':
            self.drawLineTo(event.pos())
        if self.state == 'Start':
            self.firstPoint = event.pos()
            self.stateUpdate('FirstSweep')
        elif self.state == 'FirstSweep':
            self.secondPoint = event.pos()
            self.stateUpdate('SecondSweep')
        elif self.state == 'SecondSweep':
            pass
        elif self.state == 'ThirdSweep':
            self.stateUpdate('Complete')
        elif self.state == 'Complete':
            self.restoreDrawing()
            self.update()

        self.clicked = False

    def saveDrawing(self):
        self.oldimage = QtGui.QImage(self.image)

    def restoreDrawing(self):
        self.imagePainter.drawImage(QtCore.QPoint(0, 0), self.oldimage)
        self.imagePainter.drawImage(0, 0, toQImage(self.edges))

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(event.rect(), self.image)

    def resizeEvent(self, event):
        if self.width() > self.image.width() or self.height() > self.image.height():
            newWidth = max(self.width(), self.image.width())
            newHeight = max(self.height(), self.image.height())
            self.resizeImage(self.image, QtCore.QSize(newWidth, newHeight))
            self.update()

        super(ScribbleArea, self).resizeEvent(event)

    def beforeDraw(self, temp):
        if not self.imagePainter:
            self.imagePainter = QtGui.QPainter(self.image)

        if self.tempDrawing:
            self.restoreDrawing()
            if not temp:
                self.tempDrawing = False
            else:
                self.saveDrawing()
        else:
            if temp:
                self.tempDrawing = True

    def afterDraw(self, temp):
        if not temp:
            self.saveDrawing()
        else:
            pass

    def plotPoint(self, point, temp=False):
        self.beforeDraw(temp)
        if not point:
            return
        self.imagePainter.setPen(QtGui.QPen(self.myPenColor, 10,
                                            QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        self.imagePainter.drawPoint(point)
        self.afterDraw(temp)
        self.update()

    def drawLineWithColor(self, startPoint, endPoint, temp=False):
        self.beforeDraw(temp)
        self.imagePainter.setPen(QtGui.QPen(self.myPenColor, self.myPenWidth,
                                            QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        self.imagePainter.drawLine(startPoint, endPoint)
        self.afterDraw(temp)
        self.modified = True

        rad = self.myPenWidth / 2 + 2
        self.update(QtCore.QRect(self.lastPoint, endPoint).normalized().adjusted(-rad, -rad, +rad, +rad))
        self.lastPoint = QtCore.QPoint(endPoint)
        self.update()

    def drawLineTo(self, endPoint, temp=False):
        self.drawLineWithColor(self.lastPoint, endPoint, temp=temp)

    def resizeImage(self, image, newSize):
        if image.size() == newSize:
            return

        newImage = QtGui.QImage(newSize, QtGui.QImage.Format_RGB32)
        newImage.fill(QtGui.qRgb(255, 255, 255))
        painter = QtGui.QPainter(newImage)
        painter.drawImage(QtCore.QPoint(0, 0), image)
        self.image = newImage

    def print_(self):
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)

        printDialog = QtGui.QPrintDialog(printer, self)
        if printDialog.exec_() == QtGui.QDialog.Accepted:
            painter = QtGui.QPainter(printer)
            rect = painter.viewport()
            size = self.image.size()
            size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.image.rect())
            painter.drawImage(0, 0, self.image)
            painter.end()

    def isModified(self):
        return self.modified

    def penColor(self):
        return self.myPenColor

    def penWidth(self):
        return self.myPenWidth


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.saveAsActs = []
        self.appState = 'Start'
        self.scribbleArea = ScribbleArea()
        self.setCentralWidget(self.scribbleArea)
        self.createActions()
        self.createMenus()
        self.setWindowTitle("3-Sweep")
        self.resize(1500, 1500)

    def closeEvent(self, event):
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def open(self):
        if self.maybeSave():
            fileName = QtGui.QFileDialog.getOpenFileName(self, "Open File",
                                                         QtCore.QDir.currentPath())
            if fileName:
                self.scribbleArea.openImage(fileName)
                threesweep.loadImage(fileName)
                self.scribbleArea.edges = threesweep.getEdges()

    def save(self):
        action = self.sender()
        fileFormat = action.data()
        self.saveFile(fileFormat)

    def penColor(self):
        newColor = QtGui.QColorDialog.getColor(self.scribbleArea.penColor())
        if newColor.isValid():
            self.scribbleArea.setPenColor(newColor)

    def penWidth(self):
        newWidth, ok = QtGui.QInputDialog.getInteger(self, "Scribble",
                                                     "Select pen width:", self.scribbleArea.penWidth(), 1, 50, 1)
        if ok:
            self.scribbleArea.setPenWidth(newWidth)

    def about(self):
        QtGui.QMessageBox.about(self, "About 3-Sweep",
                                "To be added")

    def stateUpdate(self, state=None):
        if state == None:
            pass
        else:
            self.appState = state
        state = (self.appState)
        self.scribbleArea.state = state
        if state == 'start':
            pass
        elif state == 'sweep':
            pass

    def createActions(self):
        self.openAct = QtGui.QAction("&Open...", self, shortcut="Ctrl+O",
                                     triggered=self.open)

        for format in QtGui.QImageWriter.supportedImageFormats():
            format = str(format)

            text = format.upper() + "..."

            action = QtGui.QAction(text, self, triggered=self.save)
            action.setData(format)
            self.saveAsActs.append(action)

        self.printAct = QtGui.QAction("&Print...", self,
                                      triggered=self.scribbleArea.print_)

        self.exitAct = QtGui.QAction("&Exit", self, shortcut="Ctrl+Q",
                                     triggered=self.close)

        self.penColorAct = QtGui.QAction("&Pen Color...", self,
                                         triggered=self.penColor)

        self.penWidthAct = QtGui.QAction("Pen &Width...", self,
                                         triggered=self.penWidth)

        self.clearScreenAct = QtGui.QAction("&Clear Screen", self,
                                            shortcut="Ctrl+L", triggered=self.scribbleArea.clearImage)

        self.aboutAct = QtGui.QAction("&About", self, triggered=self.about)

        self.aboutQtAct = QtGui.QAction("About &Qt", self,
                                        triggered=QtGui.qApp.aboutQt)

    def createMenus(self):
        self.saveAsMenu = QtGui.QMenu("&Save As", self)
        for action in self.saveAsActs:
            self.saveAsMenu.addAction(action)

        fileMenu = QtGui.QMenu("&File", self)
        fileMenu.addAction(self.openAct)
        fileMenu.addMenu(self.saveAsMenu)
        fileMenu.addAction(self.printAct)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAct)

        optionMenu = QtGui.QMenu("&Options", self)
        optionMenu.addAction(self.penColorAct)
        optionMenu.addAction(self.penWidthAct)
        optionMenu.addSeparator()
        optionMenu.addAction(self.clearScreenAct)

        helpMenu = QtGui.QMenu("&Help", self)
        helpMenu.addAction(self.aboutAct)
        helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(fileMenu)
        self.menuBar().addMenu(optionMenu)
        self.menuBar().addMenu(helpMenu)

    def maybeSave(self):
        if self.scribbleArea.isModified():
            ret = QtGui.QMessageBox.warning(self, "Scribble",
                                            "The image has been modified.\n"
                                            "Do you want to save your changes?",
                                            QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard |
                                            QtGui.QMessageBox.Cancel)
            if ret == QtGui.QMessageBox.Save:
                return self.saveFile('png')
            elif ret == QtGui.QMessageBox.Cancel:
                return False

        return True

    def saveFile(self, fileFormat):
        initialPath = QtCore.QDir.currentPath() + '/untitled.' + fileFormat

        fileName = QtGui.QFileDialog.getSaveFileName(self, "Save As",
                                                     initialPath,
                                                     "%s Files (*.%s);;All Files (*)" % (
                                                     fileFormat.upper(), fileFormat))
        if fileName:
            return self.scribbleArea.saveImage(fileName, fileFormat)

        return False


if __name__ == '__main__':
    import sys

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
