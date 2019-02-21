#!/usr/bin/python3

import sys
from PySide.QtCore import *
from PySide.QtGui import *
from os.path import basename

class PathButton(QPushButton):

	name = None
	path = None

	def __init__(self, parent):
		super().__init__(parent)

	def setSettingsKey(self, name):
		self.name = name
		settings = QSettings()
		self.setPath(settings.value(name))
		self.clicked.connect(self.pathClicked)

	def setPath(self, path):
		self.path = path
		if (path):
			self.setText(basename(path))
			self.setStyleSheet("")
			settings = QSettings()
			settings.setValue(self.name, path)
		else:
			self.setStyleSheet("background-color:red")

	def pathClicked(self):
		newPath = QFileDialog.getExistingDirectory(None, "Select the "+self.name+" folder", self.path)
		if (len(newPath) > 0):
			self.setPath(newPath)
