#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from burp import IBurpExtender
from burp import IHttpListener

from authorization.authorization import handle_message

from helpers.initiator import Initiator

class BurpExtender(IBurpExtender, IHttpListener):

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
