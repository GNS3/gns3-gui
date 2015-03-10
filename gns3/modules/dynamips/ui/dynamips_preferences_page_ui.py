# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/dynamips/ui/dynamips_preferences_page.ui'
#
# Created: Mon Mar  9 17:56:06 2015
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
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.uiGeneralSettingsTabWidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.uiUseLocalServercheckBox = QtGui.QCheckBox(self.uiGeneralSettingsTabWidget)
        self.uiUseLocalServercheckBox.setChecked(True)
        self.uiUseLocalServercheckBox.setObjectName(_fromUtf8("uiUseLocalServercheckBox"))
        self.verticalLayout_2.addWidget(self.uiUseLocalServercheckBox)
        self.uiDynamipsPathLabel = QtGui.QLabel(self.uiGeneralSettingsTabWidget)
        self.uiDynamipsPathLabel.setObjectName(_fromUtf8("uiDynamipsPathLabel"))
        self.verticalLayout_2.addWidget(self.uiDynamipsPathLabel)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.uiDynamipsPathLineEdit = QtGui.QLineEdit(self.uiGeneralSettingsTabWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiDynamipsPathLineEdit.sizePolicy().hasHeightForWidth())
        self.uiDynamipsPathLineEdit.setSizePolicy(sizePolicy)
        self.uiDynamipsPathLineEdit.setObjectName(_fromUtf8("uiDynamipsPathLineEdit"))
        self.horizontalLayout.addWidget(self.uiDynamipsPathLineEdit)
        self.uiDynamipsPathToolButton = QtGui.QToolButton(self.uiGeneralSettingsTabWidget)
        self.uiDynamipsPathToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiDynamipsPathToolButton.setObjectName(_fromUtf8("uiDynamipsPathToolButton"))
        self.horizontalLayout.addWidget(self.uiDynamipsPathToolButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.uiAllocateAuxConsolePortsCheckBox = QtGui.QCheckBox(self.uiGeneralSettingsTabWidget)
        self.uiAllocateAuxConsolePortsCheckBox.setObjectName(_fromUtf8("uiAllocateAuxConsolePortsCheckBox"))
        self.verticalLayout_2.addWidget(self.uiAllocateAuxConsolePortsCheckBox)
        spacerItem = QtGui.QSpacerItem(390, 193, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.uiTabWidget.addTab(self.uiGeneralSettingsTabWidget, _fromUtf8(""))
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
        self.uiUseLocalServercheckBox.setText(_translate("DynamipsPreferencesPageWidget", "Use the local server", None))
        self.uiDynamipsPathLabel.setText(_translate("DynamipsPreferencesPageWidget", "Path to Dynamips:", None))
        self.uiDynamipsPathToolButton.setText(_translate("DynamipsPreferencesPageWidget", "&Browse...", None))
        self.uiAllocateAuxConsolePortsCheckBox.setText(_translate("DynamipsPreferencesPageWidget", "Allocate AUX console ports", None))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiGeneralSettingsTabWidget), _translate("DynamipsPreferencesPageWidget", "General settings", None))
        self.uiMemoryUsageOptimisationGroupBox.setTitle(_translate("DynamipsPreferencesPageWidget", "Memory usage optimisation", None))
        self.uiGhostIOSSupportCheckBox.setToolTip(_translate("DynamipsPreferencesPageWidget", "The ghost IOS feature is a solution that helps to decrease memory usage by sharing an IOS image between different router instances.", None))
        self.uiGhostIOSSupportCheckBox.setText(_translate("DynamipsPreferencesPageWidget", "Enable ghost IOS support", None))
        self.uiMmapSupportCheckBox.setToolTip(_translate("DynamipsPreferencesPageWidget", "The mmap feature tells Dynamips to use disk files instead of real memory for router instances.", None))
        self.uiMmapSupportCheckBox.setText(_translate("DynamipsPreferencesPageWidget", "Enable mmap support", None))
        self.uiSparseMemorySupportCheckBox.setToolTip(_translate("DynamipsPreferencesPageWidget", "The sparse memory feature reduces the amount of virtual memory used by router instances.", None))
        self.uiSparseMemorySupportCheckBox.setText(_translate("DynamipsPreferencesPageWidget", "Enable sparse memory support", None))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiAdvancedSettingsTabWidget), _translate("DynamipsPreferencesPageWidget", "Advanced settings", None))
        self.uiRestoreDefaultsPushButton.setText(_translate("DynamipsPreferencesPageWidget", "Restore defaults", None))

