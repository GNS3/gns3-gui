# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/vpcs/ui/vpcs_preferences_page.ui'
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

class Ui_VPCSPreferencesPageWidget(object):
    def setupUi(self, VPCSPreferencesPageWidget):
        VPCSPreferencesPageWidget.setObjectName(_fromUtf8("VPCSPreferencesPageWidget"))
        VPCSPreferencesPageWidget.resize(430, 469)
        self.verticalLayout_2 = QtGui.QVBoxLayout(VPCSPreferencesPageWidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.uiTabWidget = QtGui.QTabWidget(VPCSPreferencesPageWidget)
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
        self.uiVPCSPathLabel = QtGui.QLabel(self.uiGeneralSettingsTabWidget)
        self.uiVPCSPathLabel.setObjectName(_fromUtf8("uiVPCSPathLabel"))
        self.verticalLayout.addWidget(self.uiVPCSPathLabel)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.uiVPCSPathLineEdit = QtGui.QLineEdit(self.uiGeneralSettingsTabWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVPCSPathLineEdit.sizePolicy().hasHeightForWidth())
        self.uiVPCSPathLineEdit.setSizePolicy(sizePolicy)
        self.uiVPCSPathLineEdit.setObjectName(_fromUtf8("uiVPCSPathLineEdit"))
        self.horizontalLayout_5.addWidget(self.uiVPCSPathLineEdit)
        self.uiVPCSPathToolButton = QtGui.QToolButton(self.uiGeneralSettingsTabWidget)
        self.uiVPCSPathToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiVPCSPathToolButton.setObjectName(_fromUtf8("uiVPCSPathToolButton"))
        self.horizontalLayout_5.addWidget(self.uiVPCSPathToolButton)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        spacerItem = QtGui.QSpacerItem(390, 193, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.uiTabWidget.addTab(self.uiGeneralSettingsTabWidget, _fromUtf8(""))
        self.uiVPCSTabWidget = QtGui.QWidget()
        self.uiVPCSTabWidget.setObjectName(_fromUtf8("uiVPCSTabWidget"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.uiVPCSTabWidget)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.uiScriptFileLabel = QtGui.QLabel(self.uiVPCSTabWidget)
        self.uiScriptFileLabel.setObjectName(_fromUtf8("uiScriptFileLabel"))
        self.verticalLayout_3.addWidget(self.uiScriptFileLabel)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.uiScriptFileEdit = QtGui.QLineEdit(self.uiVPCSTabWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiScriptFileEdit.sizePolicy().hasHeightForWidth())
        self.uiScriptFileEdit.setSizePolicy(sizePolicy)
        self.uiScriptFileEdit.setObjectName(_fromUtf8("uiScriptFileEdit"))
        self.horizontalLayout_6.addWidget(self.uiScriptFileEdit)
        self.uiScriptFileToolButton = QtGui.QToolButton(self.uiVPCSTabWidget)
        self.uiScriptFileToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiScriptFileToolButton.setObjectName(_fromUtf8("uiScriptFileToolButton"))
        self.horizontalLayout_6.addWidget(self.uiScriptFileToolButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout_6)
        spacerItem1 = QtGui.QSpacerItem(20, 387, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.uiTabWidget.addTab(self.uiVPCSTabWidget, _fromUtf8(""))
        self.verticalLayout_2.addWidget(self.uiTabWidget)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem2 = QtGui.QSpacerItem(138, 17, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.uiRestoreDefaultsPushButton = QtGui.QPushButton(VPCSPreferencesPageWidget)
        self.uiRestoreDefaultsPushButton.setObjectName(_fromUtf8("uiRestoreDefaultsPushButton"))
        self.horizontalLayout_2.addWidget(self.uiRestoreDefaultsPushButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(VPCSPreferencesPageWidget)
        self.uiTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(VPCSPreferencesPageWidget)

    def retranslateUi(self, VPCSPreferencesPageWidget):
        VPCSPreferencesPageWidget.setWindowTitle(_translate("VPCSPreferencesPageWidget", "VPCS", None))
        self.uiUseLocalServercheckBox.setText(_translate("VPCSPreferencesPageWidget", "Use the local server", None))
        self.uiVPCSPathLabel.setText(_translate("VPCSPreferencesPageWidget", "Path to VPCS:", None))
        self.uiVPCSPathToolButton.setText(_translate("VPCSPreferencesPageWidget", "&Browse...", None))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiGeneralSettingsTabWidget), _translate("VPCSPreferencesPageWidget", "General settings", None))
        self.uiScriptFileLabel.setText(_translate("VPCSPreferencesPageWidget", "Path to VPCS base script file:", None))
        self.uiScriptFileToolButton.setText(_translate("VPCSPreferencesPageWidget", "&Browse...", None))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiVPCSTabWidget), _translate("VPCSPreferencesPageWidget", "VPCS VM settings", None))
        self.uiRestoreDefaultsPushButton.setText(_translate("VPCSPreferencesPageWidget", "Restore defaults", None))

