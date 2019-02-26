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
		self._loadInitialImage(file)

	def _loadInitialImage(self, file):
		if (file):
			# load previous image
			try:
				self._loadFile(file)
				print("Loaded previous image")
				return
			except:
				None
		path = self.ui.wallpaper.path
		if (path):
			# load the first image from the path
			self._selectNextImage(FORWARDS)
			print("Loaded path image?")

	def dragEnterEvent(self, e):
		file = e.mimeData().urls()[0].toLocalFile().strip()
		self.ui.label.setText(file)
		e.accept()

	def dragLeaveEvent(self, e):
		self.ui.label.setText("Drop an image onto the window")
		e.accept()

	def dropEvent(self, e):
		file = e.mimeData().urls()[0].toLocalFile().strip()
		try:
			self._loadFile(file)
		except:
			None # ignore
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
		files = self._getImages(path)
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
		# Indicate if there is an original file
		backupPath, wallpaperPath = self._getPaths()
		if (os.path.isfile(backupPath)):
			file += "*"
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
			Qt.Key_Minus: lambda: self._addPadding(-1),
			Qt.Key_Plus: lambda: self._addPadding(1),
			Qt.Key_Equal: lambda: self._addPadding(1),
			Qt.Key_Space: self._togglePreview,
			Qt.Key_O: self._toggleOriginal,
		}
		func = switcher.get(e.key())
		if (func):
			func()
			e.accept()
			return True

		return False

	def _selectNextImage(self, backwards):
		path = os.path.dirname(self.imagePath)
		files = self._getImages(path)
		if (len(files) == 0):
			print("No files?!")
			return
		# Simply by reversing the list, we can use the same logic to move backwards
		if backwards:
			files.reverse()
		lastFile = None
		for f in files:
			file = path+"/"+f
			#print(f"file {file} lastFile {lastFile} imagePath {self.imagePath}")
			if (lastFile == self.imagePath):
				#print("lastFile is current file, load next file")
				try:
					self._loadFile(file)
					return
				except:
					None # just keep looking
			lastFile = file
		#print("load first file")
		file = path+"/"+files[0]
		try:
			self._loadFile(file)
		except:
			self.ui.label.setText("Drop an image onto the window")

	def _getImages(self, path):
		allFiles = os.listdir(path)
		allFiles.sort()
		files = []
		for f in allFiles:
			# skip hidden (dot) files
			if (f[0] == "."): continue
			for fmt in QImageReader.supportedImageFormats():
				#print("Does file "+f+" match format "+fmt+"")
				if (f.endswith("."+str(fmt))):
					files.append(f)
					break
		return files

	def _getPaths(self):
		backupPath = self.ui.originals.path
		wallpaperPath = self.ui.wallpaper.path
		if (not backupPath or not wallpaperPath):
			print("Both the wallpaper and originals paths must be set!")
			return None, None
		fileName = os.path.basename(self.imagePath)
		backupPath += "/"+fileName
		if (not os.path.isfile(backupPath)):
			#print("trying alternative backupPath values...")
			for fmt in QImageReader.supportedImageFormats():
				altPath = self.ui.originals.path + "/" + os.path.splitext(fileName)[0] + "." + str(fmt)
				#print("altPath "+altPath)
				if (os.path.isfile(altPath)):
					backupPath = altPath
					break
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
			if (backupPath.endswith(".jpg")):
				shutil.move(backupPath, wallpaperPath)
			else:
				QImage(backupPath).save(wallpaperPath)

		if (wallpaperPath == self.imagePath):
			# reload the changed image
			self._loadFile(wallpaperPath)

	def _addPadding(self, amount):
		self.ui.label.addPadding(amount)

	def _togglePreview(self):
		self.ui.label.togglePreview()

	def _toggleOriginal(self):
		backupPath, wallpaperPath = self._getPaths()
		if (os.path.isfile(backupPath)):
			if (self.ui.label.toggleOriginal(backupPath)):
				self.setWindowTitle(backupPath)
			else:
				self.setWindowTitle(self.imagePath+"*")

