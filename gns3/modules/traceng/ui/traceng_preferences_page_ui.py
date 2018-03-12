# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/traceng/ui/traceng_preferences_page.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_TraceNGPreferencesPageWidget(object):
    def setupUi(self, TraceNGPreferencesPageWidget):
        TraceNGPreferencesPageWidget.setObjectName("TraceNGPreferencesPageWidget")
        TraceNGPreferencesPageWidget.resize(623, 280)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(TraceNGPreferencesPageWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.uiTabWidget = QtWidgets.QTabWidget(TraceNGPreferencesPageWidget)
        self.uiTabWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.uiTabWidget.setObjectName("uiTabWidget")
        self.uiGeneralSettingsTabWidget = QtWidgets.QWidget()
        self.uiGeneralSettingsTabWidget.setObjectName("uiGeneralSettingsTabWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.uiGeneralSettingsTabWidget)
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiTraceNGPathLabel = QtWidgets.QLabel(self.uiGeneralSettingsTabWidget)
        self.uiTraceNGPathLabel.setObjectName("uiTraceNGPathLabel")
        self.verticalLayout.addWidget(self.uiTraceNGPathLabel)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.uiTraceNGPathLineEdit = QtWidgets.QLineEdit(self.uiGeneralSettingsTabWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiTraceNGPathLineEdit.sizePolicy().hasHeightForWidth())
        self.uiTraceNGPathLineEdit.setSizePolicy(sizePolicy)
        self.uiTraceNGPathLineEdit.setObjectName("uiTraceNGPathLineEdit")
        self.horizontalLayout_5.addWidget(self.uiTraceNGPathLineEdit)
        self.uiTraceNGPathToolButton = QtWidgets.QToolButton(self.uiGeneralSettingsTabWidget)
        self.uiTraceNGPathToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiTraceNGPathToolButton.setObjectName("uiTraceNGPathToolButton")
        self.horizontalLayout_5.addWidget(self.uiTraceNGPathToolButton)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        spacerItem = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.uiTabWidget.addTab(self.uiGeneralSettingsTabWidget, "")
        self.verticalLayout_2.addWidget(self.uiTabWidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(138, 17, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.uiRestoreDefaultsPushButton = QtWidgets.QPushButton(TraceNGPreferencesPageWidget)
        self.uiRestoreDefaultsPushButton.setObjectName("uiRestoreDefaultsPushButton")
        self.horizontalLayout_2.addWidget(self.uiRestoreDefaultsPushButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(TraceNGPreferencesPageWidget)
        self.uiTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(TraceNGPreferencesPageWidget)

    def retranslateUi(self, TraceNGPreferencesPageWidget):
        _translate = QtCore.QCoreApplication.translate
        TraceNGPreferencesPageWidget.setWindowTitle(_translate("TraceNGPreferencesPageWidget", "TraceNG"))
        self.uiTraceNGPathLabel.setText(_translate("TraceNGPreferencesPageWidget", "Path to TraceNG executable:"))
        self.uiTraceNGPathToolButton.setText(_translate("TraceNGPreferencesPageWidget", "&Browse..."))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiGeneralSettingsTabWidget), _translate("TraceNGPreferencesPageWidget", "Local settings"))
        self.uiRestoreDefaultsPushButton.setText(_translate("TraceNGPreferencesPageWidget", "Restore defaults"))

