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
	originalImage = None	# as-loaded
	paddedImage = None		# padded so that the whole picture can be seen after clipping
	clipRect = None			# defaults to part of the image (no padding visible)
	preview = None			# a clipped copy of the image for better "full screen" preview
	scaledImage = None		# the padded image scaled for display
	paddingBackground = Qt.black

	movingFrame = False
	tmpEraseRect = None		# for drawing the drag
	eraseRect = None		# used when saving the image
	mouseDownPos = None
	mousePos = None

	def __init__(self, text: str):
		super().__init__(text)
		self.setMinimumSize(1, 1) # allow resizing smaller

	def setText(self, text):
		self.originalImage = self.paddedImage = self.clipRect = self.preview = self.scaledImage = None
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
		self.eraseRect = None
		if not (self.originalImage and self.desktopWidth and self.desktopHeight):
			self.paddedImage = self.clipRect = None
			return

		imageSize = self.originalImage.size()
		clipWidth = imageSize.width()
		clipHeight = imageSize.height()
		paddedWidth = imageSize.width()
		paddedHeight = imageSize.height()
		if imageSize.width() / float(imageSize.height()) > self.desktopWidth / float(self.desktopHeight):
			clipWidth = int(imageSize.height() / float(self.desktopHeight) * self.desktopWidth) + 1
			paddedHeight = int(paddedWidth / float(self.desktopWidth) * self.desktopHeight) + 1
		else:
			clipHeight = int(imageSize.width() / float(self.desktopWidth) * self.desktopHeight) + 1
			paddedWidth = int(paddedHeight / float(self.desktopHeight) * self.desktopWidth) + 1
		#print(f"imageSize   {imageSize.width()} {imageSize.height()}")
		#print(f"clip size   {clipWidth} {clipHeight}")
		#print(f"padded size {paddedWidth} {paddedHeight}")

		x = (paddedWidth / 2) - (clipWidth / 2)
		if x < 0: x = 0
		y = (paddedHeight / 2) - (clipHeight / 2)
		if y < 0: y = 0

		self.clipRect = QRect(x, y, clipWidth, clipHeight)
		self._setPaddedFromImage()

	def _setPaddedFromImage(self):
		imageSize = self.originalImage.size()
		paddedWidth = imageSize.width()
		paddedHeight = imageSize.height()
		if imageSize.width() / float(imageSize.height()) > self.desktopWidth / float(self.desktopHeight):
			paddedHeight = int(paddedWidth / float(self.desktopWidth) * self.desktopHeight) + 1
		else:
			paddedWidth = int(paddedHeight / float(self.desktopHeight) * self.desktopWidth) + 1
		#print(f"scaled size {paddedWidth} {paddedHeight}")

		x = (paddedWidth / 2) - (imageSize.width() / 2)
		if x < 0: x = 0
		y = (paddedHeight / 2) - (imageSize.height() / 2)
		if y < 0: y = 0

		scaledPixmap = QPixmap(paddedWidth, paddedHeight)
		scaledPixmap.fill(self.palette().color(self.backgroundRole()))
		with QPainter(scaledPixmap) as p:
			p.setPen(self.paddingBackground)
			p.setBrush(self.paddingBackground)
			p.drawRect(self.clipRect)
			p.drawImage(x, y, self.originalImage)
			if self.eraseRect is not None:
				p.drawRect(self.eraseRect)
		self.paddedImage = scaledPixmap.toImage()
		self._setPixmapFromImage()

	def _setPixmapFromImage(self):
		# Needs to be a pixmap for display
		image = self.paddedImage if not self.preview else self.preview
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
		frameRect.adjust(1, 1, 0, 0)
		with QPainter(self) as p:
			p.setPen(Qt.yellow)
			p.drawRect(frameRect)

		if self.tmpEraseRect is not None:
			with QPainter(self) as p:
				p.setPen(self.paddingBackground)
				p.setBrush(self.paddingBackground)
				p.drawRect(self.tmpEraseRect)

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
		ratio = imageSize.width() / float(self.paddedImage.width())
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

	def labelToImage(self, pos):
		x = pos.x()
		y = pos.y()
		x -= int((self.width() - self.scaledImage.width()) / 2.0)
		y -= int((self.height() - self.scaledImage.height()) / 2.0)
		return QPoint(x, y)

	def mousePressEvent(self, e):
		if self.scaledImage == None or self.preview:
			return
		pos = e.pos()
		print(f"mousePressEvent {pos}")
		self.mouseDownPos = pos
		self.mousePos = pos

		if (QGuiApplication.keyboardModifiers() & Qt.ShiftModifier) != 0:
			self.tmpEraseRect = QRect(pos, pos)

	def mouseMoveEvent(self, e):
		if self.scaledImage == None or self.preview:
			return
		pos = e.pos()
		print(f"mouseMoveEvent {pos}")

		if self.tmpEraseRect is None:
			self.movingFrame = True
		else:
			self.tmpEraseRect.setBottomRight(e.pos())
			print(f"eraseRect {self.tmpEraseRect}")
			self.update()

		if self.movingFrame:
			pos = self.mousePos
			self.mousePos = e.pos()

			movement = e.pos() - pos
			print(f"movement {movement}")
			ratio = self.scaledImage.width() / float(self.paddedImage.width())
			movement.setX(movement.x() / ratio)
			movement.setY(movement.y() / ratio)

			self.moveFrame(movement)
			self._setPaddedFromImage()

	def mouseReleaseEvent(self, e):
		if self.scaledImage == None or self.preview:
			return
		pos = e.pos()
		print(f"mouseReleaseEvent {pos}")

		if self.movingFrame:
			self.movingFrame = False
		elif self.tmpEraseRect is not None:
			ratio = self.paddedImage.width() / float(self.scaledImage.width())
			topLeft = self.labelToImage(self.tmpEraseRect.topLeft())
			x = topLeft.x() * ratio
			y = topLeft.y() * ratio
			w = self.tmpEraseRect.width() * ratio
			h = self.tmpEraseRect.height() * ratio
			self.eraseRect = QRect(x, y, w, h)
			self.tmpEraseRect = None
		elif pos == self.mouseDownPos:
			pixel = self.scaledImage.pixelColor(self.labelToImage(pos))
			self.paddingBackground = pixel

		self.mousePos = None
		self._setPaddedFromImage()

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
			steps *= (self.paddedImage.height() / 50)
		else:
			steps *= (self.paddedImage.width() / 50)

		# make sure steps is at least 1
		if steps > -1 and steps < 0:
			steps = -1
		if steps < 1 and steps > 0:
			steps = 1

		self.addPadding(steps)

	def saveImage(self, fileName):
		origSize = self.paddedImage.size()
		rect = self._calculateFrameRect(origSize, origSize)
		rect = rect.toRect() # can't use rectF with QImage
		clipped = self.paddedImage.copy(rect)
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
		if x + width > self.paddedImage.width():
			width = self.paddedImage.width() - x
			height = width / float(self.desktopWidth) * self.desktopHeight
		if y + height > self.paddedImage.height():
			height = self.paddedImage.height() - y
			width = height / float(self.desktopHeight) * self.desktopWidth

		self.clipRect.setWidth(width)
		self.clipRect.setHeight(height)
		self._setPaddedFromImage()
		#self.update()

	def togglePreview(self):
		if self.preview:
			self.preview = None
			self._setPixmapFromImage()
		else:
			origSize = self.paddedImage.size()
			rect = self._calculateFrameRect(origSize, origSize)
			rect = rect.toRect() # can't use rectF with QImage
			self.preview = self.paddedImage.copy(rect)
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

		min_x = 0
		min_y = 0
		max_x = self.originalImage.width() - self.clipRect.width()
		max_y = self.originalImage.height() - self.clipRect.height()

		# print(f"moveFrame {min_x} {min_y} {max_x} {max_y}")
		if self.paddedImage.width() > self.originalImage.width():
			min_x = int((self.paddedImage.width() - self.originalImage.width()) / 2.0)
			max_x += min_x
			if self.clipRect.width() > self.originalImage.width():
				diff = self.clipRect.width() - self.originalImage.width()
				min_x -= diff
				max_x += diff
				if min_x < 0: min_x = 0
				if max_x > self.paddedImage.width() - self.clipRect.width(): max_x = self.paddedImage.width() - self.clipRect.width()
		if self.paddedImage.height() > self.originalImage.height():
			min_y = int((self.paddedImage.height() - self.originalImage.height()) / 2.0)
			max_y += min_y
			if self.clipRect.height() > self.originalImage.height():
				diff = self.clipRect.height() - self.originalImage.height()
				min_y -= diff
				max_y += diff
				if min_y < 0: min_y = 0
				if max_y > self.paddedImage.height() - self.clipRect.height(): max_y = self.paddedImage.height() - self.clipRect.height()
		# print(f"adjusted {min_x} {min_y} {max_x} {max_y}")

		# Don't allow the user to drag the clip rect off of the image
		# print(f"topLeft {topLeft}")
		if topLeft.x() < min_x: topLeft.setX(min_x)
		if topLeft.y() < min_y: topLeft.setY(min_y)
		if topLeft.x() > max_x: topLeft.setX(max_x)
		if topLeft.y() > max_y: topLeft.setY(max_y)
		# print(f"adjusted {topLeft}")

		self.clipRect.moveTopLeft(topLeft)
		self.update()

	def selectAll(self):
		self.clipRect = QRect(QPoint(0, 0), self.paddedImage.size())
		self._setPaddedFromImage()
