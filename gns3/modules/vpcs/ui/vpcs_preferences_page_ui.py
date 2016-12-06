# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/modules/vpcs/ui/vpcs_preferences_page.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_VPCSPreferencesPageWidget(object):

    def setupUi(self, VPCSPreferencesPageWidget):
        VPCSPreferencesPageWidget.setObjectName("VPCSPreferencesPageWidget")
        VPCSPreferencesPageWidget.resize(469, 261)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(VPCSPreferencesPageWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.uiTabWidget = QtWidgets.QTabWidget(VPCSPreferencesPageWidget)
        self.uiTabWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.uiTabWidget.setObjectName("uiTabWidget")
        self.uiGeneralSettingsTabWidget = QtWidgets.QWidget()
        self.uiGeneralSettingsTabWidget.setObjectName("uiGeneralSettingsTabWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.uiGeneralSettingsTabWidget)
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout.setObjectName("verticalLayout")
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
        spacerItem = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.uiTabWidget.addTab(self.uiGeneralSettingsTabWidget, "")
        self.verticalLayout_2.addWidget(self.uiTabWidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(138, 17, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.uiRestoreDefaultsPushButton = QtWidgets.QPushButton(VPCSPreferencesPageWidget)
        self.uiRestoreDefaultsPushButton.setObjectName("uiRestoreDefaultsPushButton")
        self.horizontalLayout_2.addWidget(self.uiRestoreDefaultsPushButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(VPCSPreferencesPageWidget)
        self.uiTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(VPCSPreferencesPageWidget)

    def retranslateUi(self, VPCSPreferencesPageWidget):
        _translate = QtCore.QCoreApplication.translate
        VPCSPreferencesPageWidget.setWindowTitle(_translate("VPCSPreferencesPageWidget", "VPCS"))
        self.uiVPCSPathLabel.setText(_translate("VPCSPreferencesPageWidget", "Path to VPCS executable:"))
        self.uiVPCSPathToolButton.setText(_translate("VPCSPreferencesPageWidget", "&Browse..."))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiGeneralSettingsTabWidget), _translate("VPCSPreferencesPageWidget", "Local settings"))
        self.uiRestoreDefaultsPushButton.setText(_translate("VPCSPreferencesPageWidget", "Restore defaults"))
