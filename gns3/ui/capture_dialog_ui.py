# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/capture_dialog.ui'
#
# Created: Mon May 30 21:49:29 2016
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CaptureDialog(object):
    def setupUi(self, CaptureDialog):
        CaptureDialog.setObjectName("CaptureDialog")
        CaptureDialog.setWindowModality(QtCore.Qt.WindowModal)
        CaptureDialog.setMinimumSize(QtCore.QSize(500, 147))
        CaptureDialog.resize(500, 147)
        CaptureDialog.setMaximumSize(QtCore.QSize(500, 147))
        CaptureDialog.setModal(False)
        self.gridLayout = QtWidgets.QGridLayout(CaptureDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.uiLinkTypeLabel = QtWidgets.QLabel(CaptureDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiLinkTypeLabel.sizePolicy().hasHeightForWidth())
        self.uiLinkTypeLabel.setSizePolicy(sizePolicy)
        self.uiLinkTypeLabel.setScaledContents(False)
        self.uiLinkTypeLabel.setObjectName("uiLinkTypeLabel")
        self.gridLayout.addWidget(self.uiLinkTypeLabel, 0, 0, 1, 1)
        self.uiDataLinkTypeComboBox = QtWidgets.QComboBox(CaptureDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiDataLinkTypeComboBox.sizePolicy().hasHeightForWidth())
        self.uiDataLinkTypeComboBox.setSizePolicy(sizePolicy)
        self.uiDataLinkTypeComboBox.setObjectName("uiDataLinkTypeComboBox")
        self.gridLayout.addWidget(self.uiDataLinkTypeComboBox, 0, 1, 1, 1)
        self.uiFileNameLabel = QtWidgets.QLabel(CaptureDialog)
        self.uiFileNameLabel.setObjectName("uiFileNameLabel")
        self.gridLayout.addWidget(self.uiFileNameLabel, 1, 0, 1, 1)
        self.uiCaptureFileNameLineEdit = QtWidgets.QLineEdit(CaptureDialog)
        self.uiCaptureFileNameLineEdit.setObjectName("uiCaptureFileNameLineEdit")
        self.gridLayout.addWidget(self.uiCaptureFileNameLineEdit, 1, 1, 1, 1)
        self.uiStartCommandCheckBox = QtWidgets.QCheckBox(CaptureDialog)
        self.uiStartCommandCheckBox.setChecked(True)
        self.uiStartCommandCheckBox.setObjectName("uiStartCommandCheckBox")
        self.gridLayout.addWidget(self.uiStartCommandCheckBox, 2, 0, 1, 2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.uiButtonBox = QtWidgets.QDialogButtonBox(CaptureDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiButtonBox.sizePolicy().hasHeightForWidth())
        self.uiButtonBox.setSizePolicy(sizePolicy)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName("uiButtonBox")
        self.horizontalLayout.addWidget(self.uiButtonBox)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 0, 1, 2)
        spacerItem1 = QtWidgets.QSpacerItem(20, 244, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 4, 1, 1, 1)

        self.retranslateUi(CaptureDialog)
        QtCore.QMetaObject.connectSlotsByName(CaptureDialog)

    def retranslateUi(self, CaptureDialog):
        _translate = QtCore.QCoreApplication.translate
        CaptureDialog.setWindowTitle(_translate("CaptureDialog", "Packet capture"))
        self.uiLinkTypeLabel.setText(_translate("CaptureDialog", "Link type:"))
        self.uiFileNameLabel.setText(_translate("CaptureDialog", "File name:"))
        self.uiStartCommandCheckBox.setText(_translate("CaptureDialog", "Start the capture visualization program"))

from . import resources_rc
