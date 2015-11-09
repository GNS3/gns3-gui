# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/ui/style_editor_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_StyleEditorDialog(object):

    def setupUi(self, StyleEditorDialog):
        StyleEditorDialog.setObjectName("StyleEditorDialog")
        StyleEditorDialog.resize(328, 252)
        StyleEditorDialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(StyleEditorDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiStyleSettingsGroupBox = QtWidgets.QGroupBox(StyleEditorDialog)
        self.uiStyleSettingsGroupBox.setObjectName("uiStyleSettingsGroupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.uiStyleSettingsGroupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.uiColorLabel = QtWidgets.QLabel(self.uiStyleSettingsGroupBox)
        self.uiColorLabel.setObjectName("uiColorLabel")
        self.gridLayout.addWidget(self.uiColorLabel, 0, 0, 1, 1)
        self.uiColorPushButton = QtWidgets.QPushButton(self.uiStyleSettingsGroupBox)
        self.uiColorPushButton.setText("")
        self.uiColorPushButton.setObjectName("uiColorPushButton")
        self.gridLayout.addWidget(self.uiColorPushButton, 0, 1, 1, 1)
        self.uiBorderColorLabel = QtWidgets.QLabel(self.uiStyleSettingsGroupBox)
        self.uiBorderColorLabel.setObjectName("uiBorderColorLabel")
        self.gridLayout.addWidget(self.uiBorderColorLabel, 1, 0, 1, 1)
        self.uiBorderColorPushButton = QtWidgets.QPushButton(self.uiStyleSettingsGroupBox)
        self.uiBorderColorPushButton.setText("")
        self.uiBorderColorPushButton.setObjectName("uiBorderColorPushButton")
        self.gridLayout.addWidget(self.uiBorderColorPushButton, 1, 1, 1, 1)
        self.uiBorderWidthLabel = QtWidgets.QLabel(self.uiStyleSettingsGroupBox)
        self.uiBorderWidthLabel.setObjectName("uiBorderWidthLabel")
        self.gridLayout.addWidget(self.uiBorderWidthLabel, 2, 0, 1, 1)
        self.uiBorderWidthSpinBox = QtWidgets.QSpinBox(self.uiStyleSettingsGroupBox)
        self.uiBorderWidthSpinBox.setMinimum(1)
        self.uiBorderWidthSpinBox.setMaximum(100)
        self.uiBorderWidthSpinBox.setProperty("value", 2)
        self.uiBorderWidthSpinBox.setObjectName("uiBorderWidthSpinBox")
        self.gridLayout.addWidget(self.uiBorderWidthSpinBox, 2, 1, 1, 1)
        self.uiBorderStyleLabel = QtWidgets.QLabel(self.uiStyleSettingsGroupBox)
        self.uiBorderStyleLabel.setObjectName("uiBorderStyleLabel")
        self.gridLayout.addWidget(self.uiBorderStyleLabel, 3, 0, 1, 1)
        self.uiBorderStyleComboBox = QtWidgets.QComboBox(self.uiStyleSettingsGroupBox)
        self.uiBorderStyleComboBox.setObjectName("uiBorderStyleComboBox")
        self.gridLayout.addWidget(self.uiBorderStyleComboBox, 3, 1, 1, 1)
        self.uiRotationLabel = QtWidgets.QLabel(self.uiStyleSettingsGroupBox)
        self.uiRotationLabel.setObjectName("uiRotationLabel")
        self.gridLayout.addWidget(self.uiRotationLabel, 4, 0, 1, 1)
        self.uiRotationSpinBox = QtWidgets.QSpinBox(self.uiStyleSettingsGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiRotationSpinBox.sizePolicy().hasHeightForWidth())
        self.uiRotationSpinBox.setSizePolicy(sizePolicy)
        self.uiRotationSpinBox.setMinimum(-360)
        self.uiRotationSpinBox.setMaximum(360)
        self.uiRotationSpinBox.setObjectName("uiRotationSpinBox")
        self.gridLayout.addWidget(self.uiRotationSpinBox, 4, 1, 1, 1)
        self.verticalLayout.addWidget(self.uiStyleSettingsGroupBox)
        self.uiButtonBox = QtWidgets.QDialogButtonBox(StyleEditorDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply | QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName("uiButtonBox")
        self.verticalLayout.addWidget(self.uiButtonBox)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(StyleEditorDialog)
        self.uiButtonBox.accepted.connect(StyleEditorDialog.accept)
        self.uiButtonBox.rejected.connect(StyleEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(StyleEditorDialog)

    def retranslateUi(self, StyleEditorDialog):
        _translate = QtCore.QCoreApplication.translate
        StyleEditorDialog.setWindowTitle(_translate("StyleEditorDialog", "Style editor"))
        self.uiStyleSettingsGroupBox.setTitle(_translate("StyleEditorDialog", "Style settings"))
        self.uiColorLabel.setText(_translate("StyleEditorDialog", "Fill color:"))
        self.uiBorderColorLabel.setText(_translate("StyleEditorDialog", "Border color:"))
        self.uiBorderWidthLabel.setText(_translate("StyleEditorDialog", "Border width:"))
        self.uiBorderWidthSpinBox.setSuffix(_translate("StyleEditorDialog", " px"))
        self.uiBorderStyleLabel.setText(_translate("StyleEditorDialog", "Border style:"))
        self.uiRotationLabel.setText(_translate("StyleEditorDialog", "Rotation:"))
        self.uiRotationSpinBox.setToolTip(_translate("StyleEditorDialog", "Rotation can be ajusted on the scene for a selected item while\n"
                                                     "editing (notes only) with ALT and \'+\' (or P) / ALT and \'-\' (or M)"))
        self.uiRotationSpinBox.setSuffix(_translate("StyleEditorDialog", "°"))

from . import resources_rc
