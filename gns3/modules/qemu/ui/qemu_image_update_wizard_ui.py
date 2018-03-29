# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/qemu/ui/qemu_image_update_wizard.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_QemuImageUpdateWizard(object):
    def setupUi(self, QemuImageUpdateWizard):
        QemuImageUpdateWizard.setObjectName("QemuImageUpdateWizard")
        QemuImageUpdateWizard.resize(662, 493)
        QemuImageUpdateWizard.setModal(True)
        QemuImageUpdateWizard.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        self.uiBinaryWizardPage = QtWidgets.QWizardPage()
        self.uiBinaryWizardPage.setObjectName("uiBinaryWizardPage")
        self.gridLayout = QtWidgets.QGridLayout(self.uiBinaryWizardPage)
        self.gridLayout.setObjectName("gridLayout")
        self.uiBinaryLabel = QtWidgets.QLabel(self.uiBinaryWizardPage)
        self.uiBinaryLabel.setObjectName("uiBinaryLabel")
        self.gridLayout.addWidget(self.uiBinaryLabel, 0, 0, 1, 1)
        self.uiExtendLabel = QtWidgets.QLabel(self.uiBinaryWizardPage)
        self.uiExtendLabel.setObjectName("uiExtendLabel")
        self.gridLayout.addWidget(self.uiExtendLabel, 1, 0, 1, 2)
        self.uiExtendSpinBox = QtWidgets.QSpinBox(self.uiBinaryWizardPage)
        self.uiExtendSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.UpDownArrows)
        self.uiExtendSpinBox.setMinimum(0)
        self.uiExtendSpinBox.setMaximum(2000000)
        self.uiExtendSpinBox.setSingleStep(1000)
        self.uiExtendSpinBox.setProperty("value", 10000)
        self.uiExtendSpinBox.setProperty("showGroupSeparator", True)
        self.uiExtendSpinBox.setObjectName("uiExtendSpinBox")
        self.gridLayout.addWidget(self.uiExtendSpinBox, 1, 2, 1, 1)
        self.uiBinaryComboBox = QtWidgets.QComboBox(self.uiBinaryWizardPage)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiBinaryComboBox.sizePolicy().hasHeightForWidth())
        self.uiBinaryComboBox.setSizePolicy(sizePolicy)
        self.uiBinaryComboBox.setObjectName("uiBinaryComboBox")
        self.gridLayout.addWidget(self.uiBinaryComboBox, 0, 2, 1, 1)
        QemuImageUpdateWizard.addPage(self.uiBinaryWizardPage)

        self.retranslateUi(QemuImageUpdateWizard)
        QtCore.QMetaObject.connectSlotsByName(QemuImageUpdateWizard)

    def retranslateUi(self, QemuImageUpdateWizard):
        _translate = QtCore.QCoreApplication.translate
        QemuImageUpdateWizard.setWindowTitle(_translate("QemuImageUpdateWizard", "Qemu image update"))
        self.uiBinaryWizardPage.setTitle(_translate("QemuImageUpdateWizard", "Binary and resize"))
        self.uiBinaryWizardPage.setSubTitle(_translate("QemuImageUpdateWizard", "Please select a qemu-img binary and the number of MiB to extend the disk size"))
        self.uiBinaryLabel.setText(_translate("QemuImageUpdateWizard", "Qemu-img binary:"))
        self.uiExtendLabel.setText(_translate("QemuImageUpdateWizard", "Extend disk size by :"))
        self.uiExtendSpinBox.setSuffix(_translate("QemuImageUpdateWizard", " MiB"))
        self.uiExtendSpinBox.setPrefix(_translate("QemuImageUpdateWizard", "+"))

