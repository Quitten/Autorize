#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from java.awt import GridLayout
from burp import IInterceptedProxyMessage

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
        try:
                last_idx = comp.getClientProperty("autorize-last-index")
        except Exception:
                last_idx = 0
        try:
                if isinstance(last_idx, int) and 0 <= last_idx < (comp.getTabCount() - 1):
                        comp.setSelectedIndex(last_idx)
                else:
                        comp.setSelectedIndex(0)
        except Exception:
                pass
        try:
                comp.setTitleAt(comp.getTabCount()-1, "Collapse")
        except Exception:
                pass
        extender.requests_panel.remove(extender.modified_requests_tabs)
        extender.requests_panel.remove(extender.original_requests_tabs)
        extender.requests_panel.remove(extender.unauthenticated_requests_tabs)
        extender.requests_panel.add(comp)
        extender.requests_panel.setLayout(GridLayout(1,0))
        extender.requests_panel.revalidate()
        extender.expanded_requests = 1

def collapse(extender, comp):
        try:
                comp.setTitleAt(comp.getTabCount()-1, "Expand")
        except Exception:
                pass
        extender.requests_panel.setLayout(GridLayout(3,0))
        extender.requests_panel.add(extender.modified_requests_tabs)
        extender.requests_panel.add(extender.original_requests_tabs)
        extender.requests_panel.add(extender.unauthenticated_requests_tabs)
        extender.requests_panel.revalidate()
        extender.expanded_requests = 0

def handle_proxy_message(self,message):
        currentPort = message.getListenerInterface().split(":")[1]
        for i in range(0, self.IFList.getModel().getSize()):
            interceptionFilter = self.IFList.getModel().getElementAt(i)
            interceptionFilterTitle = interceptionFilter.split(":")[0]
            if interceptionFilterTitle == "Drop proxy listener ports":
                portsList = interceptionFilter[27:].split(",")
                portsList = [int(i) for i in portsList]
                if int(currentPort) in portsList:
                    message.setInterceptAction(IInterceptedProxyMessage.ACTION_DROP)