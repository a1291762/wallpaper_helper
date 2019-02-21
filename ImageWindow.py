#!/usr/bin/python3

import sys
from PySide.QtCore import *
from PySide.QtGui import *
from Ui_ImageWindow import *
import os

class ImageWindow(QMainWindow):

	image = None
	ui = None

	def __init__(self):
		super().__init__()
		self.ui = Ui_ImageWindow()
		self.ui.setupUi(self)
		#self.ui.label.installEventFilter(self)
		#self.centralWidget().installEventFilter(self)
		self.installEventFilter(self)

		desktop = QDesktopWidget()
		settings = QSettings()
		desktopWidth = int(settings.value("desktopWidth", desktop.width()))
		desktopHeight = int(settings.value("desktopHeight", desktop.height()))
		self.ui.deskWidth.setText("%d" % desktopWidth)
		self.ui.deskHeight.setText("%d" % desktopHeight)

		self.ui.deskWidth.textChanged.connect(self._setDesktopFrame)
		self.ui.deskHeight.textChanged.connect(self._setDesktopFrame)
		self._setDesktopFrame()

		self.ui.wallpaper.setSettingsKey("wallpaper");
		self.ui.originals.setSettingsKey("originals");

		path = self.ui.wallpaper.path
		if (path != None):
			self._loadFromPath(path)

	def dragEnterEvent(self, e):
		self.ui.label.setText(e.mimeData().text())
		e.accept()

	def dragLeaveEvent(self, e):
		self.ui.label.setText("Drop an image onto the window")
		e.accept()

	def dropEvent(self, e):
		file = QUrl(e.mimeData().text()).toLocalFile().strip()
		self._loadFile(file)
		e.accept()

	def closeEvent(self, e):
		settings = QSettings()
		settings.setValue("desktopWidth", self.ui.deskWidth.text())
		settings.setValue("desktopHeight", self.ui.deskHeight.text())

	def _setDesktopFrame(self):
		self.ui.label.setDesktop(
			int(self.ui.deskWidth.text()),
			int(self.ui.deskHeight.text()))
		self.update()

	def _loadFromPath(self, path):
		#print("wallpaper path "+path)
		files = os.listdir(path)
		files.sort()
		if (len(files) == 0):
			print("No files?!")
			return

		file = path+"/"+files[0]
		self._loadFile(file)

	def eventFilter(self, object, e):
		if (not isinstance(e, QKeyEvent)):
			#print("is not a key event")
			return False
		if (e.type() != QEvent.ShortcutOverride):
			return False

		switcher = {
			Qt.Key_Left: self._selectPreviousImage,
			Qt.Key_Right: self._selectNextImage
		}
		func = switcher.get(e.key())
		if (func):
			func()
			e.accept()
			return True

		return False

	def _loadFile(self, file):
		self.imagePath = file
		image = QImage(file)
		assert(image.isNull() == False)
		self.ui.label.setImage(image)

	def _selectPreviousImage(self):
		path = os.path.dirname(self.imagePath)
		files = os.listdir(path)
		files.sort()
		lastFile = None
		for file in reversed(files):
			if (lastFile == self.imagePath):
				#print("lastFile is current file, load next file")
				self._loadFile(path+"/"+file)
				return
			lastFile = path+"/"+file
		#print("load first file")
		self._loadFile(path+"/"+files[-1])

	def _selectNextImage(self):
		path = os.path.dirname(self.imagePath)
		files = os.listdir(path)
		files.sort()
		lastFile = None
		for file in files:
			if (lastFile == self.imagePath):
				#print("lastFile is current file, load next file")
				self._loadFile(path+"/"+file)
				return
			lastFile = path+"/"+file
		#print("load first file")
		self._loadFile(path+"/"+files[0])
