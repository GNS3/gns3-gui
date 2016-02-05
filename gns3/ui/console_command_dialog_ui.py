# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/ui/console_command_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_uiConsoleCommandDialog(object):
    def setupUi(self, uiConsoleCommandDialog):
        uiConsoleCommandDialog.setObjectName("uiConsoleCommandDialog")
        uiConsoleCommandDialog.resize(524, 350)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(uiConsoleCommandDialog.sizePolicy().hasHeightForWidth())
        uiConsoleCommandDialog.setSizePolicy(sizePolicy)
        uiConsoleCommandDialog.setMinimumSize(QtCore.QSize(0, 0))
        uiConsoleCommandDialog.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(uiConsoleCommandDialog)
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(uiConsoleCommandDialog)
        self.label.setTextFormat(QtCore.Qt.RichText)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(uiConsoleCommandDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.uiCommandPlainTextEdit = QtWidgets.QPlainTextEdit(uiConsoleCommandDialog)
        self.uiCommandPlainTextEdit.setMinimumSize(QtCore.QSize(500, 0))
        self.uiCommandPlainTextEdit.setObjectName("uiCommandPlainTextEdit")
        self.gridLayout.addWidget(self.uiCommandPlainTextEdit, 3, 0, 1, 1)
        self.uiButtonBox = QtWidgets.QDialogButtonBox(uiConsoleCommandDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName("uiButtonBox")
        self.gridLayout.addWidget(self.uiButtonBox, 4, 0, 1, 1)
        self.uiCommandComboBox = QtWidgets.QComboBox(uiConsoleCommandDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiCommandComboBox.sizePolicy().hasHeightForWidth())
        self.uiCommandComboBox.setSizePolicy(sizePolicy)
        self.uiCommandComboBox.setObjectName("uiCommandComboBox")
        self.gridLayout.addWidget(self.uiCommandComboBox, 1, 0, 1, 1)

        self.retranslateUi(uiConsoleCommandDialog)
        self.uiButtonBox.accepted.connect(uiConsoleCommandDialog.accept)
        self.uiButtonBox.rejected.connect(uiConsoleCommandDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(uiConsoleCommandDialog)

    def retranslateUi(self, uiConsoleCommandDialog):
        _translate = QtCore.QCoreApplication.translate
        uiConsoleCommandDialog.setWindowTitle(_translate("uiConsoleCommandDialog", "Command"))
        self.label.setText(_translate("uiConsoleCommandDialog", "<html><head/><body><p>Or customize the command in the next input field. <br/>The following variables are replaced by GNS3: </p><ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">%h: console IP or hostname</li><li style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">%p: console port</li><li style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">%s: path of the serial connection</li><li style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">%d: title of the console</li></ul></body></html>"))
        self.label_2.setText(_translate("uiConsoleCommandDialog", "Choose a predefined command:"))

