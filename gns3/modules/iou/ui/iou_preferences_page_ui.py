# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/modules/iou/ui/iou_preferences_page.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_IOUPreferencesPageWidget(object):

    def setupUi(self, IOUPreferencesPageWidget):
        IOUPreferencesPageWidget.setObjectName("IOUPreferencesPageWidget")
        IOUPreferencesPageWidget.resize(490, 532)
        self.vboxlayout = QtWidgets.QVBoxLayout(IOUPreferencesPageWidget)
        self.vboxlayout.setObjectName("vboxlayout")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.IOULicenceTextEdit = QtWidgets.QPlainTextEdit(IOUPreferencesPageWidget)
        self.IOULicenceTextEdit.setObjectName("IOULicenceTextEdit")
        self.horizontalLayout_5.addWidget(self.IOULicenceTextEdit)
        self.uiIOURCPathToolButton = QtWidgets.QToolButton(IOUPreferencesPageWidget)
        self.uiIOURCPathToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiIOURCPathToolButton.setObjectName("uiIOURCPathToolButton")
        self.horizontalLayout_5.addWidget(self.uiIOURCPathToolButton)
        self.vboxlayout.addLayout(self.horizontalLayout_5)
        self.uiLicensecheckBox = QtWidgets.QCheckBox(IOUPreferencesPageWidget)
        self.uiLicensecheckBox.setChecked(True)
        self.uiLicensecheckBox.setObjectName("uiLicensecheckBox")
        self.vboxlayout.addWidget(self.uiLicensecheckBox)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.vboxlayout.addItem(spacerItem)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(164, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.uiRestoreDefaultsPushButton = QtWidgets.QPushButton(IOUPreferencesPageWidget)
        self.uiRestoreDefaultsPushButton.setObjectName("uiRestoreDefaultsPushButton")
        self.horizontalLayout_2.addWidget(self.uiRestoreDefaultsPushButton)
        self.vboxlayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(IOUPreferencesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(IOUPreferencesPageWidget)

    def retranslateUi(self, IOUPreferencesPageWidget):
        _translate = QtCore.QCoreApplication.translate
        IOUPreferencesPageWidget.setWindowTitle(_translate("IOUPreferencesPageWidget", "IOS on UNIX"))
        self.IOULicenceTextEdit.setToolTip(_translate("IOUPreferencesPageWidget", "A license is required to run IOU. Copy & paste the content of your iourc file here or use the browse button to select a file. The license will be pushed to remote servers."))
        self.uiIOURCPathToolButton.setText(_translate("IOUPreferencesPageWidget", "&Browse..."))
        self.uiLicensecheckBox.setText(_translate("IOUPreferencesPageWidget", "Check for a valid IOU license key"))
        self.uiRestoreDefaultsPushButton.setText(_translate("IOUPreferencesPageWidget", "Restore defaults"))
