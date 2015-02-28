# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/dynamips/ui/dynamips_preferences_page.ui'
#
# Created: Sat Feb 28 15:58:23 2015
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

class Ui_DynamipsPreferencesPageWidget(object):
    def setupUi(self, DynamipsPreferencesPageWidget):
        DynamipsPreferencesPageWidget.setObjectName(_fromUtf8("DynamipsPreferencesPageWidget"))
        DynamipsPreferencesPageWidget.resize(430, 539)
        self.vboxlayout = QtGui.QVBoxLayout(DynamipsPreferencesPageWidget)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.uiTabWidget = QtGui.QTabWidget(DynamipsPreferencesPageWidget)
        self.uiTabWidget.setObjectName(_fromUtf8("uiTabWidget"))
        self.uiGeneralSettingsTabWidget = QtGui.QWidget()
        self.uiGeneralSettingsTabWidget.setObjectName(_fromUtf8("uiGeneralSettingsTabWidget"))
        self.gridLayout = QtGui.QGridLayout(self.uiGeneralSettingsTabWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.uiDynamipsPathLineEdit = QtGui.QLineEdit(self.uiGeneralSettingsTabWidget)
        self.uiDynamipsPathLineEdit.setObjectName(_fromUtf8("uiDynamipsPathLineEdit"))
        self.horizontalLayout.addWidget(self.uiDynamipsPathLineEdit)
        self.uiDynamipsPathToolButton = QtGui.QToolButton(self.uiGeneralSettingsTabWidget)
        self.uiDynamipsPathToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiDynamipsPathToolButton.setObjectName(_fromUtf8("uiDynamipsPathToolButton"))
        self.horizontalLayout.addWidget(self.uiDynamipsPathToolButton)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 2)
        self.uiDynamipsPathLabel = QtGui.QLabel(self.uiGeneralSettingsTabWidget)
        self.uiDynamipsPathLabel.setObjectName(_fromUtf8("uiDynamipsPathLabel"))
        self.gridLayout.addWidget(self.uiDynamipsPathLabel, 0, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(390, 193, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 2)
        self.uiAllocateAuxConsolePortsCheckBox = QtGui.QCheckBox(self.uiGeneralSettingsTabWidget)
        self.uiAllocateAuxConsolePortsCheckBox.setObjectName(_fromUtf8("uiAllocateAuxConsolePortsCheckBox"))
        self.gridLayout.addWidget(self.uiAllocateAuxConsolePortsCheckBox, 2, 0, 1, 2)
        self.uiTabWidget.addTab(self.uiGeneralSettingsTabWidget, _fromUtf8(""))
        self.uiServerSettingsTabWidget = QtGui.QWidget()
        self.uiServerSettingsTabWidget.setObjectName(_fromUtf8("uiServerSettingsTabWidget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.uiServerSettingsTabWidget)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.uiUseLocalServercheckBox = QtGui.QCheckBox(self.uiServerSettingsTabWidget)
        self.uiUseLocalServercheckBox.setChecked(True)
        self.uiUseLocalServercheckBox.setObjectName(_fromUtf8("uiUseLocalServercheckBox"))
        self.gridLayout_2.addWidget(self.uiUseLocalServercheckBox, 0, 0, 1, 1)
        self.uiRemoteServersGroupBox = QtGui.QGroupBox(self.uiServerSettingsTabWidget)
        self.uiRemoteServersGroupBox.setObjectName(_fromUtf8("uiRemoteServersGroupBox"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.uiRemoteServersGroupBox)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.uiRemoteServersTreeWidget = QtGui.QTreeWidget(self.uiRemoteServersGroupBox)
        self.uiRemoteServersTreeWidget.setEnabled(False)
        self.uiRemoteServersTreeWidget.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.uiRemoteServersTreeWidget.setObjectName(_fromUtf8("uiRemoteServersTreeWidget"))
        self.horizontalLayout_3.addWidget(self.uiRemoteServersTreeWidget)
        self.gridLayout_2.addWidget(self.uiRemoteServersGroupBox, 1, 0, 1, 1)
        self.uiTabWidget.addTab(self.uiServerSettingsTabWidget, _fromUtf8(""))
        self.uiAdvancedSettingsTabWidget = QtGui.QWidget()
        self.uiAdvancedSettingsTabWidget.setObjectName(_fromUtf8("uiAdvancedSettingsTabWidget"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.uiAdvancedSettingsTabWidget)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.uiMemoryUsageOptimisationGroupBox = QtGui.QGroupBox(self.uiAdvancedSettingsTabWidget)
        self.uiMemoryUsageOptimisationGroupBox.setObjectName(_fromUtf8("uiMemoryUsageOptimisationGroupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.uiMemoryUsageOptimisationGroupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.uiGhostIOSSupportCheckBox = QtGui.QCheckBox(self.uiMemoryUsageOptimisationGroupBox)
        self.uiGhostIOSSupportCheckBox.setChecked(True)
        self.uiGhostIOSSupportCheckBox.setObjectName(_fromUtf8("uiGhostIOSSupportCheckBox"))
        self.verticalLayout.addWidget(self.uiGhostIOSSupportCheckBox)
        self.uiMmapSupportCheckBox = QtGui.QCheckBox(self.uiMemoryUsageOptimisationGroupBox)
        self.uiMmapSupportCheckBox.setChecked(True)
        self.uiMmapSupportCheckBox.setObjectName(_fromUtf8("uiMmapSupportCheckBox"))
        self.verticalLayout.addWidget(self.uiMmapSupportCheckBox)
        self.uiSparseMemorySupportCheckBox = QtGui.QCheckBox(self.uiMemoryUsageOptimisationGroupBox)
        self.uiSparseMemorySupportCheckBox.setChecked(False)
        self.uiSparseMemorySupportCheckBox.setObjectName(_fromUtf8("uiSparseMemorySupportCheckBox"))
        self.verticalLayout.addWidget(self.uiSparseMemorySupportCheckBox)
        self.verticalLayout_3.addWidget(self.uiMemoryUsageOptimisationGroupBox)
        spacerItem1 = QtGui.QSpacerItem(390, 12, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.uiTabWidget.addTab(self.uiAdvancedSettingsTabWidget, _fromUtf8(""))
        self.vboxlayout.addWidget(self.uiTabWidget)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem2 = QtGui.QSpacerItem(164, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.uiTestSettingsPushButton = QtGui.QPushButton(DynamipsPreferencesPageWidget)
        self.uiTestSettingsPushButton.setObjectName(_fromUtf8("uiTestSettingsPushButton"))
        self.horizontalLayout_2.addWidget(self.uiTestSettingsPushButton)
        self.uiRestoreDefaultsPushButton = QtGui.QPushButton(DynamipsPreferencesPageWidget)
        self.uiRestoreDefaultsPushButton.setObjectName(_fromUtf8("uiRestoreDefaultsPushButton"))
        self.horizontalLayout_2.addWidget(self.uiRestoreDefaultsPushButton)
        self.vboxlayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(DynamipsPreferencesPageWidget)
        self.uiTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(DynamipsPreferencesPageWidget)
        DynamipsPreferencesPageWidget.setTabOrder(self.uiDynamipsPathLineEdit, self.uiDynamipsPathToolButton)
        DynamipsPreferencesPageWidget.setTabOrder(self.uiDynamipsPathToolButton, self.uiGhostIOSSupportCheckBox)
        DynamipsPreferencesPageWidget.setTabOrder(self.uiGhostIOSSupportCheckBox, self.uiMmapSupportCheckBox)
        DynamipsPreferencesPageWidget.setTabOrder(self.uiMmapSupportCheckBox, self.uiSparseMemorySupportCheckBox)

    def retranslateUi(self, DynamipsPreferencesPageWidget):
        DynamipsPreferencesPageWidget.setWindowTitle(_translate("DynamipsPreferencesPageWidget", "Dynamips", None))
        self.uiDynamipsPathToolButton.setText(_translate("DynamipsPreferencesPageWidget", "&Browse...", None))
        self.uiDynamipsPathLabel.setText(_translate("DynamipsPreferencesPageWidget", "Path to Dynamips:", None))
        self.uiAllocateAuxConsolePortsCheckBox.setText(_translate("DynamipsPreferencesPageWidget", "Allocate AUX console ports", None))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiGeneralSettingsTabWidget), _translate("DynamipsPreferencesPageWidget", "General settings", None))
        self.uiUseLocalServercheckBox.setText(_translate("DynamipsPreferencesPageWidget", "Always use the local server", None))
        self.uiRemoteServersGroupBox.setTitle(_translate("DynamipsPreferencesPageWidget", "Remote servers", None))
        self.uiRemoteServersTreeWidget.headerItem().setText(0, _translate("DynamipsPreferencesPageWidget", "Host", None))
        self.uiRemoteServersTreeWidget.headerItem().setText(1, _translate("DynamipsPreferencesPageWidget", "Port", None))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiServerSettingsTabWidget), _translate("DynamipsPreferencesPageWidget", "Server settings", None))
        self.uiMemoryUsageOptimisationGroupBox.setTitle(_translate("DynamipsPreferencesPageWidget", "Memory usage optimisation", None))
        self.uiGhostIOSSupportCheckBox.setToolTip(_translate("DynamipsPreferencesPageWidget", "The ghost IOS feature is a solution that helps to decrease memory usage by sharing an IOS image between different router instances.", None))
        self.uiGhostIOSSupportCheckBox.setText(_translate("DynamipsPreferencesPageWidget", "Enable ghost IOS support", None))
        self.uiMmapSupportCheckBox.setToolTip(_translate("DynamipsPreferencesPageWidget", "The mmap feature tells Dynamips to use disk files instead of real memory for router instances.", None))
        self.uiMmapSupportCheckBox.setText(_translate("DynamipsPreferencesPageWidget", "Enable mmap support", None))
        self.uiSparseMemorySupportCheckBox.setToolTip(_translate("DynamipsPreferencesPageWidget", "The sparse memory feature reduces the amount of virtual memory used by router instances.", None))
        self.uiSparseMemorySupportCheckBox.setText(_translate("DynamipsPreferencesPageWidget", "Enable sparse memory support", None))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiAdvancedSettingsTabWidget), _translate("DynamipsPreferencesPageWidget", "Advanced settings", None))
        self.uiTestSettingsPushButton.setText(_translate("DynamipsPreferencesPageWidget", "Test settings", None))
        self.uiRestoreDefaultsPushButton.setText(_translate("DynamipsPreferencesPageWidget", "Restore defaults", None))

