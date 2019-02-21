#!/usr/bin/python3

import sys
from PySide.QtCore import *
from PySide.QtGui import *
from Ui_ImageWindow import *

class ImageWindow(QMainWindow, Ui_ImageWindow):

	def __init__(self):
		super(ImageWindow, self).__init__()
		self.setupUi(self)
		self.image = None

		desktop = QDesktopWidget()
		settings = QSettings()
		desktopWidth = int(settings.value("desktopWidth", desktop.width()))
		desktopHeight = int(settings.value("desktopHeight", desktop.height()))
		self.deskWidth.setText("%d" % desktopWidth)
		self.deskHeight.setText("%d" % desktopHeight)

		self.deskWidth.textChanged.connect(self.deskWidthChanged)
		self.deskHeight.textChanged.connect(self.deskHeightChanged)

	def dragEnterEvent(self, e):
		self.label.setText(e.mimeData().text())
		e.accept()

	def dragLeaveEvent(self, e):
		self.label.setText("Drop an image onto the window")
		e.accept()

	def dropEvent(self, e):
		file = QUrl(e.mimeData().text()).toLocalFile().strip()
		self.image = QImage(file)
		assert(self.image.isNull() == False)
		self.setImageOnLabel()
		e.accept()

	def resizeEvent(self, e):
		if (self.image != None):
			self.setImageOnLabel()

	def setImageOnLabel(self):
		assert(self.image != None)
		assert(self.image.isNull() == False)
		image = self.image.scaled(
			self.label.width(),
			self.label.height(),
			QtCore.Qt.KeepAspectRatio)
		assert(image.isNull() == False)
		pixmap = QPixmap.fromImage(image)
		assert(pixmap.isNull() == False)
		self.label.setPixmap(pixmap)
		self.label.setMinimumSize(1, 1)

	def deskWidthChanged(self):
		print("desk width changed")

	def deskHeightChanged(self):
		print("desk height changed")

	def closeEvent(self, e):
		settings = QSettings()
		settings.setValue("desktopWidth", self.deskWidth.text())
		settings.setValue("desktopHeight", self.deskHeight.text())
