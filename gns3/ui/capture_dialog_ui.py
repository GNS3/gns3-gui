# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/capture_dialog.ui'
#
# Created: Sun May 22 10:18:42 2016
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CaptureDialog(object):
    def setupUi(self, CaptureDialog):
        CaptureDialog.setObjectName("CaptureDialog")
        CaptureDialog.setWindowModality(QtCore.Qt.WindowModal)
        CaptureDialog.resize(439, 159)
        CaptureDialog.setModal(False)
        self.gridLayout = QtWidgets.QGridLayout(CaptureDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(CaptureDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setScaledContents(False)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.uiDataLinkTypeComboBox = QtWidgets.QComboBox(CaptureDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiDataLinkTypeComboBox.sizePolicy().hasHeightForWidth())
        self.uiDataLinkTypeComboBox.setSizePolicy(sizePolicy)
        self.uiDataLinkTypeComboBox.setObjectName("uiDataLinkTypeComboBox")
        self.gridLayout.addWidget(self.uiDataLinkTypeComboBox, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(CaptureDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
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
        self.uiOkButton = QtWidgets.QDialogButtonBox(CaptureDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiOkButton.sizePolicy().hasHeightForWidth())
        self.uiOkButton.setSizePolicy(sizePolicy)
        self.uiOkButton.setOrientation(QtCore.Qt.Horizontal)
        self.uiOkButton.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.uiOkButton.setObjectName("uiOkButton")
        self.horizontalLayout.addWidget(self.uiOkButton)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 0, 1, 2)
        spacerItem1 = QtWidgets.QSpacerItem(20, 244, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 4, 1, 1, 1)

        self.retranslateUi(CaptureDialog)
        QtCore.QMetaObject.connectSlotsByName(CaptureDialog)

    def retranslateUi(self, CaptureDialog):
        _translate = QtCore.QCoreApplication.translate
        CaptureDialog.setWindowTitle(_translate("CaptureDialog", "Packet capture"))
        self.label.setText(_translate("CaptureDialog", "Link type:"))
        self.label_2.setText(_translate("CaptureDialog", "File name:"))
        self.uiStartCommandCheckBox.setText(_translate("CaptureDialog", "Start the capture visualization program"))

from . import resources_rc
