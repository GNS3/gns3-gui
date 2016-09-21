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
        EditProjectDialog.resize(625, 309)
        EditProjectDialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(EditProjectDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setRowWrapPolicy(QtWidgets.QFormLayout.DontWrapRows)
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignCenter)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(EditProjectDialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.uiProjectNameLineEdit = QtWidgets.QLineEdit(EditProjectDialog)
        self.uiProjectNameLineEdit.setObjectName("uiProjectNameLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.uiProjectNameLineEdit)
        self.label_2 = QtWidgets.QLabel(EditProjectDialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.uiSceneWidthSpinBox = QtWidgets.QSpinBox(EditProjectDialog)
        self.uiSceneWidthSpinBox.setMinimum(500)
        self.uiSceneWidthSpinBox.setMaximum(1000000)
        self.uiSceneWidthSpinBox.setObjectName("uiSceneWidthSpinBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.uiSceneWidthSpinBox)
        self.label_3 = QtWidgets.QLabel(EditProjectDialog)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.uiSceneHeightSpinBox = QtWidgets.QSpinBox(EditProjectDialog)
        self.uiSceneHeightSpinBox.setMinimum(500)
        self.uiSceneHeightSpinBox.setMaximum(1000000)
        self.uiSceneHeightSpinBox.setObjectName("uiSceneHeightSpinBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.uiSceneHeightSpinBox)
        self.label_4 = QtWidgets.QLabel(EditProjectDialog)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.uiProjectAutoOpenCheckBox = QtWidgets.QCheckBox(EditProjectDialog)
        self.uiProjectAutoOpenCheckBox.setText("")
        self.uiProjectAutoOpenCheckBox.setObjectName("uiProjectAutoOpenCheckBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.uiProjectAutoOpenCheckBox)
        self.label_5 = QtWidgets.QLabel(EditProjectDialog)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.uiProjectAutoStartCheckBox = QtWidgets.QCheckBox(EditProjectDialog)
        self.uiProjectAutoStartCheckBox.setText("")
        self.uiProjectAutoStartCheckBox.setObjectName("uiProjectAutoStartCheckBox")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.uiProjectAutoStartCheckBox)
        self.label_6 = QtWidgets.QLabel(EditProjectDialog)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.uiProjectAutoCloseCheckBox = QtWidgets.QCheckBox(EditProjectDialog)
        self.uiProjectAutoCloseCheckBox.setText("")
        self.uiProjectAutoCloseCheckBox.setObjectName("uiProjectAutoCloseCheckBox")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.uiProjectAutoCloseCheckBox)
        self.verticalLayout.addLayout(self.formLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.uiButtonBox = QtWidgets.QDialogButtonBox(EditProjectDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName("uiButtonBox")
        self.verticalLayout.addWidget(self.uiButtonBox)

        self.retranslateUi(EditProjectDialog)
        self.uiButtonBox.accepted.connect(EditProjectDialog.accept)
        self.uiButtonBox.rejected.connect(EditProjectDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(EditProjectDialog)

    def retranslateUi(self, EditProjectDialog):
        _translate = QtCore.QCoreApplication.translate
        EditProjectDialog.setWindowTitle(_translate("EditProjectDialog", "Edit project"))
        self.label.setText(_translate("EditProjectDialog", "Project Name:"))
        self.label_2.setText(_translate("EditProjectDialog", "Scene width"))
        self.uiSceneWidthSpinBox.setSuffix(_translate("EditProjectDialog", " px"))
        self.label_3.setText(_translate("EditProjectDialog", "Scene height:"))
        self.uiSceneHeightSpinBox.setSuffix(_translate("EditProjectDialog", " px"))
        self.label_4.setText(_translate("EditProjectDialog", "Open this project in the background when GNS3 server starts:"))
        self.label_5.setText(_translate("EditProjectDialog", "Start all nodes when this project is loaded"))
        self.label_6.setText(_translate("EditProjectDialog", "Leave this project open when closing GNS3"))
