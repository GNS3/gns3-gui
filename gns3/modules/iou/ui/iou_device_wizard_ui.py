# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/iou/ui/iou_device_wizard.ui'
#
# Created: Tue Oct  7 20:36:31 2014
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

class Ui_IOUDeviceWizard(object):
    def setupUi(self, IOUDeviceWizard):
        IOUDeviceWizard.setObjectName(_fromUtf8("IOUDeviceWizard"))
        IOUDeviceWizard.resize(514, 366)
        self.uiNameImageWizardPage = QtGui.QWizardPage()
        self.uiNameImageWizardPage.setObjectName(_fromUtf8("uiNameImageWizardPage"))
        self.gridLayout = QtGui.QGridLayout(self.uiNameImageWizardPage)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiNameLabel = QtGui.QLabel(self.uiNameImageWizardPage)
        self.uiNameLabel.setObjectName(_fromUtf8("uiNameLabel"))
        self.gridLayout.addWidget(self.uiNameLabel, 0, 0, 1, 1)
        self.uiNameLineEdit = QtGui.QLineEdit(self.uiNameImageWizardPage)
        self.uiNameLineEdit.setObjectName(_fromUtf8("uiNameLineEdit"))
        self.gridLayout.addWidget(self.uiNameLineEdit, 0, 1, 1, 1)
        self.uiIOUImageLabel = QtGui.QLabel(self.uiNameImageWizardPage)
        self.uiIOUImageLabel.setObjectName(_fromUtf8("uiIOUImageLabel"))
        self.gridLayout.addWidget(self.uiIOUImageLabel, 1, 0, 1, 1)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.uiIOUImageLineEdit = QtGui.QLineEdit(self.uiNameImageWizardPage)
        self.uiIOUImageLineEdit.setObjectName(_fromUtf8("uiIOUImageLineEdit"))
        self.horizontalLayout_5.addWidget(self.uiIOUImageLineEdit)
        self.uiIOUImageToolButton = QtGui.QToolButton(self.uiNameImageWizardPage)
        self.uiIOUImageToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiIOUImageToolButton.setObjectName(_fromUtf8("uiIOUImageToolButton"))
        self.horizontalLayout_5.addWidget(self.uiIOUImageToolButton)
        self.gridLayout.addLayout(self.horizontalLayout_5, 1, 1, 1, 1)
        self.uiTypeLabel = QtGui.QLabel(self.uiNameImageWizardPage)
        self.uiTypeLabel.setObjectName(_fromUtf8("uiTypeLabel"))
        self.gridLayout.addWidget(self.uiTypeLabel, 2, 0, 1, 1)
        self.uiTypeComboBox = QtGui.QComboBox(self.uiNameImageWizardPage)
        self.uiTypeComboBox.setObjectName(_fromUtf8("uiTypeComboBox"))
        self.gridLayout.addWidget(self.uiTypeComboBox, 2, 1, 1, 1)
        IOUDeviceWizard.addPage(self.uiNameImageWizardPage)

        self.retranslateUi(IOUDeviceWizard)
        QtCore.QMetaObject.connectSlotsByName(IOUDeviceWizard)
        IOUDeviceWizard.setTabOrder(self.uiNameLineEdit, self.uiTypeComboBox)

    def retranslateUi(self, IOUDeviceWizard):
        IOUDeviceWizard.setWindowTitle(_translate("IOUDeviceWizard", "New IOU device", None))
        self.uiNameImageWizardPage.setTitle(_translate("IOUDeviceWizard", "Name and image", None))
        self.uiNameImageWizardPage.setSubTitle(_translate("IOUDeviceWizard", "Please choose a descriptive name for the new IOU device and add an IOU image.", None))
        self.uiNameLabel.setText(_translate("IOUDeviceWizard", "Name:", None))
        self.uiIOUImageLabel.setText(_translate("IOUDeviceWizard", "IOU image:", None))
        self.uiIOUImageToolButton.setText(_translate("IOUDeviceWizard", "Browse...", None))
        self.uiTypeLabel.setText(_translate("IOUDeviceWizard", "Type:", None))

