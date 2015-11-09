# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/ui/snapshots_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SnapshotsDialog(object):

    def setupUi(self, SnapshotsDialog):
        SnapshotsDialog.setObjectName("SnapshotsDialog")
        SnapshotsDialog.setWindowModality(QtCore.Qt.WindowModal)
        SnapshotsDialog.resize(496, 288)
        self.gridLayout = QtWidgets.QGridLayout(SnapshotsDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.uiSnapshotsList = QtWidgets.QListWidget(SnapshotsDialog)
        self.uiSnapshotsList.setObjectName("uiSnapshotsList")
        self.gridLayout.addWidget(self.uiSnapshotsList, 0, 0, 1, 4)
        self.uiCreatePushButton = QtWidgets.QPushButton(SnapshotsDialog)
        self.uiCreatePushButton.setObjectName("uiCreatePushButton")
        self.gridLayout.addWidget(self.uiCreatePushButton, 1, 0, 1, 1)
        self.uiRestorePushButton = QtWidgets.QPushButton(SnapshotsDialog)
        self.uiRestorePushButton.setEnabled(False)
        self.uiRestorePushButton.setObjectName("uiRestorePushButton")
        self.gridLayout.addWidget(self.uiRestorePushButton, 1, 2, 1, 1)
        self.uiButtonBox = QtWidgets.QDialogButtonBox(SnapshotsDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.uiButtonBox.setObjectName("uiButtonBox")
        self.gridLayout.addWidget(self.uiButtonBox, 1, 3, 1, 1)
        self.uiDeletePushButton = QtWidgets.QPushButton(SnapshotsDialog)
        self.uiDeletePushButton.setEnabled(False)
        self.uiDeletePushButton.setObjectName("uiDeletePushButton")
        self.gridLayout.addWidget(self.uiDeletePushButton, 1, 1, 1, 1)

        self.retranslateUi(SnapshotsDialog)
        self.uiButtonBox.accepted.connect(SnapshotsDialog.accept)
        self.uiButtonBox.rejected.connect(SnapshotsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SnapshotsDialog)

    def retranslateUi(self, SnapshotsDialog):
        _translate = QtCore.QCoreApplication.translate
        SnapshotsDialog.setWindowTitle(_translate("SnapshotsDialog", "Snapshots"))
        self.uiCreatePushButton.setText(_translate("SnapshotsDialog", "&Create"))
        self.uiRestorePushButton.setText(_translate("SnapshotsDialog", "&Restore"))
        self.uiDeletePushButton.setText(_translate("SnapshotsDialog", "&Delete"))
