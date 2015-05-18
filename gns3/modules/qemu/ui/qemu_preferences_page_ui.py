# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qemu_preferences_page.ui'
#
# Created: Wed May  6 14:31:57 2015
#      by: PyQt5 UI code generator 5.4
#
# WARNING! All changes made in this file will be lost!

import gns3.qt
from gns3.qt import QtCore, QtGui, QtWidgets


class Ui_QemuPreferencesPageWidget:

    def setupUi(self, QemuPreferencesPageWidget):
        QemuPreferencesPageWidget.setObjectName("QemuPreferencesPageWidget")
        QemuPreferencesPageWidget.resize(200, 200)
        self.verticalLayout = QtWidgets.QVBoxLayout(QemuPreferencesPageWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiTabWidget = QtWidgets.QTabWidget(QemuPreferencesPageWidget)
        self.uiTabWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.uiTabWidget.setObjectName("uiTabWidget")
        self.uiServerSettingsTabWidget = QtWidgets.QWidget()
        self.uiServerSettingsTabWidget.setObjectName("uiServerSettingsTabWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.uiServerSettingsTabWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.uiUseLocalServercheckBox = QtWidgets.QCheckBox(self.uiServerSettingsTabWidget)
        self.uiUseLocalServercheckBox.setChecked(True)
        self.uiUseLocalServercheckBox.setObjectName("uiUseLocalServercheckBox")
        self.verticalLayout_2.addWidget(self.uiUseLocalServercheckBox)
        spacerItem = QtWidgets.QSpacerItem(20, 455, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.uiTabWidget.addTab(self.uiServerSettingsTabWidget, "")
        self.verticalLayout.addWidget(self.uiTabWidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(254, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.uiRestoreDefaultsPushButton = QtWidgets.QPushButton(QemuPreferencesPageWidget)
        self.uiRestoreDefaultsPushButton.setObjectName("uiRestoreDefaultsPushButton")
        self.horizontalLayout_2.addWidget(self.uiRestoreDefaultsPushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(QemuPreferencesPageWidget)
        self.uiTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(QemuPreferencesPageWidget)

    def retranslateUi(self, QemuPreferencesPageWidget):
        _translate = gns3.qt.translate
        QemuPreferencesPageWidget.setWindowTitle(_translate("QemuPreferencesPageWidget", "QEMU"))
        self.uiUseLocalServercheckBox.setText(_translate("QemuPreferencesPageWidget", "Use the local server"))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiServerSettingsTabWidget), _translate("QemuPreferencesPageWidget", "General settings"))
        self.uiRestoreDefaultsPushButton.setText(_translate("QemuPreferencesPageWidget", "Restore defaults"))
