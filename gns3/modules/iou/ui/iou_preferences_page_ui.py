# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/iou/ui/iou_preferences_page.ui'
#
# Created: Tue Mar 17 18:49:46 2015
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
        IOUPreferencesPageWidget.resize(425, 467)
        self.vboxlayout = QtGui.QVBoxLayout(IOUPreferencesPageWidget)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.uiTabWidget = QtGui.QTabWidget(IOUPreferencesPageWidget)
        self.uiTabWidget.setObjectName(_fromUtf8("uiTabWidget"))
        self.uiGeneralSettingsTabWidget = QtGui.QWidget()
        self.uiGeneralSettingsTabWidget.setObjectName(_fromUtf8("uiGeneralSettingsTabWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.uiGeneralSettingsTabWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.uiLocalServerGroupBox = QtGui.QGroupBox(self.uiGeneralSettingsTabWidget)
        self.uiLocalServerGroupBox.setObjectName(_fromUtf8("uiLocalServerGroupBox"))
        self.gridLayout_3 = QtGui.QGridLayout(self.uiLocalServerGroupBox)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.uiIouyapPathLineEdit = QtGui.QLineEdit(self.uiLocalServerGroupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiIouyapPathLineEdit.sizePolicy().hasHeightForWidth())
        self.uiIouyapPathLineEdit.setSizePolicy(sizePolicy)
        self.uiIouyapPathLineEdit.setObjectName(_fromUtf8("uiIouyapPathLineEdit"))
        self.horizontalLayout_6.addWidget(self.uiIouyapPathLineEdit)
        self.uiIouyapPathToolButton = QtGui.QToolButton(self.uiLocalServerGroupBox)
        self.uiIouyapPathToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiIouyapPathToolButton.setObjectName(_fromUtf8("uiIouyapPathToolButton"))
        self.horizontalLayout_6.addWidget(self.uiIouyapPathToolButton)
        self.gridLayout_3.addLayout(self.horizontalLayout_6, 5, 0, 1, 2)
        self.uiIouyapPathLabel = QtGui.QLabel(self.uiLocalServerGroupBox)
        self.uiIouyapPathLabel.setObjectName(_fromUtf8("uiIouyapPathLabel"))
        self.gridLayout_3.addWidget(self.uiIouyapPathLabel, 4, 0, 1, 1)
        self.uiLicensecheckBox = QtGui.QCheckBox(self.uiLocalServerGroupBox)
        self.uiLicensecheckBox.setChecked(True)
        self.uiLicensecheckBox.setObjectName(_fromUtf8("uiLicensecheckBox"))
        self.gridLayout_3.addWidget(self.uiLicensecheckBox, 3, 0, 1, 1)
        self.uiUseLocalServercheckBox = QtGui.QCheckBox(self.uiLocalServerGroupBox)
        self.uiUseLocalServercheckBox.setChecked(True)
        self.uiUseLocalServercheckBox.setObjectName(_fromUtf8("uiUseLocalServercheckBox"))
        self.gridLayout_3.addWidget(self.uiUseLocalServercheckBox, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.uiLocalServerGroupBox)
        self.uiAnyServerGroupBox = QtGui.QGroupBox(self.uiGeneralSettingsTabWidget)
        self.uiAnyServerGroupBox.setObjectName(_fromUtf8("uiAnyServerGroupBox"))
        self.gridLayout_4 = QtGui.QGridLayout(self.uiAnyServerGroupBox)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.uiIOURCPathLabel = QtGui.QLabel(self.uiAnyServerGroupBox)
        self.uiIOURCPathLabel.setObjectName(_fromUtf8("uiIOURCPathLabel"))
        self.gridLayout_4.addWidget(self.uiIOURCPathLabel, 0, 0, 1, 1)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.uiIOURCPathLineEdit = QtGui.QLineEdit(self.uiAnyServerGroupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiIOURCPathLineEdit.sizePolicy().hasHeightForWidth())
        self.uiIOURCPathLineEdit.setSizePolicy(sizePolicy)
        self.uiIOURCPathLineEdit.setObjectName(_fromUtf8("uiIOURCPathLineEdit"))
        self.horizontalLayout_5.addWidget(self.uiIOURCPathLineEdit)
        self.uiIOURCPathToolButton = QtGui.QToolButton(self.uiAnyServerGroupBox)
        self.uiIOURCPathToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiIOURCPathToolButton.setObjectName(_fromUtf8("uiIOURCPathToolButton"))
        self.horizontalLayout_5.addWidget(self.uiIOURCPathToolButton)
        self.gridLayout_4.addLayout(self.horizontalLayout_5, 1, 0, 1, 1)
        self.verticalLayout.addWidget(self.uiAnyServerGroupBox)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
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
        self.uiLocalServerGroupBox.setTitle(_translate("IOUPreferencesPageWidget", "Local server", None))
        self.uiIouyapPathToolButton.setText(_translate("IOUPreferencesPageWidget", "&Browse...", None))
        self.uiIouyapPathLabel.setText(_translate("IOUPreferencesPageWidget", "Path to iouyap:", None))
        self.uiLicensecheckBox.setText(_translate("IOUPreferencesPageWidget", "Check for a valid IOU license key", None))
        self.uiUseLocalServercheckBox.setText(_translate("IOUPreferencesPageWidget", "Use the local server (Linux only)", None))
        self.uiAnyServerGroupBox.setTitle(_translate("IOUPreferencesPageWidget", "Any server", None))
        self.uiIOURCPathLabel.setText(_translate("IOUPreferencesPageWidget", "Path to IOURC (license, pushed to servers):", None))
        self.uiIOURCPathToolButton.setText(_translate("IOUPreferencesPageWidget", "&Browse...", None))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiGeneralSettingsTabWidget), _translate("IOUPreferencesPageWidget", "General settings", None))
        self.uiRestoreDefaultsPushButton.setText(_translate("IOUPreferencesPageWidget", "Restore defaults", None))

