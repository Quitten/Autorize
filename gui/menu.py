#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from burp import IContextMenuFactory

from java.util import LinkedList
from javax.swing import JMenuItem
from java.awt.event import ActionListener
from javax.swing import KeyStroke
from java.awt.event import KeyEvent
from java.awt.event import InputEvent
from java.awt import Toolkit
from java.awt import KeyboardFocusManager
from java.awt import KeyEventDispatcher
from java.awt import KeyEventPostProcessor
from java.lang import System as JavaSystem

from authorization.authorization import send_request_to_autorize
from helpers.http import get_cookie_header_from_message, get_authorization_header_from_message

from thread import start_new_thread

class MenuImpl(IContextMenuFactory):
    def __init__(self, extender):
        self._extender = extender
        self._hotkey_dispatcher = None
        self._hotkey_post_processor = None
        self._hotkey_handler = None

    def register_global_hotkey(self):
        if self._hotkey_dispatcher is not None or self._hotkey_post_processor is not None:
            return
        # Use one shared handler for both hooks to avoid duplicate processing paths.
        self._hotkey_handler = GlobalSendToAutorizeDispatcher(self._extender)
        self._hotkey_dispatcher = self._hotkey_handler
        self._hotkey_post_processor = self._hotkey_handler
        manager = KeyboardFocusManager.getCurrentKeyboardFocusManager()
        manager.addKeyEventDispatcher(self._hotkey_dispatcher)
        manager.addKeyEventPostProcessor(self._hotkey_post_processor)

    def unregister_global_hotkey(self):
        if self._hotkey_dispatcher is None and self._hotkey_post_processor is None:
            return
        manager = KeyboardFocusManager.getCurrentKeyboardFocusManager()
        if self._hotkey_dispatcher is not None:
            manager.removeKeyEventDispatcher(self._hotkey_dispatcher)
        if self._hotkey_post_processor is not None:
            manager.removeKeyEventPostProcessor(self._hotkey_post_processor)
        self._hotkey_dispatcher = None
        self._hotkey_post_processor = None
        self._hotkey_handler = None

    def createMenuItems(self, invocation):
        responses = invocation.getSelectedMessages()
        if responses and len(responses) > 0:
            ret = LinkedList()
            requestMenuItem = JMenuItem("Send request to Autorize")
            cookieMenuItem = JMenuItem("Send Cookie header to Autorize")
            authMenuItem = JMenuItem("Send Authorization header to Autorize")
            try:
                menu_shortcut = Toolkit.getDefaultToolkit().getMenuShortcutKeyMaskEx()
                send_to_autorize_shortcut = KeyStroke.getKeyStroke(
                    KeyEvent.VK_A, menu_shortcut | InputEvent.SHIFT_DOWN_MASK
                )
            except:
                send_to_autorize_shortcut = KeyStroke.getKeyStroke(
                    KeyEvent.VK_A, InputEvent.CTRL_DOWN_MASK | InputEvent.SHIFT_DOWN_MASK
                )
            requestMenuItem.setAccelerator(send_to_autorize_shortcut)

            requestMenuItem.addActionListener(HandleMenuItems(self._extender, responses, "request"))
            cookieMenuItem.addActionListener(HandleMenuItems(self._extender, responses[0], "cookie"))
            authMenuItem.addActionListener(HandleMenuItems(self._extender, responses[0], "authorization"))
            ret.add(requestMenuItem)
            ret.add(cookieMenuItem)
            ret.add(authMenuItem)
            return ret
        return None

class HandleMenuItems(ActionListener):
    def __init__(self, extender, messageInfo, menuName):
        self._extender = extender
        self._menuName = menuName
        self._messageInfo = messageInfo

    def actionPerformed(self, e):
        if self._menuName == "request":
            if hasattr(self._messageInfo, "getRequest"):
                start_new_thread(send_request_to_autorize, (self._extender, self._messageInfo))
            else:
                for msg in self._messageInfo:
                    start_new_thread(send_request_to_autorize, (self._extender, msg))

        if self._menuName == "cookie":
            cookie = get_cookie_header_from_message(self._extender, self._messageInfo)
            if cookie:
                active_user = self._get_active_user_data()
                if active_user:
                    active_user['headers_instance'].replaceString.setText(cookie)
        
        if self._menuName == "authorization":
            auth = get_authorization_header_from_message(self._extender, self._messageInfo)
            if auth:
                active_user = self._get_active_user_data()
                if active_user:
                    active_user['headers_instance'].replaceString.setText(auth)

    def _get_active_user_data(self):
        if hasattr(self._extender, 'userTab') and self._extender.userTab:
            selected_index = self._extender.userTab.userTabs.getSelectedIndex()
            if selected_index >= 0:
                selected_panel = self._extender.userTab.userTabs.getComponentAt(selected_index)
                for user_id, user_data in self._extender.userTab.user_tabs.items():
                    if user_data['panel'] == selected_panel:
                        return user_data
        return None


class GlobalSendToAutorizeDispatcher(KeyEventDispatcher, KeyEventPostProcessor):
    def __init__(self, extender):
        self._extender = extender
        self._last_hotkey_fingerprint = None

    def dispatchKeyEvent(self, event):
        return self._handle_hotkey(event)

    def postProcessKeyEvent(self, event):
        return self._handle_hotkey(event)

    def _handle_hotkey(self, event):
        try:
            if event.getID() != KeyEvent.KEY_PRESSED:
                return False
            key_code = event.getKeyCode()
            key_char = str(event.getKeyChar()).lower() if event.getKeyChar() else ""
            if key_code != KeyEvent.VK_A and key_char != "a":
                return False

            modifiers = event.getModifiersEx()
            has_shift = (modifiers & InputEvent.SHIFT_DOWN_MASK) != 0
            has_ctrl_or_cmd = ((modifiers & InputEvent.CTRL_DOWN_MASK) != 0) or ((modifiers & InputEvent.META_DOWN_MASK) != 0)
            if not has_shift or not has_ctrl_or_cmd:
                return False

            # Same physical key event can pass through both dispatcher and post-processor.
            # Deduplicate by event fingerprint.
            fingerprint = "{}:{}:{}".format(event.getWhen(), key_code, modifiers)
            if fingerprint == self._last_hotkey_fingerprint:
                return False
            self._last_hotkey_fingerprint = fingerprint

            messages = self._extract_selected_messages(event.getComponent())
            if not messages:
                focus_owner = KeyboardFocusManager.getCurrentKeyboardFocusManager().getFocusOwner()
                messages = self._extract_selected_messages(focus_owner)
            if not messages:
                return False

            for message in messages:
                start_new_thread(send_request_to_autorize, (self._extender, message))
            event.consume()
            return True
        except:
            return False

    def _extract_selected_messages(self, component):
        table = self._find_table(component)
        if table is None:
            return []

        selected_rows = table.getSelectedRows() if hasattr(table, "getSelectedRows") else []
        if selected_rows is None or len(selected_rows) == 0:
            return []

        model = table.getModel() if hasattr(table, "getModel") else None
        if model is None or not hasattr(model, "getColumnCount"):
            return []

        messages = []
        seen = set()
        for view_row in selected_rows:
            try:
                model_row = table.convertRowIndexToModel(view_row) if hasattr(table, "convertRowIndexToModel") else view_row
            except:
                model_row = view_row

            cols = model.getColumnCount()
            for col in range(cols):
                value = None
                try:
                    if hasattr(table, "getValueAt"):
                        value = table.getValueAt(view_row, col)
                except:
                    value = None
                if value is None:
                    try:
                        value = model.getValueAt(model_row, col)
                    except:
                        continue
                value = self._unwrap_http_message(value)
                if self._is_http_request_response(value):
                    value_id = JavaSystem.identityHashCode(value)
                    if value_id not in seen:
                        seen.add(value_id)
                        messages.append(value)

        # Try alternative extraction paths used by Burp internal table models.
        alt_messages = self._extract_messages_via_known_methods(table, model, selected_rows)
        for value in alt_messages:
            value_id = JavaSystem.identityHashCode(value)
            if value_id not in seen:
                seen.add(value_id)
                messages.append(value)

        # Burp history fallback: map selected table rows to callbacks.getProxyHistory() entries.
        proxy_history_messages = self._extract_messages_from_proxy_history(table, model, selected_rows)
        for value in proxy_history_messages:
            value_id = JavaSystem.identityHashCode(value)
            if value_id not in seen:
                seen.add(value_id)
                messages.append(value)

        return messages

    def _extract_messages_from_proxy_history(self, table, model, selected_rows):
        if not hasattr(self._extender, "_callbacks"):
            return []
        if not hasattr(self._extender._callbacks, "getProxyHistory"):
            return []
        try:
            history = self._extender._callbacks.getProxyHistory()
        except:
            return []
        if history is None or len(history) == 0:
            return []

        extracted = []
        for view_row in selected_rows:
            try:
                model_row = table.convertRowIndexToModel(view_row) if hasattr(table, "convertRowIndexToModel") else view_row
            except:
                model_row = view_row

            row_method, row_url, row_path, row_status, row_len, row_seq, sampled_cols = self._infer_method_url_from_row(model, model_row)
            if row_method is None or row_url is None:
                continue

            matches = []
            relaxed_matches = []
            seq_matches = []
            indexed_relaxed_matches = []
            row_host = self._extract_host_from_url(row_url)
            row_path_only = self._path_only(row_path)
            for item in history:
                if item is None:
                    continue
                try:
                    req_info = self._extender._helpers.analyzeRequest(item)
                    item_method = str(req_info.getMethod())
                    item_url_obj = req_info.getUrl()
                    item_url = str(item_url_obj)
                    item_host = str(item_url_obj.getHost()) if item_url_obj is not None else ""
                    item_path = str(item_url_obj.getPath()) if item_url_obj is not None else ""
                    item_path_only = self._path_only(item_path)
                except:
                    continue
                if item_method == row_method and item_url == row_url:
                    matches.append(item)
                if item_method == row_method and row_host == item_host and row_path_only and item_path_only == row_path_only:
                    relaxed_matches.append(item)
                    idx = self._history_index_of(history, item)
                    if idx >= 0:
                        indexed_relaxed_matches.append((idx, item))

            if row_seq is not None:
                seq_candidates = self._history_candidates_by_row_seq(history, row_seq)
                for cand in seq_candidates:
                    if cand is None:
                        continue
                    try:
                        c_info = self._extender._helpers.analyzeRequest(cand)
                        c_method = str(c_info.getMethod())
                        c_url_obj = c_info.getUrl()
                        c_host = str(c_url_obj.getHost()) if c_url_obj is not None else ""
                        c_path = str(c_url_obj.getPath()) if c_url_obj is not None else ""
                        c_path_only = self._path_only(c_path)
                    except:
                        continue
                    if c_method == row_method and c_host == row_host and row_path_only and c_path_only == row_path_only:
                        seq_matches.append(cand)

            chosen = None
            decision = "none"

            if len(matches) == 1:
                chosen = matches[0]
                decision = "exact-one"
            elif len(matches) > 1:
                # Deterministic choice: most recent in proxy history.
                chosen = matches[-1]
                decision = "exact-last"
            elif len(seq_matches) == 1:
                chosen = seq_matches[0]
                decision = "seq-one"
            elif len(seq_matches) > 1:
                chosen = self._choose_by_row_seq_distance(history, row_seq, seq_matches)
                decision = "seq-nearest" if chosen is not None else "none"
            elif len(relaxed_matches) == 1:
                chosen = relaxed_matches[0]
                decision = "relaxed-one"
            elif len(relaxed_matches) > 1:
                chosen = self._choose_by_row_seq_distance(history, row_seq, relaxed_matches)
                if chosen is not None:
                    decision = "relaxed-nearest"
                else:
                    # Keep deterministic fallback only when row_seq is not available.
                    if row_seq is None:
                        chosen = relaxed_matches[-1]
                        decision = "relaxed-last-no-seq"

            if chosen is not None:
                extracted.append(chosen)
            # old branch logic retained in decision/log fields only
            if False:
                extracted.append(matches[0])

        return extracted

    def _safe_model_value(self, model, row, col):
        try:
            return model.getValueAt(row, col)
        except:
            return None

    def _infer_method_url_from_row(self, model, model_row):
        if model is None:
            return None, None, None, "", -1, None, []
        cols = 0
        try:
            cols = model.getColumnCount()
        except:
            cols = 0
        method_candidates = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD", "TRACE", "CONNECT"]
        found_method = None
        found_url = None
        host_cell = None
        path_cell = None
        row_status = ""
        row_len = -1
        row_seq = None
        sampled = []
        for col in range(cols):
            value = self._safe_model_value(model, model_row, col)
            if value is None:
                continue
            text = str(value)
            if len(sampled) < 8:
                sampled.append("c{}={}".format(col, text[:80]))
            upper = text.strip().upper()
            if found_method is None and upper in method_candidates:
                found_method = upper
            if found_url is None and (text.startswith("http://") or text.startswith("https://")):
                found_url = text
            if host_cell is None and "ZNC=" in text and "ZNz=" in text:
                host_cell = text
            if path_cell is None and text.startswith("/"):
                path_cell = text
            if row_status == "" and (text.startswith("HTTP/") or text.startswith("Status:")):
                row_status = text
            if row_len < 0:
                try:
                    if col == 7:
                        row_len = int(text)
                except:
                    pass
            if row_seq is None:
                try:
                    if col == 0:
                        row_seq = int(text)
                except:
                    pass

        # Burp proxy history table often stores host/proto in a custom object string and path separately.
        if found_url is None and host_cell is not None and path_cell is not None:
            host = self._extract_between(host_cell, "ZNC=", ",")
            proto_full = self._extract_between(host_cell, "ZNz=", "]")
            proto = "https"
            if proto_full.startswith("http://"):
                proto = "http"
            elif proto_full.startswith("https://"):
                proto = "https"
            if host:
                found_url = "{}://{}{}".format(proto, host, path_cell)
        # Convert compact status values like "200" to the same header style Burp uses.
        if row_status == "":
            candidate_status = self._safe_model_value(model, model_row, 6)
            if candidate_status is not None:
                status_str = str(candidate_status).strip()
                if status_str.isdigit():
                    row_status = "HTTP/1.1 {}".format(status_str)
                else:
                    row_status = status_str
        return found_method, found_url, path_cell, row_status, row_len, row_seq, sampled

    def _extract_host_from_url(self, url):
        if not url:
            return ""
        text = str(url)
        if "://" not in text:
            return ""
        without_scheme = text.split("://", 1)[1]
        return without_scheme.split("/", 1)[0]

    def _history_candidates_by_row_seq(self, history, row_seq):
        size = len(history)
        candidates = []
        # Candidate 1: row number maps to 1-based chronological index.
        idx_forward = row_seq - 1
        if idx_forward >= 0 and idx_forward < size:
            candidates.append(history[idx_forward])
        # Candidate 2: row number maps to reverse order in UI.
        idx_reverse = size - row_seq
        if idx_reverse >= 0 and idx_reverse < size:
            cand = history[idx_reverse]
            if cand not in candidates:
                candidates.append(cand)
        # Add a small neighborhood around reverse index to handle table/filter drifts.
        for delta in range(1, 7):
            near = idx_reverse - delta
            if near >= 0 and near < size:
                cand = history[near]
                if cand not in candidates:
                    candidates.append(cand)
            near = idx_reverse + delta
            if near >= 0 and near < size:
                cand = history[near]
                if cand not in candidates:
                    candidates.append(cand)
        return candidates

    def _path_only(self, path_value):
        if not path_value:
            return ""
        text = str(path_value)
        return text.split("?", 1)[0]

    def _history_index_of(self, history, target):
        for idx in range(len(history)):
            if history[idx] is target:
                return idx
        return -1

    def _choose_by_row_seq_distance(self, history, row_seq, candidates):
        if row_seq is None or row_seq <= 0:
            return None
        target_rev = len(history) - row_seq
        best = None
        best_dist = None
        for item in candidates:
            idx = self._history_index_of(history, item)
            if idx < 0:
                continue
            dist = abs(idx - target_rev)
            if best is None or dist < best_dist:
                best = item
                best_dist = dist
        return best

    def _extract_between(self, text, start_token, end_token):
        if text is None:
            return ""
        start_idx = text.find(start_token)
        if start_idx < 0:
            return ""
        start_idx += len(start_token)
        end_idx = text.find(end_token, start_idx)
        if end_idx < 0:
            end_idx = len(text)
        return text[start_idx:end_idx].strip()

    def _extract_messages_via_known_methods(self, table, model, selected_rows):
        found = []
        # Methods with no args returning one or many selected messages.
        for method_name in ["getSelectedMessages", "getSelection", "getSelectedObjects", "getSelectedMessage"]:
            if hasattr(table, method_name):
                try:
                    value = getattr(table, method_name)()
                    found.extend(self._coerce_messages(value))
                except:
                    pass
        # Methods with row index.
        for view_row in selected_rows:
            try:
                model_row = table.convertRowIndexToModel(view_row) if hasattr(table, "convertRowIndexToModel") else view_row
            except:
                model_row = view_row
            for method_name in ["getMessageAt", "getRequestResponseAt", "getHttpRequestResponseAt", "getObjectAt"]:
                if hasattr(table, method_name):
                    try:
                        value = getattr(table, method_name)(view_row)
                        found.extend(self._coerce_messages(value))
                    except:
                        pass
                if model is not None and hasattr(model, method_name):
                    try:
                        value = getattr(model, method_name)(model_row)
                        found.extend(self._coerce_messages(value))
                    except:
                        pass
        return found

    def _coerce_messages(self, value):
        if value is None:
            return []
        if self._is_http_request_response(value):
            return [value]
        if hasattr(value, "__iter__"):
            messages = []
            try:
                for item in value:
                    unwrapped = self._unwrap_http_message(item)
                    if self._is_http_request_response(unwrapped):
                        messages.append(unwrapped)
                return messages
            except:
                return []
        unwrapped = self._unwrap_http_message(value)
        if self._is_http_request_response(unwrapped):
            return [unwrapped]
        return []

    def _find_table(self, component):
        current = component
        while current is not None:
            if hasattr(current, "getModel") and hasattr(current, "getSelectedRows"):
                return current
            current = current.getParent() if hasattr(current, "getParent") else None
        return None

    def _is_http_request_response(self, value):
        return value is not None and hasattr(value, "getRequest") and hasattr(value, "getHttpService")

    def _unwrap_http_message(self, value):
        if value is None:
            return None
        if self._is_http_request_response(value):
            return value
        for accessor in ["getHttpRequestResponse", "getRequestResponse", "getMessageInfo"]:
            if hasattr(value, accessor):
                try:
                    nested = getattr(value, accessor)()
                    if self._is_http_request_response(nested):
                        return nested
                except:
                    pass
        return value
