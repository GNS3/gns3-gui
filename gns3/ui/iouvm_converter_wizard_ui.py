# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/ui/iouvm_converter_wizard.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_IOUVMConverterWizard(object):
    def setupUi(self, IOUVMConverterWizard):
        IOUVMConverterWizard.setObjectName("IOUVMConverterWizard")
        IOUVMConverterWizard.resize(649, 377)
        IOUVMConverterWizard.setOptions(QtWidgets.QWizard.NoCancelButton|QtWidgets.QWizard.NoDefaultButton)
        self.uiWizardWelcomePage = QtWidgets.QWizardPage()
        self.uiWizardWelcomePage.setObjectName("uiWizardWelcomePage")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.uiWizardWelcomePage)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(self.uiWizardWelcomePage)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        IOUVMConverterWizard.addPage(self.uiWizardWelcomePage)
        self.uiWizardStartConfigureGNS3 = QtWidgets.QWizardPage()
        self.uiWizardStartConfigureGNS3.setObjectName("uiWizardStartConfigureGNS3")
        self.verticalLayout_13 = QtWidgets.QVBoxLayout(self.uiWizardStartConfigureGNS3)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.label_14 = QtWidgets.QLabel(self.uiWizardStartConfigureGNS3)
        self.label_14.setObjectName("label_14")
        self.verticalLayout_13.addWidget(self.label_14)
        IOUVMConverterWizard.addPage(self.uiWizardStartConfigureGNS3)
        self.uiWizardVirtualBoxNatPage = QtWidgets.QWizardPage()
        self.uiWizardVirtualBoxNatPage.setObjectName("uiWizardVirtualBoxNatPage")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.uiWizardVirtualBoxNatPage)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.uiWizardVirtualBoxNatPage)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_3.addWidget(self.label_2)
        IOUVMConverterWizard.addPage(self.uiWizardVirtualBoxNatPage)
        self.uiWizardUpdateIOUVM = QtWidgets.QWizardPage()
        self.uiWizardUpdateIOUVM.setObjectName("uiWizardUpdateIOUVM")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.uiWizardUpdateIOUVM)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_3 = QtWidgets.QLabel(self.uiWizardUpdateIOUVM)
        self.label_3.setTextFormat(QtCore.Qt.RichText)
        self.label_3.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_4.addWidget(self.label_3)
        IOUVMConverterWizard.addPage(self.uiWizardUpdateIOUVM)
        self.uiWizardPageVirtualBoxHostOnly = QtWidgets.QWizardPage()
        self.uiWizardPageVirtualBoxHostOnly.setObjectName("uiWizardPageVirtualBoxHostOnly")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.uiWizardPageVirtualBoxHostOnly)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_4 = QtWidgets.QLabel(self.uiWizardPageVirtualBoxHostOnly)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_5.addWidget(self.label_4)
        IOUVMConverterWizard.addPage(self.uiWizardPageVirtualBoxHostOnly)
        self.uiWizardDownloadBackups = QtWidgets.QWizardPage()
        self.uiWizardDownloadBackups.setObjectName("uiWizardDownloadBackups")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.uiWizardDownloadBackups)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.label_10 = QtWidgets.QLabel(self.uiWizardDownloadBackups)
        self.label_10.setObjectName("label_10")
        self.verticalLayout_10.addWidget(self.label_10)
        IOUVMConverterWizard.addPage(self.uiWizardDownloadBackups)
        self.uiWizardRestoreBackups = QtWidgets.QWizardPage()
        self.uiWizardRestoreBackups.setObjectName("uiWizardRestoreBackups")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.uiWizardRestoreBackups)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.label_11 = QtWidgets.QLabel(self.uiWizardRestoreBackups)
        self.label_11.setWordWrap(True)
        self.label_11.setObjectName("label_11")
        self.verticalLayout_11.addWidget(self.label_11)
        IOUVMConverterWizard.addPage(self.uiWizardRestoreBackups)
        self.uiWizardPageBackup = QtWidgets.QWizardPage()
        self.uiWizardPageBackup.setObjectName("uiWizardPageBackup")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.uiWizardPageBackup)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_5 = QtWidgets.QLabel(self.uiWizardPageBackup)
        font = QtGui.QFont()
        font.setPointSize(43)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_6.addWidget(self.label_5)
        IOUVMConverterWizard.addPage(self.uiWizardPageBackup)
        self.uiWizardPageIOURCCheck = QtWidgets.QWizardPage()
        self.uiWizardPageIOURCCheck.setObjectName("uiWizardPageIOURCCheck")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.uiWizardPageIOURCCheck)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_7 = QtWidgets.QLabel(self.uiWizardPageIOURCCheck)
        self.label_7.setWordWrap(True)
        self.label_7.setObjectName("label_7")
        self.verticalLayout.addWidget(self.label_7)
        IOUVMConverterWizard.addPage(self.uiWizardPageIOURCCheck)
        self.uiWizardUpdateConfiguration = QtWidgets.QWizardPage()
        self.uiWizardUpdateConfiguration.setObjectName("uiWizardUpdateConfiguration")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.uiWizardUpdateConfiguration)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.label_12 = QtWidgets.QLabel(self.uiWizardUpdateConfiguration)
        self.label_12.setWordWrap(True)
        self.label_12.setObjectName("label_12")
        self.verticalLayout_12.addWidget(self.label_12)
        IOUVMConverterWizard.addPage(self.uiWizardUpdateConfiguration)
        self.uiWizardPagePatchTopologies = QtWidgets.QWizardPage()
        self.uiWizardPagePatchTopologies.setObjectName("uiWizardPagePatchTopologies")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.uiWizardPagePatchTopologies)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.label_6 = QtWidgets.QLabel(self.uiWizardPagePatchTopologies)
        self.label_6.setWordWrap(True)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_7.addWidget(self.label_6)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.uiLineEditTopologiesPath = QtWidgets.QLineEdit(self.uiWizardPagePatchTopologies)
        self.uiLineEditTopologiesPath.setObjectName("uiLineEditTopologiesPath")
        self.horizontalLayout_2.addWidget(self.uiLineEditTopologiesPath)
        self.uiPushButtonBrowse = QtWidgets.QPushButton(self.uiWizardPagePatchTopologies)
        self.uiPushButtonBrowse.setObjectName("uiPushButtonBrowse")
        self.horizontalLayout_2.addWidget(self.uiPushButtonBrowse)
        self.verticalLayout_7.addLayout(self.horizontalLayout_2)
        IOUVMConverterWizard.addPage(self.uiWizardPagePatchTopologies)
        self.uiWizardCongratulation = QtWidgets.QWizardPage()
        self.uiWizardCongratulation.setObjectName("uiWizardCongratulation")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.uiWizardCongratulation)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.label_8 = QtWidgets.QLabel(self.uiWizardCongratulation)
        self.label_8.setWordWrap(True)
        self.label_8.setObjectName("label_8")
        self.verticalLayout_8.addWidget(self.label_8)
        IOUVMConverterWizard.addPage(self.uiWizardCongratulation)

        self.retranslateUi(IOUVMConverterWizard)
        QtCore.QMetaObject.connectSlotsByName(IOUVMConverterWizard)

    def retranslateUi(self, IOUVMConverterWizard):
        _translate = QtCore.QCoreApplication.translate
        IOUVMConverterWizard.setWindowTitle(_translate("IOUVMConverterWizard", "GNS3 IOU Converter"))
        self.label.setText(_translate("IOUVMConverterWizard", "<h1>Welcome to the IOUVM converter</h1>\n"
"<p>This Wizard will help you to convert the IOUVM to the new GNS3 VM</p>\n"
"<p>The GNS3 VM has a self update system allowing you to easily upgrade between version of the GNS3 VM without manual operations.</p>"))
        self.label_14.setText(_translate("IOUVMConverterWizard", "<h1>Start GNS3</h1>\n"
"<ul>\n"
"<li>Start GNS3 >= 1.4</li>\n"
"<li>Configure the GNS3 VM via preferences or the initial wizard</li>\n"
"<li>Exit all instance of GNS3</li>\n"
"</ul>"))
        self.label_2.setText(_translate("IOUVMConverterWizard", "<h1>Setup NAT</h1>\n"
"<ul>\n"
"<li>Start VirtualBox </li>\n"
"<li>Click on the IOUVM</li>\n"
"<li>Click on settings</li>\n"
"<li>Click on Network</li>\n"
"<li>Change Host-only adapter to NAT</li>\n"
"<li>Click on OK</li>\n"
"<li>Start the VM<li>\n"
"</ul>"))
        self.label_3.setText(_translate("IOUVMConverterWizard", "<html><head/><body><p><span style=\" font-size:xx-large; font-weight:600;\">Update GNS3 on IOUVM</span></p><p>In the VM: </p><ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Log as root with password CISCO</li><li style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">pip3 install gns3-server==1.3.10</li><li style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">halt</li></ul></body></html>"))
        self.label_4.setText(_translate("IOUVMConverterWizard", "<h1>Restore VM network settings</h1>\n"
"<ul>\n"
"<li>Start VirtualBox </li>\n"
"<li>Click on the IOUVM</li>\n"
"<li>Click on settings</li>\n"
"<li>Click on Network</li>\n"
"<li>Change NAT adapter to Host-Only</li>\n"
"<li>Click on OK</li>\n"
"<li>Start the VM<li>\n"
"</ul>"))
        self.label_10.setText(_translate("IOUVMConverterWizard", "<h1>Download backups</h1>\n"
"<ul>\n"
"<li>Log as root with password cisco</li>\n"
"<li>Type ifconfig eth0</li>\n"
"<li>Remember the addr</li>\n"
"<li>In your browser open http://THEADDR:8000</li>\n"
"<li>Download projects and images backups</li>\n"
"<li>halt the vm</li>\n"
"</ul>"))
        self.label_11.setText(_translate("IOUVMConverterWizard", "<h1>Restore backups</h1>\n"
"<ul>\n"
"<li>Start the GNS3 VM</li>\n"
"<li>Remember the IP display on the information screen</li>\n"
"<li>In a browser open http://THEIP:8000/upload</li>\n"
"<li>Select the option for restoring projects and upload the previous backup</li>\n"
"<li>Select the option for restoring images and upload the previous backup</li>\n"
"</ul>"))
        self.label_5.setText(_translate("IOUVMConverterWizard", "<center>\n"
"BACKUP<br>\n"
"YOUR TOPOLOGIES!\n"
"</center>"))
        self.label_7.setText(_translate("IOUVMConverterWizard", "<h1>Validation of the IOURC file</h1> \n"
"The IOURC file contain your licence for IOU.<br>\n"
"The format of file is:\n"
"<pre>\n"
"[license]\n"
"gns3-iouvm = OLDLICENCE;\n"
"gns3vm = NEWLICENCE;\n"
"</pre>\n"
"<br>\n"
"The GNS3VM require a new licence. You need to add it in the file. IOU is a CISCO product. GNS3 staff is not allowed to provide this licence."))
        self.label_12.setText(_translate("IOUVMConverterWizard", "<h1>Update configuration</h1>\n"
"<p style=\"color: red\">Your GNS3 configuration will be updated.</p>\n"
"<p>All your remote servers will be removed and replace by the GNS3VM. </p><p>If you have a custom remote server <strong>DO NOT CONTINUE</strong></p>"))
        self.label_6.setText(_translate("IOUVMConverterWizard", "<h1>Patch topologies</h1>\n"
"We need to patch your topologies please select your topologies directory"))
        self.uiPushButtonBrowse.setText(_translate("IOUVMConverterWizard", "Browse..."))
        self.label_8.setText(_translate("IOUVMConverterWizard", "<center>\n"
"<h1>Congratulation you can now use the GNS3 VM</h1>\n"
"</center>"))

