#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from gui.enforcement_detector import EnforcementDetectors
from gui.interception_filters import InterceptionFilters
from gui.configuration_tab import ConfigurationTab
from gui.match_replace import MatchReplace
from gui.tabs import Tabs, ITabImpl
from gui.table import TableFilter
from gui.export import Export
from gui.menu import MenuImpl
from gui.user_tab import UserTab

from java.util import ArrayList
from threading import Lock

class Initiator():
    def __init__(self, extender):
        self._extender = extender
    
    def init_constants(self):
        self.contributors = ["Federico Dotta", "mgeeky", "Marcin Woloszyn", "jpginc", "Eric Harris", "Joao Teles", "Roy Oswaldha"]
        self._extender.version = "1.9.4"
        self._extender._log = ArrayList()
        self._extender._lock = Lock()

        self._extender.BYPASSSED_STR = "Bypassed!"
        self._extender.IS_ENFORCED_STR = "Is enforced??? (please configure enforcement detector)"
        self._extender.ENFORCED_STR = "Enforced!"
        
        self._extender.intercept = 0
        self._extender.lastCookiesHeader = ""
        self._extender.lastAuthorizationHeader = ""

        self._extender.currentRequestNumber = 1
        self._extender.expanded_requests = 0
    
    def draw_all(self):
        interception_filters = InterceptionFilters(self._extender)
        interception_filters.draw()

        enforcement_detectors = EnforcementDetectors(self._extender)
        enforcement_detectors.draw()
        enforcement_detectors.draw_unauthenticated()
    
        export = Export(self._extender)
        export.draw()

        match_replace = MatchReplace(self._extender)
        match_replace.draw()

        table_filter = TableFilter(self._extender)
        table_filter.draw()

        cfg_tab = ConfigurationTab(self._extender)
        cfg_tab.draw()

        user_tab = UserTab(self._extender)
        user_tab.draw()

        self._extender.userTab = user_tab

        tabs = Tabs(self._extender)
        tabs.draw()
        self._extender.tabs_instance = tabs
    
    def implement_all(self):
        itab = ITabImpl(self._extender)
        menu = MenuImpl(self._extender)

        self._extender._callbacks.registerContextMenuFactory(menu)
        self._extender._callbacks.addSuiteTab(itab)
        self._extender._callbacks.registerHttpListener(self._extender)
        self._extender._callbacks.registerProxyListener(self._extender)


    def init_ui(self):
        self._extender._callbacks.customizeUiComponent(self._extender._splitpane)
        self._extender._callbacks.customizeUiComponent(self._extender.logTable)
        self._extender._callbacks.customizeUiComponent(self._extender.scrollPane)
        self._extender._callbacks.customizeUiComponent(self._extender.tabs)
        self._extender._callbacks.customizeUiComponent(self._extender.filtersTabs)

    def print_welcome_message(self):
        print("""Thank you for installing Autorize v{} extension
Created by Barak Tawily
Contributors: {}

Github:\nhttps://github.com/Quitten/Autorize""".format(self._extender.version, ", ".join(self.contributors)))
