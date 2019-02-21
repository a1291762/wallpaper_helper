#!/usr/bin/python3

import sys
from PySide.QtGui import *
from Ui_ImageWindow import *

class ImageWindow(QMainWindow, Ui_ImageWindow):

	def __init__(self):
		super(ImageWindow, self).__init__()
		self.setupUi(self)
