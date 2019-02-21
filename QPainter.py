#!/usr/bin/python3

import sys
import PySide.QtGui

class QPainter(PySide.QtGui.QPainter):
	"""Add __enter__ and __exit__ methods so that the with statement can be used.

	before:
		p = QPainter()
		p.begin(self)
		# draw
		p.end()

	now:
		with QPainter(self) as p:
			# draw

	You can import like this to shadow the actual QPainter class:
		from PySide.QtGui import *
		from QPainter import *
	"""

	widget = None

	def __init__(self, widget):
		super().__init__()
		self.widget = widget

	def __enter__(self):
		self.begin(self.widget)
		return self

	def __exit__(self, type, value, traceback):
		self.end()
