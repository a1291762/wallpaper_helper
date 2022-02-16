#!/usr/bin/python3

import sys
try:
	import PySide6.QtGui as QtGui
except Exception:
	try:
		import PySide2.QtGui as QtGui
	except Exception:
		import PySide.QtGui as QtGui

class QPainter(QtGui.QPainter):
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
		from PySide6.QtGui import *
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
