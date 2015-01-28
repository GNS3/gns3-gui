# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/masci/devel/gns3/gns3-gui/gns3/ui/cloud_inspector_view.ui'
#
# Created: Tue May 27 14:46:14 2014
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


class Ui_CloudInspectorView(object):

    def setupUi(self, CloudInspectorView):
        CloudInspectorView.setObjectName(_fromUtf8("CloudInspectorView"))
        CloudInspectorView.resize(359, 283)
        CloudInspectorView.setAutoFillBackground(False)
        CloudInspectorView.setStyleSheet(_fromUtf8(""))
        self.verticalLayout = QtGui.QVBoxLayout(CloudInspectorView)
        self.verticalLayout.setMargin(6)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.uiInstancesTableView = QtGui.QTableView(CloudInspectorView)
        self.uiInstancesTableView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.uiInstancesTableView.setObjectName(_fromUtf8("uiInstancesTableView"))
        self.uiInstancesTableView.horizontalHeader().setVisible(True)
        self.verticalLayout.addWidget(self.uiInstancesTableView)
        self.uiCreateInstanceGroupBox = QtGui.QGroupBox(CloudInspectorView)
        self.uiCreateInstanceGroupBox.setObjectName(_fromUtf8("uiCreateInstanceGroupBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.uiCreateInstanceGroupBox)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.uiCreateInstanceComboBox = QtGui.QComboBox(self.uiCreateInstanceGroupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiCreateInstanceComboBox.sizePolicy().hasHeightForWidth())
        self.uiCreateInstanceComboBox.setSizePolicy(sizePolicy)
        self.uiCreateInstanceComboBox.setObjectName(_fromUtf8("uiCreateInstanceComboBox"))
        self.horizontalLayout.addWidget(self.uiCreateInstanceComboBox)
        self.uiCreateInstanceButton = QtGui.QPushButton(self.uiCreateInstanceGroupBox)
        self.uiCreateInstanceButton.setObjectName(_fromUtf8("uiCreateInstanceButton"))
        self.horizontalLayout.addWidget(self.uiCreateInstanceButton)
        self.verticalLayout.addWidget(self.uiCreateInstanceGroupBox)

        self.retranslateUi(CloudInspectorView)
        QtCore.QMetaObject.connectSlotsByName(CloudInspectorView)

    def retranslateUi(self, CloudInspectorView):
        CloudInspectorView.setWindowTitle(_translate("CloudInspectorView", "Form", None))
        self.uiCreateInstanceGroupBox.setTitle(_translate("CloudInspectorView", "Create new Instance", None))
        self.uiCreateInstanceButton.setText(_translate("CloudInspectorView", "Create", None))
