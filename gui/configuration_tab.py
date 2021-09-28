#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from javax.swing import DefaultComboBoxModel
from java.awt.event import ActionListener
from javax.swing import SwingUtilities
from javax.swing import JToggleButton
from javax.swing import JScrollPane
from javax.swing import JTabbedPane
from javax.swing import JOptionPane
from javax.swing import JSplitPane
from javax.swing import JComboBox
from javax.swing import JTextArea
from javax.swing import JCheckBox
from javax.swing import JButton
from javax.swing import JPanel
from javax.swing import JLabel

from table import UpdateTableEDT

class ConfigurationTab():
    def __init__(self, extender):
        self._extender = extender

    def draw(self):
        """  init configuration tab
        """
        self.DEFUALT_REPLACE_TEXT = "Cookie: Insert=injected; cookie=or;\nHeader: here"
        self._extender.startButton = JToggleButton("Autorize is off",
                                    actionPerformed=self.startOrStop)
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

        self._extender.saveHeadersButton = JButton("Add",
                                        actionPerformed=self.saveHeaders)
        self._extender.saveHeadersButton.setBounds(315, 115, 80, 30)
        
        self._extender.removeHeadersButton = JButton("Remove",
                                        actionPerformed=self.removeHeaders)
        self._extender.removeHeadersButton.setBounds(400, 115, 80, 30)

        savedHeadersTitles = self.getSavedHeadersTitles()
        self._extender.savedHeadersTitlesCombo = JComboBox(savedHeadersTitles)
        self._extender.savedHeadersTitlesCombo.addActionListener(SavedHeaderChange(self._extender))
        self._extender.savedHeadersTitlesCombo.setBounds(10, 115, 300, 30)

        self._extender.replaceString = JTextArea(self.DEFUALT_REPLACE_TEXT, 5, 30)
        self._extender.replaceString.setWrapStyleWord(True)
        self._extender.replaceString.setLineWrap(True)
        scrollReplaceString = JScrollPane(self._extender.replaceString)
        scrollReplaceString.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollReplaceString.setBounds(10, 150, 470, 150)

        fromLastRequestLabel = JLabel("From last request:")
        fromLastRequestLabel.setBounds(10, 305, 250, 30)

        self._extender.fetchCookiesHeaderButton = JButton("Fetch Cookies header",
                                actionPerformed=self.fetchCookiesHeader)
        self._extender.fetchCookiesHeaderButton.setEnabled(False)
        self._extender.fetchCookiesHeaderButton.setBounds(10, 330, 220, 30)

        self._extender.fetchAuthorizationHeaderButton = JButton("Fetch Authorization header",
                                actionPerformed=self.fetchAuthorizationHeader)
        self._extender.fetchAuthorizationHeaderButton.setEnabled(False)
        self._extender.fetchAuthorizationHeaderButton.setBounds(260, 330, 220, 30)

        self._extender.filtersTabs = JTabbedPane()
        self._extender.filtersTabs = self._extender.filtersTabs
        self._extender.filtersTabs.addTab("Enforcement Detector", self._extender.EDPnl)
        self._extender.filtersTabs.addTab("Detector Unauthenticated", self._extender.EDPnlUnauth)
        self._extender.filtersTabs.addTab("Interception Filters", self._extender.filtersPnl)
        self._extender.filtersTabs.addTab("Match/Replace", self._extender.MRPnl)
        self._extender.filtersTabs.addTab("Table Filter", self._extender.filterPnl)
        self._extender.filtersTabs.addTab("Save/Restore", self._extender.exportPnl)

        self._extender.filtersTabs.setSelectedIndex(2)
        self._extender.filtersTabs.setBounds(0, 350, 2000, 700)

        self.config_pnl = JPanel()
        self.config_pnl.setBounds(0, 0, 1000, 1000)
        self.config_pnl.setLayout(None)
        self.config_pnl.add(self._extender.startButton)
        self.config_pnl.add(self._extender.clearButton)
        self.config_pnl.add(scrollReplaceString)
        self.config_pnl.add(fromLastRequestLabel)
        self.config_pnl.add(self._extender.saveHeadersButton)
        self.config_pnl.add(self._extender.removeHeadersButton)
        self.config_pnl.add(self._extender.savedHeadersTitlesCombo)
        self.config_pnl.add(self._extender.fetchCookiesHeaderButton)
        self.config_pnl.add(self._extender.fetchAuthorizationHeaderButton)
        self.config_pnl.add(self._extender.autoScroll)
        self.config_pnl.add(self._extender.interceptRequestsfromRepeater)
        self.config_pnl.add(self._extender.ignore304)
        self.config_pnl.add(self._extender.prevent304)
        self.config_pnl.add(self._extender.doUnauthorizedRequest)
        self.config_pnl.add(self._extender.replaceQueryParam)
        
        self._extender._cfg_splitpane = JSplitPane(JSplitPane.VERTICAL_SPLIT)
        self._extender._cfg_splitpane.setResizeWeight(0.5)
        self._extender._cfg_splitpane.setBounds(0, 0, 1000, 1000)
        self._extender._cfg_splitpane.setRightComponent(self._extender.filtersTabs)
        self._extender._cfg_splitpane.setLeftComponent(self.config_pnl)

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
    
    def replaceQueryHanlder(self, event):
        if self._extender.replaceQueryParam.isSelected():
            self._extender.replaceString.setText("paramName=paramValue")
        else:
            self._extender.replaceString.setText(self.DEFUALT_REPLACE_TEXT)

    def saveHeaders(self, event):
        savedHeadersTitle = JOptionPane.showInputDialog("Please provide saved headers title:")
        self._extender.savedHeaders.append({'title': savedHeadersTitle, 'headers': self._extender.replaceString.getText()})
        self._extender.savedHeadersTitlesCombo.setModel(DefaultComboBoxModel(self.getSavedHeadersTitles()))
        self._extender.savedHeadersTitlesCombo.getModel().setSelectedItem(savedHeadersTitle)
    
    def removeHeaders(self, event):
        model = self._extender.savedHeadersTitlesCombo.getModel()
        selectedItem = model.getSelectedItem()
        if selectedItem == "Temporary headers":
            return

        delObject = None
        for savedHeaderObj in self._extender.savedHeaders:
            if selectedItem == savedHeaderObj['title']:
                delObject = savedHeaderObj
        self._extender.savedHeaders.remove(delObject)
        model.removeElement(selectedItem)

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

class SavedHeaderChange(ActionListener):
    def __init__(self, extender):
        self._extender = extender

    def actionPerformed(self, e):
        selectedTitle = self._extender.savedHeadersTitlesCombo.getSelectedItem()
        headers = [x for x in self._extender.savedHeaders if x['title'] == selectedTitle]
        self._extender.replaceString.setText(headers[0]['headers'])

