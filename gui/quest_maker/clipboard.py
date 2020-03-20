#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

from gui.quest_maker.ISerializable import OrderedDict


class Clipboard:

    historyStack = []
    current_idx = 0
    last_saved_idx = 0

    @classmethod
    def redo(cls):
        # go foward
        if len(cls.historyStack) > 0:
            if cls.current_idx < len(cls.historyStack) - 1:
                cls.current_idx += 1
            return cls.historyStack[cls.current_idx]
        return OrderedDict()

    @classmethod
    def undo(cls):
        # go back
        if len(cls.historyStack) > 0:
            if cls.current_idx > 0:
                cls.current_idx -= 1
            return cls.historyStack[cls.current_idx]
        return OrderedDict()

    @classmethod
    def reached_end(cls):
        empty_stack = len(cls.historyStack) == 0
        left = empty_stack or cls.current_idx == 0
        right = empty_stack \
            or cls.current_idx == len(cls.historyStack) - 1
        return (left, right)

    @classmethod
    def isHistoryCurrent(cls):
        return cls.current_idx == cls.last_saved_idx

    @classmethod
    def clearHistoryStack(cls):
        # new file
        cls.historyStack = []
        cls.current_idx = 0
        cls.last_saved_idx = 0

    @classmethod
    def addToHistory(cls, data):
        # save file
        cls.historyStack.append(data)
        cls.last_saved_idx = cls.historyStack.index(data)
        cls.current_idx = cls.last_saved_idx
        
