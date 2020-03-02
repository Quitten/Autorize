#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from burp import ITab
from burp import IBurpExtender
from burp import IHttpListener
from burp import IContextMenuFactory
from burp import IMessageEditorController

from javax.swing.table import AbstractTableModel
from javax.swing import JMenuItem
from java.util import LinkedList
from java.util import ArrayList
from java.lang import Integer
from java.lang import String
from threading import Lock
from java.net import URL

from tabs import init_tabs
from export import Export
from match_replace import init_match_replace
from configuration_tab import ConfigurationTab
from authorization import handle_message, handleMenuItems
from interception_filters import init_interception_filters
from table import init_filter
from enforcement_detector import init_enforcement_detector, init_enforcement_detector_unauthorized

#TODO
# - Disable buttons when saving state/restoring state/export
# - Add full headers in addition to cookies

class BurpExtender(IBurpExtender, ITab, IHttpListener, IMessageEditorController,
                   AbstractTableModel, IContextMenuFactory):

    def registerExtenderCallbacks(self, callbacks):
        # keep a reference to our callbacks object
        self._callbacks = callbacks
        # obtain an extension helpers object
        self._helpers = callbacks.getHelpers()
        
        # set our extension name
        callbacks.setExtensionName("Autorize")
        
        # create the log and a lock on which to synchronize when adding log
        # entries
        self._log = ArrayList()
        self._lock = Lock()

        self.BYPASSSED_STR = "Bypassed!"
        self.IS_ENFORCED_STR = "Is enforced??? (please configure enforcement detector)"
        self.ENFORCED_STR = "Enforced!"
        
        self.intercept = 0
        self.lastCookies = ""

        init_interception_filters(self)

        init_enforcement_detector(self)

        init_enforcement_detector_unauthorized(self)
    
        export = Export(self)
        export.draw()

        init_match_replace(self)

        init_filter(self)

        cfg_tab = ConfigurationTab(self)
        cfg_tab.draw()

        init_tabs(self)
        
        self.initCallbacks()

        self.currentRequestNumber = 1
        
        print("""Thank you for installing Autorize v0.22 extension
Created by Barak Tawily
Contributors: Barak Tawily, Federico Dotta, mgeeky, Marcin Woloszyn

Github:\nhttps://github.com/Quitten/Autorize
            """)
        return  

    def initCallbacks(self):
        """  init callbacks
        """

        # register HTTP listener
        self._callbacks.registerHttpListener(self)

        # customize our UI components
        self._callbacks.customizeUiComponent(self._splitpane)
        self._callbacks.customizeUiComponent(self.logTable)
        self._callbacks.customizeUiComponent(self.scrollPane)
        self._callbacks.customizeUiComponent(self.tabs)
        self._callbacks.customizeUiComponent(self.filtersTabs)
        self._callbacks.registerContextMenuFactory(self)

        # add the custom tab to Burp's UI
        self._callbacks.addSuiteTab(self)

    #
    # implement IContextMenuFactory
    #
    def createMenuItems(self, invocation):
        responses = invocation.getSelectedMessages()
        if responses > 0:
            ret = LinkedList()
            requestMenuItem = JMenuItem("Send request to Autorize")
            cookieMenuItem = JMenuItem("Send cookie to Autorize")

            for response in responses:
                requestMenuItem.addActionListener(handleMenuItems(self,response, "request"))
                cookieMenuItem.addActionListener(handleMenuItems(self, response, "cookie"))   
            ret.add(requestMenuItem)
            ret.add(cookieMenuItem)
            return ret
        return None

    #
    # implement ITab
    #
    def getTabCaption(self):
        return "Autorize"
    
    def getUiComponent(self):
        return self._splitpane
        
    #
    # extend AbstractTableModel
    #
    
    def getRowCount(self):
        try:
            return self._log.size()
        except:
            return 0

    def getColumnCount(self):
        return 8

    def getColumnName(self, columnIndex):
        data = ['ID','Method', 'URL', 'Orig. Length', 'Modif. Length', "Unauth. Length",
                "Authorization Enforcement Status", "Authorization Unauth. Status"]
        try:
            return data[columnIndex]
        except IndexError:
            return ""

    def getColumnClass(self, columnIndex):
        data = [Integer, String, String, Integer, Integer, Integer, String, String]
        try:
            return data[columnIndex]
        except IndexError:
            return ""

    def getValueAt(self, rowIndex, columnIndex):
        logEntry = self._log.get(rowIndex)
        if columnIndex == 0:
            return logEntry._id
        if columnIndex == 1:
            return logEntry._method
        if columnIndex == 2:
            return logEntry._url.toString()
        if columnIndex == 3:
            response = logEntry._originalrequestResponse.getResponse()
            return len(logEntry._originalrequestResponse.getResponse()) - self._helpers.analyzeResponse(response).getBodyOffset()
        if columnIndex == 4:
            response = logEntry._requestResponse.getResponse()
            return len(logEntry._requestResponse.getResponse()) - self._helpers.analyzeResponse(response).getBodyOffset()
        if columnIndex == 5:
            if logEntry._unauthorizedRequestResponse is not None:
                response = logEntry._unauthorizedRequestResponse.getResponse()
                return len(logEntry._unauthorizedRequestResponse.getResponse()) - self._helpers.analyzeResponse(response).getBodyOffset()
            else:
                return 0
        if columnIndex == 6:
            return logEntry._enfocementStatus   
        if columnIndex == 7:
            return logEntry._enfocementStatusUnauthorized        
        return ""

    #
    # implement IMessageEditorController
    # this allows our request/response viewers to obtain details about the
    # messages being displayed
    #
    
    def getHttpService(self):
        return self._currentlyDisplayedItem.getHttpService()

    def getRequest(self):
        return self._currentlyDisplayedItem.getRequest()

    def getResponse(self):
        return self._currentlyDisplayedItem.getResponse()

    #
    # implement IHttpListener
    #
    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):      
        handle_message(self, toolFlag, messageIsRequest, messageInfo)
