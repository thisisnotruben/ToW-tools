#!/usr/bin/env python3

from PyQt5.QtWidgets import QAction


class ISerializable:
	"""Interface to deal with I/O"""

	def serialize(self):
		"""returns an `OrderedDict`"""
		raise NotImplementedError()

	def unserialize(self, data):
		"""sets data from a `Dictionary`"""
		raise NotImplementedError()


class Dirty:
	"""Abstract class to deal check if editable
	was edited and (un)saved, is made not
	dirty by setting `dirty` to `False`
	when an `ISerializable` calls `serialize`"""

	def __init__(self):
		super().__init__()
		self.dirty = False
		self.onDirty = QAction()
		self.onDirty.setEnabled(False)

	def setDirty(self, *args, **kwargs):
		if not self.dirty:
			self.dirty = True
			self.onDirty.trigger()

	def routeDirtiables(self, parent):
		"""route all editables to parent `setDirty`"""
		raise NotImplementedError()

