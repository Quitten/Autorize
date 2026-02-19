#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("..")

from javax.swing import JLabel
from javax.swing import JList
from javax.swing import JPanel
from javax.swing import JButton
from javax.swing import JTextArea
from javax.swing import JComboBox
from javax.swing import GroupLayout
from javax.swing import JScrollPane
from javax.swing import DefaultListModel
from javax.swing.border import LineBorder
from java.awt import Color

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

        EDStrings = [
            "Headers (simple string): (enforced message headers contain)",
            "Headers NOT (simple string): (enforced message headers NOT contain)",
            "Headers (regex): (enforced message headers contain)",
            "Headers NOT (regex): (enforced message headers NOT contain)",
            "Body (simple string): (enforced message body contains)",
            "Body NOT (simple string): (enforced message body NOT contains)",
            "Body (regex): (enforced message body contains)",
            "Body NOT (regex): (enforced message body NOT contains)",
            "Full response (simple string): (enforced message contains)",
            "Full response NOT (simple string): (enforced message NOT contains)",
            "Full response (regex): (enforced message contains)",
            "Full response NOT (regex): (enforced message NOT contains)",
            "Full response length: (of enforced response)",
            "Full response NOT length: (of enforced response)",
            "Status code equals: (numbers only)",
            "Status code NOT equals: (numbers only)"
        ]
        self._extender.EDType = JComboBox(EDStrings)
        self._extender.EDType.setBounds(80, 10, 430, 30)

        self._extender.EDText = JTextArea("", 5, 30)

        scrollEDText = JScrollPane(self._extender.EDText)
        scrollEDText.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollEDText.setBounds(80, 50, 300, 110)
        scrollEDText.setBorder(LineBorder(Color.BLACK))

        self._extender.EDModel = DefaultListModel()
        self._extender.EDList = JList(self._extender.EDModel)
        self._extender.EDList.setPrototypeCellValue("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
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
        layout = GroupLayout(self._extender.EDPnl)
        self._extender.EDPnl.setLayout(layout)
        layout.setAutoCreateGaps(True)
        layout.setAutoCreateContainerGaps(True)

        layout.setHorizontalGroup(
            layout.createSequentialGroup()
                .addGroup(
                    layout.createParallelGroup()
                        .addComponent(
                            EDLType,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                        )
                        .addComponent(
                            EDLContent,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                        )
                        .addComponent(
                            EDLabelList,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                        )
                    )
                .addGroup(
                    layout.createParallelGroup()
                        .addComponent(
                            self._extender.EDType,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                        )
                        .addComponent(
                            scrollEDText,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                        )
                        .addComponent(
                            scrollEDList,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                        )
                        .addComponent(
                            self._extender.EDAdd,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                        )
                        .addComponent(
                            self._extender.AndOrType,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                        )
                        .addComponent(
                            self._extender.EDDel,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                        )
                        .addComponent(
                            self._extender.EDMod,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                        )
                    )
            )
        
        layout.setVerticalGroup(
            layout.createSequentialGroup()
                .addGroup(layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                    .addComponent(
                        EDLType,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                    .addComponent(
                        self._extender.EDType,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                )
                .addGroup(layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                    .addComponent(
                        EDLContent,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                    .addGroup(layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                        .addComponent(
                            scrollEDText,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                        )
                        
                    )
                )
                .addComponent(
                    self._extender.EDAdd,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addGroup(layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                    .addComponent(
                        EDLabelList,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                    .addComponent(
                        self._extender.AndOrType,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                )
                .addComponent(
                    scrollEDList,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    self._extender.EDDel,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    self._extender.EDMod,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
            )


    def draw_unauthenticated(self):
        """ init enforcement detector tab
        """

        EDLType = JLabel("Type:")
        EDLType.setBounds(10, 10, 140, 30)

        EDLContent = JLabel("Content:")
        EDLContent.setBounds(10, 50, 140, 30)

        EDLabelList = JLabel("Filter List:")
        EDLabelList.setBounds(10, 165, 140, 30)

        EDStrings = [
            "Headers (simple string): (enforced message headers contain)",
            "Headers NOT (simple string): (enforced message headers NOT contain)",
            "Headers (regex): (enforced message headers contain)",
            "Headers NOT (regex): (enforced message headers NOT contain)",
            "Body (simple string): (enforced message body contains)",
            "Body NOT (simple string): (enforced message body NOT contains)",
            "Body (regex): (enforced message body contains)",
            "Body NOT (regex): (enforced message body NOT contains)",
            "Full response (simple string): (enforced message contains)",
            "Full response NOT (simple string): (enforced message NOT contains)",
            "Full response (regex): (enforced message contains)",
            "Full response NOT (regex): (enforced message NOT contains)",
            "Full response length: (of enforced response)",
            "Full response NOT length: (of enforced response)",
            "Status code equals: (numbers only)",
            "Status code NOT equals: (numbers only)"
        ]
        self._extender.EDTypeUnauth = JComboBox(EDStrings)
        self._extender.EDTypeUnauth.setBounds(80, 10, 430, 30)

        self._extender.EDTextUnauth = JTextArea("", 5, 30)

        scrollEDTextUnauth = JScrollPane(self._extender.EDTextUnauth)
        scrollEDTextUnauth.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollEDTextUnauth.setBounds(80, 50, 300, 110)
        scrollEDTextUnauth.setBorder(LineBorder(Color.BLACK))

        self._extender.EDModelUnauth = DefaultListModel()
        self._extender.EDListUnauth = JList(self._extender.EDModelUnauth)
        self._extender.EDListUnauth.setPrototypeCellValue("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
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
        layout = GroupLayout(self._extender.EDPnlUnauth)
        self._extender.EDPnlUnauth.setLayout(layout)
        layout.setAutoCreateGaps(True)
        layout.setAutoCreateContainerGaps(True)

        layout.setHorizontalGroup(
            layout.createSequentialGroup()
                .addGroup(
                    layout.createParallelGroup()
                        .addComponent(
                            EDLType,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                        )
                        .addComponent(
                            EDLContent,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                        )
                        .addComponent(
                            EDLabelList,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                        )
                    )
                .addGroup(
                    layout.createParallelGroup()
                        .addComponent(
                            self._extender.EDTypeUnauth,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                        )
                        .addComponent(
                            scrollEDTextUnauth,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                        )
                        .addComponent(
                            scrollEDListUnauth,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                        )
                        .addComponent(
                            self._extender.EDAddUnauth,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                        )
                        .addComponent(
                            self._extender.AndOrTypeUnauth,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                        )
                        .addComponent(
                            self._extender.EDDelUnauth,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                        )
                        .addComponent(
                            self._extender.EDModUnauth,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                            GroupLayout.PREFERRED_SIZE,
                        )
                    )
            )
        
        

        layout.setVerticalGroup(
            layout.createSequentialGroup()
                .addGroup(layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                    .addComponent(
                        EDLType,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                    .addComponent(
                        self._extender.EDTypeUnauth,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                )
                .addGroup(layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                    .addComponent(
                        EDLContent,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                    .addComponent(
                        scrollEDTextUnauth,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                )
                .addGroup(layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                    .addComponent(
                        self._extender.EDAddUnauth,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                )
                .addGroup(layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                    .addComponent(
                        EDLabelList,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                    .addComponent(
                        self._extender.AndOrTypeUnauth,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                )
                .addComponent(
                    scrollEDListUnauth,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    self._extender.EDDelUnauth,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    self._extender.EDModUnauth,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
            )

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
