# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/style_editor_dialog.ui'
#
# Created: Sun Aug 17 18:05:14 2014
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_StyleEditorDialog(object):

    def setupUi(self, StyleEditorDialog):
        StyleEditorDialog.setObjectName(_fromUtf8("StyleEditorDialog"))
        StyleEditorDialog.resize(328, 252)
        StyleEditorDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(StyleEditorDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.uiStyleSettingsGroupBox = QtGui.QGroupBox(StyleEditorDialog)
        self.uiStyleSettingsGroupBox.setObjectName(_fromUtf8("uiStyleSettingsGroupBox"))
        self.gridLayout = QtGui.QGridLayout(self.uiStyleSettingsGroupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiColorLabel = QtGui.QLabel(self.uiStyleSettingsGroupBox)
        self.uiColorLabel.setObjectName(_fromUtf8("uiColorLabel"))
        self.gridLayout.addWidget(self.uiColorLabel, 0, 0, 1, 1)
        self.uiColorPushButton = QtGui.QPushButton(self.uiStyleSettingsGroupBox)
        self.uiColorPushButton.setText(_fromUtf8(""))
        self.uiColorPushButton.setObjectName(_fromUtf8("uiColorPushButton"))
        self.gridLayout.addWidget(self.uiColorPushButton, 0, 1, 1, 1)
        self.uiBorderColorLabel = QtGui.QLabel(self.uiStyleSettingsGroupBox)
        self.uiBorderColorLabel.setObjectName(_fromUtf8("uiBorderColorLabel"))
        self.gridLayout.addWidget(self.uiBorderColorLabel, 1, 0, 1, 1)
        self.uiBorderColorPushButton = QtGui.QPushButton(self.uiStyleSettingsGroupBox)
        self.uiBorderColorPushButton.setText(_fromUtf8(""))
        self.uiBorderColorPushButton.setObjectName(_fromUtf8("uiBorderColorPushButton"))
        self.gridLayout.addWidget(self.uiBorderColorPushButton, 1, 1, 1, 1)
        self.uiBorderWidthLabel = QtGui.QLabel(self.uiStyleSettingsGroupBox)
        self.uiBorderWidthLabel.setObjectName(_fromUtf8("uiBorderWidthLabel"))
        self.gridLayout.addWidget(self.uiBorderWidthLabel, 2, 0, 1, 1)
        self.uiBorderWidthSpinBox = QtGui.QSpinBox(self.uiStyleSettingsGroupBox)
        self.uiBorderWidthSpinBox.setMinimum(1)
        self.uiBorderWidthSpinBox.setMaximum(100)
        self.uiBorderWidthSpinBox.setProperty("value", 2)
        self.uiBorderWidthSpinBox.setObjectName(_fromUtf8("uiBorderWidthSpinBox"))
        self.gridLayout.addWidget(self.uiBorderWidthSpinBox, 2, 1, 1, 1)
        self.uiBorderStyleLabel = QtGui.QLabel(self.uiStyleSettingsGroupBox)
        self.uiBorderStyleLabel.setObjectName(_fromUtf8("uiBorderStyleLabel"))
        self.gridLayout.addWidget(self.uiBorderStyleLabel, 3, 0, 1, 1)
        self.uiBorderStyleComboBox = QtGui.QComboBox(self.uiStyleSettingsGroupBox)
        self.uiBorderStyleComboBox.setObjectName(_fromUtf8("uiBorderStyleComboBox"))
        self.gridLayout.addWidget(self.uiBorderStyleComboBox, 3, 1, 1, 1)
        self.uiRotationLabel = QtGui.QLabel(self.uiStyleSettingsGroupBox)
        self.uiRotationLabel.setObjectName(_fromUtf8("uiRotationLabel"))
        self.gridLayout.addWidget(self.uiRotationLabel, 4, 0, 1, 1)
        self.uiRotationSpinBox = QtGui.QSpinBox(self.uiStyleSettingsGroupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiRotationSpinBox.sizePolicy().hasHeightForWidth())
        self.uiRotationSpinBox.setSizePolicy(sizePolicy)
        self.uiRotationSpinBox.setMinimum(-360)
        self.uiRotationSpinBox.setMaximum(360)
        self.uiRotationSpinBox.setObjectName(_fromUtf8("uiRotationSpinBox"))
        self.gridLayout.addWidget(self.uiRotationSpinBox, 4, 1, 1, 1)
        self.verticalLayout.addWidget(self.uiStyleSettingsGroupBox)
        self.uiButtonBox = QtGui.QDialogButtonBox(StyleEditorDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply | QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName(_fromUtf8("uiButtonBox"))
        self.verticalLayout.addWidget(self.uiButtonBox)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(StyleEditorDialog)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), StyleEditorDialog.accept)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), StyleEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(StyleEditorDialog)

    def retranslateUi(self, StyleEditorDialog):
        StyleEditorDialog.setWindowTitle(_translate("StyleEditorDialog", "Style editor", None))
        self.uiStyleSettingsGroupBox.setTitle(_translate("StyleEditorDialog", "Style settings", None))
        self.uiColorLabel.setText(_translate("StyleEditorDialog", "Fill color:", None))
        self.uiBorderColorLabel.setText(_translate("StyleEditorDialog", "Border color:", None))
        self.uiBorderWidthLabel.setText(_translate("StyleEditorDialog", "Border width:", None))
        self.uiBorderWidthSpinBox.setSuffix(_translate("StyleEditorDialog", " px", None))
        self.uiBorderStyleLabel.setText(_translate("StyleEditorDialog", "Border style:", None))
        self.uiRotationLabel.setText(_translate("StyleEditorDialog", "Rotation:", None))
        self.uiRotationSpinBox.setToolTip(_translate("StyleEditorDialog", "Rotation can be ajusted on the scene for a selected item while\n"
                                                     "editing (notes only) with ALT and \'+\' (or P) / ALT and \'-\' (or M)", None))
        self.uiRotationSpinBox.setSuffix(_translate("StyleEditorDialog", "°", None))

from . import resources_rc
