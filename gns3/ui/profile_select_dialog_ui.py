# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/ui/profile_select_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.8
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ProfileSelectDialog(object):

    def setupUi(self, ProfileSelectDialog):
        ProfileSelectDialog.setObjectName("ProfileSelectDialog")
        ProfileSelectDialog.setWindowModality(QtCore.Qt.WindowModal)
        ProfileSelectDialog.resize(600, 249)
        ProfileSelectDialog.setMaximumSize(QtCore.QSize(600, 500))
        ProfileSelectDialog.setModal(False)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(ProfileSelectDialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.uiLogoLabel = QtWidgets.QLabel(ProfileSelectDialog)
        self.uiLogoLabel.setText("")
        self.uiLogoLabel.setPixmap(QtGui.QPixmap(":/images/gns3_logo.png"))
        self.uiLogoLabel.setObjectName("uiLogoLabel")
        self.horizontalLayout_3.addWidget(self.uiLogoLabel)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.horizontalLayout_3.addItem(spacerItem)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.uiProfileLabel = QtWidgets.QLabel(ProfileSelectDialog)
        self.uiProfileLabel.setObjectName("uiProfileLabel")
        self.horizontalLayout_2.addWidget(self.uiProfileLabel)
        self.uiProfileSelectComboBox = QtWidgets.QComboBox(ProfileSelectDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiProfileSelectComboBox.sizePolicy().hasHeightForWidth())
        self.uiProfileSelectComboBox.setSizePolicy(sizePolicy)
        self.uiProfileSelectComboBox.setObjectName("uiProfileSelectComboBox")
        self.horizontalLayout_2.addWidget(self.uiProfileSelectComboBox)
        self.uiNewPushButton = QtWidgets.QPushButton(ProfileSelectDialog)
        self.uiNewPushButton.setObjectName("uiNewPushButton")
        self.horizontalLayout_2.addWidget(self.uiNewPushButton)
        self.uiDeletePushButton = QtWidgets.QPushButton(ProfileSelectDialog)
        self.uiDeletePushButton.setObjectName("uiDeletePushButton")
        self.horizontalLayout_2.addWidget(self.uiDeletePushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.uiShowAtStartupCheckBox = QtWidgets.QCheckBox(ProfileSelectDialog)
        self.uiShowAtStartupCheckBox.setObjectName("uiShowAtStartupCheckBox")
        self.verticalLayout.addWidget(self.uiShowAtStartupCheckBox)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.uiButtonBox = QtWidgets.QDialogButtonBox(ProfileSelectDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiButtonBox.sizePolicy().hasHeightForWidth())
        self.uiButtonBox.setSizePolicy(sizePolicy)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName("uiButtonBox")
        self.horizontalLayout.addWidget(self.uiButtonBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(ProfileSelectDialog)
        self.uiButtonBox.accepted.connect(ProfileSelectDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(ProfileSelectDialog)

    def retranslateUi(self, ProfileSelectDialog):
        _translate = QtCore.QCoreApplication.translate
        ProfileSelectDialog.setWindowTitle(_translate("ProfileSelectDialog", "Profile selection"))
        self.uiProfileLabel.setText(_translate("ProfileSelectDialog", "Profile:"))
        self.uiNewPushButton.setText(_translate("ProfileSelectDialog", "New"))
        self.uiDeletePushButton.setText(_translate("ProfileSelectDialog", "Delete"))
        self.uiShowAtStartupCheckBox.setText(_translate("ProfileSelectDialog", "Show at next startup"))

from . import resources_rc
