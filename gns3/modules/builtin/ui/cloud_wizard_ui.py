# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/builtin/ui/cloud_wizard.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CloudNodeWizard(object):
    def setupUi(self, CloudNodeWizard):
        CloudNodeWizard.setObjectName("CloudNodeWizard")
        CloudNodeWizard.resize(670, 452)
        CloudNodeWizard.setModal(True)
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
        CloudNodeWizard.addPage(self.uiServerWizardPage)
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
        CloudNodeWizard.addPage(self.uiNameWizardPage)

        self.retranslateUi(CloudNodeWizard)
        QtCore.QMetaObject.connectSlotsByName(CloudNodeWizard)

    def retranslateUi(self, CloudNodeWizard):
        _translate = QtCore.QCoreApplication.translate
        CloudNodeWizard.setWindowTitle(_translate("CloudNodeWizard", "New cloud node template"))
        self.uiServerWizardPage.setTitle(_translate("CloudNodeWizard", "Server"))
        self.uiServerWizardPage.setSubTitle(_translate("CloudNodeWizard", "Please choose a server type to run the cloud node."))
        self.uiServerTypeGroupBox.setTitle(_translate("CloudNodeWizard", "Server type"))
        self.uiRemoteRadioButton.setText(_translate("CloudNodeWizard", "Run the cloud node on a remote computers"))
        self.uiVMRadioButton.setText(_translate("CloudNodeWizard", "Run the cloud node on the GNS3 VM"))
        self.uiLocalRadioButton.setText(_translate("CloudNodeWizard", "Run the cloud node on your local computer"))
        self.uiRemoteServersGroupBox.setTitle(_translate("CloudNodeWizard", "Remote server"))
        self.uiRemoteServersLabel.setText(_translate("CloudNodeWizard", "Run on:"))
        self.uiNameWizardPage.setTitle(_translate("CloudNodeWizard", "Name"))
        self.uiNameWizardPage.setSubTitle(_translate("CloudNodeWizard", "Please choose a descriptive name for the new cloud node."))
        self.uiNameLabel.setText(_translate("CloudNodeWizard", "Name:"))

