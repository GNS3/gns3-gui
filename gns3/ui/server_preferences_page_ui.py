# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/workspace/git/gns3-gui/gns3/ui/server_preferences_page.ui'
#
# Created: Sun Mar 30 16:26:41 2014
#      by: PyQt4 UI code generator 4.10
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

class Ui_ServerPreferencesPageWidget(object):
    def setupUi(self, ServerPreferencesPageWidget):
        ServerPreferencesPageWidget.setObjectName(_fromUtf8("ServerPreferencesPageWidget"))
        ServerPreferencesPageWidget.resize(433, 508)
        self.vboxlayout = QtGui.QVBoxLayout(ServerPreferencesPageWidget)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.uiTabWidget = QtGui.QTabWidget(ServerPreferencesPageWidget)
        self.uiTabWidget.setObjectName(_fromUtf8("uiTabWidget"))
        self.uiLocalTabWidget = QtGui.QWidget()
        self.uiLocalTabWidget.setObjectName(_fromUtf8("uiLocalTabWidget"))
        self.gridLayout = QtGui.QGridLayout(self.uiLocalTabWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiLocalServerPathLabel = QtGui.QLabel(self.uiLocalTabWidget)
        self.uiLocalServerPathLabel.setObjectName(_fromUtf8("uiLocalServerPathLabel"))
        self.gridLayout.addWidget(self.uiLocalServerPathLabel, 0, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.uiLocalServerPathLineEdit = QtGui.QLineEdit(self.uiLocalTabWidget)
        self.uiLocalServerPathLineEdit.setObjectName(_fromUtf8("uiLocalServerPathLineEdit"))
        self.horizontalLayout.addWidget(self.uiLocalServerPathLineEdit)
        self.uiLocalServerToolButton = QtGui.QToolButton(self.uiLocalTabWidget)
        self.uiLocalServerToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiLocalServerToolButton.setObjectName(_fromUtf8("uiLocalServerToolButton"))
        self.horizontalLayout.addWidget(self.uiLocalServerToolButton)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 2)
        self.uiLocalServerHostLabel = QtGui.QLabel(self.uiLocalTabWidget)
        self.uiLocalServerHostLabel.setObjectName(_fromUtf8("uiLocalServerHostLabel"))
        self.gridLayout.addWidget(self.uiLocalServerHostLabel, 2, 0, 1, 1)
        self.uiLocalServerHostComboBox = QtGui.QComboBox(self.uiLocalTabWidget)
        self.uiLocalServerHostComboBox.setObjectName(_fromUtf8("uiLocalServerHostComboBox"))
        self.gridLayout.addWidget(self.uiLocalServerHostComboBox, 3, 0, 1, 2)
        self.uiLocalServerPortLabel = QtGui.QLabel(self.uiLocalTabWidget)
        self.uiLocalServerPortLabel.setObjectName(_fromUtf8("uiLocalServerPortLabel"))
        self.gridLayout.addWidget(self.uiLocalServerPortLabel, 4, 0, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.uiTestSettingsPushButton = QtGui.QPushButton(self.uiLocalTabWidget)
        self.uiTestSettingsPushButton.setObjectName(_fromUtf8("uiTestSettingsPushButton"))
        self.horizontalLayout_2.addWidget(self.uiTestSettingsPushButton)
        self.uiRestoreDefaultsPushButton = QtGui.QPushButton(self.uiLocalTabWidget)
        self.uiRestoreDefaultsPushButton.setObjectName(_fromUtf8("uiRestoreDefaultsPushButton"))
        self.horizontalLayout_2.addWidget(self.uiRestoreDefaultsPushButton)
        self.gridLayout.addLayout(self.horizontalLayout_2, 6, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(164, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 6, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(390, 193, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 7, 0, 1, 2)
        self.uiLocalServerPortSpinBox = QtGui.QSpinBox(self.uiLocalTabWidget)
        self.uiLocalServerPortSpinBox.setSuffix(_fromUtf8(" TCP"))
        self.uiLocalServerPortSpinBox.setMaximum(65535)
        self.uiLocalServerPortSpinBox.setProperty("value", 8000)
        self.uiLocalServerPortSpinBox.setObjectName(_fromUtf8("uiLocalServerPortSpinBox"))
        self.gridLayout.addWidget(self.uiLocalServerPortSpinBox, 5, 0, 1, 2)
        self.uiTabWidget.addTab(self.uiLocalTabWidget, _fromUtf8(""))
        self.uiRemoteTabWidget = QtGui.QWidget()
        self.uiRemoteTabWidget.setObjectName(_fromUtf8("uiRemoteTabWidget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.uiRemoteTabWidget)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.uiRemoteServersTreeWidget = QtGui.QTreeWidget(self.uiRemoteTabWidget)
        self.uiRemoteServersTreeWidget.setObjectName(_fromUtf8("uiRemoteServersTreeWidget"))
        self.gridLayout_2.addWidget(self.uiRemoteServersTreeWidget, 0, 0, 1, 2)
        self.uiRemoteServerHostLabel = QtGui.QLabel(self.uiRemoteTabWidget)
        self.uiRemoteServerHostLabel.setObjectName(_fromUtf8("uiRemoteServerHostLabel"))
        self.gridLayout_2.addWidget(self.uiRemoteServerHostLabel, 1, 0, 1, 1)
        self.uiRemoteServerPortLineEdit = QtGui.QLineEdit(self.uiRemoteTabWidget)
        self.uiRemoteServerPortLineEdit.setObjectName(_fromUtf8("uiRemoteServerPortLineEdit"))
        self.gridLayout_2.addWidget(self.uiRemoteServerPortLineEdit, 2, 0, 1, 2)
        self.uiRemoteServerPortLabel = QtGui.QLabel(self.uiRemoteTabWidget)
        self.uiRemoteServerPortLabel.setObjectName(_fromUtf8("uiRemoteServerPortLabel"))
        self.gridLayout_2.addWidget(self.uiRemoteServerPortLabel, 3, 0, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.uiAddRemoteServerPushButton = QtGui.QPushButton(self.uiRemoteTabWidget)
        self.uiAddRemoteServerPushButton.setObjectName(_fromUtf8("uiAddRemoteServerPushButton"))
        self.horizontalLayout_3.addWidget(self.uiAddRemoteServerPushButton)
        self.uiDeleteRemoteServerPushButton = QtGui.QPushButton(self.uiRemoteTabWidget)
        self.uiDeleteRemoteServerPushButton.setEnabled(False)
        self.uiDeleteRemoteServerPushButton.setObjectName(_fromUtf8("uiDeleteRemoteServerPushButton"))
        self.horizontalLayout_3.addWidget(self.uiDeleteRemoteServerPushButton)
        self.gridLayout_2.addLayout(self.horizontalLayout_3, 5, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(206, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem2, 5, 1, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(390, 12, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem3, 6, 0, 1, 2)
        self.uiRemoteServerPortSpinBox = QtGui.QSpinBox(self.uiRemoteTabWidget)
        self.uiRemoteServerPortSpinBox.setSuffix(_fromUtf8(" TCP"))
        self.uiRemoteServerPortSpinBox.setMaximum(65535)
        self.uiRemoteServerPortSpinBox.setProperty("value", 8000)
        self.uiRemoteServerPortSpinBox.setObjectName(_fromUtf8("uiRemoteServerPortSpinBox"))
        self.gridLayout_2.addWidget(self.uiRemoteServerPortSpinBox, 4, 0, 1, 2)
        self.uiTabWidget.addTab(self.uiRemoteTabWidget, _fromUtf8(""))
        self.vboxlayout.addWidget(self.uiTabWidget)

        self.retranslateUi(ServerPreferencesPageWidget)
        self.uiTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(ServerPreferencesPageWidget)
        ServerPreferencesPageWidget.setTabOrder(self.uiLocalServerPathLineEdit, self.uiLocalServerToolButton)
        ServerPreferencesPageWidget.setTabOrder(self.uiLocalServerToolButton, self.uiLocalServerPortSpinBox)
        ServerPreferencesPageWidget.setTabOrder(self.uiLocalServerPortSpinBox, self.uiRemoteServerPortSpinBox)

    def retranslateUi(self, ServerPreferencesPageWidget):
        ServerPreferencesPageWidget.setWindowTitle(_translate("ServerPreferencesPageWidget", "Server", None))
        self.uiLocalServerPathLabel.setText(_translate("ServerPreferencesPageWidget", "Path:", None))
        self.uiLocalServerToolButton.setText(_translate("ServerPreferencesPageWidget", "...", None))
        self.uiLocalServerHostLabel.setText(_translate("ServerPreferencesPageWidget", "Host binding:", None))
        self.uiLocalServerPortLabel.setText(_translate("ServerPreferencesPageWidget", "Port:", None))
        self.uiTestSettingsPushButton.setText(_translate("ServerPreferencesPageWidget", "Test settings", None))
        self.uiRestoreDefaultsPushButton.setText(_translate("ServerPreferencesPageWidget", "Restore defaults", None))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiLocalTabWidget), _translate("ServerPreferencesPageWidget", "Local server", None))
        self.uiRemoteServersTreeWidget.headerItem().setText(0, _translate("ServerPreferencesPageWidget", "Host", None))
        self.uiRemoteServersTreeWidget.headerItem().setText(1, _translate("ServerPreferencesPageWidget", "Port", None))
        self.uiRemoteServerHostLabel.setText(_translate("ServerPreferencesPageWidget", "Host:", None))
        self.uiRemoteServerPortLineEdit.setText(_translate("ServerPreferencesPageWidget", "192.168.56.101", None))
        self.uiRemoteServerPortLabel.setText(_translate("ServerPreferencesPageWidget", "Port:", None))
        self.uiAddRemoteServerPushButton.setText(_translate("ServerPreferencesPageWidget", "Add", None))
        self.uiDeleteRemoteServerPushButton.setText(_translate("ServerPreferencesPageWidget", "Delete", None))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiRemoteTabWidget), _translate("ServerPreferencesPageWidget", "Remote servers", None))

