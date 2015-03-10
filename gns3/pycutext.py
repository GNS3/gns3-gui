# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This module implements a QT4 Python interpreter widget.
It is inspired by PyCute : http://gerard.vermeulen.free.fr
"""

import sys
from .qt import QtCore, QtGui


class PyCutExt(QtGui.QTextEdit):

    """
    PyCute is a Python shell for PyQt.

    Creating, displaying and controlling PyQt widgets from the Python command
    line interpreter is very hard, if not, impossible.  PyCute solves this
    problem by interfacing the Python interpreter to a PyQt widget.
    """

    def __init__(self, interpreter, message="", log="", parent=None):

        QtGui.QTextEdit.__init__(self, parent)

        self.interpreter = interpreter
        self.colorizer = SyntaxColor()

        # session log
        self.log = log or ''

        # to exit the main interpreter by a Ctrl-D if PyCute has no parent
        if parent is None:
            self.eofKey = QtCore.Qt.Key_D
        else:
            self.eofKey = None

        # capture all interactive input/output
        sys.stdout = self
        # sys.stderr = MultipleRedirection((sys.stderr, self))
        sys.stdin = self

        # last line + last incomplete lines
        self.line = ""
        self.lines = []

        # the cursor position in the last line
        self.point = 0

        # flag: the interpreter needs more input to run the last lines.
        self.more = 0

        # flag: readline() is being used for e.g. raw_input() and input()
        self.reading = 0

        # history
        self.history = []
        self.pointer = 0
        self.cursor_pos = 0

        self.setLineWrapMode(QtGui.QTextEdit.NoWrap)

        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = ">>> "
        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = "... "

        self.write(message + '\n\n')
        self.write(sys.ps1)

    def get_interpreter(self):
        """
        Return the interpreter object
        """

        return self.interpreter

    def moveCursor(self, operation, mode=QtGui.QTextCursor.MoveAnchor):
        """
        Convenience function to move the cursor
        This function will be present in PyQT4.2
        """
        cursor = self.textCursor()
        cursor.movePosition(operation, mode)
        self.setTextCursor(cursor)

    def flush(self):
        """
        Simulate stdin, stdout, and stderr.
        """
        pass

    def isatty(self):
        """
        Simulate stdin, stdout, and stderr.
        """
        return 1

    def readline(self):
        """
        Simulate stdin, stdout, and stderr.
        """

        self.reading = 1
        self._clearLine()
        self.moveCursor(QtGui.QTextCursor.End)
        while self.reading:
            QtGui.QApplication.processEvents(QtCore.QEventLoop.AllEvents, 1000)
        if len(self.line) == 0:
            return '\n'
        else:
            return self.line

    def write(self, text, error=False, warning=False):
        """
        Simulates stdin, stdout, and stderr.
        """

        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)

        pos1 = cursor.position()
        cursor.insertText(text)

        self.cursor_pos = cursor.position()
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

        # Set the format
        cursor.setPosition(pos1, QtGui.QTextCursor.KeepAnchor)
        char_format = cursor.charFormat()
        if error:
            color = QtGui.QColor(255, 0, 0)  # red
        elif warning:
            color = QtGui.QColor(255, 128, 0)  # orange
        else:
            color = QtGui.QColor(0, 0, 0)  # black
        char_format.setForeground(QtGui.QBrush(color))
        cursor.setCharFormat(char_format)

    def writelines(self, text):
        """
        Simulate stdin, stdout, and stderr.
        """
        map(self.write, text)

    def _run(self):
        """
        Append the last line to the history list, let the interpreter execute
        the last line(s), and clean up accounting for the interpreter results:
        (1) the interpreter succeeds
        (2) the interpreter fails, finds no errors and wants more line(s)
        (3) the interpreter fails, finds errors and writes them to sys.stderr
        """

        self.pointer = 0
        self.history.append(self.line)
        try:
            self.lines.append(self.line)
        except Exception as e:
            print(e)

        source = '\n'.join(self.lines)
        self.more = self.interpreter.runsource(source)

        if self.more:
            self.write(sys.ps2)
        else:
            self.write(sys.ps1)
            self.lines = []
        self._clearLine()

    def _clearLine(self):
        """
        Clear input line buffer
        """
        self.line = ""
        self.point = 0

    def _insertText(self, text):
        """
        Inserts text at the current cursor position.
        """

        self.line = self.line[:self.point] + text + self.line[self.point:]
        self.point += len(text)

        cursor = self.textCursor()
        cursor.insertText(text)
        self.color_line()

    def keyPressEvent(self, e):
        """
        Handle user input a key at a time.
        """

        text = e.text()
        key = e.key()

        if e.modifiers() == QtCore.Qt.ControlModifier:
            return super().keyPressEvent(e)

        # Keep the cursor after the last prompt.
        self.moveCursor(QtGui.QTextCursor.End)

        if key == QtCore.Qt.Key_Backspace:
            if self.point:
                cursor = self.textCursor()
                cursor.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor)
                cursor.removeSelectedText()
                self.color_line()

                self.point -= 1
                self.line = self.line[:-1]

        elif key == QtCore.Qt.Key_Delete:
            cursor = self.textCursor()
            cursor.movePosition(QtGui.QTextCursor.NextCharacter, QtGui.QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            self.color_line()

            self.line = self.line[:-1]

        elif key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            self.write("\n")
            if self.reading:
                self.reading = 0
            else:
                self._run()

        elif key == QtCore.Qt.Key_Tab:
            self.onKeyPress_Tab()
        elif key == QtCore.Qt.Key_Left:
            if self.point:
                self.moveCursor(QtGui.QTextCursor.Left)
                self.point -= 1
        elif key == QtCore.Qt.Key_Right:
            if self.point < len(self.line):
                self.moveCursor(QtGui.QTextCursor.Right)
                self.point += 1

        elif key == QtCore.Qt.Key_Home:
            cursor = self.textCursor()
            cursor.setPosition(self.cursor_pos)
            self.setTextCursor(cursor)
            self.point = 0

        elif key == QtCore.Qt.Key_End:
            self.moveCursor(QtGui.QTextCursor.EndOfLine)
            self.point = len(self.line)

        elif key == QtCore.Qt.Key_Up:

            if len(self.history):
                if self.pointer == 0:
                    self.pointer = len(self.history)
                self.pointer -= 1
                self._recall()

        elif key == QtCore.Qt.Key_Down:
            if len(self.history):
                self.pointer += 1
                if self.pointer == len(self.history):
                    self.pointer = 0
                self._recall()

        elif len(text):
            self._insertText(text)
            return

    def _recall(self):
        """
        Display the current item from the command history.
        """

        cursor = self.textCursor()
        cursor.select(QtGui.QTextCursor.LineUnderCursor)
        cursor.removeSelectedText()

        if self.more:
            self.write(sys.ps2)
        else:
            self.write(sys.ps1)

        self._clearLine()
        self._insertText(self.history[self.pointer])

    def contentsContextMenuEvent(self, ev):
        """
        Suppress the right button context menu.
        """

        return

    def color_line(self):
        """
        Color the current line.
        """

        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.StartOfLine)

        newpos = cursor.position()
        pos = -1

        while (newpos != pos):
            cursor.movePosition(QtGui.QTextCursor.NextWord)

            pos = newpos
            newpos = cursor.position()

            cursor.select(QtGui.QTextCursor.WordUnderCursor)
            word = cursor.selectedText()

            if not word:
                continue

            (R, G, B) = self.colorizer.get_color(word)
            char_format = cursor.charFormat()
            char_format.setForeground(QtGui.QBrush(QtGui.QColor(R, G, B)))
            cursor.setCharFormat(char_format)


class SyntaxColor(object):

    """
    Allows to color python keywords.
    """

    keywords = set(["and", "del", "from", "not", "while",
                    "as", "elif", "global", "or", "with",
                    "assert", "else", "if", "pass", "yield",
                    "break", "except", "import", "print",
                    "class", "exec", "in", "raise",
                    "continue", "finally", "is", "return",
                    "def", "for", "lambda", "try"])

    def get_color(self, word):
        """ Return a color tuple (R,G,B) depending of the string word """

        stripped = word.strip()

        if(stripped in self.keywords):
            return (165, 42, 42)   # brown
        elif(self.is_python_string(stripped)):
            return (61, 120, 9)   # dark green
        else:
            return (0, 0, 0)

    def is_python_string(self, string):
        """
        Return True if string is enclosed by a string mark
        """

#         return (
#             (string.startswith("'''") and string.endswith("'''")) or
#             (string.startswith('"""') and string.endswith('"""')) or
#             (string.startswith("'") and string.endswith("'")) or
#             (string.startswith('"') and string.endswith('"'))
#             )
        return False
