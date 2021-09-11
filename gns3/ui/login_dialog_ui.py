# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/login_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LoginDialog(object):
    def setupUi(self, LoginDialog):
        LoginDialog.setObjectName("LoginDialog")
        LoginDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        LoginDialog.resize(377, 111)
        LoginDialog.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(LoginDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.uiPasswordLineEdit = QtWidgets.QLineEdit(LoginDialog)
        self.uiPasswordLineEdit.setMaxLength(100)
        self.uiPasswordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.uiPasswordLineEdit.setObjectName("uiPasswordLineEdit")
        self.gridLayout.addWidget(self.uiPasswordLineEdit, 1, 1, 1, 1)
        self.uiUsernameLabel = QtWidgets.QLabel(LoginDialog)
        self.uiUsernameLabel.setObjectName("uiUsernameLabel")
        self.gridLayout.addWidget(self.uiUsernameLabel, 0, 0, 1, 1)
        self.uiUsernameLineEdit = QtWidgets.QLineEdit(LoginDialog)
        self.uiUsernameLineEdit.setObjectName("uiUsernameLineEdit")
        self.gridLayout.addWidget(self.uiUsernameLineEdit, 0, 1, 1, 1)
        self.uiPasswordLabel = QtWidgets.QLabel(LoginDialog)
        self.uiPasswordLabel.setObjectName("uiPasswordLabel")
        self.gridLayout.addWidget(self.uiPasswordLabel, 1, 0, 1, 1)
        self.uiButtonBox = QtWidgets.QDialogButtonBox(LoginDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName("uiButtonBox")
        self.gridLayout.addWidget(self.uiButtonBox, 2, 0, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)

        self.retranslateUi(LoginDialog)
        self.uiButtonBox.accepted.connect(LoginDialog.accept)
        self.uiButtonBox.rejected.connect(LoginDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(LoginDialog)
        LoginDialog.setTabOrder(self.uiUsernameLineEdit, self.uiPasswordLineEdit)

    def retranslateUi(self, LoginDialog):
        _translate = QtCore.QCoreApplication.translate
        LoginDialog.setWindowTitle(_translate("LoginDialog", "Login"))
        self.uiUsernameLabel.setText(_translate("LoginDialog", "Username:"))
        self.uiPasswordLabel.setText(_translate("LoginDialog", "Password:"))
