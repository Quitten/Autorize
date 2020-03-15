#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from java.awt import GridLayout

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

def expand(extender, comp):
        comp.setSelectedIndex(0)
        comp.setTitleAt(2, "Collapse")
        extender.requests_panel.remove(extender.modified_requests_tabs)
        extender.requests_panel.remove(extender.original_requests_tabs)
        extender.requests_panel.remove(extender.unauthenticated_requests_tabs)
        extender.requests_panel.add(comp)
        extender.requests_panel.setLayout(GridLayout(1,0))
        extender.requests_panel.revalidate()
        extender.expanded_requests = 1

def collapse(extender, comp):
        comp.setSelectedIndex(0)
        comp.setTitleAt(2, "Expand")
        extender.requests_panel.setLayout(GridLayout(3,0))
        extender.requests_panel.add(extender.modified_requests_tabs)
        extender.requests_panel.add(extender.original_requests_tabs)
        extender.requests_panel.add(extender.unauthenticated_requests_tabs)
        extender.requests_panel.revalidate()
        extender.expanded_requests = 0
        