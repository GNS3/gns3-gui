# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/modules/virtualbox/ui/virtualbox_preferences_page.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_VirtualBoxPreferencesPageWidget(object):

    def setupUi(self, VirtualBoxPreferencesPageWidget):
        VirtualBoxPreferencesPageWidget.setObjectName("VirtualBoxPreferencesPageWidget")
        VirtualBoxPreferencesPageWidget.resize(450, 228)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(VirtualBoxPreferencesPageWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.uiTabWidget = QtWidgets.QTabWidget(VirtualBoxPreferencesPageWidget)
        self.uiTabWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.uiTabWidget.setObjectName("uiTabWidget")
        self.uiGeneralSettingsTabWidget = QtWidgets.QWidget()
        self.uiGeneralSettingsTabWidget.setObjectName("uiGeneralSettingsTabWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.uiGeneralSettingsTabWidget)
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout.setObjectName("verticalLayout")
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
        spacerItem = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
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
        _translate = QtCore.QCoreApplication.translate
        VirtualBoxPreferencesPageWidget.setWindowTitle(_translate("VirtualBoxPreferencesPageWidget", "VirtualBox"))
        self.uiVboxManagePathLabel.setText(_translate("VirtualBoxPreferencesPageWidget", "Path to VBoxManage:"))
        self.uiVboxManagePathToolButton.setText(_translate("VirtualBoxPreferencesPageWidget", "&Browse..."))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiGeneralSettingsTabWidget), _translate("VirtualBoxPreferencesPageWidget", "Local settings"))
        self.uiRestoreDefaultsPushButton.setText(_translate("VirtualBoxPreferencesPageWidget", "Restore defaults"))
