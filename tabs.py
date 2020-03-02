from javax.swing import JSplitPane
from javax.swing import JMenuItem
from javax.swing import JScrollPane
from javax.swing import JPopupMenu
from javax.swing import JTabbedPane
from javax.swing.table import TableRowSorter
from javax.swing.table import AbstractTableModel
from java.lang import Math

from table import Table, LogEntry, tableFilter, autoScrollListener, copySelectedURL, \
    sendRequestRepeater, sendResponseComparer, retestSelectedRequest, deleteSelectedRequest

def init_tabs(self):
        """  init autorize tabs
        """
        
        self.logTable = Table(self)

        #self.logTable.setAutoCreateRowSorter(True)

        tableWidth = self.logTable.getPreferredSize().width        
        self.logTable.getColumn("ID").setPreferredWidth(Math.round(tableWidth / 50 * 2))
        self.logTable.getColumn("Method").setPreferredWidth(Math.round(tableWidth / 50 * 3))
        self.logTable.getColumn("URL").setPreferredWidth(Math.round(tableWidth / 50 * 25))
        self.logTable.getColumn("Orig. Length").setPreferredWidth(Math.round(tableWidth / 50 * 4))
        self.logTable.getColumn("Modif. Length").setPreferredWidth(Math.round(tableWidth / 50 * 4))
        self.logTable.getColumn("Unauth. Length").setPreferredWidth(Math.round(tableWidth / 50 * 4))
        self.logTable.getColumn("Authorization Enforcement Status").setPreferredWidth(Math.round(tableWidth / 50 * 4))
        self.logTable.getColumn("Authorization Unauth. Status").setPreferredWidth(Math.round(tableWidth / 50 * 4))

        self.tableSorter = TableRowSorter(self)
        filter = tableFilter(self)
        self.tableSorter.setRowFilter(filter)
        self.logTable.setRowSorter(self.tableSorter)

        self._splitpane = JSplitPane(JSplitPane.HORIZONTAL_SPLIT)
        self._splitpane.setResizeWeight(1)
        self.scrollPane = JScrollPane(self.logTable)
        self._splitpane.setLeftComponent(self.scrollPane)
        self.scrollPane.getVerticalScrollBar().addAdjustmentListener(autoScrollListener(self))

        copyURLitem = JMenuItem("Copy URL")
        copyURLitem.addActionListener(copySelectedURL(self))

        sendRequestMenu = JMenuItem("Send Original Request to Repeater")
        sendRequestMenu.addActionListener(sendRequestRepeater(self, self._callbacks, True))

        sendRequestMenu2 = JMenuItem("Send Modified Request to Repeater")
        sendRequestMenu2.addActionListener(sendRequestRepeater(self, self._callbacks, False))

        sendResponseMenu = JMenuItem("Send Responses to Comparer")
        sendResponseMenu.addActionListener(sendResponseComparer(self, self._callbacks))

        retestSelecteditem = JMenuItem("Retest selected request")
        retestSelecteditem.addActionListener(retestSelectedRequest(self))
        
        deleteSelectedItem = JMenuItem("Delete")
        deleteSelectedItem.addActionListener(deleteSelectedRequest(self))

        self.menu = JPopupMenu("Popup")
        self.menu.add(sendRequestMenu)
        self.menu.add(sendRequestMenu2)
        self.menu.add(sendResponseMenu)
        self.menu.add(copyURLitem)
        self.menu.add(retestSelecteditem)
        # self.menu.add(deleteSelectedItem) disabling this feature until bug will be fixed.

        self.tabs = JTabbedPane()
        self._requestViewer = self._callbacks.createMessageEditor(self, False)
        self._responseViewer = self._callbacks.createMessageEditor(self, False)

        self._originalrequestViewer = self._callbacks.createMessageEditor(self, False)
        self._originalresponseViewer = self._callbacks.createMessageEditor(self, False)

        self._unauthorizedrequestViewer = self._callbacks.createMessageEditor(self, False)
        self._unauthorizedresponseViewer = self._callbacks.createMessageEditor(self, False)        

        self.tabs.addTab("Modified Request", self._requestViewer.getComponent())
        self.tabs.addTab("Modified Response", self._responseViewer.getComponent())

        self.tabs.addTab("Original Request", self._originalrequestViewer.getComponent())
        self.tabs.addTab("Original Response", self._originalresponseViewer.getComponent())

        self.tabs.addTab("Unauthenticated Request", self._unauthorizedrequestViewer.getComponent())
        self.tabs.addTab("Unauthenticated Response", self._unauthorizedresponseViewer.getComponent())        

        self.tabs.addTab("Configuration", self.pnl)
        self.tabs.setSelectedIndex(6)
        self._splitpane.setRightComponent(self.tabs)
