# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/vpcs/ui/vpcs_preferences_page.ui'
#
# Created: Sat Jan 31 19:00:41 2015
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


class Ui_VPCSPreferencesPageWidget(object):

    def setupUi(self, VPCSPreferencesPageWidget):
        VPCSPreferencesPageWidget.setObjectName(_fromUtf8("VPCSPreferencesPageWidget"))
        VPCSPreferencesPageWidget.resize(430, 545)
        self.verticalLayout_2 = QtGui.QVBoxLayout(VPCSPreferencesPageWidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.uiTabWidget = QtGui.QTabWidget(VPCSPreferencesPageWidget)
        self.uiTabWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.uiTabWidget.setObjectName(_fromUtf8("uiTabWidget"))
        self.uiGeneralSettingsTabWidget = QtGui.QWidget()
        self.uiGeneralSettingsTabWidget.setObjectName(_fromUtf8("uiGeneralSettingsTabWidget"))
        self.gridLayout = QtGui.QGridLayout(self.uiGeneralSettingsTabWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(390, 193, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 7, 0, 1, 2)
        self.uiScriptFileLabel = QtGui.QLabel(self.uiGeneralSettingsTabWidget)
        self.uiScriptFileLabel.setObjectName(_fromUtf8("uiScriptFileLabel"))
        self.gridLayout.addWidget(self.uiScriptFileLabel, 4, 0, 1, 1)
        self.uiVPCSPathLabel = QtGui.QLabel(self.uiGeneralSettingsTabWidget)
        self.uiVPCSPathLabel.setObjectName(_fromUtf8("uiVPCSPathLabel"))
        self.gridLayout.addWidget(self.uiVPCSPathLabel, 2, 0, 1, 1)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.uiVPCSPathLineEdit = QtGui.QLineEdit(self.uiGeneralSettingsTabWidget)
        self.uiVPCSPathLineEdit.setObjectName(_fromUtf8("uiVPCSPathLineEdit"))
        self.horizontalLayout_5.addWidget(self.uiVPCSPathLineEdit)
        self.uiVPCSPathToolButton = QtGui.QToolButton(self.uiGeneralSettingsTabWidget)
        self.uiVPCSPathToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiVPCSPathToolButton.setObjectName(_fromUtf8("uiVPCSPathToolButton"))
        self.horizontalLayout_5.addWidget(self.uiVPCSPathToolButton)
        self.gridLayout.addLayout(self.horizontalLayout_5, 3, 0, 1, 2)
        self.horizontalLayout_51 = QtGui.QHBoxLayout()
        self.horizontalLayout_51.setObjectName(_fromUtf8("horizontalLayout_51"))
        self.uiScriptFileEdit = QtGui.QLineEdit(self.uiGeneralSettingsTabWidget)
        self.uiScriptFileEdit.setObjectName(_fromUtf8("uiScriptFileEdit"))
        self.horizontalLayout_51.addWidget(self.uiScriptFileEdit)
        self.uiScriptFileToolButton = QtGui.QToolButton(self.uiGeneralSettingsTabWidget)
        self.uiScriptFileToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiScriptFileToolButton.setObjectName(_fromUtf8("uiScriptFileToolButton"))
        self.horizontalLayout_51.addWidget(self.uiScriptFileToolButton)
        self.gridLayout.addLayout(self.horizontalLayout_51, 5, 0, 1, 2)
        self.uiTabWidget.addTab(self.uiGeneralSettingsTabWidget, _fromUtf8(""))
        self.uiServerSettingsTabWidget = QtGui.QWidget()
        self.uiServerSettingsTabWidget.setObjectName(_fromUtf8("uiServerSettingsTabWidget"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.uiServerSettingsTabWidget)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.uiUseLocalServercheckBox = QtGui.QCheckBox(self.uiServerSettingsTabWidget)
        self.uiUseLocalServercheckBox.setChecked(True)
        self.uiUseLocalServercheckBox.setObjectName(_fromUtf8("uiUseLocalServercheckBox"))
        self.verticalLayout_3.addWidget(self.uiUseLocalServercheckBox)
        self.uiRemoteServersGroupBox = QtGui.QGroupBox(self.uiServerSettingsTabWidget)
        self.uiRemoteServersGroupBox.setObjectName(_fromUtf8("uiRemoteServersGroupBox"))
        self.horizontalLayout_11 = QtGui.QHBoxLayout(self.uiRemoteServersGroupBox)
        self.horizontalLayout_11.setObjectName(_fromUtf8("horizontalLayout_11"))
        self.uiRemoteServersTreeWidget = QtGui.QTreeWidget(self.uiRemoteServersGroupBox)
        self.uiRemoteServersTreeWidget.setEnabled(False)
        self.uiRemoteServersTreeWidget.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.uiRemoteServersTreeWidget.setObjectName(_fromUtf8("uiRemoteServersTreeWidget"))
        self.horizontalLayout_11.addWidget(self.uiRemoteServersTreeWidget)
        self.verticalLayout_3.addWidget(self.uiRemoteServersGroupBox)
        self.uiTabWidget.addTab(self.uiServerSettingsTabWidget, _fromUtf8(""))
        self.verticalLayout_2.addWidget(self.uiTabWidget)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem1 = QtGui.QSpacerItem(138, 17, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.uiTestSettingsPushButton = QtGui.QPushButton(VPCSPreferencesPageWidget)
        self.uiTestSettingsPushButton.setObjectName(_fromUtf8("uiTestSettingsPushButton"))
        self.horizontalLayout_2.addWidget(self.uiTestSettingsPushButton)
        self.uiRestoreDefaultsPushButton = QtGui.QPushButton(VPCSPreferencesPageWidget)
        self.uiRestoreDefaultsPushButton.setObjectName(_fromUtf8("uiRestoreDefaultsPushButton"))
        self.horizontalLayout_2.addWidget(self.uiRestoreDefaultsPushButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(VPCSPreferencesPageWidget)
        self.uiTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(VPCSPreferencesPageWidget)

    def retranslateUi(self, VPCSPreferencesPageWidget):
        VPCSPreferencesPageWidget.setWindowTitle(_translate("VPCSPreferencesPageWidget", "VPCS", None))
        self.uiScriptFileLabel.setText(_translate("VPCSPreferencesPageWidget", "Path to VPCS base script file:", None))
        self.uiVPCSPathLabel.setText(_translate("VPCSPreferencesPageWidget", "Path to VPCS:", None))
        self.uiVPCSPathToolButton.setText(_translate("VPCSPreferencesPageWidget", "&Browse...", None))
        self.uiScriptFileToolButton.setText(_translate("VPCSPreferencesPageWidget", "&Browse...", None))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiGeneralSettingsTabWidget), _translate("VPCSPreferencesPageWidget", "General settings", None))
        self.uiUseLocalServercheckBox.setText(_translate("VPCSPreferencesPageWidget", "Always use the local server", None))
        self.uiRemoteServersGroupBox.setTitle(_translate("VPCSPreferencesPageWidget", "Remote servers", None))
        self.uiRemoteServersTreeWidget.headerItem().setText(0, _translate("VPCSPreferencesPageWidget", "Host", None))
        self.uiRemoteServersTreeWidget.headerItem().setText(1, _translate("VPCSPreferencesPageWidget", "Port", None))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiServerSettingsTabWidget), _translate("VPCSPreferencesPageWidget", "Server settings", None))
        self.uiTestSettingsPushButton.setText(_translate("VPCSPreferencesPageWidget", "Test settings", None))
        self.uiRestoreDefaultsPushButton.setText(_translate("VPCSPreferencesPageWidget", "Restore defaults", None))
