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
	originalImage = None
	desktopImage = None
	clipRect = None
	mousePos = None

	def __init__(self, text: str):
		super().__init__(text)
		self.setMinimumSize(1, 1) # allow resizing smaller

	def setText(self, text):
		self.originalImage = self.desktopImage = self.clipRect = None
		super().setText(text)

	def setImage(self, image: QImage):
		self.originalImage = image
		self._resetImage()

	def setDesktop(self, width: int, height: int):
		self.desktopWidth = width
		self.desktopHeight = height
		self._resetImage()

	def _resetImage(self):
		if (not (self.originalImage and self.desktopWidth and self.desktopHeight)):
			self.desktopImage = self.clipRect = None
			return

		self.desktopImage = self.originalImage.scaled(
			self.desktopWidth,
			self.desktopHeight,
			Qt.KeepAspectRatioByExpanding)
		x = self.desktopImage.width() / 2.0 - self.desktopWidth / 2.0
		y = self.desktopImage.height() / 2.0 - self.desktopHeight / 2.0
		self.clipRect = QRect(x, y, self.desktopWidth, self.desktopHeight)
		self._setPixmapFromImage()

	def _setPixmapFromImage(self):
		# Needs to be a pixmap for display
		self.scaledImage = self.originalImage.scaled(
			self.width(),
			self.height(),
			Qt.KeepAspectRatio) # ,Qt.SmoothTransformation)
		scaledPixmap = QPixmap.fromImage(self.scaledImage)
		self.setPixmap(scaledPixmap)
		#update()

	def resizeEvent(self, e):
		if (self.originalImage == None):
			return
		self._setPixmapFromImage()

	def paintEvent(self, e):
		super().paintEvent(e) # text or pixmap
		if (self.originalImage == None):
			return

		frameRect = self._calculateFrameRect(self.scaledImage.size(), self.size())
		# drawRect wants the size to be one pixel less?
		frameRect.adjust(0, 0, -1, -1)
		with QPainter(self) as p:
			p.setPen(Qt.yellow)
			p.drawRect(frameRect)

	def _calculateFrameRect(self, imageSize, selfSize):
		"""self.clipRect needs to be scaled down to fit the display size"""

		if (imageSize.width() < selfSize.width()):
			offset_y = 0
			offset_x = (selfSize.width() - imageSize.width()) / 2.0
		else:
			offset_x = 0
			offset_y = (selfSize.height() - imageSize.height()) / 2.0
		#offset = QPoint(offset_x, offset_y)
		#print(f"The offset is {offset}")

		#print(f"The clipRect is {self.clipRect}")
		ratio = imageSize.width() / float(self.desktopImage.width())
		#print(f"ratio {ratio}")
		x = self.clipRect.x() * ratio
		y = self.clipRect.y() * ratio
		width = self.clipRect.width() * ratio
		height = self.clipRect.height() * ratio
		#rect = QRect(x, y, width, height)
		#print(f"The scaled rect is {rect}")
		x += offset_x
		y += offset_y
		rect = QRectF(x, y, width, height)
		#print(f"The frame rect is {rect}")
		return rect

	def mousePressEvent(self, e):
		if (self.scaledImage == None):
			return
		#print(e.pos())
		self.mousePos = e.pos()

	def mouseMoveEvent(self, e):
		if (self.scaledImage == None):
			return
		#print(e.pos())
		pos = self.mousePos
		self.mousePos = e.pos()

		movement = e.pos() - pos
		#print(f"movement {movement}")
		ratio = self.scaledImage.width() / float(self.desktopImage.width())
		movement.setX(movement.x() / ratio)
		movement.setY(movement.y() / ratio)

		# This is where the user has moved the clip rect to...
		topLeft = self.clipRect.topLeft() + movement
		# Don't allow the user to drag the clip rect off of the image
		if (topLeft.x() < 0):
			topLeft.setX(0)
		if (topLeft.y() < 0):
			topLeft.setY(0)
		if (topLeft.x() + self.clipRect.width() > self.desktopImage.width()):
			topLeft.setX(self.desktopImage.width() - self.clipRect.width())
		if (topLeft.y() + self.clipRect.height() > self.desktopImage.height()):
			topLeft.setY(self.desktopImage.height() - self.clipRect.height())

		self.clipRect.moveTopLeft(topLeft)
		self.update()

	def mouseReleaseEvent(self, e):
		if (self.scaledImage == None):
			return
		#print(e.pos())
		self.mousePos = None

	def saveImage(self, fileName):
		origSize = self.originalImage.size()
		rect = self._calculateFrameRect(origSize, origSize)
		rect = rect.toRect() # can't use rectF with QImage
		clipped = self.originalImage.copy(rect)
		clipped.save(fileName)

	def addPadding(self, amount):
		if (self.desktopWidth > self.desktopHeight):
			height = self.clipRect.height() + amount
			width = height / float(self.desktopHeight) * self.desktopWidth
		else:
			width = self.clipRect.width() + amount
			height = width / float(self.desktopWidth) * self.desktopHeight
		if (width < 1 or height < 1):
			# too small!
			return

		x = self.clipRect.x()
		y = self.clipRect.y()
		if (x + width > self.desktopImage.width() or
			y + height > self.desktopImage.height()):
			# too big!
			return

		self.clipRect.setWidth(width)
		self.clipRect.setHeight(height)
		self.update()