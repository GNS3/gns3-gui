# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/qemu/ui/qemu_preferences_page.ui'
#
# Created: Wed Dec  7 21:25:31 2016
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_QemuPreferencesPageWidget(object):
    def setupUi(self, QemuPreferencesPageWidget):
        QemuPreferencesPageWidget.setObjectName("QemuPreferencesPageWidget")
        QemuPreferencesPageWidget.resize(366, 183)
        self.verticalLayout = QtWidgets.QVBoxLayout(QemuPreferencesPageWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiTabWidget = QtWidgets.QTabWidget(QemuPreferencesPageWidget)
        self.uiTabWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.uiTabWidget.setObjectName("uiTabWidget")
        self.uiServerSettingsTabWidget = QtWidgets.QWidget()
        self.uiServerSettingsTabWidget.setObjectName("uiServerSettingsTabWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.uiServerSettingsTabWidget)
        self.verticalLayout_2.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.uiKVMAccelerationCheckBox = QtWidgets.QCheckBox(self.uiServerSettingsTabWidget)
        self.uiKVMAccelerationCheckBox.setObjectName("uiKVMAccelerationCheckBox")
        self.verticalLayout_2.addWidget(self.uiKVMAccelerationCheckBox)
        spacerItem = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
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
        _translate = QtCore.QCoreApplication.translate
        QemuPreferencesPageWidget.setWindowTitle(_translate("QemuPreferencesPageWidget", "QEMU"))
        self.uiKVMAccelerationCheckBox.setText(_translate("QemuPreferencesPageWidget", "Enable KVM acceleration"))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiServerSettingsTabWidget), _translate("QemuPreferencesPageWidget", "Local settings"))
        self.uiRestoreDefaultsPushButton.setText(_translate("QemuPreferencesPageWidget", "Restore defaults"))

