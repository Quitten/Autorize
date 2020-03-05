#!/usr/bin/env python
# -*- coding: utf-8 -*- 

def addFilterHelper(typeObj, model, textObj):
        typeName = typeObj.getSelectedItem().split(":")[0]
        model.addElement(typeName + ": " + textObj.getText().strip())
        textObj.setText("")

def delFilterHelper(listObj):
        index = listObj.getSelectedIndex()
        if not index == -1:
                listObj.getModel().remove(index)

def modFilterHelper(listObj, typeObj, textObj):
        index = listObj.getSelectedIndex()
        if not index == -1:
                valt = listObj.getSelectedValue()
                val = valt.split(":", 1)[1].strip()
                modifiedFilter = valt.split(":", 1)[0].strip() + ":"
                typeObj.getModel().setSelectedItem(modifiedFilter)
                if ("Scope items" not in valt) and ("Content-Len" not in valt):
                        textObj.setText(val)
                listObj.getModel().remove(index)