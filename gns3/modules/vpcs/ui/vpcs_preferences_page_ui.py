# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'vpcs_preferences_page.ui'
#
# Created: Wed May  6 14:31:59 2015
#      by: PyQt5 UI code generator 5.4
#
# WARNING! All changes made in this file will be lost!

import gns3.qt
from gns3.qt import QtCore, QtGui, QtWidgets


class Ui_VPCSPreferencesPageWidget(object):

    def setupUi(self, VPCSPreferencesPageWidget):
        VPCSPreferencesPageWidget.setObjectName("VPCSPreferencesPageWidget")
        VPCSPreferencesPageWidget.resize(450, 200)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(VPCSPreferencesPageWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.uiTabWidget = QtWidgets.QTabWidget(VPCSPreferencesPageWidget)
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
        self.uiVPCSPathLabel = QtWidgets.QLabel(self.uiGeneralSettingsTabWidget)
        self.uiVPCSPathLabel.setObjectName("uiVPCSPathLabel")
        self.verticalLayout.addWidget(self.uiVPCSPathLabel)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.uiVPCSPathLineEdit = QtWidgets.QLineEdit(self.uiGeneralSettingsTabWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVPCSPathLineEdit.sizePolicy().hasHeightForWidth())
        self.uiVPCSPathLineEdit.setSizePolicy(sizePolicy)
        self.uiVPCSPathLineEdit.setObjectName("uiVPCSPathLineEdit")
        self.horizontalLayout_5.addWidget(self.uiVPCSPathLineEdit)
        self.uiVPCSPathToolButton = QtWidgets.QToolButton(self.uiGeneralSettingsTabWidget)
        self.uiVPCSPathToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiVPCSPathToolButton.setObjectName("uiVPCSPathToolButton")
        self.horizontalLayout_5.addWidget(self.uiVPCSPathToolButton)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        spacerItem = QtWidgets.QSpacerItem(390, 193, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.uiTabWidget.addTab(self.uiGeneralSettingsTabWidget, "")
        self.uiVPCSTabWidget = QtWidgets.QWidget()
        self.uiVPCSTabWidget.setObjectName("uiVPCSTabWidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.uiVPCSTabWidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.uiScriptFileLabel = QtWidgets.QLabel(self.uiVPCSTabWidget)
        self.uiScriptFileLabel.setObjectName("uiScriptFileLabel")
        self.verticalLayout_3.addWidget(self.uiScriptFileLabel)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.uiScriptFileEdit = QtWidgets.QLineEdit(self.uiVPCSTabWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiScriptFileEdit.sizePolicy().hasHeightForWidth())
        self.uiScriptFileEdit.setSizePolicy(sizePolicy)
        self.uiScriptFileEdit.setObjectName("uiScriptFileEdit")
        self.horizontalLayout_6.addWidget(self.uiScriptFileEdit)
        self.uiScriptFileToolButton = QtWidgets.QToolButton(self.uiVPCSTabWidget)
        self.uiScriptFileToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiScriptFileToolButton.setObjectName("uiScriptFileToolButton")
        self.horizontalLayout_6.addWidget(self.uiScriptFileToolButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout_6)
        spacerItem1 = QtWidgets.QSpacerItem(20, 387, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.uiTabWidget.addTab(self.uiVPCSTabWidget, "")
        self.verticalLayout_2.addWidget(self.uiTabWidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtWidgets.QSpacerItem(138, 17, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.uiRestoreDefaultsPushButton = QtWidgets.QPushButton(VPCSPreferencesPageWidget)
        self.uiRestoreDefaultsPushButton.setObjectName("uiRestoreDefaultsPushButton")
        self.horizontalLayout_2.addWidget(self.uiRestoreDefaultsPushButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(VPCSPreferencesPageWidget)
        self.uiTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(VPCSPreferencesPageWidget)

    def retranslateUi(self, VPCSPreferencesPageWidget):
        _translate = gns3.qt.translate
        VPCSPreferencesPageWidget.setWindowTitle(_translate("VPCSPreferencesPageWidget", "VPCS"))
        self.uiUseLocalServercheckBox.setText(_translate("VPCSPreferencesPageWidget", "Use the local server"))
        self.uiVPCSPathLabel.setText(_translate("VPCSPreferencesPageWidget", "Path to VPCS:"))
        self.uiVPCSPathToolButton.setText(_translate("VPCSPreferencesPageWidget", "&Browse..."))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiGeneralSettingsTabWidget), _translate("VPCSPreferencesPageWidget", "General settings"))
        self.uiScriptFileLabel.setText(_translate("VPCSPreferencesPageWidget", "Path to VPCS base script file:"))
        self.uiScriptFileToolButton.setText(_translate("VPCSPreferencesPageWidget", "&Browse..."))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiVPCSTabWidget), _translate("VPCSPreferencesPageWidget", "VPCS VM settings"))
        self.uiRestoreDefaultsPushButton.setText(_translate("VPCSPreferencesPageWidget", "Restore defaults"))
