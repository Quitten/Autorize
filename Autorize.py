#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from burp import IBurpExtender, IHttpListener, IProxyListener, IExtensionStateListener
from authorization.authorization import handle_message
from helpers.initiator import Initiator
from helpers.filters import handle_proxy_message
from java.util.concurrent import Executors

class BurpExtender(IBurpExtender, IHttpListener, IProxyListener, IExtensionStateListener):

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        
        callbacks.setExtensionName("Autorize")
        
        self.executor = Executors.newFixedThreadPool(10)
        callbacks.registerExtensionStateListener(self)

        initiator = Initiator(self)

        initiator.init_constants()
        
        initiator.draw_all()

        initiator.implement_all()

        initiator.init_ui() 
        
        initiator.print_welcome_message()
        
        return

    #
    # implement IHttpListener
    #
    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):      
        handle_message(self, toolFlag, messageIsRequest, messageInfo)

    #
    # implement IProxyListener
    #
    def processProxyMessage(self, messageIsRequest, message):
        handle_proxy_message(self, message)

    #
    # implement IExtensionStateListener
    #
    def extensionUnloaded(self):
        self.executor.shutdown()
        print "Autorize extension unloaded."
