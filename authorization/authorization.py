#!/usr/bin/env python
# -*- coding: utf-8 -*-

from operator import truediv
import sys
reload(sys)

if (sys.version_info[0] == 2):
    sys.setdefaultencoding('utf8')

sys.path.append("..")

from helpers.http import get_authorization_header_from_message, get_cookie_header_from_message, isStatusCodesReturned, makeMessage, makeRequest, getResponseBody, IHttpRequestResponseImplementation
from gui.table import LogEntry, UpdateTableEDT
from javax.swing import SwingUtilities
from java.net import URL
import re

from thread import start_new_thread

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

    for i in range(0, self.IFList.getModel().getSize()):
        interceptionFilter = self.IFList.getModel().getElementAt(i)
        try:
            interceptionFilterTitle, interceptionFilterContent = interceptionFilter.split(":", 1)
            interceptionFilterContent = interceptionFilterContent[1:]
        except Exception as e:
            print(interceptionFilter)
            print(e)
            continue

        if interceptionFilterTitle == "Scope items only":
            currentURL = URL(urlString)
            if not self._callbacks.isInScope(currentURL):
                return False

        if interceptionFilterTitle == "URL Contains (simple string)":
            if interceptionFilterContent not in urlString:
                return False

        if interceptionFilterTitle == "URL Contains (regex)":
            regex_string = interceptionFilterContent
            if re.search(regex_string, urlString, re.IGNORECASE) is None:
                return False

        if interceptionFilterTitle == "URL Not Contains (simple string)":
            if interceptionFilterContent in urlString:
                return False

        if interceptionFilterTitle == "URL Not Contains (regex)":
            regex_string = interceptionFilterContent
            if not re.search(regex_string, urlString, re.IGNORECASE) is None:
                return False

        if interceptionFilterTitle == "Request Body contains (simple string)":
            if interceptionFilterContent not in bodyStr:
                return False

        if interceptionFilterTitle == "Request Body contains (regex)":
            regex_string = interceptionFilterContent
            if re.search(regex_string, bodyStr, re.IGNORECASE) is None:
                return False

        if interceptionFilterTitle == "Request Body NOT contains (simple string)":
            if interceptionFilterContent in bodyStr:
                return False

        if interceptionFilterTitle == "Request Body Not contains (regex)":
            regex_string = interceptionFilterContent
            if not re.search(regex_string, bodyStr, re.IGNORECASE) is None:
                return False

        if interceptionFilterTitle == "Response Body contains (simple string)":
            if interceptionFilterContent not in resStr:
                return False

        if interceptionFilterTitle == "Response Body contains (regex)":
            regex_string = interceptionFilterContent
            if re.search(regex_string, resStr, re.IGNORECASE) is None:
                return False

        if interceptionFilterTitle == "Response Body NOT contains (simple string)":
            if interceptionFilterContent in resStr:
                return False

        if interceptionFilterTitle == "Response Body Not contains (regex)":
            regex_string = interceptionFilterContent
            if not re.search(regex_string, resStr, re.IGNORECASE) is None:
                return False

        if interceptionFilterTitle == "Request headers contain":
            if not any([
                interceptionFilterContent in h 
                for h in reqInfo.getHeaders()
            ]):
                return False

        if interceptionFilterTitle == "Request headers don't contain":
            if any([
                interceptionFilterContent in h 
                for h in reqInfo.getHeaders()
            ]):
                return False
        
        if interceptionFilterTitle == "Response headers contain":
            if not any([
                interceptionFilterContent in h 
                for h in resInfo.getHeaders()
            ]):
                return False

        if interceptionFilterTitle == "Response headers don't contain":
            if any([
                interceptionFilterContent in h 
                for h in resInfo.getHeaders()
            ]):
                return False

        if interceptionFilterTitle == "Only HTTP methods (newline separated)":
            filterMethods = interceptionFilterContent.split("\n")
            filterMethods = [x.lower() for x in filterMethods]
            reqMethod = str(self._helpers.analyzeRequest(messageInfo).getMethod())
            if reqMethod.lower() not in filterMethods:
                return False

        if interceptionFilterTitle == "Ignore HTTP methods (newline separated)":
            filterMethods = interceptionFilterContent.split("\n")
            filterMethods = [x.lower() for x in filterMethods]
            reqMethod = str(self._helpers.analyzeRequest(messageInfo).getMethod())
            if reqMethod.lower() in filterMethods:
                return False

        if interceptionFilterTitle == "Ignore OPTIONS requests":
            reqMethod = str(self._helpers.analyzeRequest(messageInfo).getMethod())
            if reqMethod == "OPTIONS":
                return False

    return True

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
                    # checkAuthorization(self, messageInfo,
                    # self._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders(),
                    #                         self.doUnauthorizedRequest.isSelected())
                    checkAuthorizationAllUsers(self, messageInfo, self.doUnauthorizedRequest.isSelected())
                else:
                    if message_passed_interception_filters(self, messageInfo):
                        # checkAuthorization(self, messageInfo,self._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders(),self.doUnauthorizedRequest.isSelected())
                        checkAuthorizationAllUsers(self, messageInfo, self.doUnauthorizedRequest.isSelected())

def checkAuthorizationAllUsers(self, messageInfo, checkUnauthorized=True):    
    originalHeaders = self._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders()
    
    requestResponseUnauthorized = None
    impressionUnauthorized = "Disabled"
    
    if checkUnauthorized:
        messageUnauthorized = makeMessage(self, messageInfo, True, False)
        requestResponseUnauthorized = makeRequest(self, messageInfo, messageUnauthorized)
        if requestResponseUnauthorized and requestResponseUnauthorized.getResponse():
            unauthorizedResponse = requestResponseUnauthorized.getResponse()
            analyzedResponseUnauthorized = self._helpers.analyzeResponse(unauthorizedResponse)
            statusCodeUnauthorized = analyzedResponseUnauthorized.getHeaders()[0]
            contentUnauthorized = getResponseBody(self, requestResponseUnauthorized)

            message = makeMessage(self, messageInfo, True, True)
            requestResponse = makeRequest(self, messageInfo, message)
            newResponse = requestResponse.getResponse()
            analyzedResponse = self._helpers.analyzeResponse(newResponse)

            oldStatusCode = originalHeaders[0]
            newStatusCode = analyzedResponse.getHeaders()[0]
            oldContent = getResponseBody(self, messageInfo)
            newContent = getResponseBody(self, requestResponse)

            EDFiltersUnauth = self.EDModelUnauth.toArray()
            impressionUnauthorized = checkBypass(self, oldStatusCode, statusCodeUnauthorized,
                                                oldContent, contentUnauthorized,
                                                EDFiltersUnauth, requestResponseUnauthorized,
                                                self.AndOrTypeUnauth.getSelectedItem())
            
    self._lock.acquire()
    
    row = self._log.size()
    method = self._helpers.analyzeRequest(messageInfo.getRequest()).getMethod()
    original_url = self._helpers.analyzeRequest(messageInfo).getUrl()
    
    logEntry = LogEntry(self.currentRequestNumber, 
                       method, 
                       original_url,
                       messageInfo, 
                       requestResponseUnauthorized if checkUnauthorized else None, 
                       impressionUnauthorized)
    
    for user_id, user_data in self.userTab.user_tabs.items():
        user_name = user_data['user_name']
        ed_instance = user_data['ed_instance']
        mr_instance = user_data['mr_instance']
        
        message = makeUserMessage(self, messageInfo, True, True, mr_instance)
        requestResponse = makeRequest(self, messageInfo, message)
        
        if requestResponse and requestResponse.getResponse():
            newResponse = requestResponse.getResponse()
            analyzedResponse = self._helpers.analyzeResponse(newResponse)
            newStatusCode = analyzedResponse.getHeaders()[0]
            oldContent = getResponseBody(self, messageInfo)
            newContent = getResponseBody(self, requestResponse)
            
            EDFilters = ed_instance.EDModel.toArray()
            impression = checkBypass(self, originalHeaders[0], newStatusCode, oldContent, newContent, 
                                   EDFilters, requestResponse, ed_instance.AndOrType.getSelectedItem())
            
            savedRequestResponse = self._callbacks.saveBuffersToTempFiles(requestResponse)
            logEntry.add_user_enforcement(user_id, savedRequestResponse, impression)
    
    self._log.add(logEntry)
    SwingUtilities.invokeLater(UpdateTableEDT(self,"insert",row,row))
    self.currentRequestNumber = self.currentRequestNumber + 1
    self._lock.release()

def makeUserMessage(self, messageInfo, removeOrNot, authorizeOrNot, mr_instance):
    requestInfo = self._helpers.analyzeRequest(messageInfo)
    headers = list(requestInfo.getHeaders())
    
    if removeOrNot:
        if hasattr(self, 'replaceString') and self.replaceString.getText():
            removeHeaders = self.replaceString.getText().split('\n')
            removeHeaders = [header.split(':')[0].strip() + ':' for header in removeHeaders if ':' in header]
            
            headers_to_remove = []
            for header in headers[1:]:
                for removeHeader in removeHeaders:
                    if header.lower().startswith(removeHeader.lower()):
                        headers_to_remove.append(header)
            
            for header in headers_to_remove:
                if header in headers:
                    headers.remove(header)

        if authorizeOrNot:
            for i in range(mr_instance.MRModel.getSize()):
                rule_key = mr_instance.MRModel.getElementAt(i)
                rule_data = mr_instance.badProgrammerMRModel.get(rule_key)
                
                if rule_data:
                    rule_type = rule_data['type']
                    match_pattern = rule_data['match']
                    replace_pattern = rule_data['replace']
                    regex_match = rule_data.get('regexMatch')
                    
                    if rule_type == "Headers (simple string):":
                        modifiedHeaders = [h.replace(match_pattern, replace_pattern) for h in headers[1:]]
                        headers = [headers[0]] + modifiedHeaders
                    elif rule_type == "Headers (regex):":
                        if regex_match:
                            modifiedHeaders = [regex_match.sub(replace_pattern, h) for h in headers[1:]]
                            headers = [headers[0]] + modifiedHeaders

            if hasattr(self, 'replaceString') and self.replaceString.getText():
                replaceStringLines = self.replaceString.getText().split("\n")
                for h in replaceStringLines:
                    if h.strip() and ':' in h:
                        headers.append(h.strip())

    msgBody = messageInfo.getRequest()[requestInfo.getBodyOffset():]

    if authorizeOrNot and msgBody is not None:
        msgBody_str = self._helpers.bytesToString(msgBody)
        
        for i in range(mr_instance.MRModel.getSize()):
            rule_key = mr_instance.MRModel.getElementAt(i)
            rule_data = mr_instance.badProgrammerMRModel.get(rule_key)
            
            if rule_data:
                rule_type = rule_data['type']
                match_pattern = rule_data['match']
                replace_pattern = rule_data['replace']
                regex_match = rule_data.get('regexMatch')
                
                if rule_type == "Path (simple string):":
                    uriPath = headers[0].split(" ")[1]
                    if match_pattern in uriPath:
                        headers[0] = headers[0].replace(match_pattern, replace_pattern)
                elif rule_type == "Path (regex):":
                    if regex_match:
                        uriPath = headers[0].split(" ")[1]
                        if regex_match.search(uriPath):
                            headers[0] = regex_match.sub(replace_pattern, headers[0])
                
                elif rule_type == "Body (simple string):":
                    msgBody_str = msgBody_str.replace(match_pattern, replace_pattern)
                elif rule_type == "Body (regex):":
                    if regex_match:
                        msgBody_str = regex_match.sub(replace_pattern, msgBody_str)
        
        msgBody = self._helpers.stringToBytes(msgBody_str)
    
    return self._helpers.buildHttpMessage(headers, msgBody)

def send_request_to_autorize(self, messageInfo):
    if messageInfo.getResponse() is None:
        message = makeMessage(self, messageInfo,False,False)
        requestResponse = makeRequest(self, messageInfo, message)
        # checkAuthorization(self, requestResponse,self._helpers.analyzeResponse(requestResponse.getResponse()).getHeaders(),self.doUnauthorizedRequest.isSelected())
        checkAuthorizationAllUsers(self, requestResponse, self.doUnauthorizedRequest.isSelected())
    else:
        request = messageInfo.getRequest()
        response = messageInfo.getResponse()
        httpService = messageInfo.getHttpService()
        newHttpRequestResponse = IHttpRequestResponseImplementation(httpService,request,response)
        newHttpRequestResponsePersisted = self._callbacks.saveBuffersToTempFiles(newHttpRequestResponse)
        
        checkAuthorizationAllUsers(self, newHttpRequestResponsePersisted, self.doUnauthorizedRequest.isSelected())

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

    for filter in filters:
        filter = self._helpers.bytesToString(bytes(filter))
        inverse = "NOT" in filter
        filter = filter.replace(" NOT", "")
        filter_name, filter_content = filter.split(':', 1)
        filter_content = filter_content[1:]  # remove the ' '
        
        if filter_name == "Status code equals":
            statusCode = filter_content
            filterMatched = inverse ^ isStatusCodesReturned(self, requestResponse, statusCode)

        elif filter_name == "Headers (simple string)":
            filterMatched = inverse ^ (filter_content in self._helpers.bytesToString(requestResponse.getResponse()[0:analyzedResponse.getBodyOffset()]))

        elif filter_name == "Headers (regex)":
            regex_string = filter_content
            p = re.compile(regex_string, re.IGNORECASE)
            filterMatched = inverse ^ bool(p.search(self._helpers.bytesToString(requestResponse.getResponse()[0:analyzedResponse.getBodyOffset()])))

        elif filter_name == "Body (simple string)":
            filterMatched = inverse ^ (filter_content in self._helpers.bytesToString(requestResponse.getResponse()[analyzedResponse.getBodyOffset():]))

        elif filter_name == "Body (regex)":
            regex_string = filter_content
            p = re.compile(regex_string, re.IGNORECASE)
            filterMatched = inverse ^ bool(p.search(self._helpers.bytesToString(requestResponse.getResponse()[analyzedResponse.getBodyOffset():])))

        elif filter_name == "Full response (simple string)":
            filterMatched = inverse ^ (filter_content in self._helpers.bytesToString(requestResponse.getResponse()))

        elif filter_name == "Full response (regex)":
            regex_string = filter_content
            p = re.compile(regex_string, re.IGNORECASE)
            filterMatched = inverse ^ bool(p.search(self._helpers.bytesToString(requestResponse.getResponse())))

        elif filter_name == "Full response length":
            filterMatched = inverse ^ (str(len(response)) == filter_content.strip())

        if andEnforcementCheck:
            if auth_enforced and not filterMatched:
                auth_enforced = False
        else:
            if not auth_enforced and filterMatched:
                auth_enforced = True

    return auth_enforced

def checkBypass(self, oldStatusCode, newStatusCode, oldContent,
                 newContent, filters, requestResponse, andOrEnforcement):
    if oldStatusCode == newStatusCode:
        auth_enforced = 0
        if len(filters) > 0:
            auth_enforced = auth_enforced_via_enforcement_detectors(self, filters, requestResponse, andOrEnforcement)
        if auth_enforced:
            return self.ENFORCED_STR
        elif oldContent == newContent:
            return self.BYPASSSED_STR
        else:
            return self.IS_ENFORCED_STR
    else:
        return self.ENFORCED_STR

def checkAuthorization(self, messageInfo, originalHeaders, checkUnauthorized):
    # Check unauthorized request
    if checkUnauthorized:
        messageUnauthorized = makeMessage(self, messageInfo, True, False)
        requestResponseUnauthorized = makeRequest(self, messageInfo, messageUnauthorized)
        unauthorizedResponse = requestResponseUnauthorized.getResponse()
        analyzedResponseUnauthorized = self._helpers.analyzeResponse(unauthorizedResponse)
        statusCodeUnauthorized = analyzedResponseUnauthorized.getHeaders()[0]
        contentUnauthorized = getResponseBody(self, requestResponseUnauthorized)

    message = makeMessage(self, messageInfo, True, True)
    requestResponse = makeRequest(self, messageInfo, message)
    newResponse = requestResponse.getResponse()
    analyzedResponse = self._helpers.analyzeResponse(newResponse)

    oldStatusCode = originalHeaders[0]
    newStatusCode = analyzedResponse.getHeaders()[0]
    oldContent = getResponseBody(self, messageInfo)
    newContent = getResponseBody(self, requestResponse)

    EDFilters = self.EDModel.toArray()

    impression = checkBypass(self, oldStatusCode, newStatusCode, oldContent, newContent, EDFilters, requestResponse, self.AndOrType.getSelectedItem())

    if checkUnauthorized:
        EDFiltersUnauth = self.EDModelUnauth.toArray()
        impressionUnauthorized = checkBypass(self, oldStatusCode, statusCodeUnauthorized, oldContent, contentUnauthorized, EDFiltersUnauth, requestResponseUnauthorized, self.AndOrTypeUnauth.getSelectedItem())

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
    self.logTable.setAutoCreateRowSorter(True)
    for i in range(self.tableModel.getRowCount()):
        logEntry = self._log.get(self.logTable.convertRowIndexToModel(i))
        start_new_thread(handle_message, (self, "AUTORIZE", False, logEntry._originalrequestResponse))