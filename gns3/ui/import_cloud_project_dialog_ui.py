# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/ui/import_cloud_project_dialog.ui'
#
# Created: Fri Apr 17 10:44:30 2015
#      by: PyQt5 UI code generator 5.4
#
# WARNING! All changes made in this file will be lost!

from gns3.qt import QtCore, QtGui, QtWidgets


class Ui_ImportCloudProjectDialog:

    def setupUi(self, ImportCloudProjectDialog):
        ImportCloudProjectDialog.setObjectName("ImportCloudProjectDialog")
        ImportCloudProjectDialog.resize(471, 402)
        self.listWidget = QtWidgets.QListWidget(ImportCloudProjectDialog)
        self.listWidget.setGeometry(QtCore.QRect(20, 30, 431, 271))
        self.listWidget.setObjectName("listWidget")
        self.uiImportProjectAction = QtWidgets.QPushButton(ImportCloudProjectDialog)
        self.uiImportProjectAction.setGeometry(QtCore.QRect(110, 320, 99, 24))
        self.uiImportProjectAction.setObjectName("uiImportProjectAction")
        self.uiDeleteProjectAction = QtWidgets.QPushButton(ImportCloudProjectDialog)
        self.uiDeleteProjectAction.setGeometry(QtCore.QRect(260, 320, 99, 24))
        self.uiDeleteProjectAction.setObjectName("uiDeleteProjectAction")
        self.buttonBox = QtWidgets.QDialogButtonBox(ImportCloudProjectDialog)
        self.buttonBox.setGeometry(QtCore.QRect(300, 360, 160, 25))
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.setObjectName("buttonBox")

        self.retranslateUi(ImportCloudProjectDialog)
        self.buttonBox.rejected.connect(ImportCloudProjectDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ImportCloudProjectDialog)

    def retranslateUi(self, ImportCloudProjectDialog):
        _translate = QtCore.QCoreApplication.translate
        ImportCloudProjectDialog.setWindowTitle(_translate("ImportCloudProjectDialog", "Dialog"))
        self.uiImportProjectAction.setText(_translate("ImportCloudProjectDialog", "Import"))
        self.uiDeleteProjectAction.setText(_translate("ImportCloudProjectDialog", "Delete"))
