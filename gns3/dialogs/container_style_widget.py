# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared, explicit container appearance controls; all values are serializable."""
from ..qt import QtCore, QtGui, QtWidgets

DEFAULT_STYLE = dict(shape='rect', border_color='#ff3484c6', border_width=1,
                     border_style=1, fill_color='#00000000')


def validated_style(value=None):
    result = dict(DEFAULT_STYLE)
    if value is not None:
        if not isinstance(value, dict):
            raise ValueError('Invalid container style')
        result.update({key: value[key] for key in DEFAULT_STYLE if key in value})
    if result['shape'] not in ('rect', 'triangle', 'ellipse'):
        raise ValueError('Invalid container shape')
    width = result['border_width']
    if isinstance(width, bool) or not isinstance(width, (int, float)) or not 0 <= width <= 100:
        raise ValueError('Invalid container border width')
    if type(result['border_style']) is not int or result['border_style'] not in range(6):
        raise ValueError('Invalid container border style')
    for key in ('border_color', 'fill_color'):
        if not isinstance(result[key], str) or not QtGui.QColor(result[key]).isValid():
            raise ValueError('Invalid container color')
    return result


class ContainerStyleWidget(QtWidgets.QWidget):
    def __init__(self, style=None, parent=None):
        super().__init__(parent)
        self.values = validated_style(style)
        form = QtWidgets.QFormLayout(self)
        choices = QtWidgets.QWidget(self)
        row = QtWidgets.QHBoxLayout(choices)
        self.shapes = QtWidgets.QButtonGroup(self)
        self.shapes.setExclusive(True)
        self.shape_buttons = {}
        for shape, title in [('rect', 'Rectangle'), ('triangle', 'Triangle'), ('ellipse', 'Ellipse')]:
            button = QtWidgets.QToolButton(choices)
            button.setCheckable(True)
            button.setToolTip(title)
            button.setAccessibleName(title)
            pixmap = QtGui.QPixmap(40, 32)
            pixmap.fill(QtCore.Qt.GlobalColor.transparent)
            painter = QtGui.QPainter(pixmap)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            painter.setPen(QtGui.QPen(QtGui.QColor('#3484c6'), 2))
            if shape == 'rect':
                painter.drawRect(5, 5, 30, 22)
            elif shape == 'ellipse':
                painter.drawEllipse(5, 5, 30, 22)
            else:
                painter.drawPolygon(QtGui.QPolygonF([QtCore.QPointF(20, 4), QtCore.QPointF(35, 27), QtCore.QPointF(5, 27)]))
            painter.end()
            button.setIcon(QtGui.QIcon(pixmap))
            button.setIconSize(QtCore.QSize(40, 32))
            button.setProperty('containerShape', shape)
            self.shapes.addButton(button)
            self.shape_buttons[shape] = button
            row.addWidget(button)
        self.shape_buttons[self.values['shape']].setChecked(True)
        form.addRow('Shape:', choices)
        self.borderStyle = QtWidgets.QComboBox(self)
        for label, value in [('No border', 0), ('Solid', 1), ('Dash', 2), ('Dot', 3), ('Dash dot', 4), ('Dash dot dot', 5)]:
            self.borderStyle.addItem(label, value)
        self.borderStyle.setCurrentIndex(self.values['border_style'])
        form.addRow('Border:', self.borderStyle)
        self.borderWidth = QtWidgets.QDoubleSpinBox(self)
        self.borderWidth.setStyleSheet("QDoubleSpinBox { background-color: white; color: black; } QLineEdit { background-color: white; color: black; }")
        self.borderWidth.setRange(0, 100)
        self.borderWidth.setValue(self.values['border_width'])
        form.addRow('Border width:', self.borderWidth)
        for key, label in [('border_color', 'Border color:'), ('fill_color', 'Background:')]:
            button = QtWidgets.QPushButton(self)
            button.setText('Choose color…')
            self.updateColorButton(button, self.values[key])
            button.clicked.connect(lambda checked=False, key=key, button=button: self.chooseColor(key, button))
            form.addRow(label, button)

    def updateColorButton(self, button, color):
        value = QtGui.QColor(color)
        if value.alpha() == 0:
            button.setText('Transparent')
            button.setStyleSheet('background-color: white; color: black;')
        else:
            button.setText('Choose color…' if value.alpha() == 255 else 'Opacity: {}%'.format(round(value.alphaF() * 100)))
            foreground = 'black' if value.lightness() > 128 else 'white'
            button.setStyleSheet('background-color: {}; color: {};'.format(value.name(), foreground))

    def chooseColor(self, key, button):
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self.values[key]), self, 'Select color',
                                               QtWidgets.QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if color.isValid():
            self.values[key] = color.name(QtGui.QColor.NameFormat.HexArgb)
            self.updateColorButton(button, self.values[key])

    def styleData(self):
        return validated_style(dict(self.values, shape=self.shapes.checkedButton().property('containerShape'),
                                    border_style=self.borderStyle.currentData(), border_width=self.borderWidth.value()))
