# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'virtualbox_preferences_page.ui'
#
# Created by: PyQt5 UI code generator 5.4.1
#
# WARNING! All changes made in this file will be lost!

import gns3.qt
from gns3.qt import QtCore, QtGui, QtWidgets

class Ui_VirtualBoxPreferencesPageWidget(object):
    def setupUi(self, VirtualBoxPreferencesPageWidget):
        VirtualBoxPreferencesPageWidget.setObjectName("VirtualBoxPreferencesPageWidget")
        VirtualBoxPreferencesPageWidget.resize(450, 250)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(VirtualBoxPreferencesPageWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.uiTabWidget = QtWidgets.QTabWidget(VirtualBoxPreferencesPageWidget)
        self.uiTabWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.uiTabWidget.setObjectName("uiTabWidget")
        self.uiGeneralSettingsTabWidget = QtWidgets.QWidget()
        self.uiGeneralSettingsTabWidget.setObjectName("uiGeneralSettingsTabWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.uiGeneralSettingsTabWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiUseLocalServercheckBox = QtWidgets.QCheckBox(self.uiGeneralSettingsTabWidget)
        self.uiUseLocalServercheckBox.setChecked(True)
        self.uiUseLocalServercheckBox.setObjectName("uiUseLocalServercheckBox")
        self.verticalLayout.addWidget(self.uiUseLocalServercheckBox)
        self.uiVboxManagePathLabel = QtWidgets.QLabel(self.uiGeneralSettingsTabWidget)
        self.uiVboxManagePathLabel.setObjectName("uiVboxManagePathLabel")
        self.verticalLayout.addWidget(self.uiVboxManagePathLabel)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.uiVboxManagePathLineEdit = QtWidgets.QLineEdit(self.uiGeneralSettingsTabWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVboxManagePathLineEdit.sizePolicy().hasHeightForWidth())
        self.uiVboxManagePathLineEdit.setSizePolicy(sizePolicy)
        self.uiVboxManagePathLineEdit.setObjectName("uiVboxManagePathLineEdit")
        self.horizontalLayout_5.addWidget(self.uiVboxManagePathLineEdit)
        self.uiVboxManagePathToolButton = QtWidgets.QToolButton(self.uiGeneralSettingsTabWidget)
        self.uiVboxManagePathToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiVboxManagePathToolButton.setObjectName("uiVboxManagePathToolButton")
        self.horizontalLayout_5.addWidget(self.uiVboxManagePathToolButton)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.uiVboxManageUserLabel = QtWidgets.QLabel(self.uiGeneralSettingsTabWidget)
        self.uiVboxManageUserLabel.setObjectName("uiVboxManageUserLabel")
        self.verticalLayout.addWidget(self.uiVboxManageUserLabel)
        self.uiVboxManageUserLineEdit = QtWidgets.QLineEdit(self.uiGeneralSettingsTabWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVboxManageUserLineEdit.sizePolicy().hasHeightForWidth())
        self.uiVboxManageUserLineEdit.setSizePolicy(sizePolicy)
        self.uiVboxManageUserLineEdit.setObjectName("uiVboxManageUserLineEdit")
        self.verticalLayout.addWidget(self.uiVboxManageUserLineEdit)
        spacerItem = QtWidgets.QSpacerItem(390, 193, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.uiTabWidget.addTab(self.uiGeneralSettingsTabWidget, "")
        self.verticalLayout_2.addWidget(self.uiTabWidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(164, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.uiRestoreDefaultsPushButton = QtWidgets.QPushButton(VirtualBoxPreferencesPageWidget)
        self.uiRestoreDefaultsPushButton.setObjectName("uiRestoreDefaultsPushButton")
        self.horizontalLayout_2.addWidget(self.uiRestoreDefaultsPushButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(VirtualBoxPreferencesPageWidget)
        self.uiTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(VirtualBoxPreferencesPageWidget)

    def retranslateUi(self, VirtualBoxPreferencesPageWidget):
        _translate = gns3.qt.translate
        VirtualBoxPreferencesPageWidget.setWindowTitle(_translate("VirtualBoxPreferencesPageWidget", "VirtualBox"))
        self.uiUseLocalServercheckBox.setText(_translate("VirtualBoxPreferencesPageWidget", "Use the local server"))
        self.uiVboxManagePathLabel.setText(_translate("VirtualBoxPreferencesPageWidget", "Path to VBoxManage:"))
        self.uiVboxManagePathToolButton.setText(_translate("VirtualBoxPreferencesPageWidget", "&Browse..."))
        self.uiVboxManageUserLabel.setText(_translate("VirtualBoxPreferencesPageWidget", "Run VirtualBox as another user (GNS3 running as root):"))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiGeneralSettingsTabWidget), _translate("VirtualBoxPreferencesPageWidget", "General settings"))
        self.uiRestoreDefaultsPushButton.setText(_translate("VirtualBoxPreferencesPageWidget", "Restore defaults"))

