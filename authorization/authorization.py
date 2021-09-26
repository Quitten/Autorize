#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sys  
reload(sys)  

sys.setdefaultencoding('utf8')
sys.path.append("..")

from helpers.http import get_authorization_header_from_message, get_cookie_header_from_message, isStatusCodesReturned, makeMessage, makeRequest, getResponseContentLength, IHttpRequestResponseImplementation
from gui.table import LogEntry, UpdateTableEDT
from javax.swing import SwingUtilities
from java.net import URL
import re

def tool_needs_to_be_ignored(self, toolFlag):
    for i in range(0, self.IFList.getModel().getSize()):
        if self.IFList.getModel().getElementAt(i).split(":")[0] == "Ignore spider requests":
            if (toolFlag == self._callbacks.TOOL_SPIDER):
                return True
        if self.IFList.getModel().getElementAt(i).split(":")[0] == "Ignore proxy requests":
            if (toolFlag == self._callbacks.TOOL_PROXY):
                return True
        if self.IFList.getModel().getElementAt(i).split(":")[0] == "Ignore target requests":
            if (toolFlag == self._callbacks.TOOL_TARGET):
                return True
    return False

def capture_last_cookie_header(self, messageInfo):
    cookies = get_cookie_header_from_message(self, messageInfo)
    if cookies:
        self.lastCookiesHeader = cookies
        self.fetchCookiesHeaderButton.setEnabled(True)

def capture_last_authorization_header(self, messageInfo):
    authorization = get_authorization_header_from_message(self, messageInfo)
    if authorization:
        self.lastAuthorizationHeader = authorization
        self.fetchAuthorizationHeaderButton.setEnabled(True)


def valid_tool(self, toolFlag):
    return (toolFlag == self._callbacks.TOOL_PROXY or
            (toolFlag == self._callbacks.TOOL_REPEATER and
            self.interceptRequestsfromRepeater.isSelected()))

def handle_304_status_code_prevention(self, messageIsRequest, messageInfo):
    should_prevent = False
    if self.prevent304.isSelected():
        if messageIsRequest:
            requestHeaders = list(self._helpers.analyzeRequest(messageInfo).getHeaders())
            newHeaders = list()   
            for header in requestHeaders:
                if not "If-None-Match:" in header and not "If-Modified-Since:" in header:
                    newHeaders.append(header)
                    should_prevent = True
        if should_prevent:
            requestInfo = self._helpers.analyzeRequest(messageInfo)
            bodyBytes = messageInfo.getRequest()[requestInfo.getBodyOffset():]
            bodyStr = self._helpers.bytesToString(bodyBytes)
            messageInfo.setRequest(self._helpers.buildHttpMessage(newHeaders, bodyStr))
    
def message_not_from_autorize(self, messageInfo):
    return not self.replaceString.getText() in self._helpers.analyzeRequest(messageInfo).getHeaders()

def no_filters_defined(self):
    return self.IFList.getModel().getSize() == 0

def message_passed_interception_filters(self, messageInfo):
    urlString = str(self._helpers.analyzeRequest(messageInfo).getUrl())
    reqInfo = self._helpers.analyzeRequest(messageInfo)
    reqBodyBytes = messageInfo.getRequest()[reqInfo.getBodyOffset():]
    bodyStr = self._helpers.bytesToString(reqBodyBytes)

    resInfo = self._helpers.analyzeResponse(messageInfo.getResponse())
    resBodyBytes = messageInfo.getResponse()[resInfo.getBodyOffset():]
    resStr = self._helpers.bytesToString(resBodyBytes)

    message_passed_filters = True
    for i in range(0, self.IFList.getModel().getSize()):
        if self.IFList.getModel().getElementAt(i).split(":")[0] == "Scope items only":
            currentURL = URL(urlString)
            if not self._callbacks.isInScope(currentURL):
                message_passed_filters = False

        if self.IFList.getModel().getElementAt(i).split(":")[0] == "URL Contains (simple string)":
            if self.IFList.getModel().getElementAt(i)[30:] not in urlString:
                message_passed_filters = False

        if self.IFList.getModel().getElementAt(i).split(":")[0] == "URL Contains (regex)":
            regex_string = self.IFList.getModel().getElementAt(i)[22:]
            if re.search(regex_string, urlString, re.IGNORECASE) is None:
                message_passed_filters = False

        if self.IFList.getModel().getElementAt(i).split(":")[0] == "URL Not Contains (simple string)":
            if self.IFList.getModel().getElementAt(i)[34:] in urlString:
                message_passed_filters = False

        if self.IFList.getModel().getElementAt(i).split(":")[0] == "URL Not Contains (regex)":
            regex_string = self.IFList.getModel().getElementAt(i)[26:]
            if not re.search(regex_string, urlString, re.IGNORECASE) is None:
                message_passed_filters = False

        if self.IFList.getModel().getElementAt(i).split(":")[0] == "Request Body contains (simple string)":
            if self.IFList.getModel().getElementAt(i)[40:] not in bodyStr:
                message_passed_filters = False
                
        if self.IFList.getModel().getElementAt(i).split(":")[0] == "Request Body contains (regex)":
            regex_string = self.IFList.getModel().getElementAt(i)[32:]
            if re.search(regex_string, bodyStr, re.IGNORECASE) is None:
                message_passed_filters = False
        
        if self.IFList.getModel().getElementAt(i).split(":")[0] == "Request Body NOT contains (simple string)":
            if self.IFList.getModel().getElementAt(i)[44:] in bodyStr:
                message_passed_filters = False
                
        if self.IFList.getModel().getElementAt(i).split(":")[0] == "Request Body Not contains (regex)":
            regex_string = self.IFList.getModel().getElementAt(i)[36:]
            if not re.search(regex_string, bodyStr, re.IGNORECASE) is None:
                message_passed_filters = False

        if self.IFList.getModel().getElementAt(i).split(":")[0] == "Response Body contains (simple string)":
            if self.IFList.getModel().getElementAt(i)[41:] not in resStr:
                message_passed_filters = False

        if self.IFList.getModel().getElementAt(i).split(":")[0] == "Response Body contains (regex)":
            regex_string = self.IFList.getModel().getElementAt(i)[33:]
            if re.search(regex_string, resStr, re.IGNORECASE) is None:
                message_passed_filters = False

        if self.IFList.getModel().getElementAt(i).split(":")[0] == "Response Body NOT contains (simple string)":
            if self.IFList.getModel().getElementAt(i)[45:] in resStr:
                message_passed_filters = False
                
        if self.IFList.getModel().getElementAt(i).split(":")[0] == "Response Body Not contains (regex)":
            regex_string = self.IFList.getModel().getElementAt(i)[37:]
            if not re.search(regex_string, resStr, re.IGNORECASE) is None:
                message_passed_filters = False

        if self.IFList.getModel().getElementAt(i).split(":")[0] == "Only HTTP methods (newline separated)":
            filterMethods = self.IFList.getModel().getElementAt(i)[39:].split("\n")
            filterMethods = [x.lower() for x in filterMethods]
            reqMethod = str(self._helpers.analyzeRequest(messageInfo).getMethod())
            if reqMethod.lower() not in filterMethods:
                message_passed_filters = False

        if self.IFList.getModel().getElementAt(i).split(":")[0] == "Ignore HTTP methods (newline separated)":
            filterMethods = self.IFList.getModel().getElementAt(i)[41:].split("\n")
            filterMethods = [x.lower() for x in filterMethods]
            reqMethod = str(self._helpers.analyzeRequest(messageInfo).getMethod())
            if reqMethod.lower() in filterMethods:
                message_passed_filters = False

    return message_passed_filters

def handle_message(self, toolFlag, messageIsRequest, messageInfo):
    if tool_needs_to_be_ignored(self, toolFlag):
        return

    capture_last_cookie_header(self, messageInfo)
    capture_last_authorization_header(self, messageInfo)

    if (self.intercept and valid_tool(self, toolFlag) or toolFlag == "AUTORIZE"):
        handle_304_status_code_prevention(self, messageIsRequest, messageInfo)
    
        if not messageIsRequest:
            if message_not_from_autorize(self, messageInfo):
                if self.ignore304.isSelected():
                    if isStatusCodesReturned(self, messageInfo, ["304", "204"]):
                        return

                if no_filters_defined(self):
                    checkAuthorization(self, messageInfo,
                    self._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders(),
                                            self.doUnauthorizedRequest.isSelected())
                else:
                    if message_passed_interception_filters(self, messageInfo):
                        checkAuthorization(self, messageInfo,self._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders(),self.doUnauthorizedRequest.isSelected())

def send_request_to_autorize(self, messageInfo):
    if messageInfo.getResponse() is None:
        message = makeMessage(self, messageInfo,False,False)
        requestResponse = makeRequest(self, messageInfo, message)
        checkAuthorization(self, requestResponse,self._helpers.analyzeResponse(requestResponse.getResponse()).getHeaders(),self.doUnauthorizedRequest.isSelected())
    else:
        request = messageInfo.getRequest()
        response = messageInfo.getResponse()
        httpService = messageInfo.getHttpService()
        newHttpRequestResponse = IHttpRequestResponseImplementation(httpService,request,response)
        newHttpRequestResponsePersisted = self._callbacks.saveBuffersToTempFiles(newHttpRequestResponse)
        checkAuthorization(self, newHttpRequestResponsePersisted,self._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders(),self.doUnauthorizedRequest.isSelected())

def auth_enforced_via_enforcement_detectors(self, filters, requestResponse, andOrEnforcement):
    response = requestResponse.getResponse()
    analyzedResponse = self._helpers.analyzeResponse(response)
    auth_enforced = False
    if andOrEnforcement == "And":
        andEnforcementCheck = True
        auth_enforced = True
    else:
        andEnforcementCheck = False
        auth_enforced = False
    
    response = requestResponse.getResponse()
    for filter in filters:
        filter = self._helpers.bytesToString(bytes(filter))
        if filter.startswith("Status code equals: "):
            statusCode = filter[20:]
            if andEnforcementCheck:
                if auth_enforced and not isStatusCodesReturned(self, requestResponse, statusCode):
                    auth_enforced = False
            else:
                if not auth_enforced and isStatusCodesReturned(self, requestResponse, statusCode):
                    auth_enforced = True

        if filter.startswith("Headers (simple string): "):
            if andEnforcementCheck:
                if auth_enforced and not filter[25:] in self._helpers.bytesToString(requestResponse.getResponse()[0:analyzedResponse.getBodyOffset()]):
                    auth_enforced = False
            else:
                if not auth_enforced and filter[25:] in self._helpers.bytesToString(requestResponse.getResponse()[0:analyzedResponse.getBodyOffset()]):
                    auth_enforced = True

        if filter.startswith("Headers (regex): "):
            regex_string = filter[17:]
            p = re.compile(regex_string, re.IGNORECASE)                        
            if andEnforcementCheck:
                if auth_enforced and not p.search(self._helpers.bytesToString(requestResponse.getResponse()[0:analyzedResponse.getBodyOffset()])):
                    auth_enforced = False
            else:
                if not auth_enforced and p.search(self._helpers.bytesToString(requestResponse.getResponse()[0:analyzedResponse.getBodyOffset()])):
                    auth_enforced = True

        if filter.startswith("Body (simple string): "):
            if andEnforcementCheck:
                if auth_enforced and not filter[22:] in self._helpers.bytesToString(requestResponse.getResponse()[analyzedResponse.getBodyOffset():]):
                    auth_enforced = False
            else:
                if not auth_enforced and filter[22:] in self._helpers.bytesToString(requestResponse.getResponse()[analyzedResponse.getBodyOffset():]):
                    auth_enforced = True

        if filter.startswith("Body (regex): "):
            regex_string = filter[14:]
            p = re.compile(regex_string, re.IGNORECASE)
            if andEnforcementCheck:
                if auth_enforced and not p.search(self._helpers.bytesToString(requestResponse.getResponse()[analyzedResponse.getBodyOffset():])):
                    auth_enforced = False
            else:
                if not auth_enforced and p.search(self._helpers.bytesToString(requestResponse.getResponse()[analyzedResponse.getBodyOffset():])):
                    auth_enforced = True

        if filter.startswith("Full response (simple string): "):
            if andEnforcementCheck:
                if auth_enforced and not filter[31:] in self._helpers.bytesToString(requestResponse.getResponse()):
                    auth_enforced = False
            else:
                if not auth_enforced and filter[31:] in self._helpers.bytesToString(requestResponse.getResponse()):
                    auth_enforced = True

        if filter.startswith("Full response (regex): "):
            regex_string = filter[23:]
            p = re.compile(regex_string, re.IGNORECASE)
            if andEnforcementCheck:
                if auth_enforced and not p.search(self._helpers.bytesToString(requestResponse.getResponse())):
                    auth_enforced = False
            else:
                if not auth_enforced and p.search(self._helpers.bytesToString(requestResponse.getResponse())):
                    auth_enforced = True

        if filter.startswith("Full response length: "):
            if andEnforcementCheck:
                if auth_enforced and not str(len(response)) == filter[22:].strip():
                    auth_enforced = False
            else:
                if not auth_enforced and str(len(response)) == filter[22:].strip():
                    auth_enforced = True
        return auth_enforced

def checkBypass(self, oldStatusCode, newStatusCode, oldContentLen,
                 newContentLen, filters, requestResponse, andOrEnforcement):
    if oldStatusCode == newStatusCode:
        auth_enforced = 0
        if len(filters) > 0:
            auth_enforced = auth_enforced_via_enforcement_detectors(self, filters, requestResponse, andOrEnforcement)
        if auth_enforced:
            return self.ENFORCED_STR
        elif oldContentLen == newContentLen:
            return self.BYPASSSED_STR
        else:
            return self.IS_ENFORCED_STR
    else:
        return self.ENFORCED_STR

def checkAuthorization(self, messageInfo, originalHeaders, checkUnauthorized):
    oldResponse = messageInfo.getResponse()
    message = makeMessage(self, messageInfo, True, True)
    requestResponse = makeRequest(self, messageInfo, message)
    newResponse = requestResponse.getResponse()
    analyzedResponse = self._helpers.analyzeResponse(newResponse)
    
    oldStatusCode = originalHeaders[0]
    newStatusCode = analyzedResponse.getHeaders()[0]
    oldContentLen = getResponseContentLength(self, oldResponse)
    newContentLen = getResponseContentLength(self, newResponse)

    # Check unauthorized request
    if checkUnauthorized:
        messageUnauthorized = makeMessage(self, messageInfo, True, False)
        requestResponseUnauthorized = makeRequest(self, messageInfo, messageUnauthorized)
        unauthorizedResponse = requestResponseUnauthorized.getResponse()
        analyzedResponseUnauthorized = self._helpers.analyzeResponse(unauthorizedResponse)  
        statusCodeUnauthorized = analyzedResponseUnauthorized.getHeaders()[0]
        contentLenUnauthorized = getResponseContentLength(self, unauthorizedResponse)

    EDFilters = self.EDModel.toArray()

    impression = checkBypass(self, oldStatusCode,newStatusCode,oldContentLen,newContentLen,EDFilters,requestResponse,self.AndOrType.getSelectedItem())

    if checkUnauthorized:
        EDFiltersUnauth = self.EDModelUnauth.toArray()
        impressionUnauthorized = checkBypass(self, oldStatusCode,statusCodeUnauthorized,oldContentLen,contentLenUnauthorized,EDFiltersUnauth,requestResponseUnauthorized,self.AndOrTypeUnauth.getSelectedItem())

    self._lock.acquire()
    
    row = self._log.size()
    method = self._helpers.analyzeRequest(messageInfo.getRequest()).getMethod()
    
    if checkUnauthorized:
        self._log.add(LogEntry(self.currentRequestNumber,self._callbacks.saveBuffersToTempFiles(requestResponse), method, self._helpers.analyzeRequest(requestResponse).getUrl(),messageInfo,impression,self._callbacks.saveBuffersToTempFiles(requestResponseUnauthorized),impressionUnauthorized)) # same requests not include again.
    else:
        self._log.add(LogEntry(self.currentRequestNumber,self._callbacks.saveBuffersToTempFiles(requestResponse), method, self._helpers.analyzeRequest(requestResponse).getUrl(),messageInfo,impression,None,"Disabled")) # same requests not include again.
    
    SwingUtilities.invokeLater(UpdateTableEDT(self,"insert",row,row))
    self.currentRequestNumber = self.currentRequestNumber + 1
    self._lock.release()
    
def checkAuthorizationV2(self, messageInfo):
    checkAuthorization(self, messageInfo, self._extender._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders(), self._extender.doUnauthorizedRequest.isSelected())

def retestAllRequests(self):
    for i in range(self.tableModel.getRowCount()):
        logEntry = self._log.get(self.logTable.convertRowIndexToModel(i))
        handle_message(self, "AUTORIZE", False, logEntry._originalrequestResponse)