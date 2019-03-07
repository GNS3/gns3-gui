# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/export_project_wizard.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ExportProjectWizard(object):
    def setupUi(self, ExportProjectWizard):
        ExportProjectWizard.setObjectName("ExportProjectWizard")
        ExportProjectWizard.setWindowModality(QtCore.Qt.ApplicationModal)
        ExportProjectWizard.resize(900, 600)
        ExportProjectWizard.setOptions(QtWidgets.QWizard.HaveHelpButton)
        self.uiExportOptionsWizardPage = QtWidgets.QWizardPage()
        self.uiExportOptionsWizardPage.setObjectName("uiExportOptionsWizardPage")
        self.gridLayout = QtWidgets.QGridLayout(self.uiExportOptionsWizardPage)
        self.gridLayout.setObjectName("gridLayout")
        self.uiPathLabel = QtWidgets.QLabel(self.uiExportOptionsWizardPage)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiPathLabel.sizePolicy().hasHeightForWidth())
        self.uiPathLabel.setSizePolicy(sizePolicy)
        self.uiPathLabel.setObjectName("uiPathLabel")
        self.gridLayout.addWidget(self.uiPathLabel, 0, 0, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.uiPathLineEdit = QtWidgets.QLineEdit(self.uiExportOptionsWizardPage)
        self.uiPathLineEdit.setObjectName("uiPathLineEdit")
        self.horizontalLayout_3.addWidget(self.uiPathLineEdit)
        self.uiPathBrowserToolButton = QtWidgets.QToolButton(self.uiExportOptionsWizardPage)
        self.uiPathBrowserToolButton.setObjectName("uiPathBrowserToolButton")
        self.horizontalLayout_3.addWidget(self.uiPathBrowserToolButton)
        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 1, 1, 2)
        self.uiCompressionLabel = QtWidgets.QLabel(self.uiExportOptionsWizardPage)
        self.uiCompressionLabel.setObjectName("uiCompressionLabel")
        self.gridLayout.addWidget(self.uiCompressionLabel, 1, 0, 1, 1)
        self.uiIncludeImagesCheckBox = QtWidgets.QCheckBox(self.uiExportOptionsWizardPage)
        self.uiIncludeImagesCheckBox.setObjectName("uiIncludeImagesCheckBox")
        self.gridLayout.addWidget(self.uiIncludeImagesCheckBox, 2, 0, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(20, 247, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 1, 1, 1)
        self.uiCompressionComboBox = QtWidgets.QComboBox(self.uiExportOptionsWizardPage)
        self.uiCompressionComboBox.setObjectName("uiCompressionComboBox")
        self.gridLayout.addWidget(self.uiCompressionComboBox, 1, 1, 1, 2)
        ExportProjectWizard.addPage(self.uiExportOptionsWizardPage)
        self.uiProjectReadmeWizardPage = QtWidgets.QWizardPage()
        self.uiProjectReadmeWizardPage.setObjectName("uiProjectReadmeWizardPage")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.uiProjectReadmeWizardPage)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.uiReadmeTextEdit = QtWidgets.QTextEdit(self.uiProjectReadmeWizardPage)
        self.uiReadmeTextEdit.setObjectName("uiReadmeTextEdit")
        self.verticalLayout_2.addWidget(self.uiReadmeTextEdit)
        ExportProjectWizard.addPage(self.uiProjectReadmeWizardPage)

        self.retranslateUi(ExportProjectWizard)
        QtCore.QMetaObject.connectSlotsByName(ExportProjectWizard)

    def retranslateUi(self, ExportProjectWizard):
        _translate = QtCore.QCoreApplication.translate
        ExportProjectWizard.setWindowTitle(_translate("ExportProjectWizard", "Export project"))
        self.uiExportOptionsWizardPage.setTitle(_translate("ExportProjectWizard", "Export project"))
        self.uiExportOptionsWizardPage.setSubTitle(_translate("ExportProjectWizard", "Please select the location, whether to include base images or not and the compression type."))
        self.uiPathLabel.setText(_translate("ExportProjectWizard", "Path:"))
        self.uiPathBrowserToolButton.setText(_translate("ExportProjectWizard", "Browse..."))
        self.uiCompressionLabel.setText(_translate("ExportProjectWizard", "Compression:"))
        self.uiIncludeImagesCheckBox.setText(_translate("ExportProjectWizard", "Include base images"))
        self.uiProjectReadmeWizardPage.setTitle(_translate("ExportProjectWizard", "Readme file"))
        self.uiProjectReadmeWizardPage.setSubTitle(_translate("ExportProjectWizard", "Write a summary of the project."))
        self.uiReadmeTextEdit.setHtml(_translate("ExportProjectWizard", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'.SF NS Text\'; font-size:13pt;\"><br /></p></body></html>"))

