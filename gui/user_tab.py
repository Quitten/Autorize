#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from javax.swing import JPanel
from javax.swing import JLabel
from javax.swing import JButton
from javax.swing import JTabbedPane
from javax.swing import JOptionPane
from javax.swing import JTextArea
from javax.swing import JScrollPane
from javax.swing import GroupLayout
from java.awt import BorderLayout
from java.awt import FlowLayout
from java.awt import Font
from java.awt.event import ActionListener

from gui.enforcement_detector import EnforcementDetectors
from gui.match_replace import MatchReplace

class UserHeaders():
    DEFUALT_REPLACE_TEXT = "Cookie: Insert=injected; cookie=or;\nHeader: here"

    def __init__(self, user_id, extender):
        self.user_id = user_id
        self._extender = extender

    def draw(self):
        self.headersPnl = JPanel()
        layout = GroupLayout(self.headersPnl)
        self.headersPnl.setLayout(layout)
        layout.setAutoCreateGaps(True)
        layout.setAutoCreateContainerGaps(True)

        self.replaceString = JTextArea(self.DEFUALT_REPLACE_TEXT, 5, 30)
        self.replaceString.setWrapStyleWord(True)
        self.replaceString.setLineWrap(True)

        self.scrollReplaceString = JScrollPane(self.replaceString)
        self.scrollReplaceString.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)

        self.fromLastRequestLabel = JLabel("From last request:")

        self.fetchCookiesHeaderButton = JButton("Fetch Cookies header",
                                actionPerformed=self.fetchCookiesHeader)
        self.fetchCookiesHeaderButton.setEnabled(False)

        self.fetchAuthorizationHeaderButton = JButton("Fetch Authorization header",
                                actionPerformed=self.fetchAuthorizationHeader)
        self.fetchAuthorizationHeaderButton.setEnabled(False)

        layout.setHorizontalGroup(
            layout.createParallelGroup()
                .addComponent(self.scrollReplaceString,
                    GroupLayout.DEFAULT_SIZE, GroupLayout.DEFAULT_SIZE, 2147483647)
                .addComponent(self.fromLastRequestLabel)
                .addGroup(layout.createSequentialGroup()
                    .addComponent(self.fetchCookiesHeaderButton)
                    .addComponent(self.fetchAuthorizationHeaderButton)
                )
        )

        layout.setVerticalGroup(
            layout.createSequentialGroup()
                .addComponent(self.scrollReplaceString,
                    GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE, GroupLayout.PREFERRED_SIZE)
                .addComponent(self.fromLastRequestLabel)
                .addGroup(layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                    .addComponent(self.fetchCookiesHeaderButton)
                    .addComponent(self.fetchAuthorizationHeaderButton)
                )
        )

    def fetchCookiesHeader(self, event):
        if self._extender.lastCookiesHeader:
            self.replaceString.setText(self._extender.lastCookiesHeader)

    def fetchAuthorizationHeader(self, event):
        if self._extender.lastAuthorizationHeader:
            self.replaceString.setText(self._extender.lastAuthorizationHeader)


class UserTab():
    def __init__(self, extender):
        self._extender = extender
        self.user_count = 0
        self.user_tabs = {}
        self.user_names = []

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
        unique_user_name = self.get_unique_name(user_name)

        self.user_names.append(unique_user_name)

        userPanel = JPanel(BorderLayout())
        
        headerPanel = JPanel(FlowLayout(FlowLayout.LEFT))
        headerLabel = JLabel(unique_user_name)
        headerLabel.setFont(Font("Tahoma", Font.BOLD, 12))
        headerPanel.add(headerLabel)
        
        userSubTabs = JTabbedPane()
        
        user_headers = UserHeaders(self.user_count, self._extender)
        user_headers.draw()

        if self._extender.lastCookiesHeader:
            user_headers.fetchCookiesHeaderButton.setEnabled(True)
        if self._extender.lastAuthorizationHeader:
            user_headers.fetchAuthorizationHeaderButton.setEnabled(True)

        user_ed = UserEnforcementDetector(self.user_count)
        user_ed.draw()
        
        user_mr = UserMatchReplace(self.user_count)
        user_mr.draw()
        
        userSubTabs.addTab("Headers", user_headers.headersPnl)
        userSubTabs.addTab("Enforcement Detector", user_ed.EDPnl)
        userSubTabs.addTab("Match/Replace", user_mr.MRPnl)
        
        userPanel.add(headerPanel, BorderLayout.NORTH)
        userPanel.add(userSubTabs, BorderLayout.CENTER)
        
        self.user_tabs[self.user_count] = {
            'user_id': self.user_count,
            'user_name': unique_user_name,
            'panel': userPanel,
            'subtabs': userSubTabs,
            'headers_instance': user_headers,
            'ed_instance': user_ed,
            'mr_instance': user_mr,
            'header_label': headerLabel
        }
        
        self.userTabs.addTab(unique_user_name, userPanel)
        
        self.userTabs.setSelectedIndex(self.userTabs.getTabCount() - 1)

        self.refreshTableStructure()

    def remove_user(self):
        if self.userTabs.getTabCount() <= 1:
            JOptionPane.showMessageDialog(None, "Cannot remove the last user!", "Warning", JOptionPane.WARNING_MESSAGE)
            return
        
        selected_index = self.userTabs.getSelectedIndex()

        if selected_index >= 0:
            selected_panel = self.userTabs.getComponentAt(selected_index)

            user_id_to_remove = None
            user_name_to_remove = None

            for user_id, user_data in self.user_tabs.items():
                if user_data['panel'] == selected_panel:
                    user_id_to_remove = user_id
                    user_name_to_remove = user_data['user_name']
                    break

            if user_id_to_remove and user_name_to_remove:
                if user_name_to_remove in self.user_names:
                    self.user_names.remove(user_name_to_remove)

                del self.user_tabs[user_id_to_remove]

                self.userTabs.removeTabAt(selected_index)

                self.refreshTableStructure()

    def reset_user(self):
        self.userTabs.removeAll()
        self.user_tabs.clear()
        del self.user_names[:]
        self.user_count = 0
        self.add_user()
        
    def duplicate_user(self):
        selected_index = self.userTabs.getSelectedIndex()

        if selected_index >= 0:
            selected_panel = self.userTabs.getComponentAt(selected_index)
            source_user_data = None
            
            for user_id, user_data in self.user_tabs.items():
                if user_data['panel'] == selected_panel:
                    source_user_data = user_data
                    break
            
            if source_user_data:
                self.add_user()
                new_user_id = self.user_count
                new_user_data = self.user_tabs[new_user_id]

                self.copy_headers_settings(source_user_data['headers_instance'], new_user_data['headers_instance'])
                self.copy_ed_settings(source_user_data['ed_instance'], new_user_data['ed_instance'])
                self.copy_mr_settings(source_user_data['mr_instance'], new_user_data['mr_instance'])
    
    def copy_ed_settings(self, source_ed, target_ed):
        target_ed.EDModel.clear()
        for i in range(source_ed.EDModel.getSize()):
            target_ed.EDModel.addElement(source_ed.EDModel.getElementAt(i))
        
        target_ed.EDType.setSelectedIndex(source_ed.EDType.getSelectedIndex())
        target_ed.EDText.setText(source_ed.EDText.getText())
        target_ed.AndOrType.setSelectedIndex(source_ed.AndOrType.getSelectedIndex())

    def copy_headers_settings(self, source_headers, target_headers):
        target_headers.replaceString.setText(source_headers.replaceString.getText())

    def copy_mr_settings(self, source_mr, target_mr):
        target_mr.MRModel.clear()
        for i in range(source_mr.MRModel.getSize()):
            target_mr.MRModel.addElement(source_mr.MRModel.getElementAt(i))
        
        target_mr.MRType.setSelectedIndex(source_mr.MRType.getSelectedIndex())
        target_mr.MText.setText(source_mr.MText.getText())
        target_mr.RText.setText(source_mr.RText.getText())
        
        target_mr.badProgrammerMRModel.clear()
        for key, value in source_mr.badProgrammerMRModel.items():
            if hasattr(value, 'copy'):
                target_mr.badProgrammerMRModel[key] = value.copy()
            elif isinstance(value, dict):
                target_mr.badProgrammerMRModel[key] = dict(value)
            else:
                target_mr.badProgrammerMRModel[key] = value
                            
    def rename_user(self):
        selected_index = self.userTabs.getSelectedIndex()

        if selected_index >= 0:
            current_name = self.userTabs.getTitleAt(selected_index)
            new_name = JOptionPane.showInputDialog(None, "Enter new name for user:", "Rename User", JOptionPane.QUESTION_MESSAGE, None, None, current_name)
            
            if new_name and new_name.strip():
                if current_name in self.user_names:
                    self.user_names.remove(current_name)

                unique_name = self.get_unique_name(new_name.strip())
                self.user_names.append(unique_name)

                self.userTabs.setTitleAt(selected_index, unique_name)

                selected_panel = self.userTabs.getComponentAt(selected_index)

                for user_id, user_data in self.user_tabs.items():
                    if user_data['panel'] == selected_panel:
                        user_data['header_label'].setText(unique_name)
                        user_data['user_name'] = unique_name
                        break

                self.refreshTableStructure()

    def get_unique_name(self, name):
        if name not in self.user_names:
            return name
        
        counter = 1
        while True:
            candidate_name = "{} Copy".format(name) if counter == 1 else "{} Copy {}".format(name, counter)
            
            if candidate_name not in self.user_names:
                return candidate_name
            
            counter += 1
            
            if counter > 100:
                return "{} Copy {}".format(name, counter)
    
    def refreshTableStructure(self):
        if hasattr(self._extender, 'tableModel'):
            self._extender.tableModel.fireTableStructureChanged()
        if hasattr(self._extender, 'logTable'):
            self._extender.logTable.updateColumnWidths()
            
class UserEnforcementDetector(EnforcementDetectors):

    def __init__(self, user_id):
        self.isolated_extender = type('IsolatedExtender', (object,), {})()
        self.user_id = user_id
        
        EnforcementDetectors.__init__(self, self.isolated_extender)

    def draw(self):
        EnforcementDetectors.draw(self)
        self.EDPnl = self.isolated_extender.EDPnl
        self.EDType = self.isolated_extender.EDType
        self.EDText = self.isolated_extender.EDText
        self.EDModel = self.isolated_extender.EDModel
        self.EDList = self.isolated_extender.EDList
        self.AndOrType = self.isolated_extender.AndOrType

class UserMatchReplace(MatchReplace):
    def __init__(self, user_id):
        self.isolated_extender = type('IsolatedExtender', (object,), {})()
        self.user_id = user_id
        
        MatchReplace.__init__(self, self.isolated_extender)

    def draw(self):
        MatchReplace.draw(self)

        self.MRPnl = self.isolated_extender.MRPnl
        self.MRType = self.isolated_extender.MRType
        self.MText = self.isolated_extender.MText
        self.RText = self.isolated_extender.RText
        self.MRModel = self.isolated_extender.MRModel
        self.MRList = self.isolated_extender.MRList
        self.badProgrammerMRModel = self.isolated_extender.badProgrammerMRModel

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