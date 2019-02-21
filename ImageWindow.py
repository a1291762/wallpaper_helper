#!/usr/bin/python3

import sys
from PySide.QtCore import QUrl
from PySide.QtGui import *
from Ui_ImageWindow import *

class ImageWindow(QMainWindow, Ui_ImageWindow):

	def __init__(self):
		super(ImageWindow, self).__init__()
		self.setupUi(self)

	def dragEnterEvent(self, e):
		self.label.setText(e.mimeData().text())
		e.accept()

	def dragLeaveEvent(self, e):
		self.label.setText("Drop an image onto the window")
		e.accept()

	def dropEvent(self, e):
		print("url "+e.mimeData().text())
		file = QUrl(e.mimeData().text()).toLocalFile().strip()
		print("file '"+file+"'")
		print(QImageReader.supportedImageFormats())
		image = QImage()
		ok = image.load(file)
		assert(ok)
		assert(image.isNull() == False)
		pixmap = QPixmap.fromImage(image)
		assert(pixmap.isNull() == False)
		#pixmap = pixmap.scaled(500, 500, QtCore.Qt.KeepAspectRatio)
		self.label.setPixmap(pixmap)
		#self.label.setText("")
		e.accept()
		