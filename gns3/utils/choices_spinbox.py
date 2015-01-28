# -*- coding: utf-8 -*-
from ..qt import QtGui


class ChoicesSpinBox(QtGui.QSpinBox):

    """
    A custom QSpinBox that shows only values contained in `choices` iterable
    """

    def __init__(self, choices, parent=None):
        super(ChoicesSpinBox, self).__init__(parent)

        self._choices = choices
        self._current_idx = 0
        self.setRange(min(choices), max(choices))

    def stepBy(self, p_int):
        idx = self._current_idx + p_int
        if idx < 0:
            idx = 0
        elif idx >= len(self._choices):
            idx = len(self._choices) - 1

        self._current_idx = idx
        self.setValue(self._choices[idx])

    def setValue(self, p_int):
        try:
            self._current_idx = self._choices.index(p_int)
        except ValueError:
            if p_int > self.maximum():
                p_int = self.maximum()
                self._current_idx = len(self._choices) - 1
            elif p_int < self.minimum():
                p_int = self.minimum()
                self._current_idx = 0

        super(ChoicesSpinBox, self).setValue(p_int)
