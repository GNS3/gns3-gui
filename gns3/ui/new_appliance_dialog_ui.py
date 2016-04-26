# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/ui/new_appliance_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_NewApplianceDialog(object):
    def setupUi(self, NewApplianceDialog):
        NewApplianceDialog.setObjectName("NewApplianceDialog")
        NewApplianceDialog.setWindowModality(QtCore.Qt.WindowModal)
        NewApplianceDialog.resize(617, 538)
        NewApplianceDialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(NewApplianceDialog)
        self.verticalLayout.setContentsMargins(-1, -1, 12, -1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(NewApplianceDialog)
        self.label_2.setTextFormat(QtCore.Qt.RichText)
        self.label_2.setWordWrap(True)
        self.label_2.setOpenExternalLinks(True)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.uiImportApplianceTemplatePushButton = QtWidgets.QPushButton(NewApplianceDialog)
        self.uiImportApplianceTemplatePushButton.setObjectName("uiImportApplianceTemplatePushButton")
        self.verticalLayout.addWidget(self.uiImportApplianceTemplatePushButton)
        self.label = QtWidgets.QLabel(NewApplianceDialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.uiAddIOSRouterRadioButton = QtWidgets.QRadioButton(NewApplianceDialog)
        self.uiAddIOSRouterRadioButton.setObjectName("uiAddIOSRouterRadioButton")
        self.verticalLayout.addWidget(self.uiAddIOSRouterRadioButton)
        self.uiAddIOUDeviceRadioButton = QtWidgets.QRadioButton(NewApplianceDialog)
        self.uiAddIOUDeviceRadioButton.setObjectName("uiAddIOUDeviceRadioButton")
        self.verticalLayout.addWidget(self.uiAddIOUDeviceRadioButton)
        self.uiAddQemuVMRadioButton = QtWidgets.QRadioButton(NewApplianceDialog)
        self.uiAddQemuVMRadioButton.setObjectName("uiAddQemuVMRadioButton")
        self.verticalLayout.addWidget(self.uiAddQemuVMRadioButton)
        self.uiAddDockerVMRadioButton = QtWidgets.QRadioButton(NewApplianceDialog)
        self.uiAddDockerVMRadioButton.setObjectName("uiAddDockerVMRadioButton")
        self.verticalLayout.addWidget(self.uiAddDockerVMRadioButton)
        self.uiAddVirtualBoxVMRadioButton = QtWidgets.QRadioButton(NewApplianceDialog)
        self.uiAddVirtualBoxVMRadioButton.setObjectName("uiAddVirtualBoxVMRadioButton")
        self.verticalLayout.addWidget(self.uiAddVirtualBoxVMRadioButton)
        self.uiAddVMwareVMRadioButton = QtWidgets.QRadioButton(NewApplianceDialog)
        self.uiAddVMwareVMRadioButton.setObjectName("uiAddVMwareVMRadioButton")
        self.verticalLayout.addWidget(self.uiAddVMwareVMRadioButton)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.uiOkButton = QtWidgets.QDialogButtonBox(NewApplianceDialog)
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

        self.retranslateUi(NewApplianceDialog)
        QtCore.QMetaObject.connectSlotsByName(NewApplianceDialog)

    def retranslateUi(self, NewApplianceDialog):
        _translate = QtCore.QCoreApplication.translate
        NewApplianceDialog.setWindowTitle(_translate("NewApplianceDialog", "New appliance"))
        self.label_2.setText(_translate("NewApplianceDialog", "<html><head/><body><p><span style=\" font-size:xx-large; font-weight:600;\">Create a new appliance</span></p><p>This dialog will help you to create new appliance in GNS3. In all cases you will need to provide your own images. </p><p><span style=\" font-size:x-large; font-weight:600;\">Create an appliance from a template</span></p><p>You can download appliances template from the the GNS3 website:</p><p><a href=\"https://gns3.com/marketplace/appliances\"><span style=\" text-decoration: underline; color:#0000ff;\">https://gns3.com/marketplace/appliances</span></a></p><p>This template will provide you tested configuration from the community. The template extension .gns3a</p></body></html>"))
        self.uiImportApplianceTemplatePushButton.setText(_translate("NewApplianceDialog", "Import appliance template"))
        self.label.setText(_translate("NewApplianceDialog", "<html><head/><body><p><span style=\" font-size:x-large; font-weight:600;\">Manual creation</span></p><p>You will need to configure everything by hand.</p><p>Please select the emulator you want to configure:</p></body></html>"))
        self.uiAddIOSRouterRadioButton.setText(_translate("NewApplianceDialog", "Dynamips (old IOS images)"))
        self.uiAddIOUDeviceRadioButton.setText(_translate("NewApplianceDialog", "IOU"))
        self.uiAddQemuVMRadioButton.setText(_translate("NewApplianceDialog", "Qemu"))
        self.uiAddDockerVMRadioButton.setText(_translate("NewApplianceDialog", "Docker"))
        self.uiAddVirtualBoxVMRadioButton.setText(_translate("NewApplianceDialog", "VirtualBox"))
        self.uiAddVMwareVMRadioButton.setText(_translate("NewApplianceDialog", "VMware"))

from . import resources_rc
