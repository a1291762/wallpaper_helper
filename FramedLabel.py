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
	scaledImage = None
	frameRect = None

	def __init__(self, text: str):
		super().__init__(text)
		self.setMinimumSize(1, 1) # allow resizing smaller!

	def setText(self, text):
		self.image = None
		super().setText(text)

	def setImage(self, image: QImage):
		self.image = image
		self._setPixmapFromImage()

	def _setPixmapFromImage(self):
		# Scale the image first
		self.scaledImage = self.image.scaled(
			self.width(),
			self.height(),
			Qt.KeepAspectRatio)
		assert(self.scaledImage.isNull() == False)
		# Needs to be a pixmap for display
		scaledPixmap = QPixmap.fromImage(self.scaledImage)
		assert(scaledPixmap.isNull() == False)
		self.setPixmap(scaledPixmap)
		self._calculateFrameRect()

	def setDesktop(self, width: int, height: int):
		self.desktopWidth = width
		self.desktopHeight = height
		self._calculateFrameRect()

	def resizeEvent(self, e):
		if (self.image == None): return
		self._setPixmapFromImage()

	def _calculateFrameRect(self):
		self.frameRect = None
		if (self.image == None):
			return

		#print("scaled "+str(self.scaledImage.rect()))
		#print("label "+str(self.rect()))
		width = self.scaledImage.width()
		height = self.scaledImage.height()
		if (self.image.width() != self.desktopWidth or self.image.height() != self.desktopHeight):
			# The image is too wide or high... frame needs to be smaller
			if ((width > height) == (self.desktopWidth > self.desktopHeight)):
				#print("too tall")
				height = round(width / float(self.desktopWidth) * self.desktopHeight)
			else:
				#print("too fat")
				width = round(height / float(self.desktopHeight) * self.desktopWidth)
		#else:
		#	print("just right!")

		# FIXME between the width/height calculations above and these calculations here,
		# it's extremely likely that the frame will NOT be drawn on the correct pixels
		x = (self.width() / float(2)) - (width / float(2))
		y = (self.height() / float(2)) - (height / float(2))
		self.frameRect = QRect(x, y, width - 1, height - 1)

		#print("frame "+str(self.frameRect))
		#print("")

	def paintEvent(self, e):
		super().paintEvent(e) # text or pixmap
		if (self.frameRect == None):
			return

		with QPainter(self) as p:
			p.setPen(Qt.yellow)
			p.drawRect(self.frameRect)
