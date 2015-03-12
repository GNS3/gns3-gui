# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/iou/ui/iou_preferences_page.ui'
#
# Created: Wed Mar 11 18:55:05 2015
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

class Ui_IOUPreferencesPageWidget(object):
    def setupUi(self, IOUPreferencesPageWidget):
        IOUPreferencesPageWidget.setObjectName(_fromUtf8("IOUPreferencesPageWidget"))
        IOUPreferencesPageWidget.resize(430, 490)
        self.vboxlayout = QtGui.QVBoxLayout(IOUPreferencesPageWidget)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.uiTabWidget = QtGui.QTabWidget(IOUPreferencesPageWidget)
        self.uiTabWidget.setObjectName(_fromUtf8("uiTabWidget"))
        self.uiGeneralSettingsTabWidget = QtGui.QWidget()
        self.uiGeneralSettingsTabWidget.setObjectName(_fromUtf8("uiGeneralSettingsTabWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.uiGeneralSettingsTabWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.uiUseLocalServercheckBox = QtGui.QCheckBox(self.uiGeneralSettingsTabWidget)
        self.uiUseLocalServercheckBox.setChecked(True)
        self.uiUseLocalServercheckBox.setObjectName(_fromUtf8("uiUseLocalServercheckBox"))
        self.verticalLayout.addWidget(self.uiUseLocalServercheckBox)
        self.uiIOURCPathLabel = QtGui.QLabel(self.uiGeneralSettingsTabWidget)
        self.uiIOURCPathLabel.setObjectName(_fromUtf8("uiIOURCPathLabel"))
        self.verticalLayout.addWidget(self.uiIOURCPathLabel)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.uiIOURCPathLineEdit = QtGui.QLineEdit(self.uiGeneralSettingsTabWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiIOURCPathLineEdit.sizePolicy().hasHeightForWidth())
        self.uiIOURCPathLineEdit.setSizePolicy(sizePolicy)
        self.uiIOURCPathLineEdit.setObjectName(_fromUtf8("uiIOURCPathLineEdit"))
        self.horizontalLayout_5.addWidget(self.uiIOURCPathLineEdit)
        self.uiIOURCPathToolButton = QtGui.QToolButton(self.uiGeneralSettingsTabWidget)
        self.uiIOURCPathToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiIOURCPathToolButton.setObjectName(_fromUtf8("uiIOURCPathToolButton"))
        self.horizontalLayout_5.addWidget(self.uiIOURCPathToolButton)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.uiIouyapPathLabel = QtGui.QLabel(self.uiGeneralSettingsTabWidget)
        self.uiIouyapPathLabel.setObjectName(_fromUtf8("uiIouyapPathLabel"))
        self.verticalLayout.addWidget(self.uiIouyapPathLabel)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.uiIouyapPathLineEdit = QtGui.QLineEdit(self.uiGeneralSettingsTabWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiIouyapPathLineEdit.sizePolicy().hasHeightForWidth())
        self.uiIouyapPathLineEdit.setSizePolicy(sizePolicy)
        self.uiIouyapPathLineEdit.setObjectName(_fromUtf8("uiIouyapPathLineEdit"))
        self.horizontalLayout_6.addWidget(self.uiIouyapPathLineEdit)
        self.uiIouyapPathToolButton = QtGui.QToolButton(self.uiGeneralSettingsTabWidget)
        self.uiIouyapPathToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiIouyapPathToolButton.setObjectName(_fromUtf8("uiIouyapPathToolButton"))
        self.horizontalLayout_6.addWidget(self.uiIouyapPathToolButton)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.uiLicensecheckBox = QtGui.QCheckBox(self.uiGeneralSettingsTabWidget)
        self.uiLicensecheckBox.setChecked(True)
        self.uiLicensecheckBox.setObjectName(_fromUtf8("uiLicensecheckBox"))
        self.verticalLayout.addWidget(self.uiLicensecheckBox)
        spacerItem = QtGui.QSpacerItem(390, 193, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.uiTabWidget.addTab(self.uiGeneralSettingsTabWidget, _fromUtf8(""))
        self.vboxlayout.addWidget(self.uiTabWidget)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem1 = QtGui.QSpacerItem(164, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.uiRestoreDefaultsPushButton = QtGui.QPushButton(IOUPreferencesPageWidget)
        self.uiRestoreDefaultsPushButton.setObjectName(_fromUtf8("uiRestoreDefaultsPushButton"))
        self.horizontalLayout_2.addWidget(self.uiRestoreDefaultsPushButton)
        self.vboxlayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(IOUPreferencesPageWidget)
        self.uiTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(IOUPreferencesPageWidget)

    def retranslateUi(self, IOUPreferencesPageWidget):
        IOUPreferencesPageWidget.setWindowTitle(_translate("IOUPreferencesPageWidget", "IOS on UNIX", None))
        self.uiUseLocalServercheckBox.setText(_translate("IOUPreferencesPageWidget", "Use the local server (Linux only)", None))
        self.uiIOURCPathLabel.setText(_translate("IOUPreferencesPageWidget", "Path to IOURC:", None))
        self.uiIOURCPathToolButton.setText(_translate("IOUPreferencesPageWidget", "&Browse...", None))
        self.uiIouyapPathLabel.setText(_translate("IOUPreferencesPageWidget", "Path to iouyap:", None))
        self.uiIouyapPathToolButton.setText(_translate("IOUPreferencesPageWidget", "&Browse...", None))
        self.uiLicensecheckBox.setText(_translate("IOUPreferencesPageWidget", "Check for a valid IOU license key", None))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiGeneralSettingsTabWidget), _translate("IOUPreferencesPageWidget", "General settings", None))
        self.uiRestoreDefaultsPushButton.setText(_translate("IOUPreferencesPageWidget", "Restore defaults", None))

