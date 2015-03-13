# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/iou/ui/iou_device_wizard.ui'
#
# Created: Fri Mar 13 11:09:58 2015
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
        IOUDeviceWizard.setModal(True)
        self.uiServerWizardPage = QtGui.QWizardPage()
        self.uiServerWizardPage.setObjectName(_fromUtf8("uiServerWizardPage"))
        self.gridLayout_2 = QtGui.QGridLayout(self.uiServerWizardPage)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.uiServerTypeGroupBox = QtGui.QGroupBox(self.uiServerWizardPage)
        self.uiServerTypeGroupBox.setObjectName(_fromUtf8("uiServerTypeGroupBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.uiServerTypeGroupBox)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.uiRemoteRadioButton = QtGui.QRadioButton(self.uiServerTypeGroupBox)
        self.uiRemoteRadioButton.setChecked(True)
        self.uiRemoteRadioButton.setObjectName(_fromUtf8("uiRemoteRadioButton"))
        self.horizontalLayout.addWidget(self.uiRemoteRadioButton)
        self.uiCloudRadioButton = QtGui.QRadioButton(self.uiServerTypeGroupBox)
        self.uiCloudRadioButton.setObjectName(_fromUtf8("uiCloudRadioButton"))
        self.horizontalLayout.addWidget(self.uiCloudRadioButton)
        self.uiLocalRadioButton = QtGui.QRadioButton(self.uiServerTypeGroupBox)
        self.uiLocalRadioButton.setObjectName(_fromUtf8("uiLocalRadioButton"))
        self.horizontalLayout.addWidget(self.uiLocalRadioButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout_2.addWidget(self.uiServerTypeGroupBox, 0, 0, 1, 1)
        self.uiRemoteServersGroupBox = QtGui.QGroupBox(self.uiServerWizardPage)
        self.uiRemoteServersGroupBox.setObjectName(_fromUtf8("uiRemoteServersGroupBox"))
        self.gridLayout_7 = QtGui.QGridLayout(self.uiRemoteServersGroupBox)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.uiLoadBalanceCheckBox = QtGui.QCheckBox(self.uiRemoteServersGroupBox)
        self.uiLoadBalanceCheckBox.setChecked(True)
        self.uiLoadBalanceCheckBox.setObjectName(_fromUtf8("uiLoadBalanceCheckBox"))
        self.gridLayout_7.addWidget(self.uiLoadBalanceCheckBox, 0, 0, 1, 2)
        self.uiRemoteServersLabel = QtGui.QLabel(self.uiRemoteServersGroupBox)
        self.uiRemoteServersLabel.setObjectName(_fromUtf8("uiRemoteServersLabel"))
        self.gridLayout_7.addWidget(self.uiRemoteServersLabel, 1, 0, 1, 1)
        self.uiRemoteServersComboBox = QtGui.QComboBox(self.uiRemoteServersGroupBox)
        self.uiRemoteServersComboBox.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiRemoteServersComboBox.sizePolicy().hasHeightForWidth())
        self.uiRemoteServersComboBox.setSizePolicy(sizePolicy)
        self.uiRemoteServersComboBox.setObjectName(_fromUtf8("uiRemoteServersComboBox"))
        self.gridLayout_7.addWidget(self.uiRemoteServersComboBox, 1, 1, 1, 1)
        self.gridLayout_2.addWidget(self.uiRemoteServersGroupBox, 1, 0, 1, 1)
        IOUDeviceWizard.addPage(self.uiServerWizardPage)
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
        IOUDeviceWizard.setWindowTitle(_translate("IOUDeviceWizard", "New IOU device template", None))
        self.uiServerWizardPage.setTitle(_translate("IOUDeviceWizard", "Server", None))
        self.uiServerWizardPage.setSubTitle(_translate("IOUDeviceWizard", "Please choose a server type to run your new IOU device.", None))
        self.uiServerTypeGroupBox.setTitle(_translate("IOUDeviceWizard", "Server type", None))
        self.uiRemoteRadioButton.setText(_translate("IOUDeviceWizard", "Remote", None))
        self.uiCloudRadioButton.setText(_translate("IOUDeviceWizard", "Cloud", None))
        self.uiLocalRadioButton.setText(_translate("IOUDeviceWizard", "Local", None))
        self.uiRemoteServersGroupBox.setTitle(_translate("IOUDeviceWizard", "Remote servers", None))
        self.uiLoadBalanceCheckBox.setText(_translate("IOUDeviceWizard", "Load balance across all available remote servers", None))
        self.uiRemoteServersLabel.setText(_translate("IOUDeviceWizard", "Run on server:", None))
        self.uiNameImageWizardPage.setTitle(_translate("IOUDeviceWizard", "Name and image", None))
        self.uiNameImageWizardPage.setSubTitle(_translate("IOUDeviceWizard", "Please choose a descriptive name for the new IOU device and add an IOU image.", None))
        self.uiNameLabel.setText(_translate("IOUDeviceWizard", "Name:", None))
        self.uiIOUImageLabel.setText(_translate("IOUDeviceWizard", "IOU image:", None))
        self.uiIOUImageToolButton.setText(_translate("IOUDeviceWizard", "&Browse...", None))
        self.uiTypeLabel.setText(_translate("IOUDeviceWizard", "Type:", None))

