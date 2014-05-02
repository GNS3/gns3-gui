# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/masci/devel/gns3/gns3-gui/gns3/ui/cloud_preferences_page.ui'
#
# Created: Fri May  2 15:24:25 2014
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

class Ui_CloudPreferencesPageWidget(object):
    def setupUi(self, CloudPreferencesPageWidget):
        CloudPreferencesPageWidget.setObjectName(_fromUtf8("CloudPreferencesPageWidget"))
        CloudPreferencesPageWidget.resize(471, 384)
        self.gridLayout = QtGui.QGridLayout(CloudPreferencesPageWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(CloudPreferencesPageWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 9, 0, 1, 2)
        self.uiCloudProviderLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiCloudProviderLabel.setObjectName(_fromUtf8("uiCloudProviderLabel"))
        self.gridLayout.addWidget(self.uiCloudProviderLabel, 2, 0, 1, 1)
        self.uiRegionComboBox = QtGui.QComboBox(CloudPreferencesPageWidget)
        self.uiRegionComboBox.setObjectName(_fromUtf8("uiRegionComboBox"))
        self.gridLayout.addWidget(self.uiRegionComboBox, 5, 0, 1, 1)
        self.uiRegionLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiRegionLabel.setObjectName(_fromUtf8("uiRegionLabel"))
        self.gridLayout.addWidget(self.uiRegionLabel, 4, 0, 1, 1)
        self.uiForgetAPIKeyRadioButton = QtGui.QRadioButton(CloudPreferencesPageWidget)
        self.uiForgetAPIKeyRadioButton.setObjectName(_fromUtf8("uiForgetAPIKeyRadioButton"))
        self.gridLayout.addWidget(self.uiForgetAPIKeyRadioButton, 4, 1, 1, 1)
        self.uiCreateAccountLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiCreateAccountLabel.setTextFormat(QtCore.Qt.RichText)
        self.uiCreateAccountLabel.setObjectName(_fromUtf8("uiCreateAccountLabel"))
        self.gridLayout.addWidget(self.uiCreateAccountLabel, 2, 1, 1, 1)
        self.uiUserNameLineEdit = QtGui.QLineEdit(CloudPreferencesPageWidget)
        self.uiUserNameLineEdit.setObjectName(_fromUtf8("uiUserNameLineEdit"))
        self.gridLayout.addWidget(self.uiUserNameLineEdit, 1, 0, 1, 1)
        self.uiAPIKeyLineEdit = QtGui.QLineEdit(CloudPreferencesPageWidget)
        self.uiAPIKeyLineEdit.setObjectName(_fromUtf8("uiAPIKeyLineEdit"))
        self.gridLayout.addWidget(self.uiAPIKeyLineEdit, 1, 1, 1, 1)
        self.uiAPIKeyLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiAPIKeyLabel.setObjectName(_fromUtf8("uiAPIKeyLabel"))
        self.gridLayout.addWidget(self.uiAPIKeyLabel, 0, 1, 1, 1)
        self.uiCloudProviderComboBox = QtGui.QComboBox(CloudPreferencesPageWidget)
        self.uiCloudProviderComboBox.setObjectName(_fromUtf8("uiCloudProviderComboBox"))
        self.gridLayout.addWidget(self.uiCloudProviderComboBox, 3, 0, 1, 1)
        self.uiRememberAPIKeyRadioButton = QtGui.QRadioButton(CloudPreferencesPageWidget)
        self.uiRememberAPIKeyRadioButton.setObjectName(_fromUtf8("uiRememberAPIKeyRadioButton"))
        self.gridLayout.addWidget(self.uiRememberAPIKeyRadioButton, 3, 1, 1, 1)
        self.uiUserNameLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiUserNameLabel.setObjectName(_fromUtf8("uiUserNameLabel"))
        self.gridLayout.addWidget(self.uiUserNameLabel, 0, 0, 1, 1)
        self.uiStartNewProjectsLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiStartNewProjectsLabel.setObjectName(_fromUtf8("uiStartNewProjectsLabel"))
        self.gridLayout.addWidget(self.uiStartNewProjectsLabel, 6, 0, 1, 2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.uiNumOfInstancesSpinBox = QtGui.QSpinBox(CloudPreferencesPageWidget)
        self.uiNumOfInstancesSpinBox.setObjectName(_fromUtf8("uiNumOfInstancesSpinBox"))
        self.horizontalLayout.addWidget(self.uiNumOfInstancesSpinBox)
        self.uiNumOfInstancesLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiNumOfInstancesLabel.setObjectName(_fromUtf8("uiNumOfInstancesLabel"))
        self.horizontalLayout.addWidget(self.uiNumOfInstancesLabel)
        self.uiMemPerInstanceSpinBox = QtGui.QSpinBox(CloudPreferencesPageWidget)
        self.uiMemPerInstanceSpinBox.setObjectName(_fromUtf8("uiMemPerInstanceSpinBox"))
        self.horizontalLayout.addWidget(self.uiMemPerInstanceSpinBox)
        self.uiMemLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiMemLabel.setObjectName(_fromUtf8("uiMemLabel"))
        self.horizontalLayout.addWidget(self.uiMemLabel)
        self.uiHourlyPriceLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiHourlyPriceLabel.setObjectName(_fromUtf8("uiHourlyPriceLabel"))
        self.horizontalLayout.addWidget(self.uiHourlyPriceLabel)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.horizontalLayout, 7, 0, 1, 2)
        self.PLACEHOLDER = QtGui.QFrame(CloudPreferencesPageWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PLACEHOLDER.sizePolicy().hasHeightForWidth())
        self.PLACEHOLDER.setSizePolicy(sizePolicy)
        self.PLACEHOLDER.setMinimumSize(QtCore.QSize(0, 25))
        self.PLACEHOLDER.setFrameShape(QtGui.QFrame.StyledPanel)
        self.PLACEHOLDER.setFrameShadow(QtGui.QFrame.Raised)
        self.PLACEHOLDER.setObjectName(_fromUtf8("PLACEHOLDER"))
        self.gridLayout.addWidget(self.PLACEHOLDER, 14, 0, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.uiMemPerNewInstanceSpinBox = QtGui.QSpinBox(CloudPreferencesPageWidget)
        self.uiMemPerNewInstanceSpinBox.setObjectName(_fromUtf8("uiMemPerNewInstanceSpinBox"))
        self.horizontalLayout_2.addWidget(self.uiMemPerNewInstanceSpinBox)
        self.uiMemNewLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiMemNewLabel.setObjectName(_fromUtf8("uiMemNewLabel"))
        self.horizontalLayout_2.addWidget(self.uiMemNewLabel)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.uiTermsCheckBox = QtGui.QCheckBox(CloudPreferencesPageWidget)
        self.uiTermsCheckBox.setObjectName(_fromUtf8("uiTermsCheckBox"))
        self.horizontalLayout_2.addWidget(self.uiTermsCheckBox)
        self.gridLayout.addLayout(self.horizontalLayout_2, 10, 0, 2, 2)

        self.retranslateUi(CloudPreferencesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(CloudPreferencesPageWidget)

    def retranslateUi(self, CloudPreferencesPageWidget):
        CloudPreferencesPageWidget.setWindowTitle(_translate("CloudPreferencesPageWidget", "Cloud", None))
        self.label.setText(_translate("CloudPreferencesPageWidget", "New instances are:", None))
        self.uiCloudProviderLabel.setText(_translate("CloudPreferencesPageWidget", "Cloud provider", None))
        self.uiRegionLabel.setText(_translate("CloudPreferencesPageWidget", "Region (optional)", None))
        self.uiForgetAPIKeyRadioButton.setText(_translate("CloudPreferencesPageWidget", "Forget these settings on exit\n"
"(Suggested for public computers)", None))
        self.uiCreateAccountLabel.setText(_translate("CloudPreferencesPageWidget", "No API Key? <a href=\"#\">Create Cloud Account.</a>", None))
        self.uiAPIKeyLabel.setText(_translate("CloudPreferencesPageWidget", "API Key", None))
        self.uiRememberAPIKeyRadioButton.setText(_translate("CloudPreferencesPageWidget", "Remeber these settings\n"
"(Suggested for private computers)", None))
        self.uiUserNameLabel.setText(_translate("CloudPreferencesPageWidget", "User Name:", None))
        self.uiStartNewProjectsLabel.setText(_translate("CloudPreferencesPageWidget", "Start new projects with:", None))
        self.uiNumOfInstancesLabel.setText(_translate("CloudPreferencesPageWidget", "instance(s) with", None))
        self.uiMemLabel.setText(_translate("CloudPreferencesPageWidget", "Gb", None))
        self.uiHourlyPriceLabel.setText(_translate("CloudPreferencesPageWidget", "($0.00 per hour per instance)", None))
        self.uiMemNewLabel.setText(_translate("CloudPreferencesPageWidget", "Gb in size", None))
        self.uiTermsCheckBox.setText(_translate("CloudPreferencesPageWidget", "Accept Terms and Conditions", None))

