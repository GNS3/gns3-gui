# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/text_editor_dialog.ui'
#
# Created: Tue Dec 23 15:45:13 2014
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


class Ui_TextEditorDialog(object):

    def setupUi(self, TextEditorDialog):
        TextEditorDialog.setObjectName(_fromUtf8("TextEditorDialog"))
        TextEditorDialog.resize(457, 333)
        TextEditorDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(TextEditorDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.uiTextSettingsGroupBox = QtGui.QGroupBox(TextEditorDialog)
        self.uiTextSettingsGroupBox.setObjectName(_fromUtf8("uiTextSettingsGroupBox"))
        self.gridLayout = QtGui.QGridLayout(self.uiTextSettingsGroupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiColorLabel = QtGui.QLabel(self.uiTextSettingsGroupBox)
        self.uiColorLabel.setObjectName(_fromUtf8("uiColorLabel"))
        self.gridLayout.addWidget(self.uiColorLabel, 0, 0, 1, 1)
        self.uiColorPushButton = QtGui.QPushButton(self.uiTextSettingsGroupBox)
        self.uiColorPushButton.setText(_fromUtf8(""))
        self.uiColorPushButton.setObjectName(_fromUtf8("uiColorPushButton"))
        self.gridLayout.addWidget(self.uiColorPushButton, 0, 1, 1, 1)
        self.uiRotationLabel = QtGui.QLabel(self.uiTextSettingsGroupBox)
        self.uiRotationLabel.setObjectName(_fromUtf8("uiRotationLabel"))
        self.gridLayout.addWidget(self.uiRotationLabel, 1, 0, 1, 1)
        self.uiRotationSpinBox = QtGui.QSpinBox(self.uiTextSettingsGroupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiRotationSpinBox.sizePolicy().hasHeightForWidth())
        self.uiRotationSpinBox.setSizePolicy(sizePolicy)
        self.uiRotationSpinBox.setMinimum(-360)
        self.uiRotationSpinBox.setMaximum(360)
        self.uiRotationSpinBox.setObjectName(_fromUtf8("uiRotationSpinBox"))
        self.gridLayout.addWidget(self.uiRotationSpinBox, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.uiTextSettingsGroupBox)
        self.uiApplyTextToAllItemsCheckBox = QtGui.QCheckBox(TextEditorDialog)
        self.uiApplyTextToAllItemsCheckBox.setObjectName(_fromUtf8("uiApplyTextToAllItemsCheckBox"))
        self.verticalLayout.addWidget(self.uiApplyTextToAllItemsCheckBox)
        self.uiPlainTextEdit = QtGui.QPlainTextEdit(TextEditorDialog)
        self.uiPlainTextEdit.setObjectName(_fromUtf8("uiPlainTextEdit"))
        self.verticalLayout.addWidget(self.uiPlainTextEdit)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.uiFontPushButton = QtGui.QPushButton(TextEditorDialog)
        self.uiFontPushButton.setObjectName(_fromUtf8("uiFontPushButton"))
        self.horizontalLayout.addWidget(self.uiFontPushButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.uiButtonBox = QtGui.QDialogButtonBox(TextEditorDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply | QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName(_fromUtf8("uiButtonBox"))
        self.horizontalLayout.addWidget(self.uiButtonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)

        self.retranslateUi(TextEditorDialog)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), TextEditorDialog.accept)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), TextEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(TextEditorDialog)

    def retranslateUi(self, TextEditorDialog):
        TextEditorDialog.setWindowTitle(_translate("TextEditorDialog", "Text editor", None))
        self.uiTextSettingsGroupBox.setTitle(_translate("TextEditorDialog", "Text settings", None))
        self.uiColorLabel.setText(_translate("TextEditorDialog", "Color:", None))
        self.uiRotationLabel.setText(_translate("TextEditorDialog", "Rotation:", None))
        self.uiRotationSpinBox.setToolTip(_translate("TextEditorDialog", "Rotation can be ajusted on the scene for a selected item while\n"
                                                     "editing (notes only) with ALT and \'+\' (or P) / ALT and \'-\' (or M)", None))
        self.uiRotationSpinBox.setSuffix(_translate("TextEditorDialog", "°", None))
        self.uiApplyTextToAllItemsCheckBox.setText(_translate("TextEditorDialog", "Apply the text below to all selected items", None))
        self.uiFontPushButton.setText(_translate("TextEditorDialog", "&Select font", None))

from . import resources_rc
