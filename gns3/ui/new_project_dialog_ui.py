# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/ui/new_project_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_NewProjectDialog(object):
    def setupUi(self, NewProjectDialog):
        NewProjectDialog.setObjectName("NewProjectDialog")
        NewProjectDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        NewProjectDialog.resize(577, 188)
        NewProjectDialog.setModal(True)
        self.gridLayout_2 = QtWidgets.QGridLayout(NewProjectDialog)
        self.gridLayout_2.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.uiButtonBox = QtWidgets.QDialogButtonBox(NewProjectDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName("uiButtonBox")
        self.gridLayout_2.addWidget(self.uiButtonBox, 2, 2, 1, 1)
        self.uiOpenProjectPushButton = QtWidgets.QPushButton(NewProjectDialog)
        self.uiOpenProjectPushButton.setObjectName("uiOpenProjectPushButton")
        self.gridLayout_2.addWidget(self.uiOpenProjectPushButton, 2, 0, 1, 1)
        self.uiRecentProjectsPushButton = QtWidgets.QPushButton(NewProjectDialog)
        self.uiRecentProjectsPushButton.setObjectName("uiRecentProjectsPushButton")
        self.gridLayout_2.addWidget(self.uiRecentProjectsPushButton, 2, 1, 1, 1)
        self.uiProjectGroupBox = QtWidgets.QGroupBox(NewProjectDialog)
        self.uiProjectGroupBox.setObjectName("uiProjectGroupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.uiProjectGroupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.uiNameLabel = QtWidgets.QLabel(self.uiProjectGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiNameLabel.sizePolicy().hasHeightForWidth())
        self.uiNameLabel.setSizePolicy(sizePolicy)
        self.uiNameLabel.setTextFormat(QtCore.Qt.AutoText)
        self.uiNameLabel.setObjectName("uiNameLabel")
        self.gridLayout.addWidget(self.uiNameLabel, 0, 0, 1, 1)
        self.uiNameLineEdit = QtWidgets.QLineEdit(self.uiProjectGroupBox)
        self.uiNameLineEdit.setObjectName("uiNameLineEdit")
        self.gridLayout.addWidget(self.uiNameLineEdit, 0, 1, 1, 3)
        self.uiLocationLabel = QtWidgets.QLabel(self.uiProjectGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiLocationLabel.sizePolicy().hasHeightForWidth())
        self.uiLocationLabel.setSizePolicy(sizePolicy)
        self.uiLocationLabel.setObjectName("uiLocationLabel")
        self.gridLayout.addWidget(self.uiLocationLabel, 1, 0, 1, 1)
        self.uiLocationLineEdit = QtWidgets.QLineEdit(self.uiProjectGroupBox)
        self.uiLocationLineEdit.setObjectName("uiLocationLineEdit")
        self.gridLayout.addWidget(self.uiLocationLineEdit, 1, 1, 1, 2)
        self.uiLocationBrowserToolButton = QtWidgets.QToolButton(self.uiProjectGroupBox)
        self.uiLocationBrowserToolButton.setObjectName("uiLocationBrowserToolButton")
        self.gridLayout.addWidget(self.uiLocationBrowserToolButton, 1, 3, 1, 1)
        self.gridLayout_2.addWidget(self.uiProjectGroupBox, 0, 0, 1, 4)

        self.retranslateUi(NewProjectDialog)
        self.uiButtonBox.accepted.connect(NewProjectDialog.accept)
        self.uiButtonBox.rejected.connect(NewProjectDialog.reject)
        self.uiNameLineEdit.returnPressed.connect(NewProjectDialog.accept)
        self.uiLocationLineEdit.returnPressed.connect(NewProjectDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(NewProjectDialog)

    def retranslateUi(self, NewProjectDialog):
        _translate = QtCore.QCoreApplication.translate
        NewProjectDialog.setWindowTitle(_translate("NewProjectDialog", "New project"))
        self.uiOpenProjectPushButton.setText(_translate("NewProjectDialog", "&Open a project"))
        self.uiRecentProjectsPushButton.setText(_translate("NewProjectDialog", "&Recent projects..."))
        self.uiProjectGroupBox.setTitle(_translate("NewProjectDialog", "Project"))
        self.uiNameLabel.setText(_translate("NewProjectDialog", "Name:"))
        self.uiLocationLabel.setText(_translate("NewProjectDialog", "Location:"))
        self.uiLocationBrowserToolButton.setText(_translate("NewProjectDialog", "Browse..."))

