# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/virtualbox/ui/virtualbox_vm_preferences_page.ui'
#
# Created: Wed Mar 11 22:04:56 2015
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

class Ui_VirtualBoxVMPreferencesPageWidget(object):
    def setupUi(self, VirtualBoxVMPreferencesPageWidget):
        VirtualBoxVMPreferencesPageWidget.setObjectName(_fromUtf8("VirtualBoxVMPreferencesPageWidget"))
        VirtualBoxVMPreferencesPageWidget.resize(499, 546)
        VirtualBoxVMPreferencesPageWidget.setAccessibleDescription(_fromUtf8(""))
        self.gridLayout = QtGui.QGridLayout(VirtualBoxVMPreferencesPageWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.uiNewVirtualBoxVMPushButton = QtGui.QPushButton(VirtualBoxVMPreferencesPageWidget)
        self.uiNewVirtualBoxVMPushButton.setObjectName(_fromUtf8("uiNewVirtualBoxVMPushButton"))
        self.horizontalLayout_5.addWidget(self.uiNewVirtualBoxVMPushButton)
        self.uiEditVirtualBoxVMPushButton = QtGui.QPushButton(VirtualBoxVMPreferencesPageWidget)
        self.uiEditVirtualBoxVMPushButton.setEnabled(False)
        self.uiEditVirtualBoxVMPushButton.setObjectName(_fromUtf8("uiEditVirtualBoxVMPushButton"))
        self.horizontalLayout_5.addWidget(self.uiEditVirtualBoxVMPushButton)
        self.uiDeleteVirtualBoxVMPushButton = QtGui.QPushButton(VirtualBoxVMPreferencesPageWidget)
        self.uiDeleteVirtualBoxVMPushButton.setEnabled(False)
        self.uiDeleteVirtualBoxVMPushButton.setObjectName(_fromUtf8("uiDeleteVirtualBoxVMPushButton"))
        self.horizontalLayout_5.addWidget(self.uiDeleteVirtualBoxVMPushButton)
        self.gridLayout.addLayout(self.horizontalLayout_5, 1, 1, 1, 1)
        self.uiVirtualBoxVMInfoTreeWidget = QtGui.QTreeWidget(VirtualBoxVMPreferencesPageWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVirtualBoxVMInfoTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiVirtualBoxVMInfoTreeWidget.setSizePolicy(sizePolicy)
        self.uiVirtualBoxVMInfoTreeWidget.setIndentation(10)
        self.uiVirtualBoxVMInfoTreeWidget.setAllColumnsShowFocus(True)
        self.uiVirtualBoxVMInfoTreeWidget.setObjectName(_fromUtf8("uiVirtualBoxVMInfoTreeWidget"))
        self.uiVirtualBoxVMInfoTreeWidget.header().setVisible(False)
        self.gridLayout.addWidget(self.uiVirtualBoxVMInfoTreeWidget, 0, 1, 1, 1)
        self.uiVirtualBoxVMsTreeWidget = QtGui.QTreeWidget(VirtualBoxVMPreferencesPageWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVirtualBoxVMsTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiVirtualBoxVMsTreeWidget.setSizePolicy(sizePolicy)
        self.uiVirtualBoxVMsTreeWidget.setMaximumSize(QtCore.QSize(160, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.uiVirtualBoxVMsTreeWidget.setFont(font)
        self.uiVirtualBoxVMsTreeWidget.setIconSize(QtCore.QSize(32, 32))
        self.uiVirtualBoxVMsTreeWidget.setRootIsDecorated(False)
        self.uiVirtualBoxVMsTreeWidget.setObjectName(_fromUtf8("uiVirtualBoxVMsTreeWidget"))
        self.uiVirtualBoxVMsTreeWidget.headerItem().setText(0, _fromUtf8("1"))
        self.uiVirtualBoxVMsTreeWidget.header().setVisible(False)
        self.gridLayout.addWidget(self.uiVirtualBoxVMsTreeWidget, 0, 0, 2, 1)

        self.retranslateUi(VirtualBoxVMPreferencesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(VirtualBoxVMPreferencesPageWidget)

    def retranslateUi(self, VirtualBoxVMPreferencesPageWidget):
        VirtualBoxVMPreferencesPageWidget.setWindowTitle(_translate("VirtualBoxVMPreferencesPageWidget", "VirtualBox VMs", None))
        VirtualBoxVMPreferencesPageWidget.setAccessibleName(_translate("VirtualBoxVMPreferencesPageWidget", "VirtualBox VM templates", None))
        self.uiNewVirtualBoxVMPushButton.setText(_translate("VirtualBoxVMPreferencesPageWidget", "&New", None))
        self.uiEditVirtualBoxVMPushButton.setText(_translate("VirtualBoxVMPreferencesPageWidget", "&Edit", None))
        self.uiDeleteVirtualBoxVMPushButton.setText(_translate("VirtualBoxVMPreferencesPageWidget", "&Delete", None))
        self.uiVirtualBoxVMInfoTreeWidget.headerItem().setText(0, _translate("VirtualBoxVMPreferencesPageWidget", "1", None))
        self.uiVirtualBoxVMInfoTreeWidget.headerItem().setText(1, _translate("VirtualBoxVMPreferencesPageWidget", "2", None))

