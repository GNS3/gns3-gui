# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/workspace/git/gns3-gui/gns3/ui/early_release_dialog.ui'
#
# Created: Wed Mar 19 16:26:12 2014
#      by: PyQt4 UI code generator 4.10
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

class Ui_EarlyReleaseDialog(object):
    def setupUi(self, EarlyReleaseDialog):
        EarlyReleaseDialog.setObjectName(_fromUtf8("EarlyReleaseDialog"))
        EarlyReleaseDialog.resize(467, 285)
        EarlyReleaseDialog.setModal(True)
        self.gridLayout_2 = QtGui.QGridLayout(EarlyReleaseDialog)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.uiEmailLineEdit = QtGui.QLineEdit(EarlyReleaseDialog)
        self.uiEmailLineEdit.setObjectName(_fromUtf8("uiEmailLineEdit"))
        self.gridLayout_2.addWidget(self.uiEmailLineEdit, 2, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 4, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 4, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(EarlyReleaseDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 5, 1, 1, 1)
        self.uiEmailLabel = QtGui.QLabel(EarlyReleaseDialog)
        self.uiEmailLabel.setObjectName(_fromUtf8("uiEmailLabel"))
        self.gridLayout_2.addWidget(self.uiEmailLabel, 2, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(EarlyReleaseDialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiDisclaimerLabel = QtGui.QLabel(self.groupBox)
        self.uiDisclaimerLabel.setObjectName(_fromUtf8("uiDisclaimerLabel"))
        self.gridLayout.addWidget(self.uiDisclaimerLabel, 0, 0, 1, 2)
        self.uiDisclaimerCheckBox = QtGui.QCheckBox(self.groupBox)
        self.uiDisclaimerCheckBox.setObjectName(_fromUtf8("uiDisclaimerCheckBox"))
        self.gridLayout.addWidget(self.uiDisclaimerCheckBox, 1, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 3, 0, 1, 2)
        self.uiUsernameLineEdit = QtGui.QLineEdit(EarlyReleaseDialog)
        self.uiUsernameLineEdit.setObjectName(_fromUtf8("uiUsernameLineEdit"))
        self.gridLayout_2.addWidget(self.uiUsernameLineEdit, 1, 1, 1, 1)
        self.uiUsernameLabel = QtGui.QLabel(EarlyReleaseDialog)
        self.uiUsernameLabel.setObjectName(_fromUtf8("uiUsernameLabel"))
        self.gridLayout_2.addWidget(self.uiUsernameLabel, 1, 0, 1, 1)
        self.label = QtGui.QLabel(EarlyReleaseDialog)
        self.label.setOpenExternalLinks(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 2)

        self.retranslateUi(EarlyReleaseDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), EarlyReleaseDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), EarlyReleaseDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(EarlyReleaseDialog)
        EarlyReleaseDialog.setTabOrder(self.uiUsernameLineEdit, self.uiEmailLineEdit)
        EarlyReleaseDialog.setTabOrder(self.uiEmailLineEdit, self.uiDisclaimerCheckBox)
        EarlyReleaseDialog.setTabOrder(self.uiDisclaimerCheckBox, self.buttonBox)

    def retranslateUi(self, EarlyReleaseDialog):
        EarlyReleaseDialog.setWindowTitle(_translate("EarlyReleaseDialog", "GNS3 Early Release", None))
        self.uiEmailLabel.setText(_translate("EarlyReleaseDialog", "Email address:", None))
        self.groupBox.setTitle(_translate("EarlyReleaseDialog", "Disclaimer", None))
        self.uiDisclaimerLabel.setText(_translate("EarlyReleaseDialog", "<html><head/><body><p>This is an alpha release of the new GNS3, please do not use it<br>for production or any important work. Bugs are very likely and<br>existing features  can change without warning until the beta<br>release cycle starts. Thank you for your understanding!\n"
"</p></body></html>", None))
        self.uiDisclaimerCheckBox.setText(_translate("EarlyReleaseDialog", "I understand", None))
        self.uiUsernameLabel.setText(_translate("EarlyReleaseDialog", "GNS3 username:", None))
        self.label.setText(_translate("EarlyReleaseDialog", "<html><head/><body><p>This is a early release of the new GNS3, you need a GNS3 membership<br>in order to use it. Please visit our <a href=\"http://new.gns3.net\"><span style=\" text-decoration: underline; color:#0000ff;\">crowdfunding page</span></a> to get one.</p></body></html>", None))

