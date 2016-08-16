# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/ui/edit_project_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_EditProjectDialog(object):
    def setupUi(self, EditProjectDialog):
        EditProjectDialog.setObjectName("EditProjectDialog")
        EditProjectDialog.resize(525, 169)
        EditProjectDialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(EditProjectDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(EditProjectDialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.uiProjectNameLineEdit = QtWidgets.QLineEdit(EditProjectDialog)
        self.uiProjectNameLineEdit.setObjectName("uiProjectNameLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.uiProjectNameLineEdit)
        self.label_2 = QtWidgets.QLabel(EditProjectDialog)
        self.label_2.setText("")
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.uiProjectAutoCloseCheckBox = QtWidgets.QCheckBox(EditProjectDialog)
        self.uiProjectAutoCloseCheckBox.setObjectName("uiProjectAutoCloseCheckBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.uiProjectAutoCloseCheckBox)
        self.label_3 = QtWidgets.QLabel(EditProjectDialog)
        self.label_3.setText("")
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.uiProjectAutoOpenCheckBox = QtWidgets.QCheckBox(EditProjectDialog)
        self.uiProjectAutoOpenCheckBox.setObjectName("uiProjectAutoOpenCheckBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.uiProjectAutoOpenCheckBox)
        self.uiProjectAutoStartCheckBox = QtWidgets.QCheckBox(EditProjectDialog)
        self.uiProjectAutoStartCheckBox.setObjectName("uiProjectAutoStartCheckBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.uiProjectAutoStartCheckBox)
        self.verticalLayout.addLayout(self.formLayout)
        self.uiButtonBox = QtWidgets.QDialogButtonBox(EditProjectDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName("uiButtonBox")
        self.verticalLayout.addWidget(self.uiButtonBox)

        self.retranslateUi(EditProjectDialog)
        self.uiButtonBox.accepted.connect(EditProjectDialog.accept)
        self.uiButtonBox.rejected.connect(EditProjectDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(EditProjectDialog)

    def retranslateUi(self, EditProjectDialog):
        _translate = QtCore.QCoreApplication.translate
        EditProjectDialog.setWindowTitle(_translate("EditProjectDialog", "Edit project"))
        self.label.setText(_translate("EditProjectDialog", "Name:"))
        self.uiProjectAutoCloseCheckBox.setText(_translate("EditProjectDialog", "Leave this project open when closing GNS3"))
        self.uiProjectAutoOpenCheckBox.setText(_translate("EditProjectDialog", "Open the project in background when GNS3 server start"))
        self.uiProjectAutoStartCheckBox.setText(_translate("EditProjectDialog", "Start nodes when project is open"))

