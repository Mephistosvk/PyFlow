"""@file GetVarNode.py

Builtin node to set variable value.
"""
from copy import copy

from Qt.QtWidgets import QStyle
from Qt.QtWidgets import QGraphicsItem
from Qt.QtWidgets import QLineEdit
from Qt import QtCore
from Qt import QtGui

from PyFlow.UI.Utils.Settings import *
from PyFlow.Core.Common import *
from PyFlow.UI import RESOURCES_DIR
from PyFlow.UI.Canvas.UINodeBase import UINodeBase
from PyFlow.Commands.RemoveNodes import RemoveNodes
from PyFlow.UI.Widgets.InputWidgets import createInputWidget
from PyFlow.UI.Widgets.EnumComboBox import EnumComboBox
from PyFlow.UI.Widgets.PropertiesFramework import CollapsibleFormWidget


# Variable setter node
class UISetVarNode(UINodeBase):
    """docstring for UISetVarNode"""
    def __init__(self, raw_node):
        super(UISetVarNode, self).__init__(raw_node)
        self.image = RESOURCES_DIR + "/gear.svg"
        self.headColorOverride = Colors.Gray
        self.color = Colors.DarkGray

    @property
    def var(self):
        return self._rawNode.var

    @var.setter
    def var(self, newVar):
        self.var.nameChanged.disconnect(self.updateHeaderText)
        self._rawNode.var = newVar
        self.var.nameChanged.connect(self.updateHeaderText)
        self._createUIPinWrapper(self._rawNode.inp)
        self._createUIPinWrapper(self._rawNode.out)

    def onVariableWasChanged(self):
        self._createUIPinWrapper(self._rawNode.inp)
        self._createUIPinWrapper(self._rawNode.out)

    def serialize(self):
        template = UINodeBase.serialize(self)
        template['meta']['var'] = self.var.serialize()
        return template

    def onVarSelected(self, varName):
        if self.var.name == varName:
            return

        var = self.canvasRef().graphManager.findVariable(varName)

        if var:
            inLinkedTo = getConnectedPins(self._rawNode.inp)
            outLinkedTo = getConnectedPins(self._rawNode.out)
            self.var = var
            self._rawNode.updateStructure()
            for i in outLinkedTo:
                self.canvasRef().connectPinsInternal(self._rawNode.out.getWrapper()(), i.getWrapper()())

            for o in inLinkedTo:
                self.canvasRef().connectPinsInternal(o.getWrapper()(), self._rawNode.inp.getWrapper()())

            self.updateHeaderText()

    def createInputWidgets(self, propertiesWidget):
        inputsCategory = CollapsibleFormWidget(headName="Variable")
        validVars = self.graph().getVarList()
        cbVars = EnumComboBox([v.name for v in validVars])
        cbVars.setCurrentText(self.var.name)
        cbVars.changeCallback.connect(self.onVarSelected)
        inputsCategory.addWidget("var", cbVars)

        propertiesWidget.addWidget(inputsCategory)

        super(UISetVarNode, self).createInputWidgets(propertiesWidget)

    def postCreate(self, template):
        super(UISetVarNode, self).postCreate(template)
        self.var.nameChanged.connect(self.updateHeaderText)
        self.updateHeaderText()

        for pin in self.UIPins.values():
            pin.setMenuItemEnabled("InitAs", False)

    def updateHeaderText(self):
        self.setHeaderHtml("Set {0}".format(self.var.name))
        self.updateNodeShape()

    @staticmethod
    def category():
        return 'Variables'