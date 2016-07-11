# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/vpcs/ui/vpcs_node_wizard.ui'
#
# Created: Sun Jul 10 16:48:58 2016
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_VPCSNodeWizard(object):
    def setupUi(self, VPCSNodeWizard):
        VPCSNodeWizard.setObjectName("VPCSNodeWizard")
        VPCSNodeWizard.resize(585, 423)
        VPCSNodeWizard.setModal(True)
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
        self.uiVMRadioButton = QtWidgets.QRadioButton(self.uiServerTypeGroupBox)
        self.uiVMRadioButton.setObjectName("uiVMRadioButton")
        self.verticalLayout.addWidget(self.uiVMRadioButton)
        self.uiLocalRadioButton = QtWidgets.QRadioButton(self.uiServerTypeGroupBox)
        self.uiLocalRadioButton.setObjectName("uiLocalRadioButton")
        self.verticalLayout.addWidget(self.uiLocalRadioButton)
        self.gridLayout_2.addWidget(self.uiServerTypeGroupBox, 0, 0, 1, 1)
        self.uiRemoteServersGroupBox = QtWidgets.QGroupBox(self.uiServerWizardPage)
        self.uiRemoteServersGroupBox.setObjectName("uiRemoteServersGroupBox")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.uiRemoteServersGroupBox)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.uiRemoteServersLabel = QtWidgets.QLabel(self.uiRemoteServersGroupBox)
        self.uiRemoteServersLabel.setObjectName("uiRemoteServersLabel")
        self.gridLayout_7.addWidget(self.uiRemoteServersLabel, 0, 0, 1, 1)
        self.uiRemoteServersComboBox = QtWidgets.QComboBox(self.uiRemoteServersGroupBox)
        self.uiRemoteServersComboBox.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiRemoteServersComboBox.sizePolicy().hasHeightForWidth())
        self.uiRemoteServersComboBox.setSizePolicy(sizePolicy)
        self.uiRemoteServersComboBox.setObjectName("uiRemoteServersComboBox")
        self.gridLayout_7.addWidget(self.uiRemoteServersComboBox, 0, 1, 1, 1)
        self.gridLayout_2.addWidget(self.uiRemoteServersGroupBox, 1, 0, 1, 1)
        VPCSNodeWizard.addPage(self.uiServerWizardPage)
        self.uiNameWizardPage = QtWidgets.QWizardPage()
        self.uiNameWizardPage.setObjectName("uiNameWizardPage")
        self.gridLayout = QtWidgets.QGridLayout(self.uiNameWizardPage)
        self.gridLayout.setObjectName("gridLayout")
        self.uiNameLabel = QtWidgets.QLabel(self.uiNameWizardPage)
        self.uiNameLabel.setObjectName("uiNameLabel")
        self.gridLayout.addWidget(self.uiNameLabel, 0, 0, 1, 1)
        self.uiNameLineEdit = QtWidgets.QLineEdit(self.uiNameWizardPage)
        self.uiNameLineEdit.setObjectName("uiNameLineEdit")
        self.gridLayout.addWidget(self.uiNameLineEdit, 0, 1, 1, 1)
        VPCSNodeWizard.addPage(self.uiNameWizardPage)

        self.retranslateUi(VPCSNodeWizard)
        QtCore.QMetaObject.connectSlotsByName(VPCSNodeWizard)

    def retranslateUi(self, VPCSNodeWizard):
        _translate = QtCore.QCoreApplication.translate
        VPCSNodeWizard.setWindowTitle(_translate("VPCSNodeWizard", "New VPCS node template"))
        self.uiServerWizardPage.setTitle(_translate("VPCSNodeWizard", "Server"))
        self.uiServerWizardPage.setSubTitle(_translate("VPCSNodeWizard", "Please choose a server type to run your new VPCS node."))
        self.uiServerTypeGroupBox.setTitle(_translate("VPCSNodeWizard", "Server type"))
        self.uiRemoteRadioButton.setText(_translate("VPCSNodeWizard", "Run the VPCS node on a remote computer"))
        self.uiVMRadioButton.setText(_translate("VPCSNodeWizard", "Run the VPCS node on the GNS3 VM"))
        self.uiLocalRadioButton.setText(_translate("VPCSNodeWizard", "Run the VPCS node on your local computer"))
        self.uiRemoteServersGroupBox.setTitle(_translate("VPCSNodeWizard", "Remote server"))
        self.uiRemoteServersLabel.setText(_translate("VPCSNodeWizard", "Run on:"))
        self.uiNameWizardPage.setTitle(_translate("VPCSNodeWizard", "Name"))
        self.uiNameWizardPage.setSubTitle(_translate("VPCSNodeWizard", "Please choose a descriptive name for the new VPCS node."))
        self.uiNameLabel.setText(_translate("VPCSNodeWizard", "Name:"))

