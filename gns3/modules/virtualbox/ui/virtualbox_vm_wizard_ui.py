# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/virtualbox/ui/virtualbox_vm_wizard.ui'
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

class Ui_VirtualBoxVMWizard(object):
    def setupUi(self, VirtualBoxVMWizard):
        VirtualBoxVMWizard.setObjectName(_fromUtf8("VirtualBoxVMWizard"))
        VirtualBoxVMWizard.resize(514, 367)
        VirtualBoxVMWizard.setModal(True)
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
        self.gridLayout_8 = QtGui.QGridLayout(self.uiRemoteServersGroupBox)
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.uiRemoteServersComboBox = QtGui.QComboBox(self.uiRemoteServersGroupBox)
        self.uiRemoteServersComboBox.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiRemoteServersComboBox.sizePolicy().hasHeightForWidth())
        self.uiRemoteServersComboBox.setSizePolicy(sizePolicy)
        self.uiRemoteServersComboBox.setObjectName(_fromUtf8("uiRemoteServersComboBox"))
        self.gridLayout_8.addWidget(self.uiRemoteServersComboBox, 0, 1, 1, 1)
        self.uiRemoteServersLabel = QtGui.QLabel(self.uiRemoteServersGroupBox)
        self.uiRemoteServersLabel.setObjectName(_fromUtf8("uiRemoteServersLabel"))
        self.gridLayout_8.addWidget(self.uiRemoteServersLabel, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.uiRemoteServersGroupBox, 1, 0, 1, 1)
        VirtualBoxVMWizard.addPage(self.uiServerWizardPage)
        self.uiVirtualBoxWizardPage = QtGui.QWizardPage()
        self.uiVirtualBoxWizardPage.setObjectName(_fromUtf8("uiVirtualBoxWizardPage"))
        self.gridLayout = QtGui.QGridLayout(self.uiVirtualBoxWizardPage)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiVMListLabel = QtGui.QLabel(self.uiVirtualBoxWizardPage)
        self.uiVMListLabel.setObjectName(_fromUtf8("uiVMListLabel"))
        self.gridLayout.addWidget(self.uiVMListLabel, 0, 0, 1, 1)
        self.uiVMListComboBox = QtGui.QComboBox(self.uiVirtualBoxWizardPage)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVMListComboBox.sizePolicy().hasHeightForWidth())
        self.uiVMListComboBox.setSizePolicy(sizePolicy)
        self.uiVMListComboBox.setObjectName(_fromUtf8("uiVMListComboBox"))
        self.gridLayout.addWidget(self.uiVMListComboBox, 0, 1, 1, 1)
        self.uiBaseVMCheckBox = QtGui.QCheckBox(self.uiVirtualBoxWizardPage)
        self.uiBaseVMCheckBox.setEnabled(True)
        self.uiBaseVMCheckBox.setObjectName(_fromUtf8("uiBaseVMCheckBox"))
        self.gridLayout.addWidget(self.uiBaseVMCheckBox, 1, 0, 1, 2)
        VirtualBoxVMWizard.addPage(self.uiVirtualBoxWizardPage)

        self.retranslateUi(VirtualBoxVMWizard)
        QtCore.QMetaObject.connectSlotsByName(VirtualBoxVMWizard)

    def retranslateUi(self, VirtualBoxVMWizard):
        VirtualBoxVMWizard.setWindowTitle(_translate("VirtualBoxVMWizard", "New VirtualBox VM template", None))
        self.uiServerWizardPage.setTitle(_translate("VirtualBoxVMWizard", "Server", None))
        self.uiServerWizardPage.setSubTitle(_translate("VirtualBoxVMWizard", "Please choose a server type to run your new VirtualBox VM.", None))
        self.uiServerTypeGroupBox.setTitle(_translate("VirtualBoxVMWizard", "Server type", None))
        self.uiRemoteRadioButton.setText(_translate("VirtualBoxVMWizard", "Remote", None))
        self.uiCloudRadioButton.setText(_translate("VirtualBoxVMWizard", "Cloud", None))
        self.uiLocalRadioButton.setText(_translate("VirtualBoxVMWizard", "Local", None))
        self.uiRemoteServersGroupBox.setTitle(_translate("VirtualBoxVMWizard", "Remote servers", None))
        self.uiRemoteServersLabel.setText(_translate("VirtualBoxVMWizard", "Run on server:", None))
        self.uiVirtualBoxWizardPage.setTitle(_translate("VirtualBoxVMWizard", "VirtualBox Virtual Machine", None))
        self.uiVirtualBoxWizardPage.setSubTitle(_translate("VirtualBoxVMWizard", "Please choose a VirtualBox virtual machine from the list.", None))
        self.uiVMListLabel.setText(_translate("VirtualBoxVMWizard", "VM list:", None))
        self.uiBaseVMCheckBox.setText(_translate("VirtualBoxVMWizard", "Use as a linked base VM (experimental)", None))

