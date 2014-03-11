# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/workspace/git/gns3-gui/gns3/modules/iou/ui/iou_device_configuration_page.ui'
#
# Created: Sat Mar  8 18:19:32 2014
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

class Ui_iouDeviceConfigPageWidget(object):
    def setupUi(self, iouDeviceConfigPageWidget):
        iouDeviceConfigPageWidget.setObjectName(_fromUtf8("iouDeviceConfigPageWidget"))
        iouDeviceConfigPageWidget.resize(403, 461)
        self.gridLayout = QtGui.QGridLayout(iouDeviceConfigPageWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiNameLabel = QtGui.QLabel(iouDeviceConfigPageWidget)
        self.uiNameLabel.setObjectName(_fromUtf8("uiNameLabel"))
        self.gridLayout.addWidget(self.uiNameLabel, 0, 0, 1, 1)
        self.uiIOUImageLabel = QtGui.QLabel(iouDeviceConfigPageWidget)
        self.uiIOUImageLabel.setObjectName(_fromUtf8("uiIOUImageLabel"))
        self.gridLayout.addWidget(self.uiIOUImageLabel, 1, 0, 1, 1)
        self.uiStartupConfigLabel = QtGui.QLabel(iouDeviceConfigPageWidget)
        self.uiStartupConfigLabel.setObjectName(_fromUtf8("uiStartupConfigLabel"))
        self.gridLayout.addWidget(self.uiStartupConfigLabel, 2, 0, 1, 1)
        self.uiConsolePortLabel = QtGui.QLabel(iouDeviceConfigPageWidget)
        self.uiConsolePortLabel.setObjectName(_fromUtf8("uiConsolePortLabel"))
        self.gridLayout.addWidget(self.uiConsolePortLabel, 3, 0, 1, 1)
        self.uiRamLabel = QtGui.QLabel(iouDeviceConfigPageWidget)
        self.uiRamLabel.setObjectName(_fromUtf8("uiRamLabel"))
        self.gridLayout.addWidget(self.uiRamLabel, 4, 0, 1, 1)
        self.uiNvramLabel = QtGui.QLabel(iouDeviceConfigPageWidget)
        self.uiNvramLabel.setObjectName(_fromUtf8("uiNvramLabel"))
        self.gridLayout.addWidget(self.uiNvramLabel, 5, 0, 1, 1)
        self.uiEthernetAdaptersLabel = QtGui.QLabel(iouDeviceConfigPageWidget)
        self.uiEthernetAdaptersLabel.setObjectName(_fromUtf8("uiEthernetAdaptersLabel"))
        self.gridLayout.addWidget(self.uiEthernetAdaptersLabel, 6, 0, 1, 3)
        self.uiEthernetAdaptersSpinBox = QtGui.QSpinBox(iouDeviceConfigPageWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiEthernetAdaptersSpinBox.sizePolicy().hasHeightForWidth())
        self.uiEthernetAdaptersSpinBox.setSizePolicy(sizePolicy)
        self.uiEthernetAdaptersSpinBox.setMaximum(16)
        self.uiEthernetAdaptersSpinBox.setSingleStep(2)
        self.uiEthernetAdaptersSpinBox.setObjectName(_fromUtf8("uiEthernetAdaptersSpinBox"))
        self.gridLayout.addWidget(self.uiEthernetAdaptersSpinBox, 6, 3, 1, 1)
        self.uiSerialAdaptersLabel = QtGui.QLabel(iouDeviceConfigPageWidget)
        self.uiSerialAdaptersLabel.setObjectName(_fromUtf8("uiSerialAdaptersLabel"))
        self.gridLayout.addWidget(self.uiSerialAdaptersLabel, 7, 0, 1, 2)
        self.uiSerialAdaptersSpinBox = QtGui.QSpinBox(iouDeviceConfigPageWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiSerialAdaptersSpinBox.sizePolicy().hasHeightForWidth())
        self.uiSerialAdaptersSpinBox.setSizePolicy(sizePolicy)
        self.uiSerialAdaptersSpinBox.setMaximum(16)
        self.uiSerialAdaptersSpinBox.setSingleStep(2)
        self.uiSerialAdaptersSpinBox.setObjectName(_fromUtf8("uiSerialAdaptersSpinBox"))
        self.gridLayout.addWidget(self.uiSerialAdaptersSpinBox, 7, 3, 1, 1)
        spacerItem = QtGui.QSpacerItem(263, 212, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 8, 3, 1, 1)
        self.uiNvramSpinBox = QtGui.QSpinBox(iouDeviceConfigPageWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiNvramSpinBox.sizePolicy().hasHeightForWidth())
        self.uiNvramSpinBox.setSizePolicy(sizePolicy)
        self.uiNvramSpinBox.setMaximum(4096)
        self.uiNvramSpinBox.setSingleStep(4)
        self.uiNvramSpinBox.setProperty("value", 128)
        self.uiNvramSpinBox.setObjectName(_fromUtf8("uiNvramSpinBox"))
        self.gridLayout.addWidget(self.uiNvramSpinBox, 5, 3, 1, 1)
        self.uiRamSpinBox = QtGui.QSpinBox(iouDeviceConfigPageWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiRamSpinBox.sizePolicy().hasHeightForWidth())
        self.uiRamSpinBox.setSizePolicy(sizePolicy)
        self.uiRamSpinBox.setMaximum(4096)
        self.uiRamSpinBox.setSingleStep(4)
        self.uiRamSpinBox.setProperty("value", 128)
        self.uiRamSpinBox.setObjectName(_fromUtf8("uiRamSpinBox"))
        self.gridLayout.addWidget(self.uiRamSpinBox, 4, 3, 1, 1)
        self.uiConsolePortSpinBox = QtGui.QSpinBox(iouDeviceConfigPageWidget)
        self.uiConsolePortSpinBox.setMaximum(65535)
        self.uiConsolePortSpinBox.setObjectName(_fromUtf8("uiConsolePortSpinBox"))
        self.gridLayout.addWidget(self.uiConsolePortSpinBox, 3, 3, 1, 1)
        self.uiStartupConfigTextLabel = QtGui.QLabel(iouDeviceConfigPageWidget)
        self.uiStartupConfigTextLabel.setText(_fromUtf8(""))
        self.uiStartupConfigTextLabel.setObjectName(_fromUtf8("uiStartupConfigTextLabel"))
        self.gridLayout.addWidget(self.uiStartupConfigTextLabel, 2, 3, 1, 1)
        self.uiIOUImageTextLabel = QtGui.QLabel(iouDeviceConfigPageWidget)
        self.uiIOUImageTextLabel.setText(_fromUtf8(""))
        self.uiIOUImageTextLabel.setObjectName(_fromUtf8("uiIOUImageTextLabel"))
        self.gridLayout.addWidget(self.uiIOUImageTextLabel, 1, 3, 1, 1)
        self.uiNameLineEdit = QtGui.QLineEdit(iouDeviceConfigPageWidget)
        self.uiNameLineEdit.setObjectName(_fromUtf8("uiNameLineEdit"))
        self.gridLayout.addWidget(self.uiNameLineEdit, 0, 3, 1, 1)

        self.retranslateUi(iouDeviceConfigPageWidget)
        QtCore.QMetaObject.connectSlotsByName(iouDeviceConfigPageWidget)

    def retranslateUi(self, iouDeviceConfigPageWidget):
        iouDeviceConfigPageWidget.setWindowTitle(_translate("iouDeviceConfigPageWidget", "IOU device configuration", None))
        self.uiNameLabel.setText(_translate("iouDeviceConfigPageWidget", "Name:", None))
        self.uiIOUImageLabel.setText(_translate("iouDeviceConfigPageWidget", "IOU image:", None))
        self.uiStartupConfigLabel.setText(_translate("iouDeviceConfigPageWidget", "Startup-config:", None))
        self.uiConsolePortLabel.setText(_translate("iouDeviceConfigPageWidget", "Console port:", None))
        self.uiRamLabel.setText(_translate("iouDeviceConfigPageWidget", "RAM size:", None))
        self.uiNvramLabel.setText(_translate("iouDeviceConfigPageWidget", "NVRAM size:", None))
        self.uiEthernetAdaptersLabel.setText(_translate("iouDeviceConfigPageWidget", "Ethernet adapters:", None))
        self.uiSerialAdaptersLabel.setText(_translate("iouDeviceConfigPageWidget", "Serial adapters:", None))
        self.uiNvramSpinBox.setSuffix(_translate("iouDeviceConfigPageWidget", " KiB", None))
        self.uiRamSpinBox.setSuffix(_translate("iouDeviceConfigPageWidget", " MiB", None))

