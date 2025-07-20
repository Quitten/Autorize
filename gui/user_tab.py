#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from javax.swing import (JPanel, JLabel, JButton, JTabbedPane, JOptionPane)
from java.awt import BorderLayout, FlowLayout, Font
from java.awt.event import ActionListener

from gui.enforcement_detector import EnforcementDetectors
from gui.match_replace import MatchReplace

class UserTab():
    def __init__(self, extender):
        self._extender = extender
        self.user_count = 0
        self.user_tabs = {}
    
    def draw(self):
        self._extender.userPanel = JPanel(BorderLayout())
        
        buttonPanel = JPanel(FlowLayout(FlowLayout.LEFT))
        
        self.addUserBtn = JButton("Add User")
        self.addUserBtn.addActionListener(AddUserAction(self))
        buttonPanel.add(self.addUserBtn)
        
        self.removeUserBtn = JButton("Remove User")
        self.removeUserBtn.addActionListener(RemoveUserAction(self))
        buttonPanel.add(self.removeUserBtn)
        
        self.duplicateUserBtn = JButton("Duplicate User")
        self.duplicateUserBtn.addActionListener(DuplicateUserAction(self))
        buttonPanel.add(self.duplicateUserBtn)
        
        self.renameUserBtn = JButton("Rename User")
        self.renameUserBtn.addActionListener(RenameUserAction(self))
        buttonPanel.add(self.renameUserBtn)
        
        self.userTabs = JTabbedPane()
        
        self.add_user()
        
        self._extender.userPanel.add(buttonPanel, BorderLayout.NORTH)
        self._extender.userPanel.add(self.userTabs, BorderLayout.CENTER)
    
    def add_user(self):
        self.user_count += 1
        user_name = "User {}".format(self.user_count)
        
        userPanel = JPanel(BorderLayout())
        
        headerPanel = JPanel(FlowLayout(FlowLayout.LEFT))
        headerLabel = JLabel(user_name)
        headerLabel.setFont(Font("Tahoma", Font.BOLD, 12))
        headerPanel.add(headerLabel)
        
        userSubTabs = JTabbedPane()
        
        user_ed = UserEnforcementDetector(self._extender, self.user_count)
        user_ed.draw()
        user_ed.draw_unauthenticated()
        
        user_mr = UserMatchReplace(self._extender, self.user_count)
        user_mr.draw()
        
        userSubTabs.addTab("Enforcement Detector", user_ed.EDPnl)
        
        userSubTabs.addTab("Unauthentication Detector", user_ed.EDPnlUnauth)
        
        userSubTabs.addTab("Match/Replace", user_mr.MRPnl)
        
        userPanel.add(headerPanel, BorderLayout.NORTH)
        userPanel.add(userSubTabs, BorderLayout.CENTER)
        
        self.user_tabs[self.user_count] = {
            'panel': userPanel,
            'subtabs': userSubTabs,
            'ed_instance': user_ed,
            'mr_instance': user_mr,
            'header_label': headerLabel
        }
        
        self.userTabs.addTab(user_name, userPanel)
        
        self.userTabs.setSelectedIndex(self.userTabs.getTabCount() - 1)
    
    def remove_user(self):
        if self.userTabs.getTabCount() <= 1:
            JOptionPane.showMessageDialog(None, "Cannot remove the last user!", "Warning", JOptionPane.WARNING_MESSAGE)
            return
        
        selected_index = self.userTabs.getSelectedIndex()
        if selected_index >= 0:
            self.userTabs.removeTabAt(selected_index)
    
    def duplicate_user(self):
        selected_index = self.userTabs.getSelectedIndex()
        if selected_index >= 0:
            self.add_user()
    
    def rename_user(self):
        selected_index = self.userTabs.getSelectedIndex()
        if selected_index >= 0:
            current_name = self.userTabs.getTitleAt(selected_index)
            new_name = JOptionPane.showInputDialog(None, "Enter new name for user:", "Rename User", JOptionPane.QUESTION_MESSAGE, None, None, current_name)
            
            if new_name and new_name.strip():
                self.userTabs.setTitleAt(selected_index, new_name.strip())
                for user_id, user_data in self.user_tabs.items():
                    if user_data['panel'] == self.userTabs.getComponentAt(selected_index):
                        user_data['header_label'].setText(new_name.strip())
                        break

class UserEnforcementDetector(EnforcementDetectors):
    def __init__(self, extender, user_id):
        EnforcementDetectors.__init__(self, extender)
        self.user_id = user_id
        self.prefix = "User{}_".format(user_id)
    
    def draw(self):
        EnforcementDetectors.draw(self)
        
        self.EDPnl = self._extender.EDPnl
        setattr(self._extender, self.prefix + "EDPnl", self._extender.EDPnl)
        setattr(self._extender, self.prefix + "EDType", self._extender.EDType)
        setattr(self._extender, self.prefix + "EDText", self._extender.EDText)
        setattr(self._extender, self.prefix + "EDModel", self._extender.EDModel)
        setattr(self._extender, self.prefix + "EDList", self._extender.EDList)
        setattr(self._extender, self.prefix + "AndOrType", self._extender.AndOrType)
    
    def draw_unauthenticated(self):
        EnforcementDetectors.draw_unauthenticated(self)
        
        self.EDPnlUnauth = self._extender.EDPnlUnauth
        setattr(self._extender, self.prefix + "EDPnlUnauth", self._extender.EDPnlUnauth)
        setattr(self._extender, self.prefix + "EDTypeUnauth", self._extender.EDTypeUnauth)
        setattr(self._extender, self.prefix + "EDTextUnauth", self._extender.EDTextUnauth)
        setattr(self._extender, self.prefix + "EDModelUnauth", self._extender.EDModelUnauth)
        setattr(self._extender, self.prefix + "EDListUnauth", self._extender.EDListUnauth)
        setattr(self._extender, self.prefix + "AndOrTypeUnauth", self._extender.AndOrTypeUnauth)

class UserMatchReplace(MatchReplace):
    def __init__(self, extender, user_id):
        MatchReplace.__init__(self, extender)
        self.user_id = user_id
        self.prefix = "User{}_".format(user_id)
    
    def draw(self):
        MatchReplace.draw(self)
        
        self.MRPnl = self._extender.MRPnl
        setattr(self._extender, self.prefix + "MRPnl", self._extender.MRPnl)
        setattr(self._extender, self.prefix + "MRType", self._extender.MRType)
        setattr(self._extender, self.prefix + "MText", self._extender.MText)
        setattr(self._extender, self.prefix + "RText", self._extender.RText)
        setattr(self._extender, self.prefix + "MRModel", self._extender.MRModel)
        setattr(self._extender, self.prefix + "MRList", self._extender.MRList)
        setattr(self._extender, self.prefix + "badProgrammerMRModel", self._extender.badProgrammerMRModel)

class AddUserAction(ActionListener):
    def __init__(self, user_tab):
        self.user_tab = user_tab
    
    def actionPerformed(self, event):
        self.user_tab.add_user()

class RemoveUserAction(ActionListener):
    def __init__(self, user_tab):
        self.user_tab = user_tab
    
    def actionPerformed(self, event):
        self.user_tab.remove_user()

class DuplicateUserAction(ActionListener):
    def __init__(self, user_tab):
        self.user_tab = user_tab
    
    def actionPerformed(self, event):
        self.user_tab.duplicate_user()

class RenameUserAction(ActionListener):
    def __init__(self, user_tab):
        self.user_tab = user_tab
    
    def actionPerformed(self, event):
        self.user_tab.rename_user()