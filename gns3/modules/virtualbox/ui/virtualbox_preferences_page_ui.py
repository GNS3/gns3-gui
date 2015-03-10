# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/virtualbox/ui/virtualbox_preferences_page.ui'
#
# Created: Mon Mar  9 18:00:29 2015
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
        VirtualBoxPreferencesPageWidget.resize(430, 490)
        self.verticalLayout_2 = QtGui.QVBoxLayout(VirtualBoxPreferencesPageWidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.uiTabWidget = QtGui.QTabWidget(VirtualBoxPreferencesPageWidget)
        self.uiTabWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.uiTabWidget.setObjectName(_fromUtf8("uiTabWidget"))
        self.uiGeneralSettingsTabWidget = QtGui.QWidget()
        self.uiGeneralSettingsTabWidget.setObjectName(_fromUtf8("uiGeneralSettingsTabWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.uiGeneralSettingsTabWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.uiUseLocalServercheckBox = QtGui.QCheckBox(self.uiGeneralSettingsTabWidget)
        self.uiUseLocalServercheckBox.setChecked(True)
        self.uiUseLocalServercheckBox.setObjectName(_fromUtf8("uiUseLocalServercheckBox"))
        self.verticalLayout.addWidget(self.uiUseLocalServercheckBox)
        self.uiVboxManagePathLabel = QtGui.QLabel(self.uiGeneralSettingsTabWidget)
        self.uiVboxManagePathLabel.setObjectName(_fromUtf8("uiVboxManagePathLabel"))
        self.verticalLayout.addWidget(self.uiVboxManagePathLabel)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.uiVboxManagePathLineEdit = QtGui.QLineEdit(self.uiGeneralSettingsTabWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVboxManagePathLineEdit.sizePolicy().hasHeightForWidth())
        self.uiVboxManagePathLineEdit.setSizePolicy(sizePolicy)
        self.uiVboxManagePathLineEdit.setObjectName(_fromUtf8("uiVboxManagePathLineEdit"))
        self.horizontalLayout_5.addWidget(self.uiVboxManagePathLineEdit)
        self.uiVboxManagePathToolButton = QtGui.QToolButton(self.uiGeneralSettingsTabWidget)
        self.uiVboxManagePathToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiVboxManagePathToolButton.setObjectName(_fromUtf8("uiVboxManagePathToolButton"))
        self.horizontalLayout_5.addWidget(self.uiVboxManagePathToolButton)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.uiVboxManageUserLabel = QtGui.QLabel(self.uiGeneralSettingsTabWidget)
        self.uiVboxManageUserLabel.setObjectName(_fromUtf8("uiVboxManageUserLabel"))
        self.verticalLayout.addWidget(self.uiVboxManageUserLabel)
        self.uiVboxManageUserLineEdit = QtGui.QLineEdit(self.uiGeneralSettingsTabWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVboxManageUserLineEdit.sizePolicy().hasHeightForWidth())
        self.uiVboxManageUserLineEdit.setSizePolicy(sizePolicy)
        self.uiVboxManageUserLineEdit.setObjectName(_fromUtf8("uiVboxManageUserLineEdit"))
        self.verticalLayout.addWidget(self.uiVboxManageUserLineEdit)
        spacerItem = QtGui.QSpacerItem(390, 193, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.uiTabWidget.addTab(self.uiGeneralSettingsTabWidget, _fromUtf8(""))
        self.verticalLayout_2.addWidget(self.uiTabWidget)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem1 = QtGui.QSpacerItem(164, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.uiRestoreDefaultsPushButton = QtGui.QPushButton(VirtualBoxPreferencesPageWidget)
        self.uiRestoreDefaultsPushButton.setObjectName(_fromUtf8("uiRestoreDefaultsPushButton"))
        self.horizontalLayout_2.addWidget(self.uiRestoreDefaultsPushButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(VirtualBoxPreferencesPageWidget)
        self.uiTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(VirtualBoxPreferencesPageWidget)

    def retranslateUi(self, VirtualBoxPreferencesPageWidget):
        VirtualBoxPreferencesPageWidget.setWindowTitle(_translate("VirtualBoxPreferencesPageWidget", "VirtualBox", None))
        self.uiUseLocalServercheckBox.setText(_translate("VirtualBoxPreferencesPageWidget", "Use the local server", None))
        self.uiVboxManagePathLabel.setText(_translate("VirtualBoxPreferencesPageWidget", "Path to VBoxManage:", None))
        self.uiVboxManagePathToolButton.setText(_translate("VirtualBoxPreferencesPageWidget", "&Browse...", None))
        self.uiVboxManageUserLabel.setText(_translate("VirtualBoxPreferencesPageWidget", "Run VirtualBox as another user (GNS3 running as root):", None))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiGeneralSettingsTabWidget), _translate("VirtualBoxPreferencesPageWidget", "General settings", None))
        self.uiRestoreDefaultsPushButton.setText(_translate("VirtualBoxPreferencesPageWidget", "Restore defaults", None))

