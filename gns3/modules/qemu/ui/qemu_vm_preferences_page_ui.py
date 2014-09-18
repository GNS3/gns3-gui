# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/qemu/ui/qemu_vm_preferences_page.ui'
#
# Created: Wed Sep 17 15:18:23 2014
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

class Ui_QemuVMPreferencesPageWidget(object):
    def setupUi(self, QemuVMPreferencesPageWidget):
        QemuVMPreferencesPageWidget.setObjectName(_fromUtf8("QemuVMPreferencesPageWidget"))
        QemuVMPreferencesPageWidget.resize(421, 537)
        self.vboxlayout = QtGui.QVBoxLayout(QemuVMPreferencesPageWidget)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.uiTabWidget = QtGui.QTabWidget(QemuVMPreferencesPageWidget)
        self.uiTabWidget.setEnabled(True)
        self.uiTabWidget.setObjectName(_fromUtf8("uiTabWidget"))
        self.uiQemuVMTabWidget = QtGui.QWidget()
        self.uiQemuVMTabWidget.setObjectName(_fromUtf8("uiQemuVMTabWidget"))
        self.gridLayout = QtGui.QGridLayout(self.uiQemuVMTabWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiQemuVMsTreeWidget = QtGui.QTreeWidget(self.uiQemuVMTabWidget)
        self.uiQemuVMsTreeWidget.setObjectName(_fromUtf8("uiQemuVMsTreeWidget"))
        self.gridLayout.addWidget(self.uiQemuVMsTreeWidget, 0, 0, 1, 3)
        self.uiQemuListLabel = QtGui.QLabel(self.uiQemuVMTabWidget)
        self.uiQemuListLabel.setObjectName(_fromUtf8("uiQemuListLabel"))
        self.gridLayout.addWidget(self.uiQemuListLabel, 1, 0, 1, 2)
        self.uiQemuListComboBox = QtGui.QComboBox(self.uiQemuVMTabWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiQemuListComboBox.sizePolicy().hasHeightForWidth())
        self.uiQemuListComboBox.setSizePolicy(sizePolicy)
        self.uiQemuListComboBox.setObjectName(_fromUtf8("uiQemuListComboBox"))
        self.gridLayout.addWidget(self.uiQemuListComboBox, 1, 2, 1, 1)
        self.uiNameLabel = QtGui.QLabel(self.uiQemuVMTabWidget)
        self.uiNameLabel.setObjectName(_fromUtf8("uiNameLabel"))
        self.gridLayout.addWidget(self.uiNameLabel, 2, 0, 1, 1)
        self.uiNameLineEdit = QtGui.QLineEdit(self.uiQemuVMTabWidget)
        self.uiNameLineEdit.setObjectName(_fromUtf8("uiNameLineEdit"))
        self.gridLayout.addWidget(self.uiNameLineEdit, 2, 2, 1, 1)
        self.uiDiskImageLabel = QtGui.QLabel(self.uiQemuVMTabWidget)
        self.uiDiskImageLabel.setObjectName(_fromUtf8("uiDiskImageLabel"))
        self.gridLayout.addWidget(self.uiDiskImageLabel, 3, 0, 1, 1)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.uiDiskImageLineEdit = QtGui.QLineEdit(self.uiQemuVMTabWidget)
        self.uiDiskImageLineEdit.setObjectName(_fromUtf8("uiDiskImageLineEdit"))
        self.horizontalLayout_6.addWidget(self.uiDiskImageLineEdit)
        self.uiDiskImageToolButton = QtGui.QToolButton(self.uiQemuVMTabWidget)
        self.uiDiskImageToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiDiskImageToolButton.setObjectName(_fromUtf8("uiDiskImageToolButton"))
        self.horizontalLayout_6.addWidget(self.uiDiskImageToolButton)
        self.gridLayout.addLayout(self.horizontalLayout_6, 3, 2, 1, 1)
        self.uiRamLabel = QtGui.QLabel(self.uiQemuVMTabWidget)
        self.uiRamLabel.setObjectName(_fromUtf8("uiRamLabel"))
        self.gridLayout.addWidget(self.uiRamLabel, 4, 0, 1, 1)
        self.uiAdaptersLabel = QtGui.QLabel(self.uiQemuVMTabWidget)
        self.uiAdaptersLabel.setObjectName(_fromUtf8("uiAdaptersLabel"))
        self.gridLayout.addWidget(self.uiAdaptersLabel, 5, 0, 1, 1)
        self.uiAdapterTypesLabel = QtGui.QLabel(self.uiQemuVMTabWidget)
        self.uiAdapterTypesLabel.setObjectName(_fromUtf8("uiAdapterTypesLabel"))
        self.gridLayout.addWidget(self.uiAdapterTypesLabel, 6, 0, 1, 1)
        self.uiQemuOptionsLabel = QtGui.QLabel(self.uiQemuVMTabWidget)
        self.uiQemuOptionsLabel.setObjectName(_fromUtf8("uiQemuOptionsLabel"))
        self.gridLayout.addWidget(self.uiQemuOptionsLabel, 7, 0, 1, 1)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.uiRefreshPushButton = QtGui.QPushButton(self.uiQemuVMTabWidget)
        self.uiRefreshPushButton.setObjectName(_fromUtf8("uiRefreshPushButton"))
        self.horizontalLayout_5.addWidget(self.uiRefreshPushButton)
        self.uiSaveQemuVMPushButton = QtGui.QPushButton(self.uiQemuVMTabWidget)
        self.uiSaveQemuVMPushButton.setObjectName(_fromUtf8("uiSaveQemuVMPushButton"))
        self.horizontalLayout_5.addWidget(self.uiSaveQemuVMPushButton)
        self.uiDeleteQemuVMPushButton = QtGui.QPushButton(self.uiQemuVMTabWidget)
        self.uiDeleteQemuVMPushButton.setEnabled(False)
        self.uiDeleteQemuVMPushButton.setObjectName(_fromUtf8("uiDeleteQemuVMPushButton"))
        self.horizontalLayout_5.addWidget(self.uiDeleteQemuVMPushButton)
        self.gridLayout.addLayout(self.horizontalLayout_5, 8, 0, 1, 3)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 9, 0, 1, 1)
        self.uiRamSpinBox = QtGui.QSpinBox(self.uiQemuVMTabWidget)
        self.uiRamSpinBox.setMinimum(32)
        self.uiRamSpinBox.setMaximum(65535)
        self.uiRamSpinBox.setProperty("value", 256)
        self.uiRamSpinBox.setObjectName(_fromUtf8("uiRamSpinBox"))
        self.gridLayout.addWidget(self.uiRamSpinBox, 4, 2, 1, 1)
        self.uiAdaptersSpinBox = QtGui.QSpinBox(self.uiQemuVMTabWidget)
        self.uiAdaptersSpinBox.setMinimum(1)
        self.uiAdaptersSpinBox.setMaximum(8)
        self.uiAdaptersSpinBox.setObjectName(_fromUtf8("uiAdaptersSpinBox"))
        self.gridLayout.addWidget(self.uiAdaptersSpinBox, 5, 2, 1, 1)
        self.uiAdapterTypesComboBox = QtGui.QComboBox(self.uiQemuVMTabWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiAdapterTypesComboBox.sizePolicy().hasHeightForWidth())
        self.uiAdapterTypesComboBox.setSizePolicy(sizePolicy)
        self.uiAdapterTypesComboBox.setObjectName(_fromUtf8("uiAdapterTypesComboBox"))
        self.gridLayout.addWidget(self.uiAdapterTypesComboBox, 6, 2, 1, 1)
        self.uiQemuOptionsLineEdit = QtGui.QLineEdit(self.uiQemuVMTabWidget)
        self.uiQemuOptionsLineEdit.setObjectName(_fromUtf8("uiQemuOptionsLineEdit"))
        self.gridLayout.addWidget(self.uiQemuOptionsLineEdit, 7, 2, 1, 1)
        self.uiTabWidget.addTab(self.uiQemuVMTabWidget, _fromUtf8(""))
        self.vboxlayout.addWidget(self.uiTabWidget)

        self.retranslateUi(QemuVMPreferencesPageWidget)
        self.uiTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(QemuVMPreferencesPageWidget)

    def retranslateUi(self, QemuVMPreferencesPageWidget):
        QemuVMPreferencesPageWidget.setWindowTitle(_translate("QemuVMPreferencesPageWidget", "QEMU VMs", None))
        self.uiQemuVMsTreeWidget.headerItem().setText(0, _translate("QemuVMPreferencesPageWidget", "VM", None))
        self.uiQemuVMsTreeWidget.headerItem().setText(1, _translate("QemuVMPreferencesPageWidget", "Server", None))
        self.uiQemuListLabel.setText(_translate("QemuVMPreferencesPageWidget", "Qemu binary:", None))
        self.uiNameLabel.setText(_translate("QemuVMPreferencesPageWidget", "VM name:", None))
        self.uiDiskImageLabel.setText(_translate("QemuVMPreferencesPageWidget", "Disk image:", None))
        self.uiDiskImageToolButton.setText(_translate("QemuVMPreferencesPageWidget", "...", None))
        self.uiRamLabel.setText(_translate("QemuVMPreferencesPageWidget", "RAM:", None))
        self.uiAdaptersLabel.setText(_translate("QemuVMPreferencesPageWidget", "Adapters:", None))
        self.uiAdapterTypesLabel.setText(_translate("QemuVMPreferencesPageWidget", "Type:", None))
        self.uiQemuOptionsLabel.setText(_translate("QemuVMPreferencesPageWidget", "Options:", None))
        self.uiRefreshPushButton.setText(_translate("QemuVMPreferencesPageWidget", "Refresh QEMU list", None))
        self.uiSaveQemuVMPushButton.setText(_translate("QemuVMPreferencesPageWidget", "Save", None))
        self.uiDeleteQemuVMPushButton.setText(_translate("QemuVMPreferencesPageWidget", "Delete", None))
        self.uiRamSpinBox.setSuffix(_translate("QemuVMPreferencesPageWidget", " MB", None))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiQemuVMTabWidget), _translate("QemuVMPreferencesPageWidget", "Generic VMs", None))

