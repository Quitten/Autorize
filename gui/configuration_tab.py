#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from javax.swing import SwingUtilities
from javax.swing import JToggleButton
from javax.swing import JScrollPane
from javax.swing import JTabbedPane
from javax.swing import JOptionPane
from javax.swing import GroupLayout
from javax.swing import JSplitPane
from javax.swing import JTextArea
from javax.swing import JCheckBox
from javax.swing import JButton
from javax.swing import JPanel
from javax.swing import JLabel
from javax.swing import BorderFactory
from javax.swing.event import DocumentListener
from java.awt import GridLayout, BorderLayout, Color
from java.awt.event import ItemListener, MouseAdapter
from java.lang import Runnable

from table import UpdateTableEDT

class ConfigurationTab():
    def __init__(self, extender):
        self._extender = extender
        try:
            self._extender._cfg_tab = self
            if not hasattr(self._extender, '_hoveredRuleTitle'):
                self._extender._hoveredRuleTitle = None
        except Exception:
            pass

    def draw(self):
        """  init configuration tab """
        self.DEFUALT_REPLACE_TEXT = "Cookie: Insert=injected; cookie=or;\nHeader: here"

        # Top controls
        self._extender.startButton = JToggleButton("Autorize is off", actionPerformed=self.startOrStop)
        self._extender.startButton.setBounds(10, 20, 230, 30)

        self._extender.clearButton = JButton("Clear List", actionPerformed=self.clearList)
        self._extender.clearButton.setBounds(10, 80, 100, 30)
        self._extender.autoScroll = JCheckBox("Auto Scroll")
        self._extender.autoScroll.setBounds(145, 80, 130, 30)

        self._extender.ignore304 = JCheckBox("Ignore 304/204 status code responses")
        self._extender.ignore304.setBounds(280, 5, 300, 30)
        self._extender.ignore304.setSelected(True)

        self._extender.prevent304 = JCheckBox("Prevent 304 Not Modified status code")
        self._extender.prevent304.setBounds(280, 25, 300, 30)
        self._extender.interceptRequestsfromRepeater = JCheckBox("Intercept requests from Repeater")
        self._extender.interceptRequestsfromRepeater.setBounds(280, 45, 300, 30)

        self._extender.doUnauthorizedRequest = JCheckBox("Check unauthenticated")
        self._extender.doUnauthorizedRequest.setBounds(280, 65, 300, 30)
        self._extender.doUnauthorizedRequest.setSelected(True)

        self._extender.replaceQueryParam = JCheckBox("Replace query params", actionPerformed=self.replaceQueryHanlder)
        self._extender.replaceQueryParam.setBounds(280, 85, 300, 30)
        self._extender.replaceQueryParam.setSelected(False)

        self._extender.saveHeadersButton = JButton("Add", actionPerformed=self.saveHeaders)
        self._extender.saveHeadersButton.setBounds(315, 115, 80, 30)
        self._extender.removeHeadersButton = JButton("Remove", actionPerformed=self.removeHeaders)
        self._extender.removeHeadersButton.setBounds(400, 115, 80, 30)
        self._extender._selectedRuleTitle = None

        self._extender.rulesChecklistPanel = JPanel()
        self._extender.rulesChecklistPanel.setLayout(GridLayout(0, 1))
        try:
            self._extender.rulesChecklistScroll = JScrollPane(self._extender.rulesChecklistPanel)
            self._extender.rulesChecklistScroll.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_NEVER)
            self._extender.rulesChecklistScroll.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_NEVER)
            self._extender.rulesChecklistScroll.setBorder(None)
            self._extender.rulesChecklistScroll.setViewportBorder(None)
        except Exception:
            pass
        try:
            self._extender.rulesChecklistPanel.setBorder(None)
            self._extender.rulesChecklistPanel.setOpaque(False)
        except Exception:
            pass

        self._extender.replaceString = JTextArea(self.DEFUALT_REPLACE_TEXT, 5, 30)
        self._extender.replaceString.setWrapStyleWord(True)
        self._extender.replaceString.setLineWrap(True)
        self._extender._suppressTextEvents = False
        self._extender.replaceString.getDocument().addDocumentListener(ReplaceStringDocumentListener(self._extender))

        scrollReplaceString = JScrollPane(self._extender.replaceString)
        scrollReplaceString.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollReplaceString.setBounds(10, 255, 470, 150)

        fromLastRequestLabel = JLabel("From last request:")
        fromLastRequestLabel.setBounds(10, 305, 250, 30)

        self._extender.fetchCookiesHeaderButton = JButton("Fetch Cookies header", actionPerformed=self.fetchCookiesHeader)
        self._extender.fetchCookiesHeaderButton.setEnabled(False)
        self._extender.fetchCookiesHeaderButton.setBounds(10, 330, 220, 30)

        self._extender.fetchAuthorizationHeaderButton = JButton("Fetch Authorization header", actionPerformed=self.fetchAuthorizationHeader)
        self._extender.fetchAuthorizationHeaderButton.setEnabled(False)
        self._extender.fetchAuthorizationHeaderButton.setBounds(260, 330, 220, 30)

        # Bottom filters tabs
        self._extender.filtersTabs = JTabbedPane()
        self._extender.filtersTabs.addTab("Enforcement Detector", self._extender.EDPnl)
        self._extender.filtersTabs.addTab("Detector Unauthenticated", self._extender.EDPnlUnauth)
        self._extender.filtersTabs.addTab("Interception Filters", self._extender.filtersPnl)
        self._extender.filtersTabs.addTab("Match/Replace", self._extender.MRPnl)
        self._extender.filtersTabs.addTab("Table Filter", self._extender.filterPnl)
        self._extender.filtersTabs.addTab("Save/Restore", self._extender.exportPnl)
        self._extender.filtersTabs.setSelectedIndex(2)
        self._extender.filtersTabs.setBounds(0, 350, 2000, 700)

        # Layout
        self.config_pnl = JPanel()
        layout = GroupLayout(self.config_pnl)
        self.config_pnl.setLayout(layout)
        layout.setAutoCreateGaps(True)
        layout.setAutoCreateContainerGaps(True)

        layout.setHorizontalGroup(
            layout.createSequentialGroup()
                .addGroup(
                    layout.createParallelGroup()
                        .addComponent(self._extender.startButton, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                        .addComponent(self._extender.clearButton, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                        .addComponent(self._extender.rulesChecklistPanel, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                        .addComponent(scrollReplaceString, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                        .addComponent(fromLastRequestLabel, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                        .addGroup(layout.createSequentialGroup()
                            .addComponent(self._extender.fetchCookiesHeaderButton, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                            .addComponent(self._extender.fetchAuthorizationHeaderButton, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                        )
                )
                .addGroup(
                    layout.createParallelGroup()
                        .addComponent(self._extender.ignore304, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                        .addComponent(self._extender.prevent304, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                        .addComponent(self._extender.interceptRequestsfromRepeater, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                        .addComponent(self._extender.doUnauthorizedRequest, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                        .addComponent(self._extender.autoScroll, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                        .addComponent(self._extender.replaceQueryParam, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                        .addComponent(self._extender.saveHeadersButton, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                        .addComponent(self._extender.removeHeadersButton, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                )
        )

        layout.setVerticalGroup(
            layout.createSequentialGroup()
                .addGroup(layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                    .addComponent(self._extender.startButton, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                    .addComponent(self._extender.ignore304, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                )
                .addComponent(self._extender.prevent304, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                .addComponent(self._extender.interceptRequestsfromRepeater, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                .addComponent(self._extender.doUnauthorizedRequest, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                .addComponent(self._extender.replaceQueryParam, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                .addGroup(layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                    .addComponent(self._extender.clearButton, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                    .addComponent(self._extender.autoScroll, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                )
                .addGroup(layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                    .addGroup(layout.createSequentialGroup()
                        .addComponent(self._extender.saveHeadersButton, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                        .addComponent(self._extender.removeHeadersButton, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                    )
                )
                .addComponent(self._extender.rulesChecklistPanel, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                .addComponent(scrollReplaceString, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                .addComponent(fromLastRequestLabel, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                .addGroup(layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                    .addComponent(self._extender.fetchCookiesHeaderButton, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                    .addComponent(self._extender.fetchAuthorizationHeaderButton, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                )
        )

        self._extender._cfg_splitpane = JSplitPane(JSplitPane.VERTICAL_SPLIT)
        self._extender._cfg_splitpane.setResizeWeight(0.5)
        self._extender._cfg_splitpane.setBounds(0, 0, 1000, 1000)
        self._extender._cfg_splitpane.setRightComponent(self._extender.filtersTabs)
        self._extender._cfg_splitpane.setLeftComponent(self.config_pnl)

        try:
            self.refreshRulesChecklist()
        except Exception:
            pass
        try:
            self.updateReplaceQueryVisualCue()
        except Exception:
            pass

    def startOrStop(self, event):
        if self._extender.startButton.getText() == "Autorize is off":
            self._extender.startButton.setText("Autorize is on")
            self._extender.startButton.setSelected(True)
            self._extender.intercept = 1
        else:
            self._extender.startButton.setText("Autorize is off")
            self._extender.startButton.setSelected(False)
            self._extender.intercept = 0
    
    def clearList(self, event):
        self._extender._lock.acquire()
        oldSize = self._extender._log.size()
        self._extender._log.clear()
        SwingUtilities.invokeLater(UpdateTableEDT(self._extender,"delete",0, oldSize - 1))
        self._extender._lock.release()
        try:
            self._extender._currentlyDisplayedItem = None
            class _ClearViewers(Runnable):
                def __init__(self, ext):
                    self.ext = ext
                def run(self):
                    try:
                        try:
                            self.ext.logTable.clearSelection()
                        except Exception:
                            pass
                        try:
                            empty_bytes = self.ext._helpers.stringToBytes("") if hasattr(self.ext, '_helpers') else None
                            if empty_bytes is None:
                                try:
                                    empty_bytes = "".encode('utf-8')
                                except Exception:
                                    empty_bytes = ""
                            try:
                                self.ext._requestViewer = self.ext._callbacks.createMessageEditor(None, False)
                                self.ext._responseViewer = self.ext._callbacks.createMessageEditor(None, False)
                                self.ext._originalrequestViewer = self.ext._callbacks.createMessageEditor(None, False)
                                self.ext._originalresponseViewer = self.ext._callbacks.createMessageEditor(None, False)
                                self.ext._unauthorizedrequestViewer = self.ext._callbacks.createMessageEditor(None, False)
                                self.ext._unauthorizedresponseViewer = self.ext._callbacks.createMessageEditor(None, False)
                            except Exception:
                                pass

                            try:
                                self.ext._requestViewer.setMessage(empty_bytes, True)
                                self.ext._responseViewer.setMessage(empty_bytes, False)
                                self.ext._originalrequestViewer.setMessage(empty_bytes, True)
                                self.ext._originalresponseViewer.setMessage(empty_bytes, False)
                                self.ext._unauthorizedrequestViewer.setMessage(empty_bytes, True)
                                self.ext._unauthorizedresponseViewer.setMessage(empty_bytes, False)
                            except Exception:
                                pass
                        except Exception:
                            pass
                        
                        try:
                            tabs = self.ext.modified_requests_tabs
                            while tabs.getTabCount() > 0:
                                tabs.removeTabAt(0)
                            tabs.addTab("Modified Request", self.ext._requestViewer.getComponent())
                            tabs.addTab("Modified Response", self.ext._responseViewer.getComponent())
                            tabs.addTab("Expand", None)
                            tabs.setSelectedIndex(0)
                            tabs.revalidate()
                            tabs.repaint()
                        except Exception:
                            pass
                        try:
                            tabs = self.ext.original_requests_tabs
                            while tabs.getTabCount() > 0:
                                tabs.removeTabAt(0)
                            tabs.addTab("Original Request", self.ext._originalrequestViewer.getComponent())
                            tabs.addTab("Original Response", self.ext._originalresponseViewer.getComponent())
                            tabs.addTab("Expand", None)
                            tabs.setSelectedIndex(0)
                            tabs.revalidate()
                            tabs.repaint()
                        except Exception:
                            pass
                        try:
                            tabs = self.ext.unauthenticated_requests_tabs
                            while tabs.getTabCount() > 0:
                                tabs.removeTabAt(0)
                            tabs.addTab("Unauthenticated Request", self.ext._unauthorizedrequestViewer.getComponent())
                            tabs.addTab("Unauthenticated Response", self.ext._unauthorizedresponseViewer.getComponent())
                            tabs.addTab("Expand", None)
                            tabs.setSelectedIndex(0)
                            tabs.revalidate()
                            tabs.repaint()
                        except Exception:
                            pass
                        try:
                            self.ext.requests_panel.revalidate()
                            self.ext.requests_panel.repaint()
                        except Exception:
                            pass
                    except Exception:
                        pass
            SwingUtilities.invokeLater(_ClearViewers(self._extender))
        except Exception:
            pass
    
    def replaceQueryHanlder(self, event):
        selected = getattr(self._extender, '_selectedRuleTitle', None)
        if not selected:
            self._extender.replaceString.setText("paramName=paramValue" if self._extender.replaceQueryParam.isSelected() else self.DEFUALT_REPLACE_TEXT)
            try:
                self.updateReplaceQueryVisualCue()
            except Exception:
                pass
            return
        is_query = self._extender.replaceQueryParam.isSelected()
        for obj in self._extender.savedHeaders:
            if obj.get('title') == selected:
                if 'param' not in obj:
                    obj['param'] = "paramName=paramValue"
                if 'headers' not in obj:
                    obj['headers'] = self.DEFUALT_REPLACE_TEXT
                obj['isQueryParam'] = bool(is_query)
                try:
                    self._extender._suppressTextEvents = True
                    self._extender.replaceString.setText(obj['param'] if is_query else obj['headers'])
                finally:
                    self._extender._suppressTextEvents = False
                try:
                    badges = getattr(self._extender, '_rulesTypeLabels', {})
                    if selected in badges:
                        badges[selected].setText("QP" if is_query else "H")
                except Exception:
                    pass
                break
        try:
            self.updateReplaceQueryVisualCue()
        except Exception:
            pass

    def saveHeaders(self, event):
        savedHeadersTitle = JOptionPane.showInputDialog("Please provide saved rule title:")
        if savedHeadersTitle is None or savedHeadersTitle == "":
            return
        text = self._extender.replaceString.getText()
        currentIsQuery = self._extender.replaceQueryParam.isSelected()
        updated = False
        for obj in self._extender.savedHeaders:
            if obj['title'] == savedHeadersTitle:
                if 'param' not in obj:
                    obj['param'] = "paramName=paramValue"
                if currentIsQuery:
                    obj['param'] = text
                    obj['isQueryParam'] = True
                else:
                    obj['headers'] = text
                    obj['isQueryParam'] = False
                if 'enabled' not in obj:
                    obj['enabled'] = True
                updated = True
                break
        if not updated:
            self._extender.savedHeaders.append({
                'title': savedHeadersTitle,
                'headers': text if not currentIsQuery else self.DEFUALT_REPLACE_TEXT,
                'param': text if currentIsQuery else "paramName=paramValue",
                'isQueryParam': bool(currentIsQuery),
                'enabled': True
            })
        try:
            self.refreshRulesChecklist()
            self._extender._selectedRuleTitle = savedHeadersTitle
            try:
                self._extender._suppressTextEvents = True
                self._extender.replaceQueryParam.setSelected(bool(currentIsQuery))
                self._extender.replaceString.setText(text)
            finally:
                self._extender._suppressTextEvents = False
            try:
                self.updateReplaceQueryVisualCue()
            except Exception:
                pass
            
            try:
                if hasattr(self._extender, '_cfg_tab') and self._extender._cfg_tab is not None:
                    self._extender._cfg_tab.updateRuleHighlights()
            except Exception:
                pass
        except Exception:
            pass
    
    def removeHeaders(self, event):
        selectedItem = getattr(self._extender, '_selectedRuleTitle', None)
        if not selectedItem or selectedItem == "Temporary headers":
            return

        delObject = None
        for savedHeaderObj in self._extender.savedHeaders:
            if selectedItem == savedHeaderObj['title']:
                delObject = savedHeaderObj
        self._extender.savedHeaders.remove(delObject)
        try:
            self.refreshRulesChecklist()
            titles = self.getSavedHeadersTitles()
            self._extender._selectedRuleTitle = titles[0] if titles else None
            if self._extender._selectedRuleTitle:
                headers = [x for x in self._extender.savedHeaders if x['title'] == self._extender._selectedRuleTitle]
                obj = headers[0] if headers else None
                if obj is not None:
                    if 'param' not in obj:
                        obj['param'] = "paramName=paramValue"
                    if 'isQueryParam' not in obj:
                        obj['isQueryParam'] = False
                    try:
                        self._extender._suppressTextEvents = True
                        self._extender.replaceQueryParam.setSelected(bool(obj.get('isQueryParam', False)))
                        self._extender.replaceString.setText(obj['param'] if obj.get('isQueryParam', False) else obj.get('headers', ""))
                    finally:
                        self._extender._suppressTextEvents = False
                    try:
                        self.updateReplaceQueryVisualCue()
                    except Exception:
                        pass
            try:
                if hasattr(self._extender, '_cfg_tab') and self._extender._cfg_tab is not None:
                    self._extender._cfg_tab.updateRuleHighlights()
            except Exception:
                pass
        except Exception:
            pass

    def getSavedHeadersTitles(self):
        titles = []
        for savedHeaderObj in self._extender.savedHeaders:
            titles.append(savedHeaderObj['title'])
        return titles

    def fetchCookiesHeader(self, event):
        if self._extender.lastCookiesHeader:
            self._extender.replaceString.setText(self._extender.lastCookiesHeader)
    
    def fetchAuthorizationHeader(self, event):
        if self._extender.lastAuthorizationHeader:
            self._extender.replaceString.setText(self._extender.lastAuthorizationHeader)

    def refreshRulesChecklist(self):
        try:
            panel = self._extender.rulesChecklistPanel
            panel.removeAll()
            self._extender._rulesRowPanels = {}
            self._extender._rulesCheckboxes = {}
            self._extender._rulesTypeLabels = {}
            first_title = None
            for obj in self._extender.savedHeaders:
                title = obj.get('title', 'Untitled')
                if first_title is None:
                    first_title = title
                if 'enabled' not in obj:
                    obj['enabled'] = True
                row = JPanel()
                row.setLayout(BorderLayout())
                cb = JCheckBox("")
                cb.setSelected(bool(obj.get('enabled', True)))
                cb.addItemListener(RuleEnableListener(self._extender, title))
                lbl = JLabel(title)
                type_lbl = JLabel("QP" if bool(obj.get('isQueryParam', False)) else "H")
                try:
                    type_lbl.setForeground(Color(90, 90, 90))
                    type_lbl.setBorder(BorderFactory.createEmptyBorder(0, 6, 0, 6))
                except Exception:
                    pass
                self._extender._rulesRowPanels[title] = row
                self._extender._rulesCheckboxes[title] = cb
                self._extender._rulesTypeLabels[title] = type_lbl
                row.addMouseListener(RuleRowSelect(self._extender, title))
                lbl.addMouseListener(RuleRowSelect(self._extender, title))
                row.add(cb, BorderLayout.WEST)
                row.add(lbl, BorderLayout.CENTER)
                row.add(type_lbl, BorderLayout.EAST)
                
                try:
                    row.setBorder(BorderFactory.createEmptyBorder(2, 4, 2, 4))
                except Exception:
                    pass
                panel.add(row)
            panel.revalidate()
            panel.repaint()

            if getattr(self._extender, '_selectedRuleTitle', None) is None and first_title is not None:
                self._extender._selectedRuleTitle = first_title
                headers = [x for x in self._extender.savedHeaders if x['title'] == first_title]
                obj = headers[0] if headers else None
                try:
                    self._extender._suppressTextEvents = True
                    if obj is not None:
                        if 'param' not in obj:
                            obj['param'] = "paramName=paramValue"
                        if 'isQueryParam' not in obj:
                            obj['isQueryParam'] = False
                        self._extender.replaceQueryParam.setSelected(bool(obj.get('isQueryParam', False)))
                        self._extender.replaceString.setText(obj['param'] if obj.get('isQueryParam', False) else obj.get('headers', ""))
                finally:
                    self._extender._suppressTextEvents = False
                try:
                    self.updateReplaceQueryVisualCue()
                except Exception:
                    pass

            try:
                self.updateRuleHighlights()
            except Exception:
                pass
        except Exception:
            pass

    def updateRuleHighlights(self):
        try:
            selected = getattr(self._extender, '_selectedRuleTitle', None)
            hovered = getattr(self._extender, '_hoveredRuleTitle', None)
            panels = getattr(self._extender, '_rulesRowPanels', {})
            for t, pnl in panels.items():
                try:
                    if t == selected:
                        pnl.setBorder(BorderFactory.createCompoundBorder(
                            BorderFactory.createLineBorder(Color(0,120,215)),
                            BorderFactory.createEmptyBorder(2, 4, 2, 4)
                        ))
                        pnl.setOpaque(True)
                        pnl.setBackground(Color(240, 248, 255))
                    elif t == hovered:
                        pnl.setBorder(BorderFactory.createLineBorder(Color(220, 220, 220)))
                        pnl.setOpaque(False)
                    else:
                        pnl.setBorder(BorderFactory.createEmptyBorder(2, 4, 2, 4))
                        pnl.setOpaque(False)
                except Exception:
                    pass

            try:
                self.updateReplaceQueryVisualCue()
            except Exception:
                pass
        except Exception:
            pass

    def updateReplaceQueryVisualCue(self):
        """Slight visual cue on Replace Query Params to reflect current rule type and aid discovery."""
        try:
            is_query = self._extender.replaceQueryParam.isSelected()
            self._extender.replaceQueryParam.setToolTipText("This rule edits query parameters" if is_query else "This rule edits headers")
            try:
                self._extender.replaceQueryParam.setForeground(Color(10, 90, 160) if is_query else Color.BLACK)
            except Exception:
                pass
        except Exception:
            pass

class RuleEnableListener(ItemListener):
    def __init__(self, extender, title):
        self._extender = extender
        self._title = title

    def itemStateChanged(self, e):
        try:
            selected = (e.getStateChange() == 1)
            for obj in self._extender.savedHeaders:
                if obj.get('title') == self._title:
                    obj['enabled'] = bool(selected)
                    break

            self._extender._selectedRuleTitle = self._title
            headers = [x for x in self._extender.savedHeaders if x['title'] == self._title]
            obj = headers[0] if headers else None
            try:
                self._extender._suppressTextEvents = True
                if obj is not None:
                    if 'param' not in obj:
                        obj['param'] = "paramName=paramValue"
                    if 'isQueryParam' not in obj:
                        obj['isQueryParam'] = False
                    self._extender.replaceQueryParam.setSelected(bool(obj.get('isQueryParam', False)))
                    self._extender.replaceString.setText(obj['param'] if obj.get('isQueryParam', False) else obj.get('headers', ""))
            finally:
                self._extender._suppressTextEvents = False
            try:
                if hasattr(self._extender, '_cfg_tab') and self._extender._cfg_tab is not None:
                    self._extender._cfg_tab.updateReplaceQueryVisualCue()
            except Exception:
                pass
            try:
                if hasattr(self._extender, '_cfg_tab') and self._extender._cfg_tab is not None:
                    self._extender._cfg_tab.updateRuleHighlights()
            except Exception:
                pass
        except Exception:
            pass

class RuleRowSelect(MouseAdapter):
    def __init__(self, extender, title):
        self._extender = extender
        self._title = title

    def mousePressed(self, evt):
        try:
            self._extender._selectedRuleTitle = self._title
            headers = [x for x in self._extender.savedHeaders if x['title'] == self._title]
            obj = headers[0] if headers else None
            try:
                self._extender._suppressTextEvents = True
                if obj is not None:
                    if 'param' not in obj:
                        obj['param'] = "paramName=paramValue"
                    if 'isQueryParam' not in obj:
                        obj['isQueryParam'] = False
                    self._extender.replaceQueryParam.setSelected(bool(obj.get('isQueryParam', False)))
                    self._extender.replaceString.setText(obj['param'] if obj.get('isQueryParam', False) else obj.get('headers', ""))
            finally:
                self._extender._suppressTextEvents = False
            try:
                if hasattr(self._extender, '_cfg_tab') and self._extender._cfg_tab is not None:
                    self._extender._cfg_tab.updateReplaceQueryVisualCue()
            except Exception:
                pass

            try:
                if hasattr(self._extender, '_cfg_tab') and self._extender._cfg_tab is not None:
                    self._extender._cfg_tab.updateRuleHighlights()
            except Exception:
                pass
        except Exception:
            pass

    def mouseEntered(self, evt):
        try:
            self._extender._hoveredRuleTitle = self._title
            if hasattr(self._extender, '_cfg_tab') and self._extender._cfg_tab is not None:
                self._extender._cfg_tab.updateRuleHighlights()
        except Exception:
            pass

    def mouseExited(self, evt):
        try:
            if getattr(self._extender, '_hoveredRuleTitle', None) == self._title:
                self._extender._hoveredRuleTitle = None
            if hasattr(self._extender, '_cfg_tab') and self._extender._cfg_tab is not None:
                self._extender._cfg_tab.updateRuleHighlights()
        except Exception:
            pass

class ReplaceStringDocumentListener(DocumentListener):
    def __init__(self, extender):
        self._extender = extender

    def insertUpdate(self, e):
        self._update()

    def removeUpdate(self, e):
        self._update()

    def changedUpdate(self, e):
        self._update()

    def _update(self):
        try:
            if getattr(self._extender, '_suppressTextEvents', False):
                return
            selected = getattr(self._extender, '_selectedRuleTitle', None)
            if selected is None:
                return
            text = self._extender.replaceString.getText()
            for obj in self._extender.savedHeaders:
                if obj['title'] == selected:
                    if obj.get('isQueryParam', False):
                        obj['param'] = text
                    else:
                        obj['headers'] = text
                    break
        except Exception:
            pass

