# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/exec_command_dialog.ui'
#
# Created: Mon Oct 13 17:41:51 2014
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


class Ui_ExecCommandDialog(object):

    def setupUi(self, ExecCommandDialog):
        ExecCommandDialog.setObjectName(_fromUtf8("ExecCommandDialog"))
        ExecCommandDialog.resize(651, 343)
        ExecCommandDialog.setModal(True)
        self.gridLayout = QtGui.QGridLayout(ExecCommandDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiOutputTextEdit = QtGui.QPlainTextEdit(ExecCommandDialog)
        self.uiOutputTextEdit.setObjectName(_fromUtf8("uiOutputTextEdit"))
        self.gridLayout.addWidget(self.uiOutputTextEdit, 0, 0, 1, 2)
        self.uiButtonBox = QtGui.QDialogButtonBox(ExecCommandDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName(_fromUtf8("uiButtonBox"))
        self.gridLayout.addWidget(self.uiButtonBox, 1, 1, 1, 1)

        self.retranslateUi(ExecCommandDialog)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ExecCommandDialog.accept)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ExecCommandDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ExecCommandDialog)

    def retranslateUi(self, ExecCommandDialog):
        ExecCommandDialog.setWindowTitle(_translate("ExecCommandDialog", "Command execution", None))

from . import resources_rc
