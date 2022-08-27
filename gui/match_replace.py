#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from javax.swing import JLabel
from javax.swing import JComboBox
from javax.swing import JTextArea
from javax.swing import JScrollPane
from javax.swing import DefaultListModel
from javax.swing import JList
from javax.swing import JPanel
from javax.swing import JButton

from java.awt import Color
from javax.swing.border import LineBorder

import re

class MatchReplace():
    def __init__(self, extender):
        self._extender = extender
    
    def draw(self):
        """ init the match/replace tab
        """
        #todo add an option to ignore large requests 
        padding = 5
        labelWidth = 140
        labelHeight = 30
        editHeight = 110
        editWidth = 300
        buttonWidth = 120 
        buttonHeight = 30
        column1X = 10
        column2X = column1X + labelWidth + padding
        column3X = column2X + editWidth + padding
        MRStrings = ["Headers (simple string):",
                     "Headers (regex):",
                     "Body (simple string):",
                     "Body (regex):"]
        row1Y = 10
        row2Y = row1Y + labelHeight + padding
        row3Y = row2Y + editHeight + padding
        row4Y = row3Y + editHeight + padding
        row5Y = row4Y + labelHeight + padding
        row6Y = row5Y + buttonHeight + padding

        MRTypeLabel = JLabel("Type:")
        MRTypeLabel.setBounds(column1X, row1Y, labelWidth, labelHeight)

        MContent = JLabel("Match:")
        MContent.setBounds(column1X, row2Y, labelWidth, labelHeight)

        RContent = JLabel("Replace:")
        RContent.setBounds(column1X, row3Y, labelWidth, labelHeight)

        MRLabelList = JLabel("Filter List:")
        MRLabelList.setBounds(column1X, row5Y, labelWidth, labelHeight)

        self._extender.MRType = JComboBox(MRStrings)
        self._extender.MRType.setBounds(column2X, row1Y, editWidth, labelHeight)
       
        self._extender.MText = JTextArea("", 5, 30)
        scrollMText = JScrollPane(self._extender.MText)
        scrollMText.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollMText.setBounds(column2X, row2Y, editWidth, editHeight)

        self._extender.RText = JTextArea("", 5, 30)
        scrollRText = JScrollPane(self._extender.RText)
        scrollRText.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollRText.setBounds(column2X, row3Y, editWidth, editHeight)

        # i couldn't figure out how to have a model that contained anythin other than a string
        # so i'll use 2 models, one with the data and one for the JList
        self._extender.badProgrammerMRModel = {}
        self._extender.MRModel = DefaultListModel()
        self._extender.MRList = JList(self._extender.MRModel)

        scrollMRList = JScrollPane(self._extender.MRList)
        scrollMRList.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollMRList.setBounds(column2X, row5Y, editWidth, editHeight)
        scrollMRList.setBorder(LineBorder(Color.BLACK)) 

        self._extender.MRAdd = JButton("Add filter", actionPerformed=self.addMRFilter) 
        self._extender.MRAdd.setBounds(column2X, row4Y, buttonWidth, buttonHeight)
        self._extender.MRDel = JButton("Remove filter", actionPerformed=self.delMRFilter) 
        self._extender.MRDel.setBounds(column3X, row5Y, buttonWidth, buttonHeight)
        self._extender.MRMod = JButton("Modify filter", actionPerformed=self.modMRFilter)
        self._extender.MRMod.setBounds(column3X, row5Y + buttonHeight + padding, buttonWidth, buttonHeight)

        self._extender.MRFeedback = JLabel("")
        self._extender.MRFeedback.setBounds(column1X, row6Y, column3X + buttonWidth, labelHeight)

        self._extender.MRPnl = JPanel()
        self._extender.MRPnl.setLayout(None)
        self._extender.MRPnl.setBounds(0, 0, 1000, 1000)
        self._extender.MRPnl.add(MRTypeLabel)
        self._extender.MRPnl.add(self._extender.MRType)
        self._extender.MRPnl.add(MContent)
        self._extender.MRPnl.add(scrollMText)
        self._extender.MRPnl.add(RContent)
        self._extender.MRPnl.add(scrollRText)
        self._extender.MRPnl.add(self._extender.MRAdd)
        self._extender.MRPnl.add(MRLabelList)
        self._extender.MRPnl.add(scrollMRList)
        self._extender.MRPnl.add(self._extender.MRDel)
        self._extender.MRPnl.add(self._extender.MRMod)
        self._extender.MRPnl.add(self._extender.MRFeedback)

    def addMRFilter(self, event):
        typeName = self._extender.MRType.getSelectedItem()
        match = self._extender.MText.getText()
        replace = self._extender.RText.getText()
        key = typeName + " " + match + "->" + replace
        if key in self._extender.badProgrammerMRModel:
            self._extender.MRFeedback.setText("Match/Replace already exists")
            return

        regexMatch = None
        try:
            if "(regex)" in typeName:
                regexMatch = re.compile(match)
        except re.error:
            self._extender.MRFeedback.setText("ERROR: Invalid regex")
            return
        self._extender.badProgrammerMRModel[key] = {"match": match, "regexMatch": regexMatch, "replace" : replace, "type": typeName}
        self._extender.MRModel.addElement(key)
        self._extender.MText.setText("")
        self._extender.RText.setText("")
        self._extender.MRFeedback.setText("")

    def delMRFilter(self, event):
        index = self._extender.MRList.getSelectedIndex()
        if not index == -1:
            key = self._extender.MRList.getSelectedValue()
            del self._extender.badProgrammerMRModel[key]
            self._extender.MRList.getModel().remove(index)
    
    def modMRFilter(self, event):
        index = self._extender.MRList.getSelectedIndex()
        if not index == -1:
            key = self._extender.MRList.getSelectedValue()
            self._extender.MRType.getModel().setSelectedItem(self._extender.badProgrammerMRModel[key]["type"])
            self._extender.MText.setText(self._extender.badProgrammerMRModel[key]["match"])
            self._extender.RText.setText(self._extender.badProgrammerMRModel[key]["replace"])
            self.delMRFilter(event)
