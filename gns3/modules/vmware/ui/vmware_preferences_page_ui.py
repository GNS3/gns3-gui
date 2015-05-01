# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/vmware/ui/vmware_preferences_page.ui'
#
# Created: Thu Apr 30 17:53:01 2015
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

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
        self.verticalLayout = QtWidgets.QVBoxLayout(self.uiGeneralSettingsTabWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiUseLocalServercheckBox = QtWidgets.QCheckBox(self.uiGeneralSettingsTabWidget)
        self.uiUseLocalServercheckBox.setChecked(True)
        self.uiUseLocalServercheckBox.setObjectName("uiUseLocalServercheckBox")
        self.verticalLayout.addWidget(self.uiUseLocalServercheckBox)
        self.uiVmrunPathLabel = QtWidgets.QLabel(self.uiGeneralSettingsTabWidget)
        self.uiVmrunPathLabel.setObjectName("uiVmrunPathLabel")
        self.verticalLayout.addWidget(self.uiVmrunPathLabel)
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
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        spacerItem = QtWidgets.QSpacerItem(390, 193, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
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
        _translate = QtCore.QCoreApplication.translate
        VMwarePreferencesPageWidget.setWindowTitle(_translate("VMwarePreferencesPageWidget", "VMware"))
        self.uiUseLocalServercheckBox.setText(_translate("VMwarePreferencesPageWidget", "Use the local server"))
        self.uiVmrunPathLabel.setText(_translate("VMwarePreferencesPageWidget", "Path to vmrun:"))
        self.uiVmrunPathToolButton.setText(_translate("VMwarePreferencesPageWidget", "&Browse..."))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiGeneralSettingsTabWidget), _translate("VMwarePreferencesPageWidget", "General settings"))
        self.uiRestoreDefaultsPushButton.setText(_translate("VMwarePreferencesPageWidget", "Restore defaults"))

