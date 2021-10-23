#!/usr/bin/python3

import sys
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import os

class PathButton(QPushButton):
	"""A button that represents a path.

	You must call setSettingsKey() for the button to work.
	The text of the button is the last part of the path only.
	Click the button to get a chooser.
	If no path is set, the button is red.
	"""

	settingsKey = None
	path = None

	def __init__(self, parent):
		super().__init__(parent)

	def setSettingsKey(self, settingsKey):
		self.settingsKey = settingsKey
		settings = QSettings()
		self._setPath(settings.value(settingsKey))
		self.clicked.connect(self._pathClicked)

	def _setPath(self, path):
		self.path = path
		if path:
			self.setText(os.path.basename(path))
			self.setStyleSheet("")
			settings = QSettings()
			settings.setValue(self.settingsKey, path)
		else:
			self.setStyleSheet("background-color:red")

	def _pathClicked(self):
		newPath = QFileDialog.getExistingDirectory(None, "Select the "+self.settingsKey+" folder", self.path)
		if len(newPath) > 0:
			self._setPath(newPath)
