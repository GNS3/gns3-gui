# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/jseutterlst/gns3/gns3-gui/gns3/ui/cloud_preferences_page.ui'
#
# Created: Thu Jul 17 14:17:33 2014
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
        CloudPreferencesPageWidget.resize(482, 485)
        self.gridLayout = QtGui.QGridLayout(CloudPreferencesPageWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiImageTemplateLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiImageTemplateLabel.setObjectName(_fromUtf8("uiImageTemplateLabel"))
        self.gridLayout.addWidget(self.uiImageTemplateLabel, 16, 0, 1, 3)
        self.uiImageTemplateComboBox = QtGui.QComboBox(CloudPreferencesPageWidget)
        self.uiImageTemplateComboBox.setObjectName(_fromUtf8("uiImageTemplateComboBox"))
        self.gridLayout.addWidget(self.uiImageTemplateComboBox, 17, 0, 1, 1)
        self.uiNewInstancesLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiNewInstancesLabel.setObjectName(_fromUtf8("uiNewInstancesLabel"))
        self.gridLayout.addWidget(self.uiNewInstancesLabel, 9, 0, 1, 3)
        self.uiCreateAccountLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiCreateAccountLabel.setTextFormat(QtCore.Qt.RichText)
        self.uiCreateAccountLabel.setObjectName(_fromUtf8("uiCreateAccountLabel"))
        self.gridLayout.addWidget(self.uiCreateAccountLabel, 2, 2, 1, 1)
        self.uiUserNameLineEdit = QtGui.QLineEdit(CloudPreferencesPageWidget)
        self.uiUserNameLineEdit.setObjectName(_fromUtf8("uiUserNameLineEdit"))
        self.gridLayout.addWidget(self.uiUserNameLineEdit, 1, 0, 1, 1)
        self.uiAPIKeyLineEdit = QtGui.QLineEdit(CloudPreferencesPageWidget)
        self.uiAPIKeyLineEdit.setObjectName(_fromUtf8("uiAPIKeyLineEdit"))
        self.gridLayout.addWidget(self.uiAPIKeyLineEdit, 1, 2, 1, 1)
        self.uiStartNewProjectLayout = QtGui.QHBoxLayout()
        self.uiStartNewProjectLayout.setObjectName(_fromUtf8("uiStartNewProjectLayout"))
        self.uiNumOfInstancesSpinBox = QtGui.QSpinBox(CloudPreferencesPageWidget)
        self.uiNumOfInstancesSpinBox.setObjectName(_fromUtf8("uiNumOfInstancesSpinBox"))
        self.uiStartNewProjectLayout.addWidget(self.uiNumOfInstancesSpinBox)
        self.uiNumOfInstancesLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiNumOfInstancesLabel.setObjectName(_fromUtf8("uiNumOfInstancesLabel"))
        self.uiStartNewProjectLayout.addWidget(self.uiNumOfInstancesLabel)
        self.uiInstanceFlavorComboBox = QtGui.QComboBox(CloudPreferencesPageWidget)
        self.uiInstanceFlavorComboBox.setObjectName(_fromUtf8("uiInstanceFlavorComboBox"))
        self.uiStartNewProjectLayout.addWidget(self.uiInstanceFlavorComboBox)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.uiStartNewProjectLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.uiStartNewProjectLayout, 7, 0, 1, 3)
        self.uiTimeoutLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiTimeoutLabel.setWordWrap(True)
        self.uiTimeoutLabel.setObjectName(_fromUtf8("uiTimeoutLabel"))
        self.gridLayout.addWidget(self.uiTimeoutLabel, 12, 0, 1, 2)
        self.uiNewInstancesLayout = QtGui.QHBoxLayout()
        self.uiNewInstancesLayout.setObjectName(_fromUtf8("uiNewInstancesLayout"))
        self.uiNewInstanceFlavorComboBox = QtGui.QComboBox(CloudPreferencesPageWidget)
        self.uiNewInstanceFlavorComboBox.setObjectName(_fromUtf8("uiNewInstanceFlavorComboBox"))
        self.uiNewInstancesLayout.addWidget(self.uiNewInstanceFlavorComboBox)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.uiNewInstancesLayout.addItem(spacerItem1)
        self.uiTermsCheckBox = QtGui.QCheckBox(CloudPreferencesPageWidget)
        self.uiTermsCheckBox.setText(_fromUtf8(""))
        self.uiTermsCheckBox.setObjectName(_fromUtf8("uiTermsCheckBox"))
        self.uiNewInstancesLayout.addWidget(self.uiTermsCheckBox)
        self.uiTermsLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiTermsLabel.setTextFormat(QtCore.Qt.RichText)
        self.uiTermsLabel.setObjectName(_fromUtf8("uiTermsLabel"))
        self.uiNewInstancesLayout.addWidget(self.uiTermsLabel)
        self.gridLayout.addLayout(self.uiNewInstancesLayout, 10, 0, 2, 3)
        self.uiCloudProviderComboBox = QtGui.QComboBox(CloudPreferencesPageWidget)
        self.uiCloudProviderComboBox.setObjectName(_fromUtf8("uiCloudProviderComboBox"))
        self.gridLayout.addWidget(self.uiCloudProviderComboBox, 3, 0, 1, 1)
        self.uiUserNameLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiUserNameLabel.setObjectName(_fromUtf8("uiUserNameLabel"))
        self.gridLayout.addWidget(self.uiUserNameLabel, 0, 0, 1, 1)
        self.uiAPIKeyLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiAPIKeyLabel.setObjectName(_fromUtf8("uiAPIKeyLabel"))
        self.gridLayout.addWidget(self.uiAPIKeyLabel, 0, 2, 1, 1)
        self.uiRememberAPIKeyRadioButton = QtGui.QRadioButton(CloudPreferencesPageWidget)
        self.uiRememberAPIKeyRadioButton.setObjectName(_fromUtf8("uiRememberAPIKeyRadioButton"))
        self.gridLayout.addWidget(self.uiRememberAPIKeyRadioButton, 3, 2, 1, 1)
        self.uiStartNewProjectsLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiStartNewProjectsLabel.setObjectName(_fromUtf8("uiStartNewProjectsLabel"))
        self.gridLayout.addWidget(self.uiStartNewProjectsLabel, 6, 0, 1, 3)
        self.uiRegionComboBox = QtGui.QComboBox(CloudPreferencesPageWidget)
        self.uiRegionComboBox.setObjectName(_fromUtf8("uiRegionComboBox"))
        self.gridLayout.addWidget(self.uiRegionComboBox, 5, 0, 1, 1)
        self.uiCloudProviderLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiCloudProviderLabel.setObjectName(_fromUtf8("uiCloudProviderLabel"))
        self.gridLayout.addWidget(self.uiCloudProviderLabel, 2, 0, 1, 1)
        self.uiRegionLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiRegionLabel.setObjectName(_fromUtf8("uiRegionLabel"))
        self.gridLayout.addWidget(self.uiRegionLabel, 4, 0, 1, 1)
        self.uiForgetAPIKeyRadioButton = QtGui.QRadioButton(CloudPreferencesPageWidget)
        self.uiForgetAPIKeyRadioButton.setObjectName(_fromUtf8("uiForgetAPIKeyRadioButton"))
        self.gridLayout.addWidget(self.uiForgetAPIKeyRadioButton, 4, 2, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.uiTimeoutSpinBox = QtGui.QSpinBox(CloudPreferencesPageWidget)
        self.uiTimeoutSpinBox.setMaximum(999)
        self.uiTimeoutSpinBox.setProperty("value", 30)
        self.uiTimeoutSpinBox.setObjectName(_fromUtf8("uiTimeoutSpinBox"))
        self.horizontalLayout_3.addWidget(self.uiTimeoutSpinBox)
        self.uiTimeoutLabel2 = QtGui.QLabel(CloudPreferencesPageWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiTimeoutLabel2.sizePolicy().hasHeightForWidth())
        self.uiTimeoutLabel2.setSizePolicy(sizePolicy)
        self.uiTimeoutLabel2.setObjectName(_fromUtf8("uiTimeoutLabel2"))
        self.horizontalLayout_3.addWidget(self.uiTimeoutLabel2)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.gridLayout.addLayout(self.horizontalLayout_3, 14, 0, 2, 3)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem3, 18, 0, 1, 1)

        self.retranslateUi(CloudPreferencesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(CloudPreferencesPageWidget)

    def retranslateUi(self, CloudPreferencesPageWidget):
        CloudPreferencesPageWidget.setWindowTitle(_translate("CloudPreferencesPageWidget", "Cloud", None))
        self.uiImageTemplateLabel.setText(_translate("CloudPreferencesPageWidget", "New instances use the following template:", None))
        self.uiNewInstancesLabel.setText(_translate("CloudPreferencesPageWidget", "New instances are:", None))
        self.uiCreateAccountLabel.setText(_translate("CloudPreferencesPageWidget", "No API Key? <a href=\"#\">Create Cloud Account.</a>", None))
        self.uiNumOfInstancesLabel.setText(_translate("CloudPreferencesPageWidget", "instance(s) with", None))
        self.uiTimeoutLabel.setText(_translate("CloudPreferencesPageWidget", "Instances are deleted after", None))
        self.uiTermsLabel.setText(_translate("CloudPreferencesPageWidget", "Accept Terms and Conditions", None))
        self.uiUserNameLabel.setText(_translate("CloudPreferencesPageWidget", "User Name:", None))
        self.uiAPIKeyLabel.setText(_translate("CloudPreferencesPageWidget", "API Key", None))
        self.uiRememberAPIKeyRadioButton.setText(_translate("CloudPreferencesPageWidget", "Remeber these settings\n"
                                                            "(Suggested for private computers)", None))
        self.uiStartNewProjectsLabel.setText(_translate("CloudPreferencesPageWidget", "Start new projects with:", None))
        self.uiCloudProviderLabel.setText(_translate("CloudPreferencesPageWidget", "Cloud provider", None))
        self.uiRegionLabel.setText(_translate("CloudPreferencesPageWidget", "Region (optional)", None))
        self.uiForgetAPIKeyRadioButton.setText(_translate("CloudPreferencesPageWidget", "Forget these settings on exit\n"
                                                          "(Suggested for public computers)", None))
        self.uiTimeoutLabel2.setText(_translate("CloudPreferencesPageWidget", "minutes of lost communication", None))
