# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/qemu/ui/qemu_vm_configuration_page.ui'
#
# Created: Wed Sep 17 15:18:24 2014
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

class Ui_QemuVMConfigPageWidget(object):
    def setupUi(self, QemuVMConfigPageWidget):
        QemuVMConfigPageWidget.setObjectName(_fromUtf8("QemuVMConfigPageWidget"))
        QemuVMConfigPageWidget.resize(360, 401)
        self.gridLayout = QtGui.QGridLayout(QemuVMConfigPageWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiQemuListLabel = QtGui.QLabel(QemuVMConfigPageWidget)
        self.uiQemuListLabel.setObjectName(_fromUtf8("uiQemuListLabel"))
        self.gridLayout.addWidget(self.uiQemuListLabel, 0, 0, 1, 1)
        self.uiQemuListComboBox = QtGui.QComboBox(QemuVMConfigPageWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiQemuListComboBox.sizePolicy().hasHeightForWidth())
        self.uiQemuListComboBox.setSizePolicy(sizePolicy)
        self.uiQemuListComboBox.setObjectName(_fromUtf8("uiQemuListComboBox"))
        self.gridLayout.addWidget(self.uiQemuListComboBox, 0, 1, 1, 1)
        self.uiNameLabel = QtGui.QLabel(QemuVMConfigPageWidget)
        self.uiNameLabel.setObjectName(_fromUtf8("uiNameLabel"))
        self.gridLayout.addWidget(self.uiNameLabel, 1, 0, 1, 1)
        self.uiNameLineEdit = QtGui.QLineEdit(QemuVMConfigPageWidget)
        self.uiNameLineEdit.setObjectName(_fromUtf8("uiNameLineEdit"))
        self.gridLayout.addWidget(self.uiNameLineEdit, 1, 1, 1, 1)
        self.uiConsolePortLabel = QtGui.QLabel(QemuVMConfigPageWidget)
        self.uiConsolePortLabel.setObjectName(_fromUtf8("uiConsolePortLabel"))
        self.gridLayout.addWidget(self.uiConsolePortLabel, 2, 0, 1, 1)
        self.uiConsolePortSpinBox = QtGui.QSpinBox(QemuVMConfigPageWidget)
        self.uiConsolePortSpinBox.setMaximum(65535)
        self.uiConsolePortSpinBox.setObjectName(_fromUtf8("uiConsolePortSpinBox"))
        self.gridLayout.addWidget(self.uiConsolePortSpinBox, 2, 1, 1, 1)
        self.uiDiskImageLabel = QtGui.QLabel(QemuVMConfigPageWidget)
        self.uiDiskImageLabel.setObjectName(_fromUtf8("uiDiskImageLabel"))
        self.gridLayout.addWidget(self.uiDiskImageLabel, 3, 0, 1, 1)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.uiDiskImageLineEdit = QtGui.QLineEdit(QemuVMConfigPageWidget)
        self.uiDiskImageLineEdit.setObjectName(_fromUtf8("uiDiskImageLineEdit"))
        self.horizontalLayout_6.addWidget(self.uiDiskImageLineEdit)
        self.uiDiskImageToolButton = QtGui.QToolButton(QemuVMConfigPageWidget)
        self.uiDiskImageToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiDiskImageToolButton.setObjectName(_fromUtf8("uiDiskImageToolButton"))
        self.horizontalLayout_6.addWidget(self.uiDiskImageToolButton)
        self.gridLayout.addLayout(self.horizontalLayout_6, 3, 1, 1, 1)
        self.uiRamLabel = QtGui.QLabel(QemuVMConfigPageWidget)
        self.uiRamLabel.setObjectName(_fromUtf8("uiRamLabel"))
        self.gridLayout.addWidget(self.uiRamLabel, 4, 0, 1, 1)
        self.uiRamSpinBox = QtGui.QSpinBox(QemuVMConfigPageWidget)
        self.uiRamSpinBox.setMinimum(32)
        self.uiRamSpinBox.setMaximum(65535)
        self.uiRamSpinBox.setProperty("value", 256)
        self.uiRamSpinBox.setObjectName(_fromUtf8("uiRamSpinBox"))
        self.gridLayout.addWidget(self.uiRamSpinBox, 4, 1, 1, 1)
        self.uiAdaptersLabel = QtGui.QLabel(QemuVMConfigPageWidget)
        self.uiAdaptersLabel.setObjectName(_fromUtf8("uiAdaptersLabel"))
        self.gridLayout.addWidget(self.uiAdaptersLabel, 5, 0, 1, 1)
        self.uiAdaptersSpinBox = QtGui.QSpinBox(QemuVMConfigPageWidget)
        self.uiAdaptersSpinBox.setMinimum(1)
        self.uiAdaptersSpinBox.setMaximum(8)
        self.uiAdaptersSpinBox.setObjectName(_fromUtf8("uiAdaptersSpinBox"))
        self.gridLayout.addWidget(self.uiAdaptersSpinBox, 5, 1, 1, 1)
        self.uiAdapterTypesLabel = QtGui.QLabel(QemuVMConfigPageWidget)
        self.uiAdapterTypesLabel.setObjectName(_fromUtf8("uiAdapterTypesLabel"))
        self.gridLayout.addWidget(self.uiAdapterTypesLabel, 6, 0, 1, 1)
        self.uiAdapterTypesComboBox = QtGui.QComboBox(QemuVMConfigPageWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiAdapterTypesComboBox.sizePolicy().hasHeightForWidth())
        self.uiAdapterTypesComboBox.setSizePolicy(sizePolicy)
        self.uiAdapterTypesComboBox.setObjectName(_fromUtf8("uiAdapterTypesComboBox"))
        self.gridLayout.addWidget(self.uiAdapterTypesComboBox, 6, 1, 1, 1)
        self.uiQemuOptionsLabel = QtGui.QLabel(QemuVMConfigPageWidget)
        self.uiQemuOptionsLabel.setObjectName(_fromUtf8("uiQemuOptionsLabel"))
        self.gridLayout.addWidget(self.uiQemuOptionsLabel, 7, 0, 1, 1)
        self.uiQemuOptionsLineEdit = QtGui.QLineEdit(QemuVMConfigPageWidget)
        self.uiQemuOptionsLineEdit.setObjectName(_fromUtf8("uiQemuOptionsLineEdit"))
        self.gridLayout.addWidget(self.uiQemuOptionsLineEdit, 7, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(263, 212, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 8, 0, 1, 2)

        self.retranslateUi(QemuVMConfigPageWidget)
        QtCore.QMetaObject.connectSlotsByName(QemuVMConfigPageWidget)

    def retranslateUi(self, QemuVMConfigPageWidget):
        QemuVMConfigPageWidget.setWindowTitle(_translate("QemuVMConfigPageWidget", "QEMU VM configuration", None))
        self.uiQemuListLabel.setText(_translate("QemuVMConfigPageWidget", "Qemu binary:", None))
        self.uiNameLabel.setText(_translate("QemuVMConfigPageWidget", "VM name:", None))
        self.uiConsolePortLabel.setText(_translate("QemuVMConfigPageWidget", "Console port:", None))
        self.uiDiskImageLabel.setText(_translate("QemuVMConfigPageWidget", "Disk image:", None))
        self.uiDiskImageToolButton.setText(_translate("QemuVMConfigPageWidget", "...", None))
        self.uiRamLabel.setText(_translate("QemuVMConfigPageWidget", "RAM:", None))
        self.uiRamSpinBox.setSuffix(_translate("QemuVMConfigPageWidget", " MB", None))
        self.uiAdaptersLabel.setText(_translate("QemuVMConfigPageWidget", "Adapters:", None))
        self.uiAdapterTypesLabel.setText(_translate("QemuVMConfigPageWidget", "Type:", None))
        self.uiQemuOptionsLabel.setText(_translate("QemuVMConfigPageWidget", "Options:", None))

