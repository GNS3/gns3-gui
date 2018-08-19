# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/new_appliance_wizard.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_NewApplianceWizard(object):
    def setupUi(self, NewApplianceWizard):
        NewApplianceWizard.setObjectName("NewApplianceWizard")
        NewApplianceWizard.resize(1399, 919)
        NewApplianceWizard.setOptions(QtWidgets.QWizard.HaveFinishButtonOnEarlyPages)
        self.uiSelectApplianceSourceWizardPage = QtWidgets.QWizardPage()
        self.uiSelectApplianceSourceWizardPage.setObjectName("uiSelectApplianceSourceWizardPage")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.uiSelectApplianceSourceWizardPage)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiAddApplianceFromServerRadioButton = QtWidgets.QRadioButton(self.uiSelectApplianceSourceWizardPage)
        self.uiAddApplianceFromServerRadioButton.setChecked(True)
        self.uiAddApplianceFromServerRadioButton.setObjectName("uiAddApplianceFromServerRadioButton")
        self.verticalLayout.addWidget(self.uiAddApplianceFromServerRadioButton)
        self.uiAddApplianceFromTemplateFileRadioButton = QtWidgets.QRadioButton(self.uiSelectApplianceSourceWizardPage)
        self.uiAddApplianceFromTemplateFileRadioButton.setObjectName("uiAddApplianceFromTemplateFileRadioButton")
        self.verticalLayout.addWidget(self.uiAddApplianceFromTemplateFileRadioButton)
        self.uiAddApplianceManuallyRadioButton = QtWidgets.QRadioButton(self.uiSelectApplianceSourceWizardPage)
        self.uiAddApplianceManuallyRadioButton.setObjectName("uiAddApplianceManuallyRadioButton")
        self.verticalLayout.addWidget(self.uiAddApplianceManuallyRadioButton)
        NewApplianceWizard.addPage(self.uiSelectApplianceSourceWizardPage)
        self.uiApplianceFromServerWizardPage = QtWidgets.QWizardPage()
        self.uiApplianceFromServerWizardPage.setObjectName("uiApplianceFromServerWizardPage")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.uiApplianceFromServerWizardPage)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.uiFilterLineEdit = QtWidgets.QLineEdit(self.uiApplianceFromServerWizardPage)
        self.uiFilterLineEdit.setObjectName("uiFilterLineEdit")
        self.verticalLayout_2.addWidget(self.uiFilterLineEdit)
        self.uiApplianceTemplatesTreeWidget = QtWidgets.QTreeWidget(self.uiApplianceFromServerWizardPage)
        self.uiApplianceTemplatesTreeWidget.setRootIsDecorated(False)
        self.uiApplianceTemplatesTreeWidget.setObjectName("uiApplianceTemplatesTreeWidget")
        self.verticalLayout_2.addWidget(self.uiApplianceTemplatesTreeWidget)
        NewApplianceWizard.addPage(self.uiApplianceFromServerWizardPage)

        self.retranslateUi(NewApplianceWizard)
        QtCore.QMetaObject.connectSlotsByName(NewApplianceWizard)

    def retranslateUi(self, NewApplianceWizard):
        _translate = QtCore.QCoreApplication.translate
        NewApplianceWizard.setWindowTitle(_translate("NewApplianceWizard", "Wizard"))
        self.uiSelectApplianceSourceWizardPage.setTitle(_translate("NewApplianceWizard", "New appliance"))
        self.uiSelectApplianceSourceWizardPage.setSubTitle(_translate("NewApplianceWizard", "Please choose how you want to add a new appliance."))
        self.uiAddApplianceFromServerRadioButton.setText(_translate("NewApplianceWizard", "&Add an appliance from the GNS3 server (recommended)"))
        self.uiAddApplianceFromTemplateFileRadioButton.setText(_translate("NewApplianceWizard", "&Add an appliance using a template file (.gns3a)"))
        self.uiAddApplianceManuallyRadioButton.setText(_translate("NewApplianceWizard", "&Add an appliance manually"))
        self.uiApplianceFromServerWizardPage.setTitle(_translate("NewApplianceWizard", "Appliance templates from server"))
        self.uiApplianceFromServerWizardPage.setSubTitle(_translate("NewApplianceWizard", "Please select an appliance to install. Update will request the server to download appliance templates from our online registry."))
        self.uiFilterLineEdit.setPlaceholderText(_translate("NewApplianceWizard", "Filter"))
        self.uiApplianceTemplatesTreeWidget.setSortingEnabled(True)
        self.uiApplianceTemplatesTreeWidget.headerItem().setText(0, _translate("NewApplianceWizard", "Appliance name"))
        self.uiApplianceTemplatesTreeWidget.headerItem().setText(1, _translate("NewApplianceWizard", "Type"))
        self.uiApplianceTemplatesTreeWidget.headerItem().setText(2, _translate("NewApplianceWizard", "Emulator"))
        self.uiApplianceTemplatesTreeWidget.headerItem().setText(3, _translate("NewApplianceWizard", "Vendor"))

