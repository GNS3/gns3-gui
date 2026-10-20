# SPDX-License-Identifier: GPL-3.0-or-later
"""Transactional, local previews of visual line styles."""

from ..qt import QtCore, QtGui, QtWidgets, sip_is_deleted


class LinePropertiesDialog(QtWidgets.QDialog):
    def __init__(self, parent, items):
        super().__init__(parent)
        self.setWindowTitle("Line properties")
        self._original = [(item, QtGui.QPen(item.pen())) for item in items]
        pen = items[0].pen()
        self._color = pen.color()
        form = QtWidgets.QFormLayout(self)
        self.lineStyle = QtWidgets.QComboBox(self)
        for label, style in (("Solid", QtCore.Qt.PenStyle.SolidLine),
                             ("Dashed", QtCore.Qt.PenStyle.DashLine),
                             ("Dotted", QtCore.Qt.PenStyle.DotLine),
                             ("Dash dot", QtCore.Qt.PenStyle.DashDotLine),
                             ("Dash dot dot", QtCore.Qt.PenStyle.DashDotDotLine)):
            self.lineStyle.addItem(label, style)
        self.lineStyle.setCurrentIndex(max(0, self.lineStyle.findData(pen.style())))
        self.thickness = QtWidgets.QSpinBox(self)
        self.thickness.setRange(1, 1000)
        self.thickness.setValue(max(1, pen.width()))
        self.thickness.setStyleSheet(
            "QSpinBox, QSpinBox QLineEdit { background-color: white; color: black; "
            "selection-background-color: #3484c6; selection-color: white; }")
        self.colorButton = QtWidgets.QPushButton(self)
        self.colorButton.clicked.connect(self.chooseColor)
        self.updateColorButton()
        form.addRow("Style:", self.lineStyle)
        form.addRow("Thickness:", self.thickness)
        form.addRow("Color:", self.colorButton)
        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok |
            QtWidgets.QDialogButtonBox.StandardButton.Cancel |
            QtWidgets.QDialogButtonBox.StandardButton.Apply, parent=self)
        self.buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        form.addRow(self.buttons)

    def updateColorButton(self):
        color = self._color
        foreground = "black" if color.lightnessF() > .5 or color.alphaF() < .5 else "white"
        self.colorButton.setText(color.name())
        self.colorButton.setStyleSheet("background-color: rgba({}, {}, {}, {}); color: {};".format(
            color.red(), color.green(), color.blue(), color.alpha(), foreground))

    def chooseColor(self):
        color = QtWidgets.QColorDialog.getColor(
            self._color, self, "Line color", QtWidgets.QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if color.isValid():
            self._color = color
            self.updateColorButton()

    def apply(self):
        pen = QtGui.QPen(self._color, self.thickness.value(),
                         self.lineStyle.currentData(), QtCore.Qt.PenCapStyle.RoundCap,
                         QtCore.Qt.PenJoinStyle.RoundJoin)
        for item, _ in self._original:
            if not sip_is_deleted(item):
                item.setPen(pen)

    def done(self, result):
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            self.apply()
        else:
            for item, pen in self._original:
                if not sip_is_deleted(item):
                    item.setPen(pen)
        super().done(result)
