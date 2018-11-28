# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/vmware/ui/vmware_vm_wizard.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_VMwareVMWizard(object):
    def setupUi(self, VMwareVMWizard):
        VMwareVMWizard.setObjectName("VMwareVMWizard")
        VMwareVMWizard.resize(755, 453)
        VMwareVMWizard.setModal(True)
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
        VMwareVMWizard.addPage(self.uiServerWizardPage)
        self.uiVMwareWizardPage = QtWidgets.QWizardPage()
        self.uiVMwareWizardPage.setObjectName("uiVMwareWizardPage")
        self.gridLayout = QtWidgets.QGridLayout(self.uiVMwareWizardPage)
        self.gridLayout.setObjectName("gridLayout")
        self.uiVMListLabel = QtWidgets.QLabel(self.uiVMwareWizardPage)
        self.uiVMListLabel.setObjectName("uiVMListLabel")
        self.gridLayout.addWidget(self.uiVMListLabel, 0, 0, 1, 1)
        self.uiVMListComboBox = QtWidgets.QComboBox(self.uiVMwareWizardPage)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVMListComboBox.sizePolicy().hasHeightForWidth())
        self.uiVMListComboBox.setSizePolicy(sizePolicy)
        self.uiVMListComboBox.setObjectName("uiVMListComboBox")
        self.gridLayout.addWidget(self.uiVMListComboBox, 0, 1, 1, 1)
        self.uiBaseVMCheckBox = QtWidgets.QCheckBox(self.uiVMwareWizardPage)
        self.uiBaseVMCheckBox.setEnabled(True)
        self.uiBaseVMCheckBox.setObjectName("uiBaseVMCheckBox")
        self.gridLayout.addWidget(self.uiBaseVMCheckBox, 1, 0, 1, 2)
        VMwareVMWizard.addPage(self.uiVMwareWizardPage)

        self.retranslateUi(VMwareVMWizard)
        QtCore.QMetaObject.connectSlotsByName(VMwareVMWizard)

    def retranslateUi(self, VMwareVMWizard):
        _translate = QtCore.QCoreApplication.translate
        VMwareVMWizard.setWindowTitle(_translate("VMwareVMWizard", "New VMware VM template"))
        self.uiServerWizardPage.setTitle(_translate("VMwareVMWizard", "Server"))
        self.uiServerWizardPage.setSubTitle(_translate("VMwareVMWizard", "Please choose a server type to run the VMware VM (Workstation, Player or Fusion)."))
        self.uiServerTypeGroupBox.setTitle(_translate("VMwareVMWizard", "Server type"))
        self.uiRemoteRadioButton.setText(_translate("VMwareVMWizard", "Run this VMware VM on a remote GNS3 computer"))
        self.uiLocalRadioButton.setText(_translate("VMwareVMWizard", "Run this VMware VM on my local computer"))
        self.uiRemoteServersGroupBox.setTitle(_translate("VMwareVMWizard", "Remote servers"))
        self.uiRemoteServersLabel.setText(_translate("VMwareVMWizard", "Run on server:"))
        self.uiVMwareWizardPage.setTitle(_translate("VMwareVMWizard", "VMware Virtual Machine"))
        self.uiVMwareWizardPage.setSubTitle(_translate("VMwareVMWizard", "Please choose a VMware virtual machine from the list."))
        self.uiVMListLabel.setText(_translate("VMwareVMWizard", "VM list:"))
        self.uiBaseVMCheckBox.setText(_translate("VMwareVMWizard", "Use as a linked base VM (experimental)"))

