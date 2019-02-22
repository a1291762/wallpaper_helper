#!/usr/bin/python3

import sys
from PySide.QtCore import *
from PySide.QtGui import *
from Ui_ImageWindow import *
import os
import shutil

FORWARDS = False
BACKWARDS = True

class ImageWindow(QMainWindow):

	image = None
	ui = None

	def __init__(self):
		super().__init__()
		self.ui = Ui_ImageWindow()
		self.ui.setupUi(self)

		# focus the label and listen for keyboard events from it
		self.ui.label.setFocus()
		self.ui.label.installEventFilter(self)

		# set (or load from config) the desktop size
		desktop = QDesktopWidget()
		settings = QSettings()
		desktopWidth = int(settings.value("desktopWidth", desktop.width()))
		desktopHeight = int(settings.value("desktopHeight", desktop.height()))
		self.ui.deskWidth.setText("%d" % desktopWidth)
		self.ui.deskHeight.setText("%d" % desktopHeight)

		# react to size changes
		self.ui.deskWidth.textChanged.connect(lambda: self._setDesktopFrame(True))
		self.ui.deskHeight.textChanged.connect(lambda: self._setDesktopFrame(True))
		self._setDesktopFrame(False)

		# path buttons need to read/save config
		self.ui.wallpaper.setSettingsKey("wallpaper");
		self.ui.originals.setSettingsKey("originals");

		file = settings.value("image")
		if (file):
			# load previous image
			self._loadFile(file)
		else:
			path = self.ui.wallpaper.path
			if (path):
				# load the first image from the path
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

	def _setDesktopFrame(self, saveSettings):
		# Used to draw the clip rect
		self.ui.label.setDesktop(
			int(self.ui.deskWidth.text()),
			int(self.ui.deskHeight.text()))

		if (saveSettings):
			settings = QSettings()
			settings.setValue("desktopWidth", self.ui.deskWidth.text())
			settings.setValue("desktopHeight", self.ui.deskHeight.text())

	def _loadFromPath(self, path):
		#print("wallpaper path "+path)
		files = os.listdir(path)
		files.sort()
		if (len(files) == 0):
			print("No files?!")
			return

		file = path+"/"+files[0]
		self._loadFile(file)

	def _loadFile(self, file):
		self.imagePath = file # for forwards/backwards moving
		settings = QSettings()
		settings.setValue("image", file) # for close/reopen
		image = QImage(file)
		assert(image.isNull() == False)
		self.ui.label.setImage(image)
		self.setWindowTitle(file)

	def eventFilter(self, object, e):
		# I only want the key press events
		if (e.type() != QEvent.KeyPress):
			return False

		switcher = {
			Qt.Key_Right: lambda: self._selectNextImage(FORWARDS),
			Qt.Key_Left: lambda: self._selectNextImage(BACKWARDS),
			Qt.Key_S: self._saveImage if e.modifiers() == Qt.ControlModifier else None,
			Qt.Key_R: self._resetImage if e.modifiers() == Qt.ControlModifier else None,
			Qt.Key_Minus: lambda: self.ui.label.addPadding(-1),
			Qt.Key_Plus: lambda: self.ui.label.addPadding(1),
			Qt.Key_Equal: lambda: self.ui.label.addPadding(1),
			Qt.Key_Space: self.ui.label.togglePreview,
		}
		func = switcher.get(e.key())
		if (func):
			func()
			e.accept()
			return True

		return False

	def _selectNextImage(self, backwards):
		path = os.path.dirname(self.imagePath)
		files = os.listdir(path)
		files.sort()
		# Simply by reversing the list, we can use the same logic to move backwards
		if backwards:
			files.reverse()
		lastFile = None
		for f in files:
			file = path+"/"+f
			#print(f"file {file} lastFile {lastFile} imagePath {self.imagePath}")
			if (lastFile == self.imagePath):
				#print("lastFile is current file, load next file")
				self._loadFile(file)
				return
			lastFile = file
		#print("load first file")
		file = path+"/"+files[0]
		self._loadFile(file)

	def _getPaths(self):
		backupPath = self.ui.originals.path
		wallpaperPath = self.ui.wallpaper.path
		if (not backupPath or not wallpaperPath):
			print("Both the wallpaper and originals paths must be set!")
			return None, None
		fileName = os.path.basename(self.imagePath)
		backupPath += "/"+fileName
		wallpaperPath += "/"+fileName
		return backupPath, wallpaperPath

	def _saveImage(self):
		backupPath, wallpaperPath = self._getPaths()
		if (not backupPath or not wallpaperPath):
			return

		if (not os.path.isfile(backupPath)):
			#print("Original file already exists!")
		#else:
			#print("Copy to backup folder")
			shutil.copyfile(self.imagePath, backupPath)

		#print("Save image!")
		self.ui.label.saveImage(wallpaperPath)
		if (wallpaperPath == self.imagePath):
			# reload the changed image
			self._loadFile(wallpaperPath)

	def _resetImage(self):
		backupPath, wallpaperPath = self._getPaths()
		if (not backupPath or not wallpaperPath):
			return

		if (os.path.isfile(backupPath)):
			shutil.move(backupPath, wallpaperPath)

		if (wallpaperPath == self.imagePath):
			# reload the changed image
			self._loadFile(wallpaperPath)
