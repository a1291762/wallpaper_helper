#!/usr/bin/python3

import sys
from PySide.QtCore import *
from PySide.QtGui import *
from Ui_ImageWindow import *

class ImageWindow(QMainWindow, Ui_ImageWindow):

	_image = None

	def __init__(self):
		super(ImageWindow, self).__init__()
		self.setupUi(self)

		desktop = QDesktopWidget()
		settings = QSettings()
		desktopWidth = int(settings.value("desktopWidth", desktop.width()))
		desktopHeight = int(settings.value("desktopHeight", desktop.height()))
		self.deskWidth.setText("%d" % desktopWidth)
		self.deskHeight.setText("%d" % desktopHeight)

		self.deskWidth.textChanged.connect(self._deskWidthChanged)
		self.deskHeight.textChanged.connect(self._deskHeightChanged)
		self._setDesktopFrame()

		#print("wallpaper path "+self.wallpaper.path)

	def dragEnterEvent(self, e):
		self.label.setText(e.mimeData().text())
		e.accept()

	def dragLeaveEvent(self, e):
		self.label.setText("Drop an image onto the window")
		e.accept()

	def dropEvent(self, e):
		file = QUrl(e.mimeData().text()).toLocalFile().strip()
		self._image = QImage(file)
		assert(self._image.isNull() == False)
		self._setImageOnLabel()
		e.accept()

	def resizeEvent(self, e):
		if (self._image != None):
			self._setImageOnLabel()

	def _setImageOnLabel(self):
		assert(self._image != None)
		assert(self._image.isNull() == False)
		image = self._image.scaled(
			self.label.width(),
			self.label.height(),
			QtCore.Qt.KeepAspectRatio)
		assert(image.isNull() == False)
		self.label.setImage(image)

	def _deskWidthChanged(self):
		print("desk width changed")
		self._setDesktopFrame()

	def _deskHeightChanged(self):
		print("desk height changed")
		self._setDesktopFrame()

	def closeEvent(self, e):
		settings = QSettings()
		settings.setValue("desktopWidth", self.deskWidth.text())
		settings.setValue("desktopHeight", self.deskHeight.text())

	def _setDesktopFrame(self):
		self.label.setDesktop(
			int(self.deskWidth.text()),
			int(self.deskHeight.text()))
