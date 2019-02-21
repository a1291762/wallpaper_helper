#!/usr/bin/python3

import sys
from PySide.QtGui import *
from PySide.QtCore import *

class FramedLabel(QLabel):

	desktopWidth = 1
	desktopHeight = 1
	image = None
	frameRect = None

	def __init__(self, text):
		super(FramedLabel, self).__init__(text)
		self.setMinimumSize(1, 1)

	def setText(self, text):
		self.image = None
		super(FramedLabel, self).setText(text)

	def setImage(self, image):
		self.image = image
		pixmap = QPixmap.fromImage(image)
		assert(pixmap.isNull() == False)
		self.setPixmap(pixmap)
		self.setFrameRect()

	def setDesktop(self, width, height):
		self.desktopWidth = width
		self.desktopHeight = height
		self.setFrameRect()

	def resizeEvent(self, e):
		if (self.image != None):
			self.setFrameRect()

	def setFrameRect(self):
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
		super(FramedLabel, self).paintEvent(e)
		if (self.frameRect == None):
			return

		p = QPainter()
		p.begin(self)

		p.setPen(Qt.yellow)
		p.drawRect(self.frameRect)

		p.end()
