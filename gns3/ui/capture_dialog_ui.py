# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/ui/capture_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CaptureDialog(object):
    def setupUi(self, CaptureDialog):
        CaptureDialog.setObjectName("CaptureDialog")
        CaptureDialog.setWindowModality(QtCore.Qt.WindowModal)
        CaptureDialog.resize(352, 201)
        CaptureDialog.setModal(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(CaptureDialog)
        self.verticalLayout.setContentsMargins(-1, -1, 12, -1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_3 = QtWidgets.QLabel(CaptureDialog)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(CaptureDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setScaledContents(False)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.uiDataLinkTypeComboBox = QtWidgets.QComboBox(CaptureDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiDataLinkTypeComboBox.sizePolicy().hasHeightForWidth())
        self.uiDataLinkTypeComboBox.setSizePolicy(sizePolicy)
        self.uiDataLinkTypeComboBox.setObjectName("uiDataLinkTypeComboBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.uiDataLinkTypeComboBox)
        self.label_2 = QtWidgets.QLabel(CaptureDialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.uiCaptureFileNameLineEdit = QtWidgets.QLineEdit(CaptureDialog)
        self.uiCaptureFileNameLineEdit.setObjectName("uiCaptureFileNameLineEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.uiCaptureFileNameLineEdit)
        self.verticalLayout.addLayout(self.formLayout)
        self.uiStartCommandCheckBox = QtWidgets.QCheckBox(CaptureDialog)
        self.uiStartCommandCheckBox.setObjectName("uiStartCommandCheckBox")
        self.verticalLayout.addWidget(self.uiStartCommandCheckBox)
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
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(CaptureDialog)
        QtCore.QMetaObject.connectSlotsByName(CaptureDialog)

    def retranslateUi(self, CaptureDialog):
        _translate = QtCore.QCoreApplication.translate
        CaptureDialog.setWindowTitle(_translate("CaptureDialog", "Packet capture"))
        self.label_3.setText(_translate("CaptureDialog", "The captures will be saved in project-files/captures inside the project directory"))
        self.label.setText(_translate("CaptureDialog", "Link type:"))
        self.label_2.setText(_translate("CaptureDialog", "File name:"))
        self.uiStartCommandCheckBox.setText(_translate("CaptureDialog", "Start the capture visualization program"))

from . import resources_rc
