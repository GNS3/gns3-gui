# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/packet_capture_preferences_page.ui'
#
# Created: Tue Sep 30 18:58:59 2014
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


class Ui_PacketCapturePreferencesPageWidget(object):

    def setupUi(self, PacketCapturePreferencesPageWidget):
        PacketCapturePreferencesPageWidget.setObjectName(_fromUtf8("PacketCapturePreferencesPageWidget"))
        PacketCapturePreferencesPageWidget.resize(409, 290)
        self.gridLayout = QtGui.QGridLayout(PacketCapturePreferencesPageWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiSettingsGroupBox = QtGui.QGroupBox(PacketCapturePreferencesPageWidget)
        self.uiSettingsGroupBox.setObjectName(_fromUtf8("uiSettingsGroupBox"))
        self.gridlayout = QtGui.QGridLayout(self.uiSettingsGroupBox)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.uiCaptureAnalyzerCommandLabel = QtGui.QLabel(self.uiSettingsGroupBox)
        self.uiCaptureAnalyzerCommandLabel.setObjectName(_fromUtf8("uiCaptureAnalyzerCommandLabel"))
        self.gridlayout.addWidget(self.uiCaptureAnalyzerCommandLabel, 5, 0, 1, 1)
        self.uiCaptureReaderCommandLabel = QtGui.QLabel(self.uiSettingsGroupBox)
        self.uiCaptureReaderCommandLabel.setEnabled(True)
        self.uiCaptureReaderCommandLabel.setObjectName(_fromUtf8("uiCaptureReaderCommandLabel"))
        self.gridlayout.addWidget(self.uiCaptureReaderCommandLabel, 2, 0, 1, 2)
        self.uiCaptureReaderCommandLineEdit = QtGui.QLineEdit(self.uiSettingsGroupBox)
        self.uiCaptureReaderCommandLineEdit.setObjectName(_fromUtf8("uiCaptureReaderCommandLineEdit"))
        self.gridlayout.addWidget(self.uiCaptureReaderCommandLineEdit, 3, 0, 1, 2)
        self.uiAutoStartCheckBox = QtGui.QCheckBox(self.uiSettingsGroupBox)
        self.uiAutoStartCheckBox.setEnabled(True)
        self.uiAutoStartCheckBox.setChecked(False)
        self.uiAutoStartCheckBox.setObjectName(_fromUtf8("uiAutoStartCheckBox"))
        self.gridlayout.addWidget(self.uiAutoStartCheckBox, 4, 0, 1, 2)
        self.uiPreconfiguredCaptureReaderCommandLabel = QtGui.QLabel(self.uiSettingsGroupBox)
        self.uiPreconfiguredCaptureReaderCommandLabel.setObjectName(_fromUtf8("uiPreconfiguredCaptureReaderCommandLabel"))
        self.gridlayout.addWidget(self.uiPreconfiguredCaptureReaderCommandLabel, 0, 0, 1, 2)
        self.uiPreconfiguredCaptureReaderCommandPushButton = QtGui.QPushButton(self.uiSettingsGroupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiPreconfiguredCaptureReaderCommandPushButton.sizePolicy().hasHeightForWidth())
        self.uiPreconfiguredCaptureReaderCommandPushButton.setSizePolicy(sizePolicy)
        self.uiPreconfiguredCaptureReaderCommandPushButton.setObjectName(_fromUtf8("uiPreconfiguredCaptureReaderCommandPushButton"))
        self.gridlayout.addWidget(self.uiPreconfiguredCaptureReaderCommandPushButton, 1, 1, 1, 1)
        self.uiPreconfiguredCaptureReaderCommandComboBox = QtGui.QComboBox(self.uiSettingsGroupBox)
        self.uiPreconfiguredCaptureReaderCommandComboBox.setObjectName(_fromUtf8("uiPreconfiguredCaptureReaderCommandComboBox"))
        self.gridlayout.addWidget(self.uiPreconfiguredCaptureReaderCommandComboBox, 1, 0, 1, 1)
        self.uiCaptureAnalyzerCommandLineEdit = QtGui.QLineEdit(self.uiSettingsGroupBox)
        self.uiCaptureAnalyzerCommandLineEdit.setObjectName(_fromUtf8("uiCaptureAnalyzerCommandLineEdit"))
        self.gridlayout.addWidget(self.uiCaptureAnalyzerCommandLineEdit, 6, 0, 1, 2)
        self.gridLayout.addWidget(self.uiSettingsGroupBox, 0, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(253, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.uiRestoreDefaultsPushButton = QtGui.QPushButton(PacketCapturePreferencesPageWidget)
        self.uiRestoreDefaultsPushButton.setObjectName(_fromUtf8("uiRestoreDefaultsPushButton"))
        self.gridLayout.addWidget(self.uiRestoreDefaultsPushButton, 1, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 101, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 2, 0, 1, 2)

        self.retranslateUi(PacketCapturePreferencesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(PacketCapturePreferencesPageWidget)

    def retranslateUi(self, PacketCapturePreferencesPageWidget):
        PacketCapturePreferencesPageWidget.setWindowTitle(_translate("PacketCapturePreferencesPageWidget", "Packet capture", None))
        self.uiSettingsGroupBox.setTitle(_translate("PacketCapturePreferencesPageWidget", "Settings", None))
        self.uiCaptureAnalyzerCommandLabel.setText(_translate("PacketCapturePreferencesPageWidget", "Packet capture analyzer command:", None))
        self.uiCaptureReaderCommandLabel.setText(_translate("PacketCapturePreferencesPageWidget", "Packet capture reader command:", None))
        self.uiCaptureReaderCommandLineEdit.setToolTip(_translate("PacketCapturePreferencesPageWidget", "<html><head/><body><p>Command line replacements:</p><p>%c = capture file (PCAP format)</p></body></html>", None))
        self.uiAutoStartCheckBox.setText(_translate("PacketCapturePreferencesPageWidget", "Automatically start the packet capture application", None))
        self.uiPreconfiguredCaptureReaderCommandLabel.setText(_translate("PacketCapturePreferencesPageWidget", "Preconfigured packet capture reader commands:", None))
        self.uiPreconfiguredCaptureReaderCommandPushButton.setText(_translate("PacketCapturePreferencesPageWidget", "&Set", None))
        self.uiRestoreDefaultsPushButton.setText(_translate("PacketCapturePreferencesPageWidget", "Restore defaults", None))
