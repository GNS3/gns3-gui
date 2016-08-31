# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/ui/console_command_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_uiConsoleCommandDialog(object):
    def setupUi(self, uiConsoleCommandDialog):
        uiConsoleCommandDialog.setObjectName("uiConsoleCommandDialog")
        uiConsoleCommandDialog.resize(544, 405)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(uiConsoleCommandDialog.sizePolicy().hasHeightForWidth())
        uiConsoleCommandDialog.setSizePolicy(sizePolicy)
        uiConsoleCommandDialog.setMinimumSize(QtCore.QSize(0, 0))
        uiConsoleCommandDialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(uiConsoleCommandDialog)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(uiConsoleCommandDialog)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.uiCommandComboBox = QtWidgets.QComboBox(uiConsoleCommandDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiCommandComboBox.sizePolicy().hasHeightForWidth())
        self.uiCommandComboBox.setSizePolicy(sizePolicy)
        self.uiCommandComboBox.setObjectName("uiCommandComboBox")
        self.horizontalLayout.addWidget(self.uiCommandComboBox)
        self.uiRemovePushButton = QtWidgets.QPushButton(uiConsoleCommandDialog)
        self.uiRemovePushButton.setObjectName("uiRemovePushButton")
        self.horizontalLayout.addWidget(self.uiRemovePushButton)
        self.uiSavePushButton = QtWidgets.QPushButton(uiConsoleCommandDialog)
        self.uiSavePushButton.setObjectName("uiSavePushButton")
        self.horizontalLayout.addWidget(self.uiSavePushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label = QtWidgets.QLabel(uiConsoleCommandDialog)
        self.label.setTextFormat(QtCore.Qt.RichText)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.uiCommandPlainTextEdit = QtWidgets.QPlainTextEdit(uiConsoleCommandDialog)
        self.uiCommandPlainTextEdit.setMinimumSize(QtCore.QSize(500, 0))
        self.uiCommandPlainTextEdit.setObjectName("uiCommandPlainTextEdit")
        self.verticalLayout.addWidget(self.uiCommandPlainTextEdit)
        self.uiButtonBox = QtWidgets.QDialogButtonBox(uiConsoleCommandDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName("uiButtonBox")
        self.verticalLayout.addWidget(self.uiButtonBox)

        self.retranslateUi(uiConsoleCommandDialog)
        self.uiButtonBox.accepted.connect(uiConsoleCommandDialog.accept)
        self.uiButtonBox.rejected.connect(uiConsoleCommandDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(uiConsoleCommandDialog)

    def retranslateUi(self, uiConsoleCommandDialog):
        _translate = QtCore.QCoreApplication.translate
        uiConsoleCommandDialog.setWindowTitle(_translate("uiConsoleCommandDialog", "Command"))
        self.label_2.setText(_translate("uiConsoleCommandDialog", "Choose a predefined command:"))
        self.uiRemovePushButton.setText(_translate("uiConsoleCommandDialog", "Remove"))
        self.uiSavePushButton.setText(_translate("uiConsoleCommandDialog", "Save"))
        self.label.setText(_translate("uiConsoleCommandDialog", "<html><head/><body><p>Or customize the command in the next input field. <br/>The following variables are replaced by GNS3: </p><ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">%h: console IP or hostname</li><li style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">%p: console port</li><li style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">%P: VNC display</li><li style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">%s: path of the serial connection</li></ul><ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">%d: title of the console</li><li style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">%i: Project UUID</li><li style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">%c: GNS3 server connection string (<span style=\" font-style:italic;\">http://user:password@server:port</span>)</li></ul></body></html>"))

