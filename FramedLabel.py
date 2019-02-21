#!/usr/bin/python3

import sys
from PySide.QtCore import *
from PySide.QtGui import *

class FramedLabel(QLabel):

	_desktopWidth = 1
	_desktopHeight = 1
	_image = None
	_frameRect = None

	def __init__(self, text):
		super(FramedLabel, self).__init__(text)
		self.setMinimumSize(1, 1)

	def setText(self, text):
		self._image = None
		super(FramedLabel, self).setText(text)

	def setImage(self, image):
		self._image = image
		pixmap = QPixmap.fromImage(image)
		assert(pixmap.isNull() == False)
		self.setPixmap(pixmap)
		self._setFrameRect()

	def setDesktop(self, width, height):
		self._desktopWidth = width
		self._desktopHeight = height
		self._setFrameRect()

	def resizeEvent(self, e):
		if (self._image != None):
			self._setFrameRect()

	def _setFrameRect(self):
		self._frameRect = None
		if (self._image == None):
			return

		x = 0
		y = 0
		width = self._image.height() / self._desktopHeight * self._desktopWidth
		if (width > self._image.width()):
			width = self._image.width()
		height = self._image.width() / self._desktopWidth * self._desktopHeight
		if (height > self._image.height()):
			height = self._image.height()
		x = self.width() / 2 - (width / 2)
		y = self.height() / 2 - (height / 2)
		self._frameRect = QRect(x, y, width - 1, height - 1)

	def paintEvent(self, e):
		super(FramedLabel, self).paintEvent(e)
		if (self._frameRect == None):
			return

		p = QPainter()
		p.begin(self)

		p.setPen(Qt.yellow)
		p.drawRect(self._frameRect)

		p.end()
