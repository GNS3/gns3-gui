# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/virtualbox/ui/virtualbox_vm_configuration_page.ui'
#
# Created: Fri Mar 13 16:56:48 2015
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

class Ui_virtualBoxVMConfigPageWidget(object):
    def setupUi(self, virtualBoxVMConfigPageWidget):
        virtualBoxVMConfigPageWidget.setObjectName(_fromUtf8("virtualBoxVMConfigPageWidget"))
        virtualBoxVMConfigPageWidget.resize(509, 346)
        self.verticalLayout = QtGui.QVBoxLayout(virtualBoxVMConfigPageWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.uiTabWidget = QtGui.QTabWidget(virtualBoxVMConfigPageWidget)
        self.uiTabWidget.setObjectName(_fromUtf8("uiTabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.gridLayout = QtGui.QGridLayout(self.tab)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiNameLabel = QtGui.QLabel(self.tab)
        self.uiNameLabel.setObjectName(_fromUtf8("uiNameLabel"))
        self.gridLayout.addWidget(self.uiNameLabel, 0, 0, 1, 1)
        self.uiNameLineEdit = QtGui.QLineEdit(self.tab)
        self.uiNameLineEdit.setObjectName(_fromUtf8("uiNameLineEdit"))
        self.gridLayout.addWidget(self.uiNameLineEdit, 0, 1, 1, 1)
        self.uiVMListLabel = QtGui.QLabel(self.tab)
        self.uiVMListLabel.setObjectName(_fromUtf8("uiVMListLabel"))
        self.gridLayout.addWidget(self.uiVMListLabel, 1, 0, 1, 1)
        self.uiVMListComboBox = QtGui.QComboBox(self.tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVMListComboBox.sizePolicy().hasHeightForWidth())
        self.uiVMListComboBox.setSizePolicy(sizePolicy)
        self.uiVMListComboBox.setObjectName(_fromUtf8("uiVMListComboBox"))
        self.gridLayout.addWidget(self.uiVMListComboBox, 1, 1, 1, 1)
        self.uiVMRamLabel = QtGui.QLabel(self.tab)
        self.uiVMRamLabel.setObjectName(_fromUtf8("uiVMRamLabel"))
        self.gridLayout.addWidget(self.uiVMRamLabel, 2, 0, 1, 1)
        self.uiVMRamSpinBox = QtGui.QSpinBox(self.tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVMRamSpinBox.sizePolicy().hasHeightForWidth())
        self.uiVMRamSpinBox.setSizePolicy(sizePolicy)
        self.uiVMRamSpinBox.setMaximum(65535)
        self.uiVMRamSpinBox.setObjectName(_fromUtf8("uiVMRamSpinBox"))
        self.gridLayout.addWidget(self.uiVMRamSpinBox, 2, 1, 1, 1)
        self.uiConsolePortLabel = QtGui.QLabel(self.tab)
        self.uiConsolePortLabel.setObjectName(_fromUtf8("uiConsolePortLabel"))
        self.gridLayout.addWidget(self.uiConsolePortLabel, 3, 0, 1, 1)
        self.uiConsolePortSpinBox = QtGui.QSpinBox(self.tab)
        self.uiConsolePortSpinBox.setMaximum(65535)
        self.uiConsolePortSpinBox.setObjectName(_fromUtf8("uiConsolePortSpinBox"))
        self.gridLayout.addWidget(self.uiConsolePortSpinBox, 3, 1, 1, 1)
        self.uiEnableConsoleCheckBox = QtGui.QCheckBox(self.tab)
        self.uiEnableConsoleCheckBox.setObjectName(_fromUtf8("uiEnableConsoleCheckBox"))
        self.gridLayout.addWidget(self.uiEnableConsoleCheckBox, 4, 0, 1, 2)
        self.uiHeadlessModeCheckBox = QtGui.QCheckBox(self.tab)
        self.uiHeadlessModeCheckBox.setChecked(False)
        self.uiHeadlessModeCheckBox.setObjectName(_fromUtf8("uiHeadlessModeCheckBox"))
        self.gridLayout.addWidget(self.uiHeadlessModeCheckBox, 5, 0, 1, 2)
        self.uiBaseVMCheckBox = QtGui.QCheckBox(self.tab)
        self.uiBaseVMCheckBox.setEnabled(True)
        self.uiBaseVMCheckBox.setObjectName(_fromUtf8("uiBaseVMCheckBox"))
        self.gridLayout.addWidget(self.uiBaseVMCheckBox, 6, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 138, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 7, 1, 1, 1)
        self.uiTabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.gridLayout_3 = QtGui.QGridLayout(self.tab_2)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.uiAdaptersLabel = QtGui.QLabel(self.tab_2)
        self.uiAdaptersLabel.setObjectName(_fromUtf8("uiAdaptersLabel"))
        self.gridLayout_3.addWidget(self.uiAdaptersLabel, 0, 0, 1, 1)
        self.uiAdaptersSpinBox = QtGui.QSpinBox(self.tab_2)
        self.uiAdaptersSpinBox.setMinimum(1)
        self.uiAdaptersSpinBox.setMaximum(36)
        self.uiAdaptersSpinBox.setObjectName(_fromUtf8("uiAdaptersSpinBox"))
        self.gridLayout_3.addWidget(self.uiAdaptersSpinBox, 0, 1, 1, 1)
        self.label = QtGui.QLabel(self.tab_2)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_3.addWidget(self.label, 1, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(248, 178, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem1, 3, 0, 1, 2)
        self.uiAdapterTypesComboBox = QtGui.QComboBox(self.tab_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiAdapterTypesComboBox.sizePolicy().hasHeightForWidth())
        self.uiAdapterTypesComboBox.setSizePolicy(sizePolicy)
        self.uiAdapterTypesComboBox.setObjectName(_fromUtf8("uiAdapterTypesComboBox"))
        self.gridLayout_3.addWidget(self.uiAdapterTypesComboBox, 1, 1, 1, 1)
        self.uiUseAnyAdapterCheckBox = QtGui.QCheckBox(self.tab_2)
        self.uiUseAnyAdapterCheckBox.setObjectName(_fromUtf8("uiUseAnyAdapterCheckBox"))
        self.gridLayout_3.addWidget(self.uiUseAnyAdapterCheckBox, 2, 0, 1, 2)
        self.uiTabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.verticalLayout.addWidget(self.uiTabWidget)

        self.retranslateUi(virtualBoxVMConfigPageWidget)
        self.uiTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(virtualBoxVMConfigPageWidget)

    def retranslateUi(self, virtualBoxVMConfigPageWidget):
        virtualBoxVMConfigPageWidget.setWindowTitle(_translate("virtualBoxVMConfigPageWidget", "VirtualBox VM configuration", None))
        self.uiNameLabel.setText(_translate("virtualBoxVMConfigPageWidget", "Name:", None))
        self.uiVMListLabel.setText(_translate("virtualBoxVMConfigPageWidget", "VM name:", None))
        self.uiVMRamLabel.setText(_translate("virtualBoxVMConfigPageWidget", "RAM:", None))
        self.uiVMRamSpinBox.setSuffix(_translate("virtualBoxVMConfigPageWidget", " MB", None))
        self.uiConsolePortLabel.setText(_translate("virtualBoxVMConfigPageWidget", "Console port:", None))
        self.uiEnableConsoleCheckBox.setText(_translate("virtualBoxVMConfigPageWidget", "Enable remote console", None))
        self.uiHeadlessModeCheckBox.setText(_translate("virtualBoxVMConfigPageWidget", "Start VM in headless mode", None))
        self.uiBaseVMCheckBox.setText(_translate("virtualBoxVMConfigPageWidget", "Use as a linked base VM (experimental)", None))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.tab), _translate("virtualBoxVMConfigPageWidget", "General settings", None))
        self.uiAdaptersLabel.setText(_translate("virtualBoxVMConfigPageWidget", "Adapters:", None))
        self.label.setText(_translate("virtualBoxVMConfigPageWidget", "Type:", None))
        self.uiUseAnyAdapterCheckBox.setText(_translate("virtualBoxVMConfigPageWidget", "Allow GNS3 to use any configured VirtualBox adapter", None))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.tab_2), _translate("virtualBoxVMConfigPageWidget", "Network", None))

