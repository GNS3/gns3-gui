# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/image_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ImageDialog(object):
    def setupUi(self, ImageDialog):
        ImageDialog.setObjectName("ImageDialog")
        ImageDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        ImageDialog.resize(732, 329)
        ImageDialog.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(ImageDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.uiImagesTreeWidget = QtWidgets.QTreeWidget(ImageDialog)
        self.uiImagesTreeWidget.setAlternatingRowColors(True)
        self.uiImagesTreeWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.uiImagesTreeWidget.setObjectName("uiImagesTreeWidget")
        self.uiImagesTreeWidget.header().setSortIndicatorShown(True)
        self.gridLayout.addWidget(self.uiImagesTreeWidget, 0, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.uiUploadImagePushButton = QtWidgets.QPushButton(ImageDialog)
        self.uiUploadImagePushButton.setObjectName("uiUploadImagePushButton")
        self.horizontalLayout.addWidget(self.uiUploadImagePushButton)
        self.uiDeleteImagePushButton = QtWidgets.QPushButton(ImageDialog)
        self.uiDeleteImagePushButton.setObjectName("uiDeleteImagePushButton")
        self.horizontalLayout.addWidget(self.uiDeleteImagePushButton)
        self.uiInstallApplianceCheckBox = QtWidgets.QCheckBox(ImageDialog)
        self.uiInstallApplianceCheckBox.setChecked(True)
        self.uiInstallApplianceCheckBox.setObjectName("uiInstallApplianceCheckBox")
        self.horizontalLayout.addWidget(self.uiInstallApplianceCheckBox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.uiRefreshImagesPushButton = QtWidgets.QPushButton(ImageDialog)
        self.uiRefreshImagesPushButton.setObjectName("uiRefreshImagesPushButton")
        self.horizontalLayout.addWidget(self.uiRefreshImagesPushButton)
        self.uiButtonBox = QtWidgets.QDialogButtonBox(ImageDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.uiButtonBox.setObjectName("uiButtonBox")
        self.horizontalLayout.addWidget(self.uiButtonBox)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.retranslateUi(ImageDialog)
        self.uiButtonBox.accepted.connect(ImageDialog.accept)
        self.uiButtonBox.rejected.connect(ImageDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ImageDialog)

    def retranslateUi(self, ImageDialog):
        _translate = QtCore.QCoreApplication.translate
        ImageDialog.setWindowTitle(_translate("ImageDialog", "Images"))
        self.uiImagesTreeWidget.setSortingEnabled(True)
        self.uiImagesTreeWidget.headerItem().setText(0, _translate("ImageDialog", "Filename"))
        self.uiImagesTreeWidget.headerItem().setText(1, _translate("ImageDialog", "Type"))
        self.uiImagesTreeWidget.headerItem().setText(2, _translate("ImageDialog", "Size"))
        self.uiUploadImagePushButton.setText(_translate("ImageDialog", "&Upload"))
        self.uiDeleteImagePushButton.setText(_translate("ImageDialog", "&Delete"))
        self.uiInstallApplianceCheckBox.setText(_translate("ImageDialog", "&Install appliance(s) after upload"))
        self.uiRefreshImagesPushButton.setText(_translate("ImageDialog", "&Refresh"))
