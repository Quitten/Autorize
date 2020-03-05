#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sys
sys.path.append("..")

from java.awt import Color
from javax.swing import JLabel
from javax.swing import JList
from javax.swing import JPanel
from javax.swing import JButton
from javax.swing import JTextArea
from javax.swing import JComboBox
from javax.swing import JScrollPane
from javax.swing import DefaultListModel
from javax.swing.border import LineBorder

from helpers.filters import addFilterHelper, delFilterHelper, modFilterHelper

class EnforcementDetectors():
    def __init__(self, extender):
        self._extender = extender

    def draw(self):
        """
        init enforcement detector tab
        """

        EDLType = JLabel("Type:")
        EDLType.setBounds(10, 10, 140, 30)

        EDLContent = JLabel("Content:")
        EDLContent.setBounds(10, 50, 140, 30)

        EDLabelList = JLabel("Filter List:")
        EDLabelList.setBounds(10, 165, 140, 30)

        EDStrings = ["Headers (simple string): (enforced message headers contains)",
                     "Headers (regex): (enforced message headers contains)",
                     "Body (simple string): (enforced message body contains)",
                     "Body (regex): (enforced message body contains)",
                     "Full response (simple string): (enforced message contains)",
                     "Full response (regex): (enforced message contains)",
                     "Full response length: (of enforced response)",
                     "Status code equals: (numbers only)"]
        self._extender.EDType = JComboBox(EDStrings)
        self._extender.EDType.setBounds(80, 10, 430, 30)
       
        self._extender.EDText = JTextArea("", 5, 30)

        scrollEDText = JScrollPane(self._extender.EDText)
        scrollEDText.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollEDText.setBounds(80, 50, 300, 110)  

        self._extender.EDModel = DefaultListModel()
        self._extender.EDList = JList(self._extender.EDModel)

        scrollEDList = JScrollPane(self._extender.EDList)
        scrollEDList.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollEDList.setBounds(80, 175, 300, 110)
        scrollEDList.setBorder(LineBorder(Color.BLACK)) 

        self._extender.EDAdd = JButton("Add filter", actionPerformed=self.addEDFilter)
        self._extender.EDAdd.setBounds(390, 85, 120, 30)
        self._extender.EDDel = JButton("Remove filter", actionPerformed=self.delEDFilter)
        self._extender.EDDel.setBounds(390, 210, 120, 30)
        self._extender.EDMod = JButton("Modify filter", actionPerformed=self.modEDFilter)
        self._extender.EDMod.setBounds(390, 250, 120, 30)

        AndOrStrings = ["And", "Or"]
        self._extender.AndOrType = JComboBox(AndOrStrings)
        self._extender.AndOrType.setBounds(390, 170, 120, 30)       

        self._extender.EDPnl = JPanel()
        self._extender.EDPnl.setLayout(None)
        self._extender.EDPnl.setBounds(0, 0, 1000, 1000)
        self._extender.EDPnl.add(EDLType)
        self._extender.EDPnl.add(self._extender.EDType)
        self._extender.EDPnl.add(EDLContent)
        self._extender.EDPnl.add(scrollEDText)
        self._extender.EDPnl.add(self._extender.EDAdd)
        self._extender.EDPnl.add(self._extender.AndOrType)
        self._extender.EDPnl.add(self._extender.EDDel)
        self._extender.EDPnl.add(self._extender.EDMod)
        self._extender.EDPnl.add(EDLabelList)
        self._extender.EDPnl.add(scrollEDList)


    def draw_unauthenticated(self):
        """ init enforcement detector tab
        """

        EDLType = JLabel("Type:")
        EDLType.setBounds(10, 10, 140, 30)

        EDLContent = JLabel("Content:")
        EDLContent.setBounds(10, 50, 140, 30)

        EDLabelList = JLabel("Filter List:")
        EDLabelList.setBounds(10, 165, 140, 30)

        EDStrings = ["Headers (simple string): (enforced message headers contains)",
                     "Headers (regex): (enforced message headers contains)",
                     "Body (simple string): (enforced message body contains)",
                     "Body (regex): (enforced message body contains)",
                     "Full response (simple string): (enforced message contains)",
                     "Full response (regex): (enforced message contains)",
                     "Full response length: (of enforced response)",
                     "Status code equals: (numbers only)"]
        self._extender.EDTypeUnauth = JComboBox(EDStrings)
        self._extender.EDTypeUnauth.setBounds(80, 10, 430, 30)
       
        self._extender.EDTextUnauth = JTextArea("", 5, 30)

        scrollEDTextUnauth = JScrollPane(self._extender.EDTextUnauth)
        scrollEDTextUnauth.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollEDTextUnauth.setBounds(80, 50, 300, 110)     

        self._extender.EDModelUnauth = DefaultListModel()
        self._extender.EDListUnauth = JList(self._extender.EDModelUnauth)

        scrollEDListUnauth = JScrollPane(self._extender.EDListUnauth)
        scrollEDListUnauth.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollEDListUnauth.setBounds(80, 175, 300, 110)
        scrollEDListUnauth.setBorder(LineBorder(Color.BLACK))    

        self._extender.EDAddUnauth = JButton("Add filter",
                                   actionPerformed=self.addEDFilterUnauth)
        self._extender.EDAddUnauth.setBounds(390, 85, 120, 30)
        self._extender.EDDelUnauth = JButton("Remove filter",
                                   actionPerformed=self.delEDFilterUnauth)
        self._extender.EDDelUnauth.setBounds(390, 210, 120, 30)
        self._extender.EDModUnauth = JButton("Modify filter",
                                   actionPerformed=self.modEDFilterUnauth)
        self._extender.EDModUnauth.setBounds(390, 250, 120, 30)

        AndOrStrings = ["And", "Or"]
        self._extender.AndOrTypeUnauth = JComboBox(AndOrStrings)
        self._extender.AndOrTypeUnauth.setBounds(390, 170, 120, 30)        

        self._extender.EDPnlUnauth = JPanel()
        self._extender.EDPnlUnauth.setLayout(None)
        self._extender.EDPnlUnauth.setBounds(0, 0, 1000, 1000)
        self._extender.EDPnlUnauth.add(EDLType)
        self._extender.EDPnlUnauth.add(self._extender.EDTypeUnauth)
        self._extender.EDPnlUnauth.add(EDLContent)
        self._extender.EDPnlUnauth.add(scrollEDTextUnauth)
        self._extender.EDPnlUnauth.add(self._extender.EDAddUnauth)
        self._extender.EDPnlUnauth.add(self._extender.AndOrTypeUnauth)
        self._extender.EDPnlUnauth.add(self._extender.EDDelUnauth)
        self._extender.EDPnlUnauth.add(self._extender.EDModUnauth)
        self._extender.EDPnlUnauth.add(EDLabelList)
        self._extender.EDPnlUnauth.add(scrollEDListUnauth)

    def addEDFilter(self, event):
        addFilterHelper(self._extender.EDType, self._extender.EDModel, self._extender.EDText)

    def delEDFilter(self, event):
        delFilterHelper(self._extender.EDList)

    def modEDFilter(self, event):
        modFilterHelper(self._extender.EDList, self._extender.EDType, self._extender.EDText)

    def addEDFilterUnauth(self, event):
        addFilterHelper(self._extender.EDTypeUnauth, self._extender.EDModelUnauth, self._extender.EDTextUnauth)

    def delEDFilterUnauth(self, event):
        delFilterHelper(self._extender.EDListUnauth)

    def modEDFilterUnauth(self, event):
        modFilterHelper(self._extender.EDListUnauth, self._extender.EDTypeUnauth, self._extender.EDTextUnauth)
