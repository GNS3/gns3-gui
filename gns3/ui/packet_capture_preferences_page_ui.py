# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/packet_capture_preferences_page.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PacketCapturePreferencesPageWidget(object):
    def setupUi(self, PacketCapturePreferencesPageWidget):
        PacketCapturePreferencesPageWidget.setObjectName("PacketCapturePreferencesPageWidget")
        PacketCapturePreferencesPageWidget.resize(839, 444)
        self.verticalLayout = QtWidgets.QVBoxLayout(PacketCapturePreferencesPageWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiSettingsGroupBox = QtWidgets.QGroupBox(PacketCapturePreferencesPageWidget)
        self.uiSettingsGroupBox.setObjectName("uiSettingsGroupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.uiSettingsGroupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.uiPreconfiguredCaptureReaderCommandLabel = QtWidgets.QLabel(self.uiSettingsGroupBox)
        self.uiPreconfiguredCaptureReaderCommandLabel.setObjectName("uiPreconfiguredCaptureReaderCommandLabel")
        self.gridLayout.addWidget(self.uiPreconfiguredCaptureReaderCommandLabel, 0, 0, 1, 2)
        self.uiPreconfiguredCaptureReaderCommandComboBox = QtWidgets.QComboBox(self.uiSettingsGroupBox)
        self.uiPreconfiguredCaptureReaderCommandComboBox.setObjectName("uiPreconfiguredCaptureReaderCommandComboBox")
        self.gridLayout.addWidget(self.uiPreconfiguredCaptureReaderCommandComboBox, 1, 0, 1, 1)
        self.uiPreconfiguredCaptureReaderCommandPushButton = QtWidgets.QPushButton(self.uiSettingsGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiPreconfiguredCaptureReaderCommandPushButton.sizePolicy().hasHeightForWidth())
        self.uiPreconfiguredCaptureReaderCommandPushButton.setSizePolicy(sizePolicy)
        self.uiPreconfiguredCaptureReaderCommandPushButton.setObjectName("uiPreconfiguredCaptureReaderCommandPushButton")
        self.gridLayout.addWidget(self.uiPreconfiguredCaptureReaderCommandPushButton, 1, 1, 1, 1)
        self.uiCaptureReaderCommandLabel = QtWidgets.QLabel(self.uiSettingsGroupBox)
        self.uiCaptureReaderCommandLabel.setEnabled(True)
        self.uiCaptureReaderCommandLabel.setObjectName("uiCaptureReaderCommandLabel")
        self.gridLayout.addWidget(self.uiCaptureReaderCommandLabel, 2, 0, 1, 1)
        self.uiAutoStartCheckBox = QtWidgets.QCheckBox(self.uiSettingsGroupBox)
        self.uiAutoStartCheckBox.setEnabled(True)
        self.uiAutoStartCheckBox.setChecked(False)
        self.uiAutoStartCheckBox.setObjectName("uiAutoStartCheckBox")
        self.gridLayout.addWidget(self.uiAutoStartCheckBox, 4, 0, 1, 2)
        self.uiCaptureAnalyzerCommandLabel = QtWidgets.QLabel(self.uiSettingsGroupBox)
        self.uiCaptureAnalyzerCommandLabel.setObjectName("uiCaptureAnalyzerCommandLabel")
        self.gridLayout.addWidget(self.uiCaptureAnalyzerCommandLabel, 5, 0, 1, 1)
        self.uiCaptureAnalyzerCommandLineEdit = QtWidgets.QLineEdit(self.uiSettingsGroupBox)
        self.uiCaptureAnalyzerCommandLineEdit.setObjectName("uiCaptureAnalyzerCommandLineEdit")
        self.gridLayout.addWidget(self.uiCaptureAnalyzerCommandLineEdit, 6, 0, 1, 2)
        self.uiCaptureReaderCommandLineEdit = QtWidgets.QLineEdit(self.uiSettingsGroupBox)
        self.uiCaptureReaderCommandLineEdit.setObjectName("uiCaptureReaderCommandLineEdit")
        self.gridLayout.addWidget(self.uiCaptureReaderCommandLineEdit, 3, 0, 1, 2)
        self.verticalLayout.addWidget(self.uiSettingsGroupBox)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(250, 17, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.uiRestoreDefaultsPushButton = QtWidgets.QPushButton(PacketCapturePreferencesPageWidget)
        self.uiRestoreDefaultsPushButton.setObjectName("uiRestoreDefaultsPushButton")
        self.horizontalLayout.addWidget(self.uiRestoreDefaultsPushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem1 = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)

        self.retranslateUi(PacketCapturePreferencesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(PacketCapturePreferencesPageWidget)

    def retranslateUi(self, PacketCapturePreferencesPageWidget):
        _translate = QtCore.QCoreApplication.translate
        PacketCapturePreferencesPageWidget.setWindowTitle(_translate("PacketCapturePreferencesPageWidget", "Packet capture"))
        self.uiSettingsGroupBox.setTitle(_translate("PacketCapturePreferencesPageWidget", "Settings"))
        self.uiPreconfiguredCaptureReaderCommandLabel.setText(_translate("PacketCapturePreferencesPageWidget", "Preconfigured packet capture reader commands:"))
        self.uiPreconfiguredCaptureReaderCommandPushButton.setText(_translate("PacketCapturePreferencesPageWidget", "&Set"))
        self.uiCaptureReaderCommandLabel.setText(_translate("PacketCapturePreferencesPageWidget", "Packet capture reader command:"))
        self.uiAutoStartCheckBox.setText(_translate("PacketCapturePreferencesPageWidget", "Automatically start the packet capture application"))
        self.uiCaptureAnalyzerCommandLabel.setText(_translate("PacketCapturePreferencesPageWidget", "Packet capture analyzer command:"))
        self.uiCaptureReaderCommandLineEdit.setToolTip(_translate("PacketCapturePreferencesPageWidget", "<html><head/><body><p>Command line replacements:</p><p>%c = capture file (PCAP format)</p></body></html>"))
        self.uiRestoreDefaultsPushButton.setText(_translate("PacketCapturePreferencesPageWidget", "Restore defaults"))

