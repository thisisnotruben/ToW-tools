#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

from collections import OrderedDict


class ISerializable:
    """Interface to deal with I/O"""

    def serialize(self):
        """returns OrderedDict"""
        raise NotImplementedError()

    def unserialize(self, data):
        """sets data from Dictionary"""
        raise NotImplementedError()

