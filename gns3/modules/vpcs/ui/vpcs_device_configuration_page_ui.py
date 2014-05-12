# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/jbbowen/Desktop/Toptal/github/gns3-gui/gns3/modules/vpcs/ui/vpcs_device_configuration_page.ui'
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

class Ui_vpcsDeviceConfigPageWidget(object):
    def setupUi(self, vpcsDeviceConfigPageWidget):
        vpcsDeviceConfigPageWidget.setObjectName(_fromUtf8("vpcsDeviceConfigPageWidget"))
        vpcsDeviceConfigPageWidget.resize(411, 252)
        self.gridLayout = QtGui.QGridLayout(vpcsDeviceConfigPageWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiNameLabel = QtGui.QLabel(vpcsDeviceConfigPageWidget)
        self.uiNameLabel.setObjectName(_fromUtf8("uiNameLabel"))
        self.gridLayout.addWidget(self.uiNameLabel, 0, 0, 1, 1)
        self.uiNameLineEdit = QtGui.QLineEdit(vpcsDeviceConfigPageWidget)
        self.uiNameLineEdit.setObjectName(_fromUtf8("uiNameLineEdit"))
        self.gridLayout.addWidget(self.uiNameLineEdit, 0, 1, 1, 1)
        self.uiScriptFileLabel = QtGui.QLabel(vpcsDeviceConfigPageWidget)
        self.uiScriptFileLabel.setObjectName(_fromUtf8("uiScriptFileLabel"))
        self.gridLayout.addWidget(self.uiScriptFileLabel, 1, 0, 1, 1)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.uiScriptFileLineEdit = QtGui.QLineEdit(vpcsDeviceConfigPageWidget)
        self.uiScriptFileLineEdit.setObjectName(_fromUtf8("uiScriptFileLineEdit"))
        self.horizontalLayout_4.addWidget(self.uiScriptFileLineEdit)
        self.uiScriptFileToolButton = QtGui.QToolButton(vpcsDeviceConfigPageWidget)
        self.uiScriptFileToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiScriptFileToolButton.setObjectName(_fromUtf8("uiScriptFileToolButton"))
        self.horizontalLayout_4.addWidget(self.uiScriptFileToolButton)
        self.gridLayout.addLayout(self.horizontalLayout_4, 1, 1, 1, 1)
        self.uiConsolePortLabel = QtGui.QLabel(vpcsDeviceConfigPageWidget)
        self.uiConsolePortLabel.setObjectName(_fromUtf8("uiConsolePortLabel"))
        self.gridLayout.addWidget(self.uiConsolePortLabel, 2, 0, 1, 1)
        self.uiConsolePortSpinBox = QtGui.QSpinBox(vpcsDeviceConfigPageWidget)
        self.uiConsolePortSpinBox.setMaximum(65535)
        self.uiConsolePortSpinBox.setObjectName(_fromUtf8("uiConsolePortSpinBox"))
        self.gridLayout.addWidget(self.uiConsolePortSpinBox, 2, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(263, 212, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 1, 1, 1)

        self.retranslateUi(vpcsDeviceConfigPageWidget)
        QtCore.QMetaObject.connectSlotsByName(vpcsDeviceConfigPageWidget)

    def retranslateUi(self, vpcsDeviceConfigPageWidget):
        vpcsDeviceConfigPageWidget.setWindowTitle(_translate("vpcsDeviceConfigPageWidget", "VPCS device configuration", None))
        self.uiNameLabel.setText(_translate("vpcsDeviceConfigPageWidget", "Name:", None))
        self.uiScriptFileLabel.setText(_translate("vpcsDeviceConfigPageWidget", "Script-File:", None))
        self.uiScriptFileToolButton.setText(_translate("vpcsDeviceConfigPageWidget", "...", None))
        self.uiConsolePortLabel.setText(_translate("vpcsDeviceConfigPageWidget", "Console port:", None))

