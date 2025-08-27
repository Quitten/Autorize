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
from java.awt import Dimension

from burp import ITab
from burp import IMessageEditorController

from authorization.authorization import handle_message, retestAllRequests

from thread import start_new_thread

from table import Table, TableRowFilter, ShiftEditorPopupListener
from helpers.filters import expand, collapse
from javax.swing import KeyStroke
from javax.swing import JTable
from javax.swing import AbstractAction
from java.awt.event import KeyEvent
from java.awt.event import InputEvent
from javax.swing import SwingUtilities
from javax.swing.event import PopupMenuListener, PopupMenuEvent

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
        self._extender.scrollPane.setMinimumSize(Dimension(1,1))
        self._extender._splitpane.setLeftComponent(self._extender.scrollPane)
        self._extender.scrollPane.getVerticalScrollBar().addAdjustmentListener(AutoScrollListener(self._extender))

        copyURLitem = JMenuItem("Copy URL")
        copyURLitem.addActionListener(CopySelectedURL(self._extender))

        sendRequestMenu = JMenuItem("Send Original Request to Repeater")
        sendRequestMenu.addActionListener(SendRequestRepeater(self._extender, self._extender._callbacks, True))

        sendRequestMenu2 = JMenuItem("Send Modified Request to Repeater")
        sendRequestMenu2.addActionListener(SendRequestRepeater(self._extender, self._extender._callbacks, False))

        try:
            controlR = KeyStroke.getKeyStroke(KeyEvent.VK_R, Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx())
        except:
            controlR = KeyStroke.getKeyStroke(KeyEvent.VK_R, InputEvent.CTRL_DOWN_MASK)

        controlC = KeyStroke.getKeyStroke(KeyEvent.VK_C, InputEvent.META_DOWN_MASK)

        inputMap = self._extender.logTable.getInputMap(JTable.WHEN_FOCUSED)
        actionMap = self._extender.logTable.getActionMap()

        inputMap.put(controlR, "SendRequestToRepeaterAction")
        actionMap.put("SendRequestToRepeaterAction", SendRequestToRepeaterAction(self._extender, self._extender._callbacks))

        inputMap.put(controlC, "copyToClipBoard")
        actionMap.put("copyToClipBoard",
                      CopySelectedURLToClipBoard(self._extender, self._extender._callbacks))

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
        self._extender.menu.add(deleteSelectedItem) 
        try:
            self._extender.menu.addPopupMenuListener(AutorizePopupContextListener(self._extender))
        except Exception:
            pass
        message_editor = MessageEditor(self._extender)

        self._extender.tabs = JTabbedPane()
        self._extender._requestViewer = self._extender._callbacks.createMessageEditor(message_editor, False)
        self._extender._responseViewer = self._extender._callbacks.createMessageEditor(message_editor, False)

        self._extender._originalrequestViewer = self._extender._callbacks.createMessageEditor(message_editor, False)
        self._extender._originalresponseViewer = self._extender._callbacks.createMessageEditor(message_editor, False)

        self._extender._unauthorizedrequestViewer = self._extender._callbacks.createMessageEditor(message_editor, False)
        self._extender._unauthorizedresponseViewer = self._extender._callbacks.createMessageEditor(message_editor, False)

        try:
            def _attach_fallback_listener(comp):
                try:
                    comp.addMouseListener(ShiftEditorPopupListener(self._extender))
                    if hasattr(comp, 'getComponentCount') and hasattr(comp, 'getComponent'):
                        try:
                            cnt = comp.getComponentCount()
                        except Exception:
                            cnt = 0
                        for i in range(0, cnt):
                            try:
                                _attach_fallback_listener(comp.getComponent(i))
                            except Exception:
                                pass
                except Exception:
                    pass
            _attach_fallback_listener(self._extender._requestViewer.getComponent())
            _attach_fallback_listener(self._extender._responseViewer.getComponent())
            _attach_fallback_listener(self._extender._originalrequestViewer.getComponent())
            _attach_fallback_listener(self._extender._originalresponseViewer.getComponent())
            _attach_fallback_listener(self._extender._unauthorizedrequestViewer.getComponent())
            _attach_fallback_listener(self._extender._unauthorizedresponseViewer.getComponent())
        except Exception:
            pass

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
        self._extender.tabs.setMinimumSize(Dimension(1,1))
        self._extender._splitpane.setRightComponent(self._extender.tabs)


class SendRequestRepeater(ActionListener):
    def __init__(self, extender, callbacks, original):
        self._extender = extender
        self._callbacks = callbacks
        self.original = original

    def actionPerformed(self, e):
        ctx = getattr(self._extender, '_contextRequestResponse', None)
        if ctx is not None and not self.original:
            request = ctx
        else:
            if self.original:
                request = self._extender._currentlyDisplayedItem._originalrequestResponse
            else:
                request = self._extender._currentlyDisplayedItem._requestResponse
        host = request.getHttpService().getHost()
        port = request.getHttpService().getPort()
        proto = request.getHttpService().getProtocol()
        secure = True if proto == "https" else False

        self._callbacks.sendToRepeater(host, port, secure, request.getRequest(), "Autorize")

class SendResponseComparer(ActionListener):
    def __init__(self, extender, callbacks):
        self._extender = extender
        self._callbacks = callbacks

    def actionPerformed(self, e):
        ctx = getattr(self._extender, '_contextRequestResponse', None)
        originalResponse = self._extender._currentlyDisplayedItem._originalrequestResponse
        modifiedResponse = ctx if ctx is not None else self._extender._currentlyDisplayedItem._requestResponse
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


class DeleteSelectedRequest(AbstractAction):
    def __init__(self, extender):
        self._extender = extender

    def actionPerformed(self, e):
        rows = self._extender.logTable.getSelectedRows()
        if len(rows) != 0:
            rows = [self._extender.logTable.convertRowIndexToModel(row) for row in rows]
            SwingUtilities.invokeLater(lambda: self._extender.tableModel.removeRows(rows))

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
        try:
            if getattr(self._extender, '_currentlyDisplayedItem', None) is None:
                return None
            return self._extender._currentlyDisplayedItem.getHttpService()
        except Exception:
            return None

    def getRequest(self):
        try:
            if getattr(self._extender, '_currentlyDisplayedItem', None) is None:
                return self._extender._helpers.stringToBytes("") if hasattr(self._extender, '_helpers') else "".encode('utf-8')
            return self._extender._currentlyDisplayedItem.getRequest()
        except Exception:
            try:
                return self._extender._helpers.stringToBytes("") if hasattr(self._extender, '_helpers') else "".encode('utf-8')
            except Exception:
                return ""

    def getResponse(self):
        try:
            if getattr(self._extender, '_currentlyDisplayedItem', None) is None:
                return self._extender._helpers.stringToBytes("") if hasattr(self._extender, '_helpers') else "".encode('utf-8')
            return self._extender._currentlyDisplayedItem.getResponse()
        except Exception:
            try:
                return self._extender._helpers.stringToBytes("") if hasattr(self._extender, '_helpers') else "".encode('utf-8')
            except Exception:
                return ""

class Mouseclick(MouseAdapter):
    def __init__(self, extender):
        self._extender = extender

    def mouseReleased(self, evt):
        comp = evt.getComponent()
        try:
            idx = comp.getSelectedIndex()
            comp.putClientProperty("autorize-last-index", idx)
        except Exception:
            pass
        try:
            if comp.getSelectedIndex() == comp.getTabCount() - 1:
                if self._extender.expanded_requests == 0:
                    expand(self._extender, comp)
                else:
                    collapse(self._extender, comp)
        except Exception:
            try:
                if comp.getSelectedIndex() == 2:
                    if self._extender.expanded_requests == 0:
                        expand(self._extender, comp)
                    else:
                        collapse(self._extender, comp)
            except Exception:
                pass
        try:
            if evt.getButton() == 3 or getattr(evt, 'button', None) == 3:
                self._extender.menu.show(comp, evt.getX(), evt.getY())
        except Exception:
            pass

class AutorizePopupContextListener(PopupMenuListener):
    def __init__(self, extender):
        self._extender = extender

    def popupMenuWillBecomeVisible(self, e):
        try:
            menu = e.getSource()
            invoker = menu.getInvoker()
            ctx_rr = None
            try:
                pane = SwingUtilities.getAncestorOfClass(JTabbedPane, invoker)
            except Exception:
                pane = None
            if pane is not None:
                try:
                    tab_rr_map = pane.getClientProperty("autorize-tab-rr-map")
                    if isinstance(tab_rr_map, list) and len(tab_rr_map) > 0:
                        idx_found = -1
                        
                        try:
                            if invoker is pane:
                                last_idx = pane.getClientProperty("autorize-last-index")
                                if isinstance(last_idx, int) and 0 <= last_idx < (pane.getTabCount() - 1):
                                    idx_found = last_idx
                                else:
                                    sel = pane.getSelectedIndex()
                                    if isinstance(sel, int) and 0 <= sel < (pane.getTabCount() - 1):
                                        idx_found = sel
                            else:
                                for i in range(0, pane.getTabCount()-1):
                                    try:
                                        comp_i = pane.getComponentAt(i)
                                        if SwingUtilities.isDescendingFrom(invoker, comp_i):
                                            idx_found = i
                                            break
                                    except Exception:
                                        pass
                        except Exception:
                            pass
                        if idx_found >= 0 and idx_found < len(tab_rr_map):
                            ctx_rr = tab_rr_map[idx_found]
                            try:
                                pane.putClientProperty("autorize-last-index", idx_found)
                            except Exception:
                                pass
                except Exception:
                    pass
                
                if ctx_rr is None:
                    try:
                        current = getattr(self._extender, '_currentlyDisplayedItem', None)
                        if current is not None:
                            if pane is self._extender.original_requests_tabs:
                                ctx_rr = current._originalrequestResponse
                            elif pane is self._extender.unauthenticated_requests_tabs:
                                ctx_rr = current._unauthorizedRequestResponse
                    except Exception:
                        pass
            if ctx_rr is None:
                try:
                    ctx_rr = invoker.getClientProperty("autorize-rr")
                except Exception:
                    ctx_rr = None
            try:
                self._extender._contextRequestResponse = ctx_rr
            except Exception:
                pass
        except Exception:
            pass

    def popupMenuWillBecomeInvisible(self, e):
        pass

    def popupMenuCanceled(self, e):
        pass

class SendRequestToRepeaterAction(AbstractAction):
    def __init__(self, extender, callbacks):
        self._extender = extender
        self._callbacks = callbacks

    def actionPerformed(self, e):
        row = self._extender.logTable.getSelectedRow()
        rowModelIndex = self._extender.logTable.convertRowIndexToModel(row)
        
        try:
            _ = self._extender.tableModel.getValueAt(rowModelIndex, 0)
        except Exception:
            pass
        
        ctx = getattr(self._extender, '_contextRequestResponse', None)
        request = ctx if ctx is not None else self._extender._currentlyDisplayedItem._requestResponse
        host = request.getHttpService().getHost()
        port = request.getHttpService().getPort()
        proto = request.getHttpService().getProtocol()
        secure = True if proto == "https" else False

        self._callbacks.sendToRepeater(host, port, secure, request.getRequest(), "Autorize")

class CopySelectedURLToClipBoard(AbstractAction):
    def __init__(self, extender, callbacks):
        self._extender = extender
        self._callbacks = callbacks

    def actionPerformed(self, e):
        ctx = getattr(self._extender, '_contextRequestResponse', None)
        rr = ctx if ctx is not None else self._extender._currentlyDisplayedItem._requestResponse
        stringSelection = StringSelection(str(self._extender._helpers.analyzeRequest(rr).getUrl()))
        clpbrd = Toolkit.getDefaultToolkit().getSystemClipboard()
        clpbrd.setContents(stringSelection, None)