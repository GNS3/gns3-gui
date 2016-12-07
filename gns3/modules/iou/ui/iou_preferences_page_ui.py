# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/iou/ui/iou_preferences_page.ui'
#
# Created: Wed Dec  7 21:53:01 2016
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_IOUPreferencesPageWidget(object):
    def setupUi(self, IOUPreferencesPageWidget):
        IOUPreferencesPageWidget.setObjectName("IOUPreferencesPageWidget")
        IOUPreferencesPageWidget.resize(490, 532)
        self.vboxlayout = QtWidgets.QVBoxLayout(IOUPreferencesPageWidget)
        self.vboxlayout.setObjectName("vboxlayout")
        self.uiTabWidget = QtWidgets.QTabWidget(IOUPreferencesPageWidget)
        self.uiTabWidget.setObjectName("uiTabWidget")
        self.uiGeneralSettingsTabWidget = QtWidgets.QWidget()
        self.uiGeneralSettingsTabWidget.setObjectName("uiGeneralSettingsTabWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.uiGeneralSettingsTabWidget)
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiIouyapPathLabel = QtWidgets.QLabel(self.uiGeneralSettingsTabWidget)
        self.uiIouyapPathLabel.setObjectName("uiIouyapPathLabel")
        self.verticalLayout.addWidget(self.uiIouyapPathLabel)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.uiIouyapPathLineEdit = QtWidgets.QLineEdit(self.uiGeneralSettingsTabWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiIouyapPathLineEdit.sizePolicy().hasHeightForWidth())
        self.uiIouyapPathLineEdit.setSizePolicy(sizePolicy)
        self.uiIouyapPathLineEdit.setObjectName("uiIouyapPathLineEdit")
        self.horizontalLayout_6.addWidget(self.uiIouyapPathLineEdit)
        self.uiIouyapPathToolButton = QtWidgets.QToolButton(self.uiGeneralSettingsTabWidget)
        self.uiIouyapPathToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiIouyapPathToolButton.setObjectName("uiIouyapPathToolButton")
        self.horizontalLayout_6.addWidget(self.uiIouyapPathToolButton)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.uiLicensecheckBox = QtWidgets.QCheckBox(self.uiGeneralSettingsTabWidget)
        self.uiLicensecheckBox.setChecked(True)
        self.uiLicensecheckBox.setObjectName("uiLicensecheckBox")
        self.verticalLayout.addWidget(self.uiLicensecheckBox)
        spacerItem = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.uiTabWidget.addTab(self.uiGeneralSettingsTabWidget, "")
        self.uiLicenseTabWidget = QtWidgets.QWidget()
        self.uiLicenseTabWidget.setObjectName("uiLicenseTabWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.uiLicenseTabWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.IOULicenceTextEdit = QtWidgets.QPlainTextEdit(self.uiLicenseTabWidget)
        self.IOULicenceTextEdit.setObjectName("IOULicenceTextEdit")
        self.horizontalLayout_5.addWidget(self.IOULicenceTextEdit)
        self.uiIOURCPathToolButton = QtWidgets.QToolButton(self.uiLicenseTabWidget)
        self.uiIOURCPathToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiIOURCPathToolButton.setObjectName("uiIOURCPathToolButton")
        self.horizontalLayout_5.addWidget(self.uiIOURCPathToolButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        spacerItem1 = QtWidgets.QSpacerItem(20, 185, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.uiTabWidget.addTab(self.uiLicenseTabWidget, "")
        self.vboxlayout.addWidget(self.uiTabWidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtWidgets.QSpacerItem(164, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.uiRestoreDefaultsPushButton = QtWidgets.QPushButton(IOUPreferencesPageWidget)
        self.uiRestoreDefaultsPushButton.setObjectName("uiRestoreDefaultsPushButton")
        self.horizontalLayout_2.addWidget(self.uiRestoreDefaultsPushButton)
        self.vboxlayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(IOUPreferencesPageWidget)
        self.uiTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(IOUPreferencesPageWidget)

    def retranslateUi(self, IOUPreferencesPageWidget):
        _translate = QtCore.QCoreApplication.translate
        IOUPreferencesPageWidget.setWindowTitle(_translate("IOUPreferencesPageWidget", "IOS on UNIX"))
        self.uiIouyapPathLabel.setText(_translate("IOUPreferencesPageWidget", "Path to iouyap:"))
        self.uiIouyapPathToolButton.setText(_translate("IOUPreferencesPageWidget", "&Browse..."))
        self.uiLicensecheckBox.setText(_translate("IOUPreferencesPageWidget", "Check for a valid IOU license key"))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiGeneralSettingsTabWidget), _translate("IOUPreferencesPageWidget", "Local settings"))
        self.IOULicenceTextEdit.setToolTip(_translate("IOUPreferencesPageWidget", "A license is required to run IOU. Copy & paste the content of your iourc file here or use the browse button to select a file. The license will be pushed to remote servers."))
        self.uiIOURCPathToolButton.setText(_translate("IOUPreferencesPageWidget", "&Browse..."))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiLicenseTabWidget), _translate("IOUPreferencesPageWidget", "License"))
        self.uiRestoreDefaultsPushButton.setText(_translate("IOUPreferencesPageWidget", "Restore defaults"))

