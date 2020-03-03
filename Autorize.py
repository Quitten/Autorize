#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from burp import IBurpExtender
from burp import IHttpListener

from java.util import ArrayList
from threading import Lock

from gui.enforcement_detector import EnforcementDetectors
from authorization.authorization import handle_message
from gui.interception_filters import InterceptionFilters
from gui.configuration_tab import ConfigurationTab
from gui.match_replace import MatchReplace
from table.table import TableFilter
from gui.export import Export
from gui.tabs import Tabs, ITabImpl
from helpers.menu import MenuImpl

class BurpExtender(IBurpExtender, IHttpListener):

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        
        callbacks.setExtensionName("Autorize")
        
        self._log = ArrayList()
        self._lock = Lock()

        self.BYPASSSED_STR = "Bypassed!"
        self.IS_ENFORCED_STR = "Is enforced??? (please configure enforcement detector)"
        self.ENFORCED_STR = "Enforced!"
        
        self.intercept = 0
        self.lastCookies = ""
        self.currentRequestNumber = 1

        interception_filters = InterceptionFilters(self)
        interception_filters.draw()

        enforcement_detectors = EnforcementDetectors(self)
        enforcement_detectors.draw()
        enforcement_detectors.draw_unauthenticated()
    
        export = Export(self)
        export.draw()

        match_replace = MatchReplace(self)
        match_replace.draw()

        table_filter = TableFilter(self)
        table_filter.draw()

        cfg_tab = ConfigurationTab(self)
        cfg_tab.draw()

        tabs = Tabs(self)
        tabs.draw()
        
        itab = ITabImpl(self)
        menu = MenuImpl(self)

        self._callbacks.registerHttpListener(self)
        
        self._callbacks.customizeUiComponent(self._splitpane)
        self._callbacks.customizeUiComponent(self.logTable)
        self._callbacks.customizeUiComponent(self.scrollPane)
        self._callbacks.customizeUiComponent(self.tabs)
        self._callbacks.customizeUiComponent(self.filtersTabs)
        self._callbacks.registerContextMenuFactory(menu)
        
        self._callbacks.addSuiteTab(itab)
        
        print("""Thank you for installing Autorize v1.23 extension
Created by Barak Tawily
Contributors: Barak Tawily, Federico Dotta, mgeeky, Marcin Woloszyn

Github:\nhttps://github.com/Quitten/Autorize
            """)
        return

    #
    # implement IHttpListener
    #
    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):      
        handle_message(self, toolFlag, messageIsRequest, messageInfo)
