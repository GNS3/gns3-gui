# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/snapshots_dialog.ui'
#
# Created: Mon Oct 20 14:23:13 2014
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


class Ui_SnapshotsDialog(object):

    def setupUi(self, SnapshotsDialog):
        SnapshotsDialog.setObjectName(_fromUtf8("SnapshotsDialog"))
        SnapshotsDialog.setWindowModality(QtCore.Qt.WindowModal)
        SnapshotsDialog.resize(496, 288)
        self.gridLayout = QtGui.QGridLayout(SnapshotsDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiSnapshotsList = QtGui.QListWidget(SnapshotsDialog)
        self.uiSnapshotsList.setObjectName(_fromUtf8("uiSnapshotsList"))
        self.gridLayout.addWidget(self.uiSnapshotsList, 0, 0, 1, 4)
        self.uiCreatePushButton = QtGui.QPushButton(SnapshotsDialog)
        self.uiCreatePushButton.setObjectName(_fromUtf8("uiCreatePushButton"))
        self.gridLayout.addWidget(self.uiCreatePushButton, 1, 0, 1, 1)
        self.uiRestorePushButton = QtGui.QPushButton(SnapshotsDialog)
        self.uiRestorePushButton.setEnabled(False)
        self.uiRestorePushButton.setObjectName(_fromUtf8("uiRestorePushButton"))
        self.gridLayout.addWidget(self.uiRestorePushButton, 1, 2, 1, 1)
        self.uiButtonBox = QtGui.QDialogButtonBox(SnapshotsDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.uiButtonBox.setObjectName(_fromUtf8("uiButtonBox"))
        self.gridLayout.addWidget(self.uiButtonBox, 1, 3, 1, 1)
        self.uiDeletePushButton = QtGui.QPushButton(SnapshotsDialog)
        self.uiDeletePushButton.setEnabled(False)
        self.uiDeletePushButton.setObjectName(_fromUtf8("uiDeletePushButton"))
        self.gridLayout.addWidget(self.uiDeletePushButton, 1, 1, 1, 1)

        self.retranslateUi(SnapshotsDialog)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SnapshotsDialog.accept)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SnapshotsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SnapshotsDialog)

    def retranslateUi(self, SnapshotsDialog):
        SnapshotsDialog.setWindowTitle(_translate("SnapshotsDialog", "Snapshots", None))
        self.uiCreatePushButton.setText(_translate("SnapshotsDialog", "&Create", None))
        self.uiRestorePushButton.setText(_translate("SnapshotsDialog", "&Restore", None))
        self.uiDeletePushButton.setText(_translate("SnapshotsDialog", "&Delete", None))
