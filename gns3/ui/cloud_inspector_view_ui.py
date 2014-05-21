# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/masci/devel/gns3/gns3-gui/gns3/ui/cloud_inspector_view.ui'
#
# Created: Wed May 21 11:12:50 2014
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
        CloudInspectorView.resize(400, 300)
        CloudInspectorView.setAutoFillBackground(False)
        CloudInspectorView.setStyleSheet(_fromUtf8(""))
        self.verticalLayout_3 = QtGui.QVBoxLayout(CloudInspectorView)
        self.verticalLayout_3.setMargin(6)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.uiInstancesGroupBox = QtGui.QGroupBox(CloudInspectorView)
        self.uiInstancesGroupBox.setObjectName(_fromUtf8("uiInstancesGroupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.uiInstancesGroupBox)
        self.verticalLayout.setMargin(6)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.uiInstancesTableView = QtGui.QTableView(self.uiInstancesGroupBox)
        self.uiInstancesTableView.setObjectName(_fromUtf8("uiInstancesTableView"))
        self.verticalLayout.addWidget(self.uiInstancesTableView)
        self.verticalLayout_3.addWidget(self.uiInstancesGroupBox)
        self.uiCreateInstanceGroupBox = QtGui.QGroupBox(CloudInspectorView)
        self.uiCreateInstanceGroupBox.setObjectName(_fromUtf8("uiCreateInstanceGroupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.uiCreateInstanceGroupBox)
        self.verticalLayout_2.setMargin(6)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.uiCreateInstanceComboBox = QtGui.QComboBox(self.uiCreateInstanceGroupBox)
        self.uiCreateInstanceComboBox.setObjectName(_fromUtf8("uiCreateInstanceComboBox"))
        self.verticalLayout_2.addWidget(self.uiCreateInstanceComboBox)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.uiCreateInstanceButton = QtGui.QPushButton(self.uiCreateInstanceGroupBox)
        self.uiCreateInstanceButton.setObjectName(_fromUtf8("uiCreateInstanceButton"))
        self.horizontalLayout.addWidget(self.uiCreateInstanceButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout_3.addWidget(self.uiCreateInstanceGroupBox)

        self.retranslateUi(CloudInspectorView)
        QtCore.QMetaObject.connectSlotsByName(CloudInspectorView)

    def retranslateUi(self, CloudInspectorView):
        CloudInspectorView.setWindowTitle(_translate("CloudInspectorView", "Form", None))
        self.uiInstancesGroupBox.setTitle(_translate("CloudInspectorView", "Instances", None))
        self.uiCreateInstanceGroupBox.setTitle(_translate("CloudInspectorView", "Create new Instance", None))
        self.uiCreateInstanceButton.setText(_translate("CloudInspectorView", "Create", None))

