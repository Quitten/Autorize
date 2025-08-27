#!/usr/bin/env python
# -*- coding: utf-8 -*-

from operator import truediv
import sys
reload(sys)

if (sys.version_info[0] == 2):
    sys.setdefaultencoding('utf8')

sys.path.append("..")

from helpers.http import get_authorization_header_from_message, get_cookie_header_from_message, isStatusCodesReturned, makeMessage, makeMessageWithReplaceText, makeRequest, getResponseBody, IHttpRequestResponseImplementation
from gui.table import LogEntry, UpdateTableEDT
from javax.swing import SwingUtilities
from java.net import URL
import re
from java.lang import Runnable
from java.util.concurrent import Executors, Callable, TimeUnit

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
        interceptionFilter = self.IFList.getModel().getElementAt(i)
        interceptionFilterTitle = interceptionFilter.split(":")[0]
        if interceptionFilterTitle == "Scope items only":
            currentURL = URL(urlString)
            if not self._callbacks.isInScope(currentURL):
                message_passed_filters = False

        if interceptionFilterTitle == "URL Contains (simple string)":
            if interceptionFilter[30:] not in urlString:
                message_passed_filters = False

        if interceptionFilterTitle == "URL Contains (regex)":
            regex_string = interceptionFilter[22:]
            if re.search(regex_string, urlString, re.IGNORECASE) is None:
                message_passed_filters = False

        if interceptionFilterTitle == "URL Not Contains (simple string)":
            if interceptionFilter[34:] in urlString:
                message_passed_filters = False

        if interceptionFilterTitle == "URL Not Contains (regex)":
            regex_string = interceptionFilter[26:]
            if not re.search(regex_string, urlString, re.IGNORECASE) is None:
                message_passed_filters = False

        if interceptionFilterTitle == "Request Body contains (simple string)":
            if interceptionFilter[40:] not in bodyStr:
                message_passed_filters = False

        if interceptionFilterTitle == "Request Body contains (regex)":
            regex_string = interceptionFilter[32:]
            if re.search(regex_string, bodyStr, re.IGNORECASE) is None:
                message_passed_filters = False

        if interceptionFilterTitle == "Request Body NOT contains (simple string)":
            if interceptionFilter[44:] in bodyStr:
                message_passed_filters = False

        if interceptionFilterTitle == "Request Body Not contains (regex)":
            regex_string = interceptionFilter[36:]
            if not re.search(regex_string, bodyStr, re.IGNORECASE) is None:
                message_passed_filters = False

        if interceptionFilterTitle == "Response Body contains (simple string)":
            if interceptionFilter[41:] not in resStr:
                message_passed_filters = False

        if interceptionFilterTitle == "Response Body contains (regex)":
            regex_string = interceptionFilter[33:]
            if re.search(regex_string, resStr, re.IGNORECASE) is None:
                message_passed_filters = False

        if interceptionFilterTitle == "Response Body NOT contains (simple string)":
            if interceptionFilter[45:] in resStr:
                message_passed_filters = False

        if interceptionFilterTitle == "Response Body Not contains (regex)":
            regex_string = interceptionFilter[37:]
            if not re.search(regex_string, resStr, re.IGNORECASE) is None:
                message_passed_filters = False

        if interceptionFilterTitle == "Header contains":
            for header in list(resInfo.getHeaders()):
                if interceptionFilter[17:] in header:
                    message_passed_filters = False

        if interceptionFilterTitle == "Header doesn't contain":
            for header in list(resInfo.getHeaders()):
                if not interceptionFilter[17:] in header:
                    message_passed_filters = False

        if interceptionFilterTitle == "Only HTTP methods (newline separated)":
            filterMethods = interceptionFilter[39:].split("\n")
            filterMethods = [x.lower() for x in filterMethods]
            reqMethod = str(self._helpers.analyzeRequest(messageInfo).getMethod())
            if reqMethod.lower() not in filterMethods:
                message_passed_filters = False

        if interceptionFilterTitle == "Ignore HTTP methods (newline separated)":
            filterMethods = interceptionFilter[41:].split("\n")
            filterMethods = [x.lower() for x in filterMethods]
            reqMethod = str(self._helpers.analyzeRequest(messageInfo).getMethod())
            if reqMethod.lower() in filterMethods:
                message_passed_filters = False

        if interceptionFilterTitle == "Ignore OPTIONS requests":
            reqMethod = str(self._helpers.analyzeRequest(messageInfo).getMethod())
            if reqMethod == "OPTIONS":
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
            # Allow internal Retest/Repeater-triggered flows (toolFlag == "AUTORIZE")
            # to bypass the self-origin guard, while still guarding normal Proxy/Repeater traffic.
            if toolFlag == "AUTORIZE" or message_not_from_autorize(self, messageInfo):
                if self.ignore304.isSelected():
                    if isStatusCodesReturned(self, messageInfo, ["304", "204"]):
                        return

                if no_filters_defined(self):
                    checkAuthorizationAllSaved(self, messageInfo,
                        self._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders())
                else:
                    if message_passed_interception_filters(self, messageInfo):
                        checkAuthorizationAllSaved(self, messageInfo,
                            self._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders())

def send_request_to_autorize(self, messageInfo):
    if messageInfo.getResponse() is None:
        message = makeMessage(self, messageInfo,False,False)
        requestResponse = makeRequest(self, messageInfo, message)
        checkAuthorizationAllSaved(self, requestResponse,
            self._helpers.analyzeResponse(requestResponse.getResponse()).getHeaders())
    else:
        request = messageInfo.getRequest()
        response = messageInfo.getResponse()
        httpService = messageInfo.getHttpService()
        newHttpRequestResponse = IHttpRequestResponseImplementation(httpService,request,response)
        newHttpRequestResponsePersisted = self._callbacks.saveBuffersToTempFiles(newHttpRequestResponse)
        checkAuthorizationAllSaved(self, newHttpRequestResponsePersisted,
            self._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders())

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
        filter_kv = filter.split(":", 1)
        inverse = "NOT" in filter_kv[0]
        filter_kv[0] = filter_kv[0].replace(" NOT", "")
        filter = ":".join(filter_kv)

        if filter.startswith("Status code equals: "):
            statusCode = filter[20:]
            filterMatched = inverse ^ isStatusCodesReturned(self, requestResponse, statusCode)

        elif filter.startswith("Headers (simple string): "):
            filterMatched = inverse ^ (filter[25:] in self._helpers.bytesToString(requestResponse.getResponse()[0:analyzedResponse.getBodyOffset()]))

        elif filter.startswith("Headers (regex): "):
            regex_string = filter[17:]
            p = re.compile(regex_string, re.IGNORECASE)
            filterMatched = inverse ^ bool(p.search(self._helpers.bytesToString(requestResponse.getResponse()[0:analyzedResponse.getBodyOffset()])))

        elif filter.startswith("Body (simple string): "):
            filterMatched = inverse ^ (filter[22:] in self._helpers.bytesToString(requestResponse.getResponse()[analyzedResponse.getBodyOffset():]))

        elif filter.startswith("Body (regex): "):
            regex_string = filter[14:]
            p = re.compile(regex_string, re.IGNORECASE)
            filterMatched = inverse ^ bool(p.search(self._helpers.bytesToString(requestResponse.getResponse()[analyzedResponse.getBodyOffset():])))

        elif filter.startswith("Full response (simple string): "):
            filterMatched = inverse ^ (filter[31:] in self._helpers.bytesToString(requestResponse.getResponse()))

        elif filter.startswith("Full response (regex): "):
            regex_string = filter[23:]
            p = re.compile(regex_string, re.IGNORECASE)
            filterMatched = inverse ^ bool(p.search(self._helpers.bytesToString(requestResponse.getResponse())))

        elif filter.startswith("Full response length: "):
            filterMatched = inverse ^ (str(len(response)) == filter[22:].strip())

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
    checkAuthorizationAllSaved(self, messageInfo,
        self._extender._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders())

def retestAllRequests(self):
    self.logTable.setAutoCreateRowSorter(True)
    for i in range(self.tableModel.getRowCount()):
        logEntry = self._log.get(self.logTable.convertRowIndexToModel(i))
        handle_message(self, "AUTORIZE", False, logEntry._originalrequestResponse)

def checkAuthorizationAllSaved(self, messageInfo, originalHeaders):
    try:
        saved_list = list(self.savedHeaders) if hasattr(self, 'savedHeaders') else []
    except Exception:
        saved_list = []

    enabled_list = []
    try:
        for obj in saved_list:
            if 'enabled' not in obj:
                obj['enabled'] = True
            if obj.get('enabled', True):
                enabled_list.append(obj)
    except Exception:
        enabled_list = saved_list

    if not enabled_list:
        enabled_list = [{
            'title': 'Temporary headers',
            'headers': self.replaceString.getText()
        }]

    url = str(self._helpers.analyzeRequest(messageInfo).getUrl())

    oldStatusCode = originalHeaders[0]
    oldContent = getResponseBody(self, messageInfo)

    do_unauth = self.doUnauthorizedRequest.isSelected() if hasattr(self, 'doUnauthorizedRequest') else False
    requestResponseUnauthorized = None
    statusCodeUnauthorized = None
    contentUnauthorized = None
    impressionUnauthorized = "Disabled"

    if do_unauth:
        try:
            unauth_remove_text = "\n".join([
                "Authorization:",
                "Cookie:",
                "Proxy-Authorization:",
                "X-Auth-Token:",
                "X-Api-Key:",
                "X-Access-Token:",
            ]) + "\n"
            prev_replace_query = False
            try:
                prev_replace_query = self.replaceQueryParam.isSelected()
                if prev_replace_query:
                    self.replaceQueryParam.setSelected(False)
            except Exception:
                pass
            try:
                messageUnauthorized = makeMessageWithReplaceText(self, messageInfo, True, False, unauth_remove_text, queryOverride=False)
            finally:
                try:
                    if prev_replace_query:
                        self.replaceQueryParam.setSelected(True)
                except Exception:
                    pass
            requestResponseUnauthorized = makeRequest(self, messageInfo, messageUnauthorized)
            unauthorizedResponse = requestResponseUnauthorized.getResponse()
            analyzedResponseUnauthorized = self._helpers.analyzeResponse(unauthorizedResponse)
            statusCodeUnauthorized = analyzedResponseUnauthorized.getHeaders()[0]
            contentUnauthorized = getResponseBody(self, requestResponseUnauthorized)
            EDFiltersUnauth = self.EDModelUnauth.toArray()
            impressionUnauthorized = checkBypass(self, oldStatusCode, statusCodeUnauthorized, oldContent, contentUnauthorized, EDFiltersUnauth, requestResponseUnauthorized, self.AndOrTypeUnauth.getSelectedItem())
        except Exception as e:
            impressionUnauthorized = "Disabled"
            requestResponseUnauthorized = None

    original_replace_text = self.replaceString.getText()

    modified_rr_list = [None] * len(enabled_list)          # list of IHttpRequestResponse (ordered)
    modified_impressions = [None] * len(enabled_list)      # list of strings (ordered)
    modified_rule_titles = [None] * len(enabled_list)      # list of rule titles (ordered)

    EDFilters = self.EDModel.toArray()

    class _RuleTask(Callable):
        def __init__(self, ext, idx, title, headers_text, is_query, param_text):
            self.ext = ext
            self.idx = idx
            self.title = title
            self.headers_text = headers_text
            self.is_query = is_query
            self.param_text = param_text
        def call(self):
            try:
                if self.is_query:
                    msg = makeMessageWithReplaceText(self.ext, messageInfo, True, True, self.param_text or "", queryOverride=True)
                else:
                    msg = makeMessageWithReplaceText(self.ext, messageInfo, True, True, self.headers_text or "", queryOverride=False)
                rr = makeRequest(self.ext, messageInfo, msg)
                try:
                    rr.setComment("Autorize Rule: {}".format(self.title))
                    rr.setHighlight("cyan")
                except Exception:
                    pass
                analyzed = self.ext._helpers.analyzeResponse(rr.getResponse())
                newStatus = analyzed.getHeaders()[0]
                newContent = getResponseBody(self.ext, rr)
                impression = checkBypass(self.ext, oldStatusCode, newStatus, oldContent, newContent, EDFilters, rr, self.ext.AndOrType.getSelectedItem())
                rr_saved = self.ext._callbacks.saveBuffersToTempFiles(rr)
                return (self.idx, rr_saved, impression, self.title, newStatus)
            except Exception as e:
                return (self.idx, None, "Error", self.title, None)

    pool_size = min(max(1, len(enabled_list)), 6)
    executor = Executors.newFixedThreadPool(pool_size)
    futures = []
    try:
        for idx, header_obj in enumerate(enabled_list):
            title = header_obj.get('title', 'Untitled')
            headers_text = header_obj.get('headers', '') or ''
            is_query = bool(header_obj.get('isQueryParam', False))
            param_text = header_obj.get('param', '') or ''
            futures.append(executor.submit(_RuleTask(self, idx, title, headers_text, is_query, param_text)))

        for f in futures:
            try:
                idx, rr_saved, impression, title, newStatus = f.get()
                modified_rr_list[idx] = rr_saved
                modified_impressions[idx] = impression
                modified_rule_titles[idx] = title
            except Exception:
                pass
    finally:
        try:
            executor.shutdown()
            executor.awaitTermination(60, TimeUnit.SECONDS)
        except Exception:
            pass

    aggregated_impression = self.ENFORCED_STR
    if len(modified_impressions) == 0:
        aggregated_impression = self.IS_ENFORCED_STR
    else:
        if any(imp == self.BYPASSSED_STR for imp in modified_impressions):
            aggregated_impression = self.BYPASSSED_STR
        elif any(imp == self.IS_ENFORCED_STR for imp in modified_impressions):
            aggregated_impression = self.IS_ENFORCED_STR
        else:
            aggregated_impression = self.ENFORCED_STR

    representative_rr = modified_rr_list[0] if modified_rr_list else None
    try:
        representative_url = self._helpers.analyzeRequest(messageInfo).getUrl()
    except Exception:
        try:
            representative_url = self._helpers.analyzeRequest(representative_rr).getUrl() if representative_rr else URL(url)
        except Exception:
            representative_url = URL(url)
    try:
        method = self._helpers.analyzeRequest(messageInfo).getMethod()
    except Exception:
        try:
            method = self._helpers.analyzeRequest(representative_rr).getMethod() if representative_rr else "GET"
        except Exception:
            method = "GET"

    self._lock.acquire()
    try:
        row = self._log.size()
        if representative_rr is None:
            representative_rr = self._callbacks.saveBuffersToTempFiles(messageInfo)

        if requestResponseUnauthorized is not None:
            entry = LogEntry(self.currentRequestNumber, representative_rr, method, representative_url, messageInfo, aggregated_impression, self._callbacks.saveBuffersToTempFiles(requestResponseUnauthorized), impressionUnauthorized)
        else:
            entry = LogEntry(self.currentRequestNumber, representative_rr, method, representative_url, messageInfo, aggregated_impression, None, "Disabled")

        try:
            entry._modified_list = modified_rr_list
            entry._modified_impressions = modified_impressions
            entry._modified_rule_titles = modified_rule_titles
        except Exception:
            pass

        self._log.add(entry)
        SwingUtilities.invokeLater(UpdateTableEDT(self, "insert", row, row))

        class _SelectRow(Runnable):
            def __init__(self, ext, r):
                self.ext = ext
                self.r = r
            def run(self):
                try:
                    if self.ext.autoScroll.isSelected():
                        self.ext.logTable.setRowSelectionInterval(self.r, self.r)
                except Exception:
                    pass
        SwingUtilities.invokeLater(_SelectRow(self, row))
        self.currentRequestNumber = self.currentRequestNumber + 1
    finally:
        self._lock.release()

