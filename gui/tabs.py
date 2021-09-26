#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from java.awt.datatransfer import StringSelection
from javax.swing.table import TableRowSorter
from java.awt.event import AdjustmentListener
from java.awt.event import ActionListener
from java.awt.event import MouseAdapter
from javax.swing import JSplitPane
from javax.swing import JMenuItem
from javax.swing import JScrollPane
from javax.swing import JPopupMenu
from javax.swing import JTabbedPane
from javax.swing import JPanel
from java.awt import GridLayout
from java.awt import Toolkit
from java.lang import Math

from burp import ITab
from burp import IMessageEditorController

from authorization.authorization import handle_message, retestAllRequests

from thread import start_new_thread

from table import Table, LogEntry, TableRowFilter
from helpers.filters import expand, collapse

class ITabImpl(ITab):
    def __init__(self, extender):
        self._extender = extender

    def getTabCaption(self):
        return "Autorize"
    
    def getUiComponent(self):
        return self._extender._splitpane

class Tabs():
    def __init__(self, extender):
        self._extender = extender

    def draw(self):
        """  init autorize tabs
        """

        self._extender.logTable = Table(self._extender)

        tableWidth = self._extender.logTable.getPreferredSize().width        
        self._extender.logTable.getColumn("ID").setPreferredWidth(Math.round(tableWidth / 50 * 2))
        self._extender.logTable.getColumn("Method").setPreferredWidth(Math.round(tableWidth / 50 * 3))
        self._extender.logTable.getColumn("URL").setPreferredWidth(Math.round(tableWidth / 50 * 25))
        self._extender.logTable.getColumn("Orig. Len").setPreferredWidth(Math.round(tableWidth / 50 * 4))
        self._extender.logTable.getColumn("Modif. Len").setPreferredWidth(Math.round(tableWidth / 50 * 4))
        self._extender.logTable.getColumn("Unauth. Len").setPreferredWidth(Math.round(tableWidth / 50 * 4))
        self._extender.logTable.getColumn("Authz. Status").setPreferredWidth(Math.round(tableWidth / 50 * 4))
        self._extender.logTable.getColumn("Unauth. Status").setPreferredWidth(Math.round(tableWidth / 50 * 4))

        self._extender.tableSorter = TableRowSorter(self._extender.tableModel)
        rowFilter = TableRowFilter(self._extender)
        self._extender.tableSorter.setRowFilter(rowFilter)
        self._extender.logTable.setRowSorter(self._extender.tableSorter)

        self._extender._splitpane = JSplitPane(JSplitPane.HORIZONTAL_SPLIT)
        self._extender._splitpane.setResizeWeight(1)
        self._extender.scrollPane = JScrollPane(self._extender.logTable)
        self._extender._splitpane.setLeftComponent(self._extender.scrollPane)
        self._extender.scrollPane.getVerticalScrollBar().addAdjustmentListener(AutoScrollListener(self._extender))

        copyURLitem = JMenuItem("Copy URL")
        copyURLitem.addActionListener(CopySelectedURL(self._extender))

        sendRequestMenu = JMenuItem("Send Original Request to Repeater")
        sendRequestMenu.addActionListener(SendRequestRepeater(self._extender, self._extender._callbacks, True))

        sendRequestMenu2 = JMenuItem("Send Modified Request to Repeater")
        sendRequestMenu2.addActionListener(SendRequestRepeater(self._extender, self._extender._callbacks, False))

        sendResponseMenu = JMenuItem("Send Responses to Comparer")
        sendResponseMenu.addActionListener(SendResponseComparer(self._extender, self._extender._callbacks))

        retestSelecteditem = JMenuItem("Retest selected request")
        retestSelecteditem.addActionListener(RetestSelectedRequest(self._extender))

        retestAllitem = JMenuItem("Retest all requests")
        retestAllitem.addActionListener(RetestAllRequests(self._extender))
        
        deleteSelectedItem = JMenuItem("Delete")
        deleteSelectedItem.addActionListener(DeleteSelectedRequest(self._extender))

        self._extender.menu = JPopupMenu("Popup")
        self._extender.menu.add(sendRequestMenu)
        self._extender.menu.add(sendRequestMenu2)
        self._extender.menu.add(sendResponseMenu)
        self._extender.menu.add(copyURLitem)
        self._extender.menu.add(retestSelecteditem)
        self._extender.menu.add(retestAllitem)
        # self.menu.add(deleteSelectedItem) disabling this feature until bug will be fixed.
        message_editor = MessageEditor(self._extender)

        self._extender.tabs = JTabbedPane()
        self._extender._requestViewer = self._extender._callbacks.createMessageEditor(message_editor, False)
        self._extender._responseViewer = self._extender._callbacks.createMessageEditor(message_editor, False)

        self._extender._originalrequestViewer = self._extender._callbacks.createMessageEditor(message_editor, False)
        self._extender._originalresponseViewer = self._extender._callbacks.createMessageEditor(message_editor, False)

        self._extender._unauthorizedrequestViewer = self._extender._callbacks.createMessageEditor(message_editor, False)
        self._extender._unauthorizedresponseViewer = self._extender._callbacks.createMessageEditor(message_editor, False)        

        self._extender.original_requests_tabs = JTabbedPane()
        self._extender.original_requests_tabs.addMouseListener(Mouseclick(self._extender))
        self._extender.original_requests_tabs.addTab("Original Request", self._extender._originalrequestViewer.getComponent())
        self._extender.original_requests_tabs.addTab("Original Response", self._extender._originalresponseViewer.getComponent())
        self._extender.original_requests_tabs.addTab("Expand", None)
        self._extender.original_requests_tabs.setSelectedIndex(0)

        self._extender.unauthenticated_requests_tabs = JTabbedPane()
        self._extender.unauthenticated_requests_tabs.addMouseListener(Mouseclick(self._extender))
        self._extender.unauthenticated_requests_tabs.addTab("Unauthenticated Request", self._extender._unauthorizedrequestViewer.getComponent())
        self._extender.unauthenticated_requests_tabs.addTab("Unauthenticated Response", self._extender._unauthorizedresponseViewer.getComponent())
        self._extender.unauthenticated_requests_tabs.addTab("Expand", None)
        self._extender.unauthenticated_requests_tabs.setSelectedIndex(0)

        self._extender.modified_requests_tabs = JTabbedPane()
        self._extender.modified_requests_tabs.addMouseListener(Mouseclick(self._extender))
        self._extender.modified_requests_tabs.addTab("Modified Request", self._extender._requestViewer.getComponent())
        self._extender.modified_requests_tabs.addTab("Modified Response", self._extender._responseViewer.getComponent())
        self._extender.modified_requests_tabs.addTab("Expand", None)
        self._extender.modified_requests_tabs.setSelectedIndex(0)

        self._extender.requests_panel = JPanel(GridLayout(3,0))
        self._extender.requests_panel.add(self._extender.modified_requests_tabs)
        self._extender.requests_panel.add(self._extender.original_requests_tabs)
        self._extender.requests_panel.add(self._extender.unauthenticated_requests_tabs)

        self._extender.tabs.addTab("Request/Response Viewers", self._extender.requests_panel)
        
        self._extender.tabs.addTab("Configuration", self._extender._cfg_splitpane)
        self._extender.tabs.setSelectedIndex(1)
        self._extender._splitpane.setRightComponent(self._extender.tabs)


class SendRequestRepeater(ActionListener):
    def __init__(self, extender, callbacks, original):
        self._extender = extender
        self._callbacks = callbacks
        self.original = original

    def actionPerformed(self, e):
        if self.original:
                request = self._extender._currentlyDisplayedItem._originalrequestResponse
        else:
                request = self._extender._currentlyDisplayedItem._requestResponse
        host = request.getHttpService().getHost()
        port = request.getHttpService().getPort()
        proto = request.getHttpService().getProtocol()
        secure = True if proto == "https" else False

        self._callbacks.sendToRepeater(host, port, secure, request.getRequest(), "Autorize");

class SendResponseComparer(ActionListener):
    def __init__(self, extender, callbacks):
        self._extender = extender
        self._callbacks = callbacks

    def actionPerformed(self, e):
        originalResponse = self._extender._currentlyDisplayedItem._originalrequestResponse
        modifiedResponse = self._extender._currentlyDisplayedItem._requestResponse
        unauthorizedResponse = self._extender._currentlyDisplayedItem._unauthorizedRequestResponse
        
        self._callbacks.sendToComparer(originalResponse.getResponse())
        self._callbacks.sendToComparer(modifiedResponse.getResponse())
        self._callbacks.sendToComparer(unauthorizedResponse.getResponse())


class RetestSelectedRequest(ActionListener):
    def __init__(self, extender):
        self._extender = extender

    def actionPerformed(self, e):
        start_new_thread(handle_message, (self._extender, "AUTORIZE", False, self._extender._currentlyDisplayedItem._originalrequestResponse))

class RetestAllRequests(ActionListener):
    def __init__(self, extender):
        self._extender = extender

    def actionPerformed(self, e):
        start_new_thread(retestAllRequests, (self._extender,))


class DeleteSelectedRequest(ActionListener):
    def __init__(self, extender):
        self._extender = extender

    def actionPerformed(self, e):
        # TODO: Implement this function.
        pass

class CopySelectedURL(ActionListener):
    def __init__(self, extender):
        self._extender = extender

    def actionPerformed(self, e):
        stringSelection = StringSelection(str(self._extender._helpers.analyzeRequest(self._extender._currentlyDisplayedItem._requestResponse).getUrl()))
        clpbrd = Toolkit.getDefaultToolkit().getSystemClipboard()
        clpbrd.setContents(stringSelection, None)

class AutoScrollListener(AdjustmentListener):
    def __init__(self, extender):
        self._extender = extender

    def adjustmentValueChanged(self, e):
        if self._extender.autoScroll.isSelected():
            e.getAdjustable().setValue(e.getAdjustable().getMaximum())

class MessageEditor(IMessageEditorController):
    def __init__(self, extender):
        self._extender = extender

    def getHttpService(self):
        return self._extender._currentlyDisplayedItem.getHttpService()

    def getRequest(self):
        return self._extender._currentlyDisplayedItem.getRequest()

    def getResponse(self):
        return self._extender._currentlyDisplayedItem.getResponse()

class Mouseclick(MouseAdapter):
    def __init__(self, extender):
        self._extender = extender

    def mouseReleased(self, evt):
        if evt.getComponent().getSelectedIndex() == 2:
            if self._extender.expanded_requests == 0:
                expand(self._extender, evt.getComponent())
            else:
                collapse(self._extender, evt.getComponent())
        
