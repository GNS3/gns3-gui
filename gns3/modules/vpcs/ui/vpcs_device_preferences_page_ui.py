# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/jbbowen/Desktop/Toptal/github/gns3-gui/gns3/modules/vpcs/ui/vpcs_device_preferences_page.ui'
#
# Created: Thu May  8 10:54:16 2014
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_VPCSDevicePreferencesPageWidget(object):
    def setupUi(self, VPCSDevicePreferencesPageWidget):
        VPCSDevicePreferencesPageWidget.setObjectName(_fromUtf8("VPCSDevicePreferencesPageWidget"))
        VPCSDevicePreferencesPageWidget.resize(404, 487)
        self.vboxlayout = QtGui.QVBoxLayout(VPCSDevicePreferencesPageWidget)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.uiTabWidget = QtGui.QTabWidget(VPCSDevicePreferencesPageWidget)
        self.uiTabWidget.setEnabled(True)
        self.uiTabWidget.setObjectName(_fromUtf8("uiTabWidget"))
        self.uiVPCSDeviceTabWidget = QtGui.QWidget()
        self.uiVPCSDeviceTabWidget.setObjectName(_fromUtf8("uiVPCSDeviceTabWidget"))
        self.gridLayout_3 = QtGui.QGridLayout(self.uiVPCSDeviceTabWidget)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.uiVPCSImageTestSettingsPushButton = QtGui.QPushButton(self.uiVPCSDeviceTabWidget)
        self.uiVPCSImageTestSettingsPushButton.setObjectName(_fromUtf8("uiVPCSImageTestSettingsPushButton"))
        self.horizontalLayout_5.addWidget(self.uiVPCSImageTestSettingsPushButton)
        self.uiSaveVPCSImagePushButton = QtGui.QPushButton(self.uiVPCSDeviceTabWidget)
        self.uiSaveVPCSImagePushButton.setObjectName(_fromUtf8("uiSaveVPCSImagePushButton"))
        self.horizontalLayout_5.addWidget(self.uiSaveVPCSImagePushButton)
        self.uiDeleteImagePushButton = QtGui.QPushButton(self.uiVPCSDeviceTabWidget)
        self.uiDeleteImagePushButton.setEnabled(False)
        self.uiDeleteImagePushButton.setObjectName(_fromUtf8("uiDeleteImagePushButton"))
        self.horizontalLayout_5.addWidget(self.uiDeleteImagePushButton)
        self.gridLayout_3.addLayout(self.horizontalLayout_5, 2, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(76, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem, 2, 1, 1, 1)
        self.groupBox = QtGui.QGroupBox(self.uiVPCSDeviceTabWidget)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.uiVPCSPathLabel = QtGui.QLabel(self.groupBox)
        self.uiVPCSPathLabel.setObjectName(_fromUtf8("uiVPCSPathLabel"))
        self.gridLayout_2.addWidget(self.uiVPCSPathLabel, 0, 0, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.uiVPCSPathLineEdit = QtGui.QLineEdit(self.groupBox)
        self.uiVPCSPathLineEdit.setObjectName(_fromUtf8("uiVPCSPathLineEdit"))
        self.horizontalLayout_3.addWidget(self.uiVPCSPathLineEdit)
        self.uiVPCSPathToolButton = QtGui.QToolButton(self.groupBox)
        self.uiVPCSPathToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiVPCSPathToolButton.setObjectName(_fromUtf8("uiVPCSPathToolButton"))
        self.horizontalLayout_3.addWidget(self.uiVPCSPathToolButton)
        self.gridLayout_2.addLayout(self.horizontalLayout_3, 0, 1, 1, 1)
        self.uiScriptFileLabel = QtGui.QLabel(self.groupBox)
        self.uiScriptFileLabel.setObjectName(_fromUtf8("uiScriptFileLabel"))
        self.gridLayout_2.addWidget(self.uiScriptFileLabel, 1, 0, 1, 1)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.uiScriptFileLineEdit = QtGui.QLineEdit(self.groupBox)
        self.uiScriptFileLineEdit.setObjectName(_fromUtf8("uiScriptFileLineEdit"))
        self.horizontalLayout_4.addWidget(self.uiScriptFileLineEdit)
        self.uiScriptFileToolButton = QtGui.QToolButton(self.groupBox)
        self.uiScriptFileToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiScriptFileToolButton.setObjectName(_fromUtf8("uiScriptFileToolButton"))
        self.horizontalLayout_4.addWidget(self.uiScriptFileToolButton)
        self.gridLayout_2.addLayout(self.horizontalLayout_4, 1, 1, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox, 1, 0, 1, 2)
        self.uiVPCSImagesTreeWidget = QtGui.QTreeWidget(self.uiVPCSDeviceTabWidget)
        self.uiVPCSImagesTreeWidget.setObjectName(_fromUtf8("uiVPCSImagesTreeWidget"))
        self.gridLayout_3.addWidget(self.uiVPCSImagesTreeWidget, 0, 0, 1, 2)
        self.uiTabWidget.addTab(self.uiVPCSDeviceTabWidget, _fromUtf8(""))
        self.uiVPCSRoutersTabWidget = QtGui.QWidget()
        self.uiVPCSRoutersTabWidget.setEnabled(False)
        self.uiVPCSRoutersTabWidget.setObjectName(_fromUtf8("uiVPCSRoutersTabWidget"))
        self.gridLayout = QtGui.QGridLayout(self.uiVPCSRoutersTabWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.treeWidget_2 = QtGui.QTreeWidget(self.uiVPCSRoutersTabWidget)
        self.treeWidget_2.setObjectName(_fromUtf8("treeWidget_2"))
        self.gridLayout.addWidget(self.treeWidget_2, 0, 0, 2, 1)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.pushButton_3 = QtGui.QPushButton(self.uiVPCSRoutersTabWidget)
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.verticalLayout.addWidget(self.pushButton_3)
        self.pushButton_4 = QtGui.QPushButton(self.uiVPCSRoutersTabWidget)
        self.pushButton_4.setObjectName(_fromUtf8("pushButton_4"))
        self.verticalLayout.addWidget(self.pushButton_4)
        self.pushButton_5 = QtGui.QPushButton(self.uiVPCSRoutersTabWidget)
        self.pushButton_5.setObjectName(_fromUtf8("pushButton_5"))
        self.verticalLayout.addWidget(self.pushButton_5)
        self.gridLayout.addLayout(self.verticalLayout, 0, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 354, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 1, 1, 1, 1)
        self.uiTabWidget.addTab(self.uiVPCSRoutersTabWidget, _fromUtf8(""))
        self.vboxlayout.addWidget(self.uiTabWidget)

        self.retranslateUi(VPCSDevicePreferencesPageWidget)
        self.uiTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(VPCSDevicePreferencesPageWidget)

    def retranslateUi(self, VPCSDevicePreferencesPageWidget):
        VPCSDevicePreferencesPageWidget.setWindowTitle(_translate("VPCSDevicePreferencesPageWidget", "VPCS devices", None))
        self.uiVPCSImageTestSettingsPushButton.setText(_translate("VPCSDevicePreferencesPageWidget", "Test settings", None))
        self.uiSaveVPCSImagePushButton.setText(_translate("VPCSDevicePreferencesPageWidget", "Save", None))
        self.uiDeleteImagePushButton.setText(_translate("VPCSDevicePreferencesPageWidget", "Delete", None))
        self.groupBox.setTitle(_translate("VPCSDevicePreferencesPageWidget", "Settings", None))
        self.uiVPCSPathLabel.setText(_translate("VPCSDevicePreferencesPageWidget", "VPCS path:", None))
        self.uiVPCSPathToolButton.setText(_translate("VPCSDevicePreferencesPageWidget", "...", None))
        self.uiScriptFileLabel.setText(_translate("VPCSDevicePreferencesPageWidget", "Script-File", None))
        self.uiScriptFileToolButton.setText(_translate("VPCSDevicePreferencesPageWidget", "...", None))
        self.uiVPCSImagesTreeWidget.headerItem().setText(0, _translate("VPCSDevicePreferencesPageWidget", "File", None))
        self.uiVPCSImagesTreeWidget.headerItem().setText(1, _translate("VPCSDevicePreferencesPageWidget", "Server", None))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiVPCSDeviceTabWidget), _translate("VPCSDevicePreferencesPageWidget", "VPCS images", None))
        self.treeWidget_2.headerItem().setText(0, _translate("VPCSDevicePreferencesPageWidget", "VPCS device", None))
        self.treeWidget_2.headerItem().setText(1, _translate("VPCSDevicePreferencesPageWidget", "VPCS file", None))
        self.pushButton_3.setText(_translate("VPCSDevicePreferencesPageWidget", "New", None))
        self.pushButton_4.setText(_translate("VPCSDevicePreferencesPageWidget", "Edit", None))
        self.pushButton_5.setText(_translate("VPCSDevicePreferencesPageWidget", "Delete", None))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiVPCSRoutersTabWidget), _translate("VPCSDevicePreferencesPageWidget", "VPCS devices", None))

