#!/usr/bin/python3

import sys
from PySide.QtCore import *
from PySide.QtGui import *
from QPainter import *

class FramedLabel(QLabel):
	"""Label that draws a crop indication on an image.

	Works like a QLabel but if you call setImage() then a
	yellow border will be drawn to indicate the way in which
	the image will be cropped.

	Call setDesktop() to set the desktop size.
	"""

	desktopWidth = 1
	desktopHeight = 1
	image = None
	frameRect = None

	def __init__(self, text: str):
		super().__init__(text)
		self.setMinimumSize(1, 1) # allow resizing smaller!

	def setText(self, text):
		self.image = None
		super().setText(text)

	def setImage(self, image: QImage):
		self.image = image
		pixmap = QPixmap.fromImage(image)
		assert(pixmap.isNull() == False)
		self.setPixmap(pixmap)
		self._setFrameRect()

	def setDesktop(self, width: int, height: int):
		self.desktopWidth = width
		self.desktopHeight = height
		self._setFrameRect()

	def resizeEvent(self, e):
		if (self.image != None):
			self._setFrameRect()

	def _setFrameRect(self):
		self.frameRect = None
		if (self.image == None):
			return

		x = 0
		y = 0
		width = self.image.height() / self.desktopHeight * self.desktopWidth
		if (width > self.image.width()):
			width = self.image.width()
		height = self.image.width() / self.desktopWidth * self.desktopHeight
		if (height > self.image.height()):
			height = self.image.height()
		x = self.width() / 2 - (width / 2)
		y = self.height() / 2 - (height / 2)
		self.frameRect = QRect(x, y, width - 1, height - 1)

	def paintEvent(self, e):
		super().paintEvent(e) # text or pixmap
		if (self.frameRect == None):
			return

		with QPainter(self) as p:
			p.setPen(Qt.yellow)
			p.drawRect(self.frameRect)
