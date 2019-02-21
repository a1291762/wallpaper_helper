#!/usr/bin/python3

import sys
from PySide.QtCore import *
from PySide.QtGui import *
from Ui_ImageWindow import *

class ImageWindow(QMainWindow):

	_image = None

	def __init__(self):
		super(ImageWindow, self).__init__()
		self.ui = Ui_ImageWindow()
		self.ui.setupUi(self)

		desktop = QDesktopWidget()
		settings = QSettings()
		desktopWidth = int(settings.value("desktopWidth", desktop.width()))
		desktopHeight = int(settings.value("desktopHeight", desktop.height()))
		self.ui.deskWidth.setText("%d" % desktopWidth)
		self.ui.deskHeight.setText("%d" % desktopHeight)

		self.ui.deskWidth.textChanged.connect(self._setDesktopFrame)
		self.ui.deskHeight.textChanged.connect(self._setDesktopFrame)
		self._setDesktopFrame()

		#print("wallpaper path "+self.wallpaper.path)

	def dragEnterEvent(self, e):
		self.ui.label.setText(e.mimeData().text())
		e.accept()

	def dragLeaveEvent(self, e):
		self.ui.label.setText("Drop an image onto the window")
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
			self.ui.label.width(),
			self.ui.label.height(),
			QtCore.Qt.KeepAspectRatio)
		assert(image.isNull() == False)
		self.ui.label.setImage(image)

	def closeEvent(self, e):
		settings = QSettings()
		settings.setValue("desktopWidth", self.ui.deskWidth.text())
		settings.setValue("desktopHeight", self.ui.deskHeight.text())

	def _setDesktopFrame(self):
		self.ui.label.setDesktop(
			int(self.ui.deskWidth.text()),
			int(self.ui.deskHeight.text()))
		self.update()
