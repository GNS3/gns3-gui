# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/idlepc_dialog.ui'
#
# Created: Wed Oct 22 18:01:47 2014
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


class Ui_IdlePCDialog(object):

    def setupUi(self, IdlePCDialog):
        IdlePCDialog.setObjectName(_fromUtf8("IdlePCDialog"))
        IdlePCDialog.setModal(True)
        self.gridLayout = QtGui.QGridLayout(IdlePCDialog)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiLabel = QtGui.QLabel(IdlePCDialog)
        self.uiLabel.setObjectName(_fromUtf8("uiLabel"))
        self.gridLayout.addWidget(self.uiLabel, 0, 0, 1, 1)
        self.uiComboBox = QtGui.QComboBox(IdlePCDialog)
        self.uiComboBox.setObjectName(_fromUtf8("uiComboBox"))
        self.gridLayout.addWidget(self.uiComboBox, 1, 0, 1, 1)
        self.uiButtonBox = QtGui.QDialogButtonBox(IdlePCDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply | QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Help | QtGui.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName(_fromUtf8("uiButtonBox"))
        self.gridLayout.addWidget(self.uiButtonBox, 2, 0, 1, 1)

        self.retranslateUi(IdlePCDialog)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), IdlePCDialog.accept)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), IdlePCDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(IdlePCDialog)

    def retranslateUi(self, IdlePCDialog):
        IdlePCDialog.setWindowTitle(_translate("IdlePCDialog", "Idle-PC values", None))
        self.uiLabel.setText(_translate("IdlePCDialog", "Potentially better Idle-PC values are marked with \'*\'", None))
