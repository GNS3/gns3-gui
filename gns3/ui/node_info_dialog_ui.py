# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/node_info_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_NodeInfoDialog(object):
    def setupUi(self, NodeInfoDialog):
        NodeInfoDialog.setObjectName("NodeInfoDialog")
        NodeInfoDialog.resize(850, 600)
        self.verticalLayout = QtWidgets.QVBoxLayout(NodeInfoDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiTabWidget = QtWidgets.QTabWidget(NodeInfoDialog)
        self.uiTabWidget.setObjectName("uiTabWidget")
        self.uiGeneralTab = QtWidgets.QWidget()
        self.uiGeneralTab.setObjectName("uiGeneralTab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.uiGeneralTab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.uiGeneralTextBrowser = QtWidgets.QTextBrowser(self.uiGeneralTab)
        self.uiGeneralTextBrowser.setObjectName("uiGeneralTextBrowser")
        self.verticalLayout_2.addWidget(self.uiGeneralTextBrowser)
        self.uiTabWidget.addTab(self.uiGeneralTab, "")
        self.uiUsageTab = QtWidgets.QWidget()
        self.uiUsageTab.setObjectName("uiUsageTab")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.uiUsageTab)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.uiUsageTextBrowser = QtWidgets.QTextBrowser(self.uiUsageTab)
        self.uiUsageTextBrowser.setObjectName("uiUsageTextBrowser")
        self.verticalLayout_3.addWidget(self.uiUsageTextBrowser)
        self.uiTabWidget.addTab(self.uiUsageTab, "")
        self.uiCommandLineTab = QtWidgets.QWidget()
        self.uiCommandLineTab.setObjectName("uiCommandLineTab")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.uiCommandLineTab)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.uiCommandLineTextBrowser = QtWidgets.QTextBrowser(self.uiCommandLineTab)
        self.uiCommandLineTextBrowser.setObjectName("uiCommandLineTextBrowser")
        self.verticalLayout_4.addWidget(self.uiCommandLineTextBrowser)
        self.uiTabWidget.addTab(self.uiCommandLineTab, "")
        self.verticalLayout.addWidget(self.uiTabWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(NodeInfoDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(NodeInfoDialog)
        self.uiTabWidget.setCurrentIndex(0)
        self.buttonBox.accepted.connect(NodeInfoDialog.accept)
        self.buttonBox.rejected.connect(NodeInfoDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(NodeInfoDialog)

    def retranslateUi(self, NodeInfoDialog):
        _translate = QtCore.QCoreApplication.translate
        NodeInfoDialog.setWindowTitle(_translate("NodeInfoDialog", "Node information"))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiGeneralTab), _translate("NodeInfoDialog", "General information"))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiUsageTab), _translate("NodeInfoDialog", "Usage instructions"))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiCommandLineTab), _translate("NodeInfoDialog", "Command line"))

from . import resources_rc
