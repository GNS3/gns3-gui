# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/docker/ui/docker_preferences_page.ui'
#
# Created: Thu May  5 18:51:18 2016
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DockerPreferencesPageWidget(object):
    def setupUi(self, DockerPreferencesPageWidget):
        DockerPreferencesPageWidget.setObjectName("DockerPreferencesPageWidget")
        DockerPreferencesPageWidget.resize(330, 200)
        self.verticalLayout = QtWidgets.QVBoxLayout(DockerPreferencesPageWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiTabWidget = QtWidgets.QTabWidget(DockerPreferencesPageWidget)
        self.uiTabWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.uiTabWidget.setObjectName("uiTabWidget")
        self.uiServerSettingsTabWidget = QtWidgets.QWidget()
        self.uiServerSettingsTabWidget.setObjectName("uiServerSettingsTabWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.uiServerSettingsTabWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.uiUseLocalServercheckBox = QtWidgets.QCheckBox(self.uiServerSettingsTabWidget)
        self.uiUseLocalServercheckBox.setChecked(True)
        self.uiUseLocalServercheckBox.setObjectName("uiUseLocalServercheckBox")
        self.verticalLayout_2.addWidget(self.uiUseLocalServercheckBox)
        spacerItem = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.uiTabWidget.addTab(self.uiServerSettingsTabWidget, "")
        self.verticalLayout.addWidget(self.uiTabWidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(254, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.uiRestoreDefaultsPushButton = QtWidgets.QPushButton(DockerPreferencesPageWidget)
        self.uiRestoreDefaultsPushButton.setObjectName("uiRestoreDefaultsPushButton")
        self.horizontalLayout_2.addWidget(self.uiRestoreDefaultsPushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(DockerPreferencesPageWidget)
        self.uiTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(DockerPreferencesPageWidget)

    def retranslateUi(self, DockerPreferencesPageWidget):
        _translate = QtCore.QCoreApplication.translate
        DockerPreferencesPageWidget.setWindowTitle(_translate("DockerPreferencesPageWidget", "Docker"))
        self.uiUseLocalServercheckBox.setText(_translate("DockerPreferencesPageWidget", "Use the local server"))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiServerSettingsTabWidget), _translate("DockerPreferencesPageWidget", "General settings"))
        self.uiRestoreDefaultsPushButton.setText(_translate("DockerPreferencesPageWidget", "Restore defaults"))

