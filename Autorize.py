#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from burp import IBurpExtender, IHttpListener, IProxyListener
from authorization.authorization import handle_message
from helpers.initiator import Initiator
from helpers.filters import handle_proxy_message

class BurpExtender(IBurpExtender, IHttpListener, IProxyListener):

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        
        callbacks.setExtensionName("Autorize")
        
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
        handle_proxy_message(self,message)
        
