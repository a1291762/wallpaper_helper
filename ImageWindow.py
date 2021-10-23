#!/usr/bin/python3

import sys
from PySide2.QtCore import *
from PySide2.QtGui import *
from Ui_ImageWindow import *
import os
import shutil
import filecmp

FORWARDS = False
BACKWARDS = True

def forceExt(path, ext):
	file = os.path.basename(path)
	path = os.path.dirname(path)
	return path + "/" + os.path.splitext(file)[0] + "." + ext

def forceJpeg(path):
	return forceExt(path, "jpg")

class ImageWindow(QMainWindow):

	image = None
	ui = None
	viewOnlyUnusedOriginals = False

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
		self.ui.wallpaper.setSettingsKey("wallpaper")
		self.ui.originals.setSettingsKey("originals")

		# help button
		self.ui.helpBtn.toggled.connect(self._toggleHelp)
		self._toggleHelp(False)

		# Load the initial image
		file = settings.value("image")
		self._loadInitialImage(file)

	def _loadInitialImage(self, file):
		if file:
			# load previous image
			try:
				self._loadFile(file)
				print("Loaded previous image")
				return
			except Exception as e:
				print("Failed to load initial image "+file+" "+str(e))
				pass # continue

		path = self.ui.wallpaper.path
		if path and os.path.exists(path) and os.path.isdir(path):
			# load the first image from the path
			self.imagePath = path + "/." # set imagePath to a file inside the wallpaper folder
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
			self.ui.label.setText("Drop an image onto the window")
		e.accept()

	def _setDesktopFrame(self, saveSettings):
		# Used to draw the clip rect
		self.ui.label.setDesktop(
			int(self.ui.deskWidth.text()),
			int(self.ui.deskHeight.text()))

		if saveSettings:
			settings = QSettings()
			settings.setValue("desktopWidth", self.ui.deskWidth.text())
			settings.setValue("desktopHeight", self.ui.deskHeight.text())

	def _loadFile(self, file):
		if self.viewOnlyUnusedOriginals:
			backupPath, wallpaperPath = self._getPaths(file)
			wallpaperPath = forceJpeg(wallpaperPath)
			if backupPath == file and not os.path.isfile(wallpaperPath):
				pass # This is an unused original
			else:
				raise Exception("Not an unused original")

		# make sure the image is valid
		image = QImage(file)
		assert(image.isNull() == False)
		self.ui.label.setImage(image)
		self.imagePath = file # for forwards/backwards moving
		settings = QSettings()
		settings.setValue("image", file) # for close/reopen

		title = file
		try:
			# Indicate if the original file is different to the wallpaper file
			backupPath, wallpaperPath = self._getPaths()
			if file != backupPath and \
				os.path.isfile(backupPath) and \
					not filecmp.cmp(file, backupPath):
				title += "*"
		except Exception as e:
			print("Error checking if backup and wallpaper differ?! "+str(e))
		self.setWindowTitle(title)

	def eventFilter(self, object, e):
		# I only want the key press events
		if e.type() != QEvent.KeyPress:
			return False

		handled = True
		modifiers = e.modifiers()
		key = e.key()
		if modifiers & Qt.ControlModifier:
			if   key == Qt.Key_S: 			self._useCroppedImage()				# control + S = use cropped image
			elif key == Qt.Key_R: 			self._useOriginalImage()			# control + R = use original image
			else: handled = False
		elif modifiers & Qt.ShiftModifier:
			if   key == Qt.Key_Right:		self._moveFrame(1, 0)				# Shift + Arrow = move frame (precise)
			elif key == Qt.Key_Left:		self._moveFrame(-1, 0)
			elif key == Qt.Key_Up:			self._moveFrame(0, -1)
			elif key == Qt.Key_Down:		self._moveFrame(0, 1)
			elif key == Qt.Key_O:			self._toggleUnusedOriginals()		# Shift + O = toggle unused originals
			else: handled = False
		else:
			if   key == Qt.Key_Right:		self._selectNextImage(FORWARDS)		# Right = Next
			elif key == Qt.Key_Left:		self._selectNextImage(BACKWARDS)	# Left = Prev
			elif key == Qt.Key_Minus:		self._addPadding(-1)				# Plus/Minus = grow/shrink (precise)
			elif key == Qt.Key_Plus:		self._addPadding(1)
			elif key == Qt.Key_Equal:		self._addPadding(1)
			elif key == Qt.Key_O:			self._toggleOriginal()				# O = toggle original
			elif key == Qt.Key_Space:		self._togglePreview()				# Space = toggle preview
			elif key == Qt.Key_Backspace:	self._removeImage()					# Do not use image
			else: handled = False

		if handled:
			e.accept()
			return True
		return False

	def _selectNextImage(self, backwards):
		path = os.path.dirname(self.imagePath)
		files = self._getImages(path)
		if len(files) == 0:
			print("No files?!")
			return

		# Simply by reversing the list, we can use the same logic to move backwards
		if backwards:
			files.reverse()

		if self.viewOnlyUnusedOriginals:
			if self._selectNextImage3(path, files):
				return
		else:
			if self._selectNextImage2(path, files):
				return

		print("load first file")
		file = path+"/"+files[0]
		try:
			self._loadFile(file)
		except Exception as e:
			print("exception: {}".format(e))
			self.ui.label.setText("Drop an image onto the window")


	def _selectNextImage2(self, path, files):
		startSearching = False
		for f in files:
			file = path+"/"+f
			if file == self.imagePath:
				startSearching = True
			elif startSearching:
				try:
					self._loadFile(file)
					return True
				except Exception as e:
					pass # keep looking


	def _selectNextImage3(self, path, files):
		startSearching = False
		for f in files:
			file = path+"/"+f
			if file == self.imagePath:
				startSearching = True
			elif startSearching:
				try:
					self._loadFile(file)
					return True
				except Exception as e:
					pass # keep looking

		# wrap around to the start
		for f in files:
			file = path+"/"+f
			if file == self.imagePath:
				return False # got to the end
			try:
				self._loadFile(file)
				return True
			except Exception as e:
				pass # keep looking


	def _getImages(self, path):
		#print(f"_getImages {path}")
		allFiles = os.listdir(path)
		#print(f"allFiles {allFiles}")
		allFiles.sort()
		files = []
		for f in allFiles:
			# skip hidden (dot) files
			if f[0] == ".": continue
			for fmt in QImageReader.supportedImageFormats():
				ext = "."+bytes(fmt).decode()
				if f.endswith(ext):
					files.append(f)
					break
		return files

	def _getPaths(self, imagePath = None):
		if imagePath == None:
			imagePath = self.imagePath
		backupPath = self.ui.originals.path
		wallpaperPath = self.ui.wallpaper.path
		if not backupPath or not wallpaperPath:
			print("Both the wallpaper and originals paths must be set!")
			return None, None
		fileName = os.path.basename(imagePath)
		backupPath += "/"+fileName
		if not os.path.isfile(backupPath):
			#print("trying alternative backupPath values...")
			for fmt in QImageReader.supportedImageFormats():
				altPath = forceExt(backupPath, str(fmt))
				#print("altPath "+altPath)
				if os.path.isfile(altPath):
					backupPath = altPath
					break
		wallpaperPath += "/"+fileName
		return backupPath, wallpaperPath

	def _useCroppedImage(self):
		backupPath, wallpaperPath = self._getPaths()
		if not backupPath or not wallpaperPath:
			return

		# If original doesn't exist, create it
		if not os.path.isfile(backupPath):
			shutil.copy(self.imagePath, backupPath)

		# Save cropped image
		origWallpaperPath = wallpaperPath
		if os.path.isfile(wallpaperPath):
			os.remove(wallpaperPath)
		wallpaperPath = forceJpeg(wallpaperPath)
		self.ui.label.saveImage(wallpaperPath)

		# If the wallpaper image is open, reload it
		# If another path was opened, do nothing
		if wallpaperPath == self.imagePath or \
				origWallpaperPath == self.imagePath:
			self._loadFile(self.imagePath)

	def _useOriginalImage(self):
		backupPath, wallpaperPath = self._getPaths()
		if not backupPath or not wallpaperPath:
			return

		# If original doesn't exist, create it
		if not os.path.isfile(backupPath):
			if wallpaperPath == self.imagePath:
				shutil.move(self.imagePath, backupPath)
			else:
				shutil.copy(self.imagePath, backupPath)

		# Save uncropped image
		origWallpaperPath = wallpaperPath
		if backupPath.endswith(".jpg"):
			shutil.copy(backupPath, wallpaperPath)
		else:
			if os.path.isfile(wallpaperPath):
				os.remove(wallpaperPath)
			wallpaperPath = forceJpeg(wallpaperPath)
			QImage(backupPath).save(wallpaperPath)

		# If the wallpaper image is open, reload it
		# If another path was opened, do nothing
		if wallpaperPath == self.imagePath or \
				origWallpaperPath == self.imagePath:
			self._loadFile(self.imagePath)

	def _addPadding(self, amount):
		self.ui.label.addPadding(amount)

	def _togglePreview(self):
		self.ui.label.togglePreview()

	def _toggleOriginal(self):
		backupPath, wallpaperPath = self._getPaths()
		if os.path.isfile(backupPath):
			if self.ui.label.toggleOriginal(backupPath):
				self.setWindowTitle(backupPath)
			else:
				self.setWindowTitle(self.imagePath+"*")

	def _moveFrame(self, x, y):
		self.ui.label.moveFrame(QPoint(x, y))

	def _toggleUnusedOriginals(self):
		if self.viewOnlyUnusedOriginals:
			self.viewOnlyUnusedOriginals = False
		else:
			self.viewOnlyUnusedOriginals = True

	def _removeImage(self):
		backupPath, wallpaperPath = self._getPaths()
		if not backupPath or not wallpaperPath:
			return

		# If original doesn't exist, create it
		if not os.path.isfile(backupPath):
			shutil.move(self.imagePath, backupPath)

		# only remove the wallpaper (not an out-of-wallpaper image)
		if self.imagePath == wallpaperPath:
			os.remove(self.imagePath)

	def _toggleHelp(self, visible):
		if visible:
			self.ui.help.show()
		else:
			self.ui.help.hide()