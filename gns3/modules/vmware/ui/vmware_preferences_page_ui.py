# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/modules/vmware/ui/vmware_preferences_page.ui'
#
# Created: Mon May  4 12:01:33 2015
#      by: PyQt5 UI code generator 5.4
#
# WARNING! All changes made in this file will be lost!

import gns3.qt
from gns3.qt import QtCore, QtGui, QtWidgets


class Ui_VMwarePreferencesPageWidget(object):

    def setupUi(self, VMwarePreferencesPageWidget):
        VMwarePreferencesPageWidget.setObjectName("VMwarePreferencesPageWidget")
        VMwarePreferencesPageWidget.resize(430, 490)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(VMwarePreferencesPageWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.uiTabWidget = QtWidgets.QTabWidget(VMwarePreferencesPageWidget)
        self.uiTabWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.uiTabWidget.setObjectName("uiTabWidget")
        self.uiGeneralSettingsTabWidget = QtWidgets.QWidget()
        self.uiGeneralSettingsTabWidget.setObjectName("uiGeneralSettingsTabWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.uiGeneralSettingsTabWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.uiVmrunPathLabel = QtWidgets.QLabel(self.uiGeneralSettingsTabWidget)
        self.uiVmrunPathLabel.setObjectName("uiVmrunPathLabel")
        self.gridLayout.addWidget(self.uiVmrunPathLabel, 1, 0, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(390, 193, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 6, 0, 1, 2)
        self.uiHostTypeLabel = QtWidgets.QLabel(self.uiGeneralSettingsTabWidget)
        self.uiHostTypeLabel.setObjectName("uiHostTypeLabel")
        self.gridLayout.addWidget(self.uiHostTypeLabel, 3, 0, 2, 2)
        self.uiUseLocalServercheckBox = QtWidgets.QCheckBox(self.uiGeneralSettingsTabWidget)
        self.uiUseLocalServercheckBox.setChecked(True)
        self.uiUseLocalServercheckBox.setObjectName("uiUseLocalServercheckBox")
        self.gridLayout.addWidget(self.uiUseLocalServercheckBox, 0, 0, 1, 2)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.uiVmrunPathLineEdit = QtWidgets.QLineEdit(self.uiGeneralSettingsTabWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVmrunPathLineEdit.sizePolicy().hasHeightForWidth())
        self.uiVmrunPathLineEdit.setSizePolicy(sizePolicy)
        self.uiVmrunPathLineEdit.setObjectName("uiVmrunPathLineEdit")
        self.horizontalLayout_5.addWidget(self.uiVmrunPathLineEdit)
        self.uiVmrunPathToolButton = QtWidgets.QToolButton(self.uiGeneralSettingsTabWidget)
        self.uiVmrunPathToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiVmrunPathToolButton.setObjectName("uiVmrunPathToolButton")
        self.horizontalLayout_5.addWidget(self.uiVmrunPathToolButton)
        self.gridLayout.addLayout(self.horizontalLayout_5, 2, 0, 1, 2)
        self.uiHostTypeComboBox = QtWidgets.QComboBox(self.uiGeneralSettingsTabWidget)
        self.uiHostTypeComboBox.setObjectName("uiHostTypeComboBox")
        self.gridLayout.addWidget(self.uiHostTypeComboBox, 5, 0, 1, 2)
        self.uiTabWidget.addTab(self.uiGeneralSettingsTabWidget, "")
        self.verticalLayout_2.addWidget(self.uiTabWidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(164, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.uiRestoreDefaultsPushButton = QtWidgets.QPushButton(VMwarePreferencesPageWidget)
        self.uiRestoreDefaultsPushButton.setObjectName("uiRestoreDefaultsPushButton")
        self.horizontalLayout_2.addWidget(self.uiRestoreDefaultsPushButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(VMwarePreferencesPageWidget)
        self.uiTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(VMwarePreferencesPageWidget)

    def retranslateUi(self, VMwarePreferencesPageWidget):
        _translate = gns3.qt.translate
        VMwarePreferencesPageWidget.setWindowTitle(_translate("VMwarePreferencesPageWidget", "VMware"))
        self.uiVmrunPathLabel.setText(_translate("VMwarePreferencesPageWidget", "Path to vmrun:"))
        self.uiHostTypeLabel.setText(_translate("VMwarePreferencesPageWidget", "Host type:"))
        self.uiUseLocalServercheckBox.setText(_translate("VMwarePreferencesPageWidget", "Use the local server"))
        self.uiVmrunPathToolButton.setText(_translate("VMwarePreferencesPageWidget", "&Browse..."))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiGeneralSettingsTabWidget), _translate("VMwarePreferencesPageWidget", "General settings"))
        self.uiRestoreDefaultsPushButton.setText(_translate("VMwarePreferencesPageWidget", "Restore defaults"))
