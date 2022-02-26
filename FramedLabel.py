#!/usr/bin/python3

import sys
try:
	from PySide6.QtCore import *
	from PySide6.QtGui import *
	from PySide6.QtWidgets import *
except Exception:
	try:
		from PySide2.QtCore import *
		from PySide2.QtGui import *
		from PySide2.QtWidgets import *
	except Exception:
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
	preview = None

	def __init__(self, text: str):
		super().__init__(text)
		self.setMinimumSize(1, 1) # allow resizing smaller

	def setText(self, text):
		self.preview = self.originalImage = self.desktopImage = self.clipRect = None
		super().setText(text)

	def setImage(self, image: QImage):
		self.originalImage = image
		self.preview = None
		self._resetImage()

	def setDesktop(self, width: int, height: int):
		self.desktopWidth = width
		self.desktopHeight = height
		self._resetImage()

	def _resetImage(self):
		if not (self.originalImage and self.desktopWidth and self.desktopHeight):
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
		image = self.originalImage if not self.preview else self.preview
		self.scaledImage = image.scaled(
			self.width(),
			self.height(),
			Qt.KeepAspectRatio) # ,Qt.SmoothTransformation)
		scaledPixmap = QPixmap.fromImage(self.scaledImage)
		self.setPixmap(scaledPixmap)
		#update()

	def resizeEvent(self, e):
		if self.originalImage == None:
			return
		self._setPixmapFromImage()

	def paintEvent(self, e):
		super().paintEvent(e) # text or pixmap
		if self.originalImage == None or self.preview:
			return

		frameRect = self._calculateFrameRect(self.scaledImage.size(), self.size())
		# drawRect wants the size to be one pixel less?
		frameRect.adjust(0, 0, -1, -1)
		with QPainter(self) as p:
			p.setPen(Qt.yellow)
			p.drawRect(frameRect)

	def _calculateFrameRect(self, imageSize, selfSize):
		"""self.clipRect needs to be scaled down to fit the display size"""

		if imageSize.width() < selfSize.width():
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
		if self.scaledImage == None or self.preview:
			return
		#print(e.pos())
		self.mousePos = e.pos()

	def mouseMoveEvent(self, e):
		if self.scaledImage == None or self.preview:
			return
		#print(e.pos())
		pos = self.mousePos
		self.mousePos = e.pos()

		movement = e.pos() - pos
		#print(f"movement {movement}")
		ratio = self.scaledImage.width() / float(self.desktopImage.width())
		movement.setX(movement.x() / ratio)
		movement.setY(movement.y() / ratio)

		self.moveFrame(movement)

	def mouseReleaseEvent(self, e):
		if self.scaledImage == None or self.preview:
			return
		#print(e.pos())
		self.mousePos = None

	def wheelEvent(self, e):
		if self.scaledImage == None or self.preview:
			return
		# mouse step = 15 degrees
		# delta is 1/8 degree increments
		try:
			delta = e.angleDelta().y()
		except Exception:
			delta = e.delta()
		steps = -(delta / 8) / 15
		#print(steps)

		# scale steps so that 50 steps == whole image (shortest size)
		if self.desktopWidth > self.desktopHeight:
			steps *= (self.desktopImage.height() / 50)
		else:
			steps *= (self.desktopImage.width() / 50)

		# make sure steps is at least 1
		if steps > -1 and steps < 0:
			steps = -1
		if steps < 1 and steps > 0:
			steps = 1

		self.addPadding(steps)

	def saveImage(self, fileName):
		origSize = self.originalImage.size()
		rect = self._calculateFrameRect(origSize, origSize)
		rect = rect.toRect() # can't use rectF with QImage
		clipped = self.originalImage.copy(rect)
		clipped.save(fileName)

	def addPadding(self, amount):
		if self.preview:
			return
		if self.desktopWidth > self.desktopHeight:
			height = self.clipRect.height() + amount
			width = height / float(self.desktopHeight) * self.desktopWidth
		else:
			width = self.clipRect.width() + amount
			height = width / float(self.desktopWidth) * self.desktopHeight
		if width < 1 or height < 1:
			# too small!
			return

		x = self.clipRect.x()
		y = self.clipRect.y()

		# Don't allow the border to go too big
		if x + width > self.desktopImage.width():
			width = self.desktopImage.width() - x
			height = width / float(self.desktopWidth) * self.desktopHeight
		if y + height > self.desktopImage.height():
			height = self.desktopImage.height() - y
			width = height / float(self.desktopHeight) * self.desktopWidth

		self.clipRect.setWidth(width)
		self.clipRect.setHeight(height)
		self.update()

	def togglePreview(self):
		if self.preview:
			self.preview = None
			self._setPixmapFromImage()
		else:
			origSize = self.originalImage.size()
			rect = self._calculateFrameRect(origSize, origSize)
			rect = rect.toRect() # can't use rectF with QImage
			self.preview = self.originalImage.copy(rect)
			self._setPixmapFromImage()

	def toggleOriginal(self, original):
		if self.preview:
			self.preview = None
			self._setPixmapFromImage()
			return False
		else:
			self.preview = QImage(original)
			self._setPixmapFromImage()
			return True

	def moveFrame(self, movement):
		# This is where the user has moved the clip rect to...
		topLeft = self.clipRect.topLeft() + movement
		# Don't allow the user to drag the clip rect off of the image
		if topLeft.x() < 0:
			topLeft.setX(0)
		if topLeft.y() < 0:
			topLeft.setY(0)
		if topLeft.x() + self.clipRect.width() > self.desktopImage.width():
			topLeft.setX(self.desktopImage.width() - self.clipRect.width())
		if topLeft.y() + self.clipRect.height() > self.desktopImage.height():
			topLeft.setY(self.desktopImage.height() - self.clipRect.height())

		self.clipRect.moveTopLeft(topLeft)
		self.update()

