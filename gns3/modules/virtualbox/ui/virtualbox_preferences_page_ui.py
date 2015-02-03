# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/virtualbox/ui/virtualbox_preferences_page.ui'
#
# Created: Sat Jan 31 19:10:58 2015
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


class Ui_VirtualBoxPreferencesPageWidget(object):

    def setupUi(self, VirtualBoxPreferencesPageWidget):
        VirtualBoxPreferencesPageWidget.setObjectName(_fromUtf8("VirtualBoxPreferencesPageWidget"))
        VirtualBoxPreferencesPageWidget.resize(432, 508)
        self.verticalLayout_2 = QtGui.QVBoxLayout(VirtualBoxPreferencesPageWidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.uiTabWidget = QtGui.QTabWidget(VirtualBoxPreferencesPageWidget)
        self.uiTabWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.uiTabWidget.setObjectName(_fromUtf8("uiTabWidget"))
        self.uiGeneralSettingsTabWidget = QtGui.QWidget()
        self.uiGeneralSettingsTabWidget.setObjectName(_fromUtf8("uiGeneralSettingsTabWidget"))
        self.gridLayout = QtGui.QGridLayout(self.uiGeneralSettingsTabWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiVboxManagePathLabel = QtGui.QLabel(self.uiGeneralSettingsTabWidget)
        self.uiVboxManagePathLabel.setObjectName(_fromUtf8("uiVboxManagePathLabel"))
        self.gridLayout.addWidget(self.uiVboxManagePathLabel, 2, 0, 1, 1)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.uiVboxManagePathLineEdit = QtGui.QLineEdit(self.uiGeneralSettingsTabWidget)
        self.uiVboxManagePathLineEdit.setObjectName(_fromUtf8("uiVboxManagePathLineEdit"))
        self.horizontalLayout_5.addWidget(self.uiVboxManagePathLineEdit)
        self.uiVboxManagePathToolButton = QtGui.QToolButton(self.uiGeneralSettingsTabWidget)
        self.uiVboxManagePathToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiVboxManagePathToolButton.setObjectName(_fromUtf8("uiVboxManagePathToolButton"))
        self.horizontalLayout_5.addWidget(self.uiVboxManagePathToolButton)
        self.gridLayout.addLayout(self.horizontalLayout_5, 3, 0, 1, 2)
        self.uiVboxManageUserLabel = QtGui.QLabel(self.uiGeneralSettingsTabWidget)
        self.uiVboxManageUserLabel.setObjectName(_fromUtf8("uiVboxManageUserLabel"))
        self.gridLayout.addWidget(self.uiVboxManageUserLabel, 5, 0, 1, 1)
        self.uiVboxManageUserLineEdit = QtGui.QLineEdit(self.uiGeneralSettingsTabWidget)
        self.uiVboxManageUserLineEdit.setObjectName(_fromUtf8("uiVboxManageUserLineEdit"))
        self.gridLayout.addWidget(self.uiVboxManageUserLineEdit, 6, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(390, 193, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 7, 0, 1, 2)
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
        spacerItem1 = QtGui.QSpacerItem(164, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.uiTestSettingsPushButton = QtGui.QPushButton(VirtualBoxPreferencesPageWidget)
        self.uiTestSettingsPushButton.setObjectName(_fromUtf8("uiTestSettingsPushButton"))
        self.horizontalLayout_2.addWidget(self.uiTestSettingsPushButton)
        self.uiRestoreDefaultsPushButton = QtGui.QPushButton(VirtualBoxPreferencesPageWidget)
        self.uiRestoreDefaultsPushButton.setObjectName(_fromUtf8("uiRestoreDefaultsPushButton"))
        self.horizontalLayout_2.addWidget(self.uiRestoreDefaultsPushButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(VirtualBoxPreferencesPageWidget)
        self.uiTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(VirtualBoxPreferencesPageWidget)

    def retranslateUi(self, VirtualBoxPreferencesPageWidget):
        VirtualBoxPreferencesPageWidget.setWindowTitle(_translate("VirtualBoxPreferencesPageWidget", "VirtualBox", None))
        self.uiVboxManagePathLabel.setText(_translate("VirtualBoxPreferencesPageWidget", "Path to VBoxManage:", None))
        self.uiVboxManagePathToolButton.setText(_translate("VirtualBoxPreferencesPageWidget", "&Browse...", None))
        self.uiVboxManageUserLabel.setText(_translate("VirtualBoxPreferencesPageWidget", "Run VirtualBox as another user (GNS3 running as root):", None))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiGeneralSettingsTabWidget), _translate("VirtualBoxPreferencesPageWidget", "General settings", None))
        self.uiUseLocalServercheckBox.setText(_translate("VirtualBoxPreferencesPageWidget", "Always use the local server", None))
        self.uiRemoteServersGroupBox.setTitle(_translate("VirtualBoxPreferencesPageWidget", "Remote servers", None))
        self.uiRemoteServersTreeWidget.headerItem().setText(0, _translate("VirtualBoxPreferencesPageWidget", "Host", None))
        self.uiRemoteServersTreeWidget.headerItem().setText(1, _translate("VirtualBoxPreferencesPageWidget", "Port", None))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiServerSettingsTabWidget), _translate("VirtualBoxPreferencesPageWidget", "Server settings", None))
        self.uiTestSettingsPushButton.setText(_translate("VirtualBoxPreferencesPageWidget", "Test settings", None))
        self.uiRestoreDefaultsPushButton.setText(_translate("VirtualBoxPreferencesPageWidget", "Restore defaults", None))
