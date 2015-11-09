# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/ui/exec_command_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ExecCommandDialog(object):

    def setupUi(self, ExecCommandDialog):
        ExecCommandDialog.setObjectName("ExecCommandDialog")
        ExecCommandDialog.resize(651, 343)
        ExecCommandDialog.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(ExecCommandDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.uiOutputTextEdit = QtWidgets.QPlainTextEdit(ExecCommandDialog)
        self.uiOutputTextEdit.setObjectName("uiOutputTextEdit")
        self.gridLayout.addWidget(self.uiOutputTextEdit, 0, 0, 1, 2)
        self.uiButtonBox = QtWidgets.QDialogButtonBox(ExecCommandDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName("uiButtonBox")
        self.gridLayout.addWidget(self.uiButtonBox, 1, 1, 1, 1)

        self.retranslateUi(ExecCommandDialog)
        self.uiButtonBox.accepted.connect(ExecCommandDialog.accept)
        self.uiButtonBox.rejected.connect(ExecCommandDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ExecCommandDialog)

    def retranslateUi(self, ExecCommandDialog):
        _translate = QtCore.QCoreApplication.translate
        ExecCommandDialog.setWindowTitle(_translate("ExecCommandDialog", "Command execution"))

from . import resources_rc
