#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from burp import IContextMenuFactory

from java.util import LinkedList
from javax.swing import JMenuItem
from java.awt.event import ActionListener

from thread import start_new_thread

class MenuImpl(IContextMenuFactory):
    def __init__(self, extender):
        self._extender = extender

    def createMenuItems(self, invocation):
        responses = invocation.getSelectedMessages()
        if responses > 0:
            ret = LinkedList()
            requestMenuItem = JMenuItem("Send request to Autorize")
            cookieMenuItem = JMenuItem("Send cookie to Autorize")

            for response in responses:
                requestMenuItem.addActionListener(HandleMenuItems(self._extender,response, "request"))
                cookieMenuItem.addActionListener(HandleMenuItems(self._extender, response, "cookie"))   
            ret.add(requestMenuItem)
            ret.add(cookieMenuItem)
            return ret
        return None

class HandleMenuItems(ActionListener):
    def __init__(self, extender, messageInfo, menuName):
        self._extender = extender
        self._menuName = menuName
        self._messageInfo = messageInfo

    def actionPerformed(self, e):
        if self._menuName == "request":
            start_new_thread(self._extender.sendRequestToAutorizeWork,(self._messageInfo,))

        if self._menuName == "cookie":
            self._extender.replaceString.setText(self._extender.getCookieFromMessage(self._messageInfo))
