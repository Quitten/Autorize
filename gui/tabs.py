#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from java.awt.datatransfer import StringSelection
from javax.swing.table import TableRowSorter
from java.awt.event import AdjustmentListener
from java.awt.event import ActionListener
from java.awt.event import MouseAdapter
from javax.swing import JSplitPane
from javax.swing import JMenuItem
from javax.swing import JMenu
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

from table import Table, TableRowFilter, resolve_modified_repeater_target
from helpers.filters import expand, collapse, rebuildViewerPanel
from javax.swing import KeyStroke
from javax.swing import JTable
from javax.swing import AbstractAction
from javax.swing.event import ChangeListener, ChangeEvent
from javax.swing.event import PopupMenuListener
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

        self._extender._splitpane = JSplitPane(JSplitPane.HORIZONTAL_SPLIT)
        self._extender._splitpane.setResizeWeight(1)
        self._extender.scrollPane = JScrollPane(self._extender.logTable)
        self._extender.scrollPane.setMinimumSize(Dimension(1,1))
        self._extender._splitpane.setLeftComponent(self._extender.scrollPane)
        self._extender.scrollPane.getVerticalScrollBar().addAdjustmentListener(AutoScrollListener(self._extender))

        copyURLitem = JMenuItem("Copy URL")
        copyURLitem.addActionListener(CopySelectedURL(self._extender))

        sendRequestMenu = JMenuItem("Send Original Request to Repeater")
        sendRequestMenu.addActionListener(SendOriginalToRepeaterAction(self._extender, self._extender._callbacks))

        self._extender.sendToRepeaterSubmenu = JMenu("Send User Request to Repeater")
        self._extender.sendToComparerSubmenu = JMenu("Send responses to Comparer")

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

        retestSelecteditem = JMenuItem("Retest selected request")
        retestSelecteditem.addActionListener(RetestSelectedRequest(self._extender))

        retestAllitem = JMenuItem("Retest all requests")
        retestAllitem.addActionListener(RetestAllRequests(self._extender))
        
        deleteSelectedItem = JMenuItem("Delete")
        deleteSelectedItem.addActionListener(DeleteSelectedRequest(self._extender))

        self._extender.menu = JPopupMenu("Popup")
        self._extender.menu.addPopupMenuListener(ContextMenuSyncListener(self._extender))
        self._extender.menu.add(sendRequestMenu)
        self._extender.menu.add(self._extender.sendToRepeaterSubmenu)
        self._extender.menu.add(self._extender.sendToComparerSubmenu)
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

    def sync_log_table_sorter(self):
        """Rebuild row sorter so added/removed user columns appear (TableRowSorter can stay stale)."""
        if not hasattr(self._extender, 'logTable') or not hasattr(self._extender, 'tableModel'):
            return
        self._extender.tableSorter = TableRowSorter(self._extender.tableModel)
        self._extender.tableSorter.setRowFilter(TableRowFilter(self._extender))
        self._extender.logTable.setRowSorter(self._extender.tableSorter)

    def setupDynamicColumns(self):
        if hasattr(self._extender, 'tableModel'):
            self._extender.tableModel.fireTableStructureChanged()
        if hasattr(self._extender, 'logTable'):
            self.sync_log_table_sorter()
            self._extender.logTable.updateColumnWidths()

    def refreshTable(self):
        self.setupDynamicColumns()

def _context_menu_user_label(extender, user_id):
    if hasattr(extender, "userTab") and extender.userTab and user_id in extender.userTab.user_tabs:
        return extender.userTab.user_tabs[user_id]["user_name"]
    return "User {}".format(user_id)


def _autorize_repeater_tab_caption(label_suffix):
    if not label_suffix:
        return "Autorize"
    return "Autorize - {}".format(label_suffix)


def rebuild_log_table_context_menu_dynamic(extender):
    if not hasattr(extender, "sendToRepeaterSubmenu"):
        return
    extender.sendToRepeaterSubmenu.removeAll()
    extender.sendToComparerSubmenu.removeAll()

    table = getattr(extender, "logTable", None)
    log_entry = getattr(extender, "_currentlyDisplayedItem", None)
    has_row = table is not None and table.getSelectedRow() >= 0

    if has_row and log_entry is not None:
        user_ids_for_menu = sorted(log_entry.get_all_users())
    else:
        user_ids_for_menu = []

    for user_id in user_ids_for_menu:
        user_name = _context_menu_user_label(extender, user_id)
        r_item = JMenuItem("Send {} to Repeater".format(user_name))
        r_item.addActionListener(SendUserToRepeaterAction(extender, extender._callbacks, user_id))
        extender.sendToRepeaterSubmenu.add(r_item)
        c_item = JMenuItem("Original vs {} response".format(user_name))
        c_item.addActionListener(SendUserComparerAction(extender, extender._callbacks, user_id))
        extender.sendToComparerSubmenu.add(c_item)

    show_unauth = bool(
        has_row and log_entry is not None and log_entry._unauthorizedRequestResponse is not None
    )

    if extender.sendToRepeaterSubmenu.getMenuComponentCount() > 0 and show_unauth:
        extender.sendToRepeaterSubmenu.addSeparator()
        extender.sendToComparerSubmenu.addSeparator()

    if show_unauth:
        u_r = JMenuItem("Send Unauthenticated to Repeater")
        u_r.addActionListener(SendUnauthenticatedToRepeaterAction(extender, extender._callbacks))
        extender.sendToRepeaterSubmenu.add(u_r)
        u_c = JMenuItem("Original vs Unauthenticated response")
        u_c.addActionListener(SendUnauthenticatedComparerAction(extender, extender._callbacks))
        extender.sendToComparerSubmenu.add(u_c)


class ContextMenuSyncListener(PopupMenuListener):
    def __init__(self, extender):
        self._extender = extender

    def popupMenuWillBecomeVisible(self, e):
        table = getattr(self._extender, "logTable", None)
        if table is not None and table.getSelectedRow() >= 0:
            table.refresh_context_menu_labels()
        rebuild_log_table_context_menu_dynamic(self._extender)

    def popupMenuWillBecomeInvisible(self, e):
        pass

    def popupMenuCanceled(self, e):
        pass


class SendUserToRepeaterAction(ActionListener):
    def __init__(self, extender, callbacks, user_id):
        self._extender = extender
        self._callbacks = callbacks
        self._user_id = user_id

    def actionPerformed(self, e):
        if not hasattr(self._extender, "_currentlyDisplayedItem") or not self._extender._currentlyDisplayedItem:
            return
        item = self._extender._currentlyDisplayedItem
        user_data = item.get_user_enforcement(self._user_id)
        if user_data and user_data["requestResponse"]:
            request_rr = user_data["requestResponse"]
        else:
            request_rr = item._originalrequestResponse
        caption = _autorize_repeater_tab_caption(_context_menu_user_label(self._extender, self._user_id))
        self._send(request_rr, caption)

    def _send(self, request_rr, caption):
        host = request_rr.getHttpService().getHost()
        port = request_rr.getHttpService().getPort()
        proto = request_rr.getHttpService().getProtocol()
        secure = True if proto == "https" else False
        self._callbacks.sendToRepeater(host, port, secure, request_rr.getRequest(), caption)


class SendUnauthenticatedToRepeaterAction(ActionListener):
    def __init__(self, extender, callbacks):
        self._extender = extender
        self._callbacks = callbacks

    def actionPerformed(self, e):
        if not hasattr(self._extender, "_currentlyDisplayedItem") or not self._extender._currentlyDisplayedItem:
            return
        item = self._extender._currentlyDisplayedItem
        request_rr = item._unauthorizedRequestResponse or item._originalrequestResponse
        host = request_rr.getHttpService().getHost()
        port = request_rr.getHttpService().getPort()
        proto = request_rr.getHttpService().getProtocol()
        secure = True if proto == "https" else False
        caption = _autorize_repeater_tab_caption("Unauthenticated")
        self._callbacks.sendToRepeater(host, port, secure, request_rr.getRequest(), caption)


class SendUserComparerAction(ActionListener):
    def __init__(self, extender, callbacks, user_id):
        self._extender = extender
        self._callbacks = callbacks
        self._user_id = user_id

    def actionPerformed(self, e):
        if not hasattr(self._extender, "_currentlyDisplayedItem") or not self._extender._currentlyDisplayedItem:
            return
        item = self._extender._currentlyDisplayedItem
        original_response = self._extender._currentlyDisplayedItem._originalrequestResponse
        user_data = item.get_user_enforcement(self._user_id)
        if user_data and user_data["requestResponse"]:
            modified = user_data["requestResponse"]
        else:
            modified = original_response
        self._callbacks.sendToComparer(original_response.getResponse())
        self._callbacks.sendToComparer(modified.getResponse())


class SendUnauthenticatedComparerAction(ActionListener):
    def __init__(self, extender, callbacks):
        self._extender = extender
        self._callbacks = callbacks

    def actionPerformed(self, e):
        if not hasattr(self._extender, "_currentlyDisplayedItem") or not self._extender._currentlyDisplayedItem:
            return
        item = self._extender._currentlyDisplayedItem
        original_response = item._originalrequestResponse
        modified = item._unauthorizedRequestResponse or original_response
        self._callbacks.sendToComparer(original_response.getResponse())
        self._callbacks.sendToComparer(modified.getResponse())


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

class SendOriginalToRepeaterAction(ActionListener):
    def __init__(self, extender, callbacks):
        self._extender = extender
        self._callbacks = callbacks

    def actionPerformed(self, e):
        if not hasattr(self._extender, '_currentlyDisplayedItem') or not self._extender._currentlyDisplayedItem:
            return
        request = self._extender._currentlyDisplayedItem._originalrequestResponse
        host = request.getHttpService().getHost()
        port = request.getHttpService().getPort()
        proto = request.getHttpService().getProtocol()
        secure = True if proto == "https" else False
        self._callbacks.sendToRepeater(
            host, port, secure, request.getRequest(), _autorize_repeater_tab_caption("Original")
        )

class SendRequestToRepeaterAction(AbstractAction):
    def __init__(self, extender, callbacks):
        self._extender = extender
        self._callbacks = callbacks

    def actionPerformed(self, e):
        if not hasattr(self._extender, '_currentlyDisplayedItem') or not self._extender._currentlyDisplayedItem:
            return

        data_col = getattr(self._extender, "_repeaterContextDataCol", -1)
        if data_col < 0:
            selected_col = self._extender.logTable.getSelectedColumn()
            data_col = (
                self._extender.tableModel.getDataColumnIndex(selected_col)
                if hasattr(self._extender, "tableModel")
                else selected_col
            )
        request, menu_name = resolve_modified_repeater_target(self._extender, data_col)
        if not request:
            return

        host = request.getHttpService().getHost()
        port = request.getHttpService().getPort()
        proto = request.getHttpService().getProtocol()
        secure = True if proto == "https" else False

        caption = _autorize_repeater_tab_caption(menu_name if menu_name else "Original")
        self._callbacks.sendToRepeater(host, port, secure, request.getRequest(), caption)

class CopySelectedURLToClipBoard(AbstractAction):
    def __init__(self, extender, callbacks):
        self._extender = extender
        self._callbacks = callbacks

    def actionPerformed(self, e):
        if hasattr(self._extender, '_currentlyDisplayedItem') and self._extender._currentlyDisplayedItem:
            stringSelection = StringSelection(str(self._extender._helpers.analyzeRequest(self._extender._currentlyDisplayedItem._originalrequestResponse).getUrl()))
            clpbrd = Toolkit.getDefaultToolkit().getSystemClipboard()
            clpbrd.setContents(stringSelection, None)