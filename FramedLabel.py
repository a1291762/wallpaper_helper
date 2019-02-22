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

		frameRect = self._calculateFrameRect()
		with QPainter(self) as p:
			p.setPen(Qt.yellow)
			p.drawRect(frameRect)

	def _calculateFrameRect(self):
		"""self.clipRect needs to be scaled down to fit the display size"""

		if (self.scaledImage.width() < self.width()):
			offset_y = 0
			offset_x = (self.width() - self.scaledImage.width()) / 2.0
		else:
			offset_x = 0
			offset_y = (self.height() - self.scaledImage.height()) / 2.0
		#offset = QPoint(offset_x, offset_y)
		#print(f"The offset is {offset}")

		#print(f"The clipRect is {self.clipRect}")
		ratio = self.scaledImage.width() / float(self.desktopImage.width())
		#print(f"ratio {ratio}")
		x = self.clipRect.x() * ratio
		y = self.clipRect.y() * ratio
		width = self.clipRect.width() * ratio
		height = self.clipRect.height() * ratio
		#rect = QRect(x, y, width, height)
		#print(f"The scaled rect is {rect}")
		x += offset_x
		y += offset_y
		# drawRect wants the size to be one pixel less?
		width -= 1
		height -= 1
		rect = QRectF(x, y, width, height)
		#print(f"The frame rect is {rect}")
		return rect

	def mousePressEvent(self, e):
		print(e.pos())

	def mouseMoveEvent(self, e):
		print(e.pos())

	def mouseReleaseEvent(self, e):
		print(e.pos())
