# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/virtualbox/ui/virtualbox_vm_wizard.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_VirtualBoxVMWizard(object):
    def setupUi(self, VirtualBoxVMWizard):
        VirtualBoxVMWizard.setObjectName("VirtualBoxVMWizard")
        VirtualBoxVMWizard.resize(706, 409)
        VirtualBoxVMWizard.setModal(True)
        self.uiServerWizardPage = QtWidgets.QWizardPage()
        self.uiServerWizardPage.setObjectName("uiServerWizardPage")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.uiServerWizardPage)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.uiServerTypeGroupBox = QtWidgets.QGroupBox(self.uiServerWizardPage)
        self.uiServerTypeGroupBox.setObjectName("uiServerTypeGroupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.uiServerTypeGroupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiRemoteRadioButton = QtWidgets.QRadioButton(self.uiServerTypeGroupBox)
        self.uiRemoteRadioButton.setChecked(True)
        self.uiRemoteRadioButton.setObjectName("uiRemoteRadioButton")
        self.verticalLayout.addWidget(self.uiRemoteRadioButton)
        self.uiLocalRadioButton = QtWidgets.QRadioButton(self.uiServerTypeGroupBox)
        self.uiLocalRadioButton.setObjectName("uiLocalRadioButton")
        self.verticalLayout.addWidget(self.uiLocalRadioButton)
        self.gridLayout_2.addWidget(self.uiServerTypeGroupBox, 0, 0, 1, 1)
        self.uiRemoteServersGroupBox = QtWidgets.QGroupBox(self.uiServerWizardPage)
        self.uiRemoteServersGroupBox.setObjectName("uiRemoteServersGroupBox")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.uiRemoteServersGroupBox)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.uiRemoteServersComboBox = QtWidgets.QComboBox(self.uiRemoteServersGroupBox)
        self.uiRemoteServersComboBox.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiRemoteServersComboBox.sizePolicy().hasHeightForWidth())
        self.uiRemoteServersComboBox.setSizePolicy(sizePolicy)
        self.uiRemoteServersComboBox.setObjectName("uiRemoteServersComboBox")
        self.gridLayout_8.addWidget(self.uiRemoteServersComboBox, 0, 1, 1, 1)
        self.uiRemoteServersLabel = QtWidgets.QLabel(self.uiRemoteServersGroupBox)
        self.uiRemoteServersLabel.setObjectName("uiRemoteServersLabel")
        self.gridLayout_8.addWidget(self.uiRemoteServersLabel, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.uiRemoteServersGroupBox, 1, 0, 1, 1)
        VirtualBoxVMWizard.addPage(self.uiServerWizardPage)
        self.uiVirtualBoxWizardPage = QtWidgets.QWizardPage()
        self.uiVirtualBoxWizardPage.setObjectName("uiVirtualBoxWizardPage")
        self.gridLayout = QtWidgets.QGridLayout(self.uiVirtualBoxWizardPage)
        self.gridLayout.setObjectName("gridLayout")
        self.uiVMListLabel = QtWidgets.QLabel(self.uiVirtualBoxWizardPage)
        self.uiVMListLabel.setObjectName("uiVMListLabel")
        self.gridLayout.addWidget(self.uiVMListLabel, 0, 0, 1, 1)
        self.uiVMListComboBox = QtWidgets.QComboBox(self.uiVirtualBoxWizardPage)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVMListComboBox.sizePolicy().hasHeightForWidth())
        self.uiVMListComboBox.setSizePolicy(sizePolicy)
        self.uiVMListComboBox.setObjectName("uiVMListComboBox")
        self.gridLayout.addWidget(self.uiVMListComboBox, 0, 1, 1, 1)
        self.uiBaseVMCheckBox = QtWidgets.QCheckBox(self.uiVirtualBoxWizardPage)
        self.uiBaseVMCheckBox.setEnabled(True)
        self.uiBaseVMCheckBox.setObjectName("uiBaseVMCheckBox")
        self.gridLayout.addWidget(self.uiBaseVMCheckBox, 1, 0, 1, 2)
        VirtualBoxVMWizard.addPage(self.uiVirtualBoxWizardPage)

        self.retranslateUi(VirtualBoxVMWizard)
        QtCore.QMetaObject.connectSlotsByName(VirtualBoxVMWizard)

    def retranslateUi(self, VirtualBoxVMWizard):
        _translate = QtCore.QCoreApplication.translate
        VirtualBoxVMWizard.setWindowTitle(_translate("VirtualBoxVMWizard", "New VirtualBox VM template"))
        self.uiServerWizardPage.setTitle(_translate("VirtualBoxVMWizard", "Server"))
        self.uiServerWizardPage.setSubTitle(_translate("VirtualBoxVMWizard", "Please choose a server type to run the VirtualBox VM."))
        self.uiServerTypeGroupBox.setTitle(_translate("VirtualBoxVMWizard", "Server type"))
        self.uiRemoteRadioButton.setText(_translate("VirtualBoxVMWizard", "Run this VirtualBox VM on a remote computer"))
        self.uiLocalRadioButton.setText(_translate("VirtualBoxVMWizard", "Run this VirtualBox VM on my local computer"))
        self.uiRemoteServersGroupBox.setTitle(_translate("VirtualBoxVMWizard", "Remote servers"))
        self.uiRemoteServersLabel.setText(_translate("VirtualBoxVMWizard", "Run on server:"))
        self.uiVirtualBoxWizardPage.setTitle(_translate("VirtualBoxVMWizard", "VirtualBox Virtual Machine"))
        self.uiVirtualBoxWizardPage.setSubTitle(_translate("VirtualBoxVMWizard", "Please choose a VirtualBox virtual machine from the list."))
        self.uiVMListLabel.setText(_translate("VirtualBoxVMWizard", "VM list:"))
        self.uiBaseVMCheckBox.setText(_translate("VirtualBoxVMWizard", "Use as a linked base VM (experimental)"))

