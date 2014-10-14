# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/virtualbox/ui/virtualbox_vm_wizard.ui'
#
# Created: Tue Oct 14 17:01:29 2014
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
        VirtualBoxVMWizard.setWindowModality(QtCore.Qt.WindowModal)
        VirtualBoxVMWizard.resize(514, 367)
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
        VirtualBoxVMWizard.addPage(self.uiVirtualBoxWizardPage)

        self.retranslateUi(VirtualBoxVMWizard)
        QtCore.QMetaObject.connectSlotsByName(VirtualBoxVMWizard)

    def retranslateUi(self, VirtualBoxVMWizard):
        VirtualBoxVMWizard.setWindowTitle(_translate("VirtualBoxVMWizard", "New VirtualBox VM", None))
        self.uiVirtualBoxWizardPage.setTitle(_translate("VirtualBoxVMWizard", "VirtualBox Virtual Machine", None))
        self.uiVirtualBoxWizardPage.setSubTitle(_translate("VirtualBoxVMWizard", "Please choose a VirtualBox virtual machine from the list.", None))
        self.uiVMListLabel.setText(_translate("VirtualBoxVMWizard", "VM list:", None))

