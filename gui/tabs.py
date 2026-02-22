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
from javax.swing import JButton
from javax.swing import JLabel
from javax.swing import JCheckBoxMenuItem
from javax.swing import ImageIcon
from java.awt import GridLayout
from java.awt import FlowLayout
from java.awt import Toolkit
from java.awt import Color as AwtColor
from java.awt import RenderingHints
from java.awt import BasicStroke
from java.lang import Math
from java.awt import Dimension
from java.awt.image import BufferedImage
from java.awt.geom import Ellipse2D
from java.awt.geom import GeneralPath

from burp import ITab
from burp import IMessageEditorController

from authorization.authorization import handle_message, retestAllRequests

from thread import start_new_thread

from table import Table, TableRowFilter
from helpers.filters import expand, collapse, rebuildViewerPanel
from javax.swing import KeyStroke
from javax.swing import JTable
from javax.swing import AbstractAction
from javax.swing.event import ChangeListener, ChangeEvent
from java.awt.event import KeyEvent
from java.awt.event import InputEvent
from javax.swing import SwingUtilities

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
        
        self.setupDynamicColumns()

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

        self._extender.sendRequestMenu2 = JMenuItem("Send Modified Request to Repeater")
        self._extender.sendRequestMenu2.addActionListener(SendRequestRepeater(self._extender, self._extender._callbacks, False))

        # Define the key combination for the shortcut
        try:
            # The keystroke combo is: Mac -> Command + r  /  Windows control + r
            # This is used to send to the repeater function in burp
            controlR = KeyStroke.getKeyStroke(KeyEvent.VK_R, Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx())
        except:
            controlR = KeyStroke.getKeyStroke(KeyEvent.VK_R, InputEvent.CTRL_DOWN_MASK)

        # The keystroke combo is: Mac -> Command + c  /  Windows control + c
        # This is used to copy the URL to the keyboard.
        controlC = KeyStroke.getKeyStroke(KeyEvent.VK_C, InputEvent.META_DOWN_MASK)

        # Get the input and action maps for the JTable
        inputMap = self._extender.logTable.getInputMap(JTable.WHEN_FOCUSED)
        actionMap = self._extender.logTable.getActionMap()

        # Bind the key combination to the action
        inputMap.put(controlR, "SendRequestToRepeaterAction")
        actionMap.put("SendRequestToRepeaterAction", SendRequestToRepeaterAction(self._extender, self._extender._callbacks))

        # Bind the key combination to the action
        inputMap.put(controlC, "copyToClipBoard")
        actionMap.put("copyToClipBoard",
                      CopySelectedURLToClipBoard(self._extender, self._extender._callbacks))

        self._extender.sendResponseMenu = JMenuItem("Send Responses to Comparer")
        self._extender.sendResponseMenu.addActionListener(SendResponseComparer(self._extender, self._extender._callbacks))

        retestSelecteditem = JMenuItem("Retest selected request")
        retestSelecteditem.addActionListener(RetestSelectedRequest(self._extender))

        retestAllitem = JMenuItem("Retest all requests")
        retestAllitem.addActionListener(RetestAllRequests(self._extender))
        
        deleteSelectedItem = JMenuItem("Delete")
        deleteSelectedItem.addActionListener(DeleteSelectedRequest(self._extender))

        self._extender.menu = JPopupMenu("Popup")
        self._extender.menu.add(sendRequestMenu)
        self._extender.menu.add(self._extender.sendRequestMenu2)
        self._extender.menu.add(self._extender.sendResponseMenu)
        self._extender.menu.add(copyURLitem)
        self._extender.menu.add(retestSelecteditem)
        self._extender.menu.add(retestAllitem)
        self._extender.menu.add(deleteSelectedItem)

        self._extender.tabs = JTabbedPane()

        self._extender.user_viewers = {}
        self._extender.viewer_visibility = {'original': True, 'unauthenticated': True}
        self._extender._viewer_last_content_tab = {}

        message_editor = MessageEditor(self._extender)

        self._extender._originalrequestViewer = self._extender._callbacks.createMessageEditor(message_editor, False)
        self._extender._originalresponseViewer = self._extender._callbacks.createMessageEditor(message_editor, False)

        self._extender._unauthorizedrequestViewer = self._extender._callbacks.createMessageEditor(message_editor, False)
        self._extender._unauthorizedresponseViewer = self._extender._callbacks.createMessageEditor(message_editor, False)        

        self._extender.original_requests_tabs = JTabbedPane()
        self._extender.original_requests_tabs.addMouseListener(Mouseclick(self._extender))
        self._extender.original_requests_tabs.addChangeListener(ViewerTabChangeListener(self._extender))
        self._extender.original_requests_tabs.addTab("Original Request", self._extender._originalrequestViewer.getComponent())
        self._extender.original_requests_tabs.addTab("Original Response", self._extender._originalresponseViewer.getComponent())
        self._extender.original_requests_tabs.addTab("Expand", None)
        self._extender.original_requests_tabs.setSelectedIndex(0)
        self._extender._viewer_last_content_tab[id(self._extender.original_requests_tabs)] = 0

        self._extender.unauthenticated_requests_tabs = JTabbedPane()
        self._extender.unauthenticated_requests_tabs.addMouseListener(Mouseclick(self._extender))
        self._extender.unauthenticated_requests_tabs.addChangeListener(ViewerTabChangeListener(self._extender))
        self._extender.unauthenticated_requests_tabs.addTab("Unauthenticated Request", self._extender._unauthorizedrequestViewer.getComponent())
        self._extender.unauthenticated_requests_tabs.addTab("Unauthenticated Response", self._extender._unauthorizedresponseViewer.getComponent())
        self._extender.unauthenticated_requests_tabs.addTab("Expand", None)
        self._extender.unauthenticated_requests_tabs.setSelectedIndex(0)
        self._extender._viewer_last_content_tab[id(self._extender.unauthenticated_requests_tabs)] = 0

        if hasattr(self._extender, 'userTab') and self._extender.userTab:
            for user_id in sorted(self._extender.userTab.user_tabs.keys()):
                user_name = self._extender.userTab.user_tabs[user_id]['user_name']
                self.createUserViewerTabs(user_id, user_name)

        self._extender.requests_panel = JPanel(GridLayout(0, 1))
        rebuildViewerPanel(self._extender)

        self._extender.tabs.addTab("Request/Response Viewers", self._extender.requests_panel)

        tabIndex = self._extender.tabs.indexOfTab("Request/Response Viewers")
        tabHeader = JPanel(FlowLayout(FlowLayout.LEFT, 5, 0))
        tabHeader.setOpaque(False)
        tabLabel = JLabel("Request/Response Viewers")
        eyeButton = JButton(createEyeIcon(16))
        eyeButton.setToolTipText("Toggle viewer visibility")
        eyeButton.setBorderPainted(False)
        eyeButton.setContentAreaFilled(False)
        eyeButton.setFocusPainted(False)
        eyeButton.addActionListener(ShowVisibilityPopup(self._extender))
        tabHeader.add(tabLabel)
        tabHeader.add(eyeButton)
        self._extender.tabs.setTabComponentAt(tabIndex, tabHeader)
        
        self._extender.tabs.addTab("Configuration", self._extender._cfg_splitpane)
        self._extender.tabs.setSelectedIndex(1)
        self._extender.tabs.setMinimumSize(Dimension(1,1))
        self._extender._splitpane.setRightComponent(self._extender.tabs)

        self._extender.tabs.addTab("Users", self._extender.userPanel)

    def createUserViewerTabs(self, user_id, user_name):
        user_msg_editor = UserMessageEditor(self._extender, user_id)
        requestViewer = self._extender._callbacks.createMessageEditor(user_msg_editor, False)
        responseViewer = self._extender._callbacks.createMessageEditor(user_msg_editor, False)

        tabs = JTabbedPane()
        tabs.addMouseListener(Mouseclick(self._extender))
        tabs.addChangeListener(ViewerTabChangeListener(self._extender))
        tabs.addTab("{} Request".format(user_name), requestViewer.getComponent())
        tabs.addTab("{} Response".format(user_name), responseViewer.getComponent())
        tabs.addTab("Expand", None)
        tabs.setSelectedIndex(0)
        self._extender._viewer_last_content_tab[id(tabs)] = 0

        self._extender.user_viewers[user_id] = {
            'requestViewer': requestViewer,
            'responseViewer': responseViewer,
            'tabs': tabs,
            'user_name': user_name
        }

        key = 'user_{}'.format(user_id)
        self._extender.viewer_visibility[key] = True

    def removeUserViewerTabs(self, user_id):
        key = 'user_{}'.format(user_id)
        if key in self._extender.viewer_visibility:
            del self._extender.viewer_visibility[key]
        if user_id in self._extender.user_viewers:
            del self._extender.user_viewers[user_id]
        rebuildViewerPanel(self._extender)

    def renameUserViewerTabs(self, user_id, new_name):
        if user_id in self._extender.user_viewers:
            viewer = self._extender.user_viewers[user_id]
            viewer['user_name'] = new_name
            viewer['tabs'].setTitleAt(0, "{} Request".format(new_name))
            viewer['tabs'].setTitleAt(1, "{} Response".format(new_name))

    def setupDynamicColumns(self):
        if hasattr(self._extender, 'tableModel'):
            self._extender.tableModel.fireTableStructureChanged()
        if hasattr(self._extender, 'logTable'):
            self._extender.logTable.updateColumnWidths()

    def refreshTable(self):
        if hasattr(self._extender, 'tableModel'):
            self._extender.tableModel.fireTableStructureChanged()
            self.setupDynamicColumns()

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

        self._callbacks.sendToRepeater(host, port, secure, request.getRequest(), "Autorize")

class SendResponseComparer(ActionListener):
    def __init__(self, extender, callbacks):
        self._extender = extender
        self._callbacks = callbacks

    def actionPerformed(self, e):
        if not hasattr(self._extender, '_currentlyDisplayedItem') or not self._extender._currentlyDisplayedItem:
            return
            
        originalResponse = self._extender._currentlyDisplayedItem._originalrequestResponse
        unauthorizedResponse = self._extender._currentlyDisplayedItem._unauthorizedRequestResponse
        
        selected_col = self._extender.logTable.getSelectedColumn()
        data_col = self._extender.tableModel.getDataColumnIndex(selected_col) if hasattr(self._extender, 'tableModel') else selected_col
        if data_col >= 6 and hasattr(self._extender, 'userTab') and self._extender.userTab:
            user_index = (data_col - 6) >> 1
            user_ids = sorted(self._extender.userTab.user_tabs.keys())
            if user_index < len(user_ids):
                user_id = user_ids[user_index]
                user_data = self._extender._currentlyDisplayedItem.get_user_enforcement(user_id)
                if user_data and user_data['requestResponse']:
                    modifiedResponse = user_data['requestResponse']
                else:
                    modifiedResponse = originalResponse
            else:
                modifiedResponse = originalResponse
        elif data_col == 4 or data_col == 5:
            modifiedResponse = unauthorizedResponse or originalResponse
        else:
            modifiedResponse = originalResponse
        
        self._callbacks.sendToComparer(originalResponse.getResponse())
        if modifiedResponse:
            self._callbacks.sendToComparer(modifiedResponse.getResponse())
        if unauthorizedResponse:
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
        if hasattr(self._extender, '_currentlyDisplayedItem') and self._extender._currentlyDisplayedItem:
            stringSelection = StringSelection(str(self._extender._helpers.analyzeRequest(self._extender._currentlyDisplayedItem._originalrequestResponse).getUrl()))
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
        return self._extender._currentlyDisplayedItem._originalrequestResponse.getHttpService()

    def getRequest(self):
        return self._extender._currentlyDisplayedItem._originalrequestResponse.getRequest()

    def getResponse(self):
        return self._extender._currentlyDisplayedItem._originalrequestResponse.getResponse()

class UserMessageEditor(IMessageEditorController):
    def __init__(self, extender, user_id):
        self._extender = extender
        self._user_id = user_id

    def getHttpService(self):
        return self._extender._currentlyDisplayedItem._originalrequestResponse.getHttpService()

    def getRequest(self):
        user_data = self._extender._currentlyDisplayedItem.get_user_enforcement(self._user_id)
        if user_data and user_data['requestResponse']:
            return user_data['requestResponse'].getRequest()
        return self._extender._currentlyDisplayedItem._originalrequestResponse.getRequest()

    def getResponse(self):
        user_data = self._extender._currentlyDisplayedItem.get_user_enforcement(self._user_id)
        if user_data and user_data['requestResponse']:
            return user_data['requestResponse'].getResponse()
        return self._extender._currentlyDisplayedItem._originalrequestResponse.getResponse()

class ViewerTabChangeListener(ChangeListener):
    def __init__(self, extender):
        self._extender = extender

    def stateChanged(self, evt):
        comp = evt.getSource()
        idx = comp.getSelectedIndex()
        if idx in (0, 1):
            self._extender._viewer_last_content_tab[id(comp)] = idx

class Mouseclick(MouseAdapter):
    def __init__(self, extender):
        self._extender = extender

    def mouseReleased(self, evt):
        comp = evt.getComponent()
        if comp.getSelectedIndex() == 2:
            last_content = self._extender._viewer_last_content_tab.get(id(comp), 0)
            if self._extender.expanded_requests == 0:
                expand(self._extender, comp)
            else:
                collapse(self._extender, comp)
            comp.setSelectedIndex(last_content)

def createEyeIcon(size=16):
    img = BufferedImage(size, size, BufferedImage.TYPE_INT_ARGB)
    g2 = img.createGraphics()
    g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON)
    g2.setColor(AwtColor(80, 80, 80))
    g2.setStroke(BasicStroke(1.5))

    cx = size / 2.0
    cy = size / 2.0
    w = size * 0.85
    h = size * 0.45

    path = GeneralPath()
    path.moveTo(cx - w / 2, cy)
    path.quadTo(cx, cy - h, cx + w / 2, cy)
    path.quadTo(cx, cy + h, cx - w / 2, cy)
    path.closePath()
    g2.draw(path)

    r = size * 0.18
    g2.fill(Ellipse2D.Double(cx - r, cy - r, r * 2, r * 2))

    g2.dispose()
    return ImageIcon(img)

class ShowVisibilityPopup(ActionListener):
    def __init__(self, extender):
        self._extender = extender

    def actionPerformed(self, e):
        popup = JPopupMenu()

        if hasattr(self._extender, 'user_viewers'):
            for user_id in sorted(self._extender.user_viewers.keys()):
                viewer = self._extender.user_viewers[user_id]
                key = 'user_{}'.format(user_id)
                item = JCheckBoxMenuItem(
                    "{} Request/Response".format(viewer['user_name']),
                    self._extender.viewer_visibility.get(key, True)
                )
                item.addActionListener(ViewerVisibilityAction(self._extender, key))
                popup.add(item)

        if popup.getComponentCount() > 0:
            popup.addSeparator()

        orig_item = JCheckBoxMenuItem(
            "Original Request/Response",
            self._extender.viewer_visibility.get('original', True)
        )
        orig_item.addActionListener(ViewerVisibilityAction(self._extender, 'original'))
        popup.add(orig_item)

        unauth_item = JCheckBoxMenuItem(
            "Unauthenticated Request/Response",
            self._extender.viewer_visibility.get('unauthenticated', True)
        )
        unauth_item.addActionListener(ViewerVisibilityAction(self._extender, 'unauthenticated'))
        popup.add(unauth_item)

        btn = e.getSource()
        popup.show(btn, 0, btn.getHeight())

class ViewerVisibilityAction(ActionListener):
    def __init__(self, extender, key):
        self._extender = extender
        self._key = key

    def actionPerformed(self, e):
        source = e.getSource()
        self._extender.viewer_visibility[self._key] = source.isSelected()
        rebuildViewerPanel(self._extender)
        if hasattr(self._extender, 'tabs_instance') and self._extender.tabs_instance:
            self._extender.tabs_instance.setupDynamicColumns()

class SendRequestRepeater(ActionListener):
    def __init__(self, extender, callbacks, original):
        self._extender = extender
        self._callbacks = callbacks
        self.original = original

    def actionPerformed(self, e):
        if not hasattr(self._extender, '_currentlyDisplayedItem') or not self._extender._currentlyDisplayedItem:
            return
            
        if self.original:
            request = self._extender._currentlyDisplayedItem._originalrequestResponse
        else:
            selected_col = self._extender.logTable.getSelectedColumn()
            data_col = self._extender.tableModel.getDataColumnIndex(selected_col) if hasattr(self._extender, 'tableModel') else selected_col
            if data_col >= 6 and hasattr(self._extender, 'userTab') and self._extender.userTab:
                user_index = (data_col - 6) >> 1
                user_ids = sorted(self._extender.userTab.user_tabs.keys())
                if user_index < len(user_ids):
                    user_id = user_ids[user_index]
                    user_data = self._extender._currentlyDisplayedItem.get_user_enforcement(user_id)
                    if user_data and user_data['requestResponse']:
                        request = user_data['requestResponse']
                    else:
                        request = self._extender._currentlyDisplayedItem._originalrequestResponse
                else:
                    request = self._extender._currentlyDisplayedItem._originalrequestResponse
            elif data_col == 4 or data_col == 5:
                request = self._extender._currentlyDisplayedItem._unauthorizedRequestResponse or self._extender._currentlyDisplayedItem._originalrequestResponse
            else:
                request = self._extender._currentlyDisplayedItem._originalrequestResponse
                
        host = request.getHttpService().getHost()
        port = request.getHttpService().getPort()
        proto = request.getHttpService().getProtocol()
        secure = True if proto == "https" else False

        self._callbacks.sendToRepeater(host, port, secure, request.getRequest(), "Autorize")

class SendRequestToRepeaterAction(AbstractAction):
    def __init__(self, extender, callbacks):
        self._extender = extender
        self._callbacks = callbacks

    def actionPerformed(self, e):
        if not hasattr(self._extender, '_currentlyDisplayedItem') or not self._extender._currentlyDisplayedItem:
            return
            
        selected_col = self._extender.logTable.getSelectedColumn()
        data_col = self._extender.tableModel.getDataColumnIndex(selected_col) if hasattr(self._extender, 'tableModel') else selected_col
        if data_col >= 6 and hasattr(self._extender, 'userTab') and self._extender.userTab:
            user_index = (data_col - 6) >> 1
            user_ids = sorted(self._extender.userTab.user_tabs.keys())
            if user_index < len(user_ids):
                user_id = user_ids[user_index]
                user_data = self._extender._currentlyDisplayedItem.get_user_enforcement(user_id)
                if user_data and user_data['requestResponse']:
                    request = user_data['requestResponse']
                else:
                    request = self._extender._currentlyDisplayedItem._originalrequestResponse
            else:
                request = self._extender._currentlyDisplayedItem._originalrequestResponse
        elif data_col == 4 or data_col == 5:
            request = self._extender._currentlyDisplayedItem._unauthorizedRequestResponse or self._extender._currentlyDisplayedItem._originalrequestResponse
        else:
            request = self._extender._currentlyDisplayedItem._originalrequestResponse

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
        if hasattr(self._extender, '_currentlyDisplayedItem') and self._extender._currentlyDisplayedItem:
            stringSelection = StringSelection(str(self._extender._helpers.analyzeRequest(self._extender._currentlyDisplayedItem._originalrequestResponse).getUrl()))
            clpbrd = Toolkit.getDefaultToolkit().getSystemClipboard()
            clpbrd.setContents(stringSelection, None)