#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from burp import IContextMenuFactory

from java.util import LinkedList
from javax.swing import JMenuItem
from java.awt.event import ActionListener

from authorization.authorization import send_request_to_autorize
from helpers.http import get_cookie_header_from_message, get_authorization_header_from_message

from thread import start_new_thread

class MenuImpl(IContextMenuFactory):
    def __init__(self, extender):
        self._extender = extender

    def createMenuItems(self, invocation):
        responses = invocation.getSelectedMessages()
        if responses > 0:
            ret = LinkedList()
            requestMenuItem = JMenuItem("Send request to Autorize")
            cookieMenuItem = JMenuItem("Send Cookie header to Autorize")
            authMenuItem = JMenuItem("Send Authorization header to Autorize")

            for response in responses:
                requestMenuItem.addActionListener(HandleMenuItems(self._extender,response, "request"))
                cookieMenuItem.addActionListener(HandleMenuItems(self._extender, response, "cookie"))
                authMenuItem.addActionListener(HandleMenuItems(self._extender, response, "authorization"))
            ret.add(requestMenuItem)
            ret.add(cookieMenuItem)
            ret.add(authMenuItem)
            return ret
        return None

class HandleMenuItems(ActionListener):
    def __init__(self, extender, messageInfo, menuName):
        self._extender = extender
        self._menuName = menuName
        self._messageInfo = messageInfo

    def actionPerformed(self, e):
        if self._menuName == "request":
            start_new_thread(send_request_to_autorize, (self._extender, self._messageInfo,))

        if self._menuName == "cookie":
            cookie = get_cookie_header_from_message(self._extender, self._messageInfo)
            if cookie:
                active_user = self._get_active_user_data()
                if active_user:
                    active_user['headers_instance'].replaceString.setText(cookie)
        
        if self._menuName == "authorization":
            auth = get_authorization_header_from_message(self._extender, self._messageInfo)
            if auth:
                active_user = self._get_active_user_data()
                if active_user:
                    active_user['headers_instance'].replaceString.setText(auth)

    def _get_active_user_data(self):
        if hasattr(self._extender, 'userTab') and self._extender.userTab:
            selected_index = self._extender.userTab.userTabs.getSelectedIndex()
            if selected_index >= 0:
                selected_panel = self._extender.userTab.userTabs.getComponentAt(selected_index)
                for user_id, user_data in self._extender.userTab.user_tabs.items():
                    if user_data['panel'] == selected_panel:
                        return user_data
        return None
