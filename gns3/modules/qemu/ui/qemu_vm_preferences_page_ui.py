# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/qemu/ui/qemu_vm_preferences_page.ui'
#
# Created: Wed Mar 11 22:03:56 2015
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
        QemuVMPreferencesPageWidget.resize(511, 543)
        self.gridLayout = QtGui.QGridLayout(QemuVMPreferencesPageWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiQemuVMsTreeWidget = QtGui.QTreeWidget(QemuVMPreferencesPageWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiQemuVMsTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiQemuVMsTreeWidget.setSizePolicy(sizePolicy)
        self.uiQemuVMsTreeWidget.setMaximumSize(QtCore.QSize(160, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.uiQemuVMsTreeWidget.setFont(font)
        self.uiQemuVMsTreeWidget.setIconSize(QtCore.QSize(32, 32))
        self.uiQemuVMsTreeWidget.setRootIsDecorated(False)
        self.uiQemuVMsTreeWidget.setObjectName(_fromUtf8("uiQemuVMsTreeWidget"))
        self.uiQemuVMsTreeWidget.headerItem().setText(0, _fromUtf8("1"))
        self.uiQemuVMsTreeWidget.header().setVisible(False)
        self.gridLayout.addWidget(self.uiQemuVMsTreeWidget, 0, 0, 2, 1)
        self.uiQemuVMInfoTreeWidget = QtGui.QTreeWidget(QemuVMPreferencesPageWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiQemuVMInfoTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiQemuVMInfoTreeWidget.setSizePolicy(sizePolicy)
        self.uiQemuVMInfoTreeWidget.setIndentation(10)
        self.uiQemuVMInfoTreeWidget.setAllColumnsShowFocus(True)
        self.uiQemuVMInfoTreeWidget.setObjectName(_fromUtf8("uiQemuVMInfoTreeWidget"))
        self.uiQemuVMInfoTreeWidget.header().setVisible(False)
        self.gridLayout.addWidget(self.uiQemuVMInfoTreeWidget, 0, 1, 1, 1)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.uiNewQemuVMPushButton = QtGui.QPushButton(QemuVMPreferencesPageWidget)
        self.uiNewQemuVMPushButton.setObjectName(_fromUtf8("uiNewQemuVMPushButton"))
        self.horizontalLayout_5.addWidget(self.uiNewQemuVMPushButton)
        self.uiEditQemuVMPushButton = QtGui.QPushButton(QemuVMPreferencesPageWidget)
        self.uiEditQemuVMPushButton.setEnabled(False)
        self.uiEditQemuVMPushButton.setObjectName(_fromUtf8("uiEditQemuVMPushButton"))
        self.horizontalLayout_5.addWidget(self.uiEditQemuVMPushButton)
        self.uiDeleteQemuVMPushButton = QtGui.QPushButton(QemuVMPreferencesPageWidget)
        self.uiDeleteQemuVMPushButton.setEnabled(False)
        self.uiDeleteQemuVMPushButton.setObjectName(_fromUtf8("uiDeleteQemuVMPushButton"))
        self.horizontalLayout_5.addWidget(self.uiDeleteQemuVMPushButton)
        self.gridLayout.addLayout(self.horizontalLayout_5, 1, 1, 1, 1)

        self.retranslateUi(QemuVMPreferencesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(QemuVMPreferencesPageWidget)
        QemuVMPreferencesPageWidget.setTabOrder(self.uiNewQemuVMPushButton, self.uiDeleteQemuVMPushButton)

    def retranslateUi(self, QemuVMPreferencesPageWidget):
        QemuVMPreferencesPageWidget.setWindowTitle(_translate("QemuVMPreferencesPageWidget", "QEMU VMs", None))
        QemuVMPreferencesPageWidget.setAccessibleName(_translate("QemuVMPreferencesPageWidget", "QEMU VM templates", None))
        self.uiQemuVMInfoTreeWidget.headerItem().setText(0, _translate("QemuVMPreferencesPageWidget", "1", None))
        self.uiQemuVMInfoTreeWidget.headerItem().setText(1, _translate("QemuVMPreferencesPageWidget", "2", None))
        self.uiNewQemuVMPushButton.setText(_translate("QemuVMPreferencesPageWidget", "&New", None))
        self.uiEditQemuVMPushButton.setText(_translate("QemuVMPreferencesPageWidget", "&Edit", None))
        self.uiDeleteQemuVMPushButton.setText(_translate("QemuVMPreferencesPageWidget", "&Delete", None))

