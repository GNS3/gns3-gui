# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'exec_command_dialog.ui'
#
# Created: Wed May  6 14:31:52 2015
#      by: PyQt5 UI code generator 5.4
#
# WARNING! All changes made in this file will be lost!

import gns3.qt
from gns3.qt import QtCore, QtGui, QtWidgets


class Ui_ExecCommandDialog:

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
        _translate = gns3.qt.translate
        ExecCommandDialog.setWindowTitle(_translate("ExecCommandDialog", "Command execution"))

from . import resources_rc
