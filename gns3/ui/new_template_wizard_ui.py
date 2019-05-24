# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/new_template_wizard.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_NewTemplateWizard(object):
    def setupUi(self, NewTemplateWizard):
        NewTemplateWizard.setObjectName("NewTemplateWizard")
        NewTemplateWizard.setWindowModality(QtCore.Qt.ApplicationModal)
        NewTemplateWizard.resize(900, 600)
        self.uiSelectTemplateSourceWizardPage = QtWidgets.QWizardPage()
        self.uiSelectTemplateSourceWizardPage.setObjectName("uiSelectTemplateSourceWizardPage")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.uiSelectTemplateSourceWizardPage)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiImportApplianceFromServerRadioButton = QtWidgets.QRadioButton(self.uiSelectTemplateSourceWizardPage)
        self.uiImportApplianceFromServerRadioButton.setChecked(True)
        self.uiImportApplianceFromServerRadioButton.setObjectName("uiImportApplianceFromServerRadioButton")
        self.verticalLayout.addWidget(self.uiImportApplianceFromServerRadioButton)
        self.uiImportApplianceFromFileRadioButton = QtWidgets.QRadioButton(self.uiSelectTemplateSourceWizardPage)
        self.uiImportApplianceFromFileRadioButton.setObjectName("uiImportApplianceFromFileRadioButton")
        self.verticalLayout.addWidget(self.uiImportApplianceFromFileRadioButton)
        self.uiCreateTemplateManuallyRadioButton = QtWidgets.QRadioButton(self.uiSelectTemplateSourceWizardPage)
        self.uiCreateTemplateManuallyRadioButton.setObjectName("uiCreateTemplateManuallyRadioButton")
        self.verticalLayout.addWidget(self.uiCreateTemplateManuallyRadioButton)
        NewTemplateWizard.addPage(self.uiSelectTemplateSourceWizardPage)
        self.uiApplianceFromServerWizardPage = QtWidgets.QWizardPage()
        self.uiApplianceFromServerWizardPage.setObjectName("uiApplianceFromServerWizardPage")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.uiApplianceFromServerWizardPage)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.uiFilterLineEdit = QtWidgets.QLineEdit(self.uiApplianceFromServerWizardPage)
        self.uiFilterLineEdit.setObjectName("uiFilterLineEdit")
        self.verticalLayout_2.addWidget(self.uiFilterLineEdit)
        self.uiAppliancesTreeWidget = QtWidgets.QTreeWidget(self.uiApplianceFromServerWizardPage)
        self.uiAppliancesTreeWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.uiAppliancesTreeWidget.setIndentation(10)
        self.uiAppliancesTreeWidget.setObjectName("uiAppliancesTreeWidget")
        self.uiAppliancesTreeWidget.header().setSortIndicatorShown(True)
        self.verticalLayout_2.addWidget(self.uiAppliancesTreeWidget)
        NewTemplateWizard.addPage(self.uiApplianceFromServerWizardPage)

        self.retranslateUi(NewTemplateWizard)
        QtCore.QMetaObject.connectSlotsByName(NewTemplateWizard)

    def retranslateUi(self, NewTemplateWizard):
        _translate = QtCore.QCoreApplication.translate
        NewTemplateWizard.setWindowTitle(_translate("NewTemplateWizard", "New template"))
        self.uiSelectTemplateSourceWizardPage.setTitle(_translate("NewTemplateWizard", "New template"))
        self.uiSelectTemplateSourceWizardPage.setSubTitle(_translate("NewTemplateWizard", "Please select how you want to create a new template"))
        self.uiImportApplianceFromServerRadioButton.setText(_translate("NewTemplateWizard", "&Install an appliance from the GNS3 server (recommended)"))
        self.uiImportApplianceFromFileRadioButton.setText(_translate("NewTemplateWizard", "&Import an appliance file (.gns3a extension)"))
        self.uiCreateTemplateManuallyRadioButton.setText(_translate("NewTemplateWizard", "&Manually create a new template"))
        self.uiApplianceFromServerWizardPage.setTitle(_translate("NewTemplateWizard", "Appliances from server"))
        self.uiApplianceFromServerWizardPage.setSubTitle(_translate("NewTemplateWizard", "Select one or more appliances to install. Update will request the server to download appliances from our online registry."))
        self.uiFilterLineEdit.setPlaceholderText(_translate("NewTemplateWizard", "Filter"))
        self.uiAppliancesTreeWidget.setSortingEnabled(True)
        self.uiAppliancesTreeWidget.headerItem().setText(0, _translate("NewTemplateWizard", "Appliance name"))
        self.uiAppliancesTreeWidget.headerItem().setText(1, _translate("NewTemplateWizard", "Emulator"))
        self.uiAppliancesTreeWidget.headerItem().setText(2, _translate("NewTemplateWizard", "Vendor"))

