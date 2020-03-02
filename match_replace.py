
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

def init_match_replace(self):
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
        MRStrings = ["Headers (simple string):" ,
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

        self.MRType = JComboBox(MRStrings)
        self.MRType.setBounds(column2X, row1Y, editWidth, labelHeight)
       
        self.MText = JTextArea("", 5, 30)
        scrollMText = JScrollPane(self.MText)
        scrollMText.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollMText.setBounds(column2X, row2Y, editWidth, editHeight)

        self.RText = JTextArea("", 5, 30)
        scrollRText = JScrollPane(self.RText)
        scrollRText.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollRText.setBounds(column2X, row3Y, editWidth, editHeight)

        # i couldn't figure out how to have a model that contained anythin other than a string
        # so i'll use 2 models, one with the data and one for the JList
        self.badProgrammerMRModel = {}
        self.MRModel = DefaultListModel()
        self.MRList = JList(self.MRModel)

        scrollMRList = JScrollPane(self.MRList)
        scrollMRList.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollMRList.setBounds(column2X, row5Y, editWidth, editHeight)
        scrollMRList.setBorder(LineBorder(Color.BLACK)) 

        self.MRAdd = JButton("Add filter", actionPerformed=addMRFilter) 
        self.MRAdd.setBounds(column2X, row4Y, buttonWidth, buttonHeight)
        self.MRDel = JButton("Remove filter", actionPerformed=delMRFilter) 
        self.MRDel.setBounds(column3X, row5Y, buttonWidth, buttonHeight)
        self.MRMod = JButton("Modify filter", actionPerformed=modMRFilter)
        self.MRMod.setBounds(column3X, row5Y + buttonHeight + padding, buttonWidth, buttonHeight)

        self.MRFeedback = JLabel("")
        self.MRFeedback.setBounds(column1X, row6Y, column3X + buttonWidth, labelHeight)

        self.MRPnl = JPanel()
        self.MRPnl.setLayout(None)
        self.MRPnl.setBounds(0, 0, 1000, 1000)
        self.MRPnl.add(MRTypeLabel)
        self.MRPnl.add(self.MRType)
        self.MRPnl.add(MContent)
        self.MRPnl.add(scrollMText)
        self.MRPnl.add(RContent)
        self.MRPnl.add(scrollRText)
        self.MRPnl.add(self.MRAdd)
        self.MRPnl.add(MRLabelList)
        self.MRPnl.add(scrollMRList)
        self.MRPnl.add(self.MRDel)
        self.MRPnl.add(self.MRMod)
        self.MRPnl.add(self.MRFeedback)

def addMRFilter(self, event):
        typeName = self.MRType.getSelectedItem()
        match = self.MText.getText()
        replace = self.RText.getText()
        key = typeName + " " + match + "->" + replace
        if key in self.badProgrammerMRModel:
            self.MRFeedback.setText("Match/Replace already exists")
            return

        regexMatch = None
        try:
            if "(regex)" in typeName :
                regexMatch = re.compile(match)
        except re.error:
            self.MRFeedback.setText("ERROR: Invalid regex")
            return
        self.badProgrammerMRModel[key] = {"match": match, "regexMatch": regexMatch, "replace" : replace, "type": typeName}
        self.MRModel.addElement(key)
        self.MText.setText("")
        self.RText.setText("")
        self.MRFeedback.setText("")

def delMRFilter(self, event):
        index = self.MRList.getSelectedIndex()
        if not index == -1:
            key = self.MRList.getSelectedValue()
            del self.badProgrammerMRModel[key]
            self.MRList.getModel().remove(index)
    
def modMRFilter(self, event):
        index = self.MRList.getSelectedIndex()
        if not index == -1:
            key = self.MRList.getSelectedValue()
            self.MRType.getModel().setSelectedItem(self.badProgrammerMRModel[key]["type"])
            self.MText.setText(self.badProgrammerMRModel[key]["match"])
            self.RText.setText(self.badProgrammerMRModel[key]["replace"])
            self.delMRFilter(event)
