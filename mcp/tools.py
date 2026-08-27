#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MCP tool registry for Autorize. Each tool is (name, description, inputSchema,
# handler). Handlers receive (server, arguments) and return a JSON-serializable
# object; the protocol layer wraps that into an MCP tools/call result.

import re

from mcp.edt import run_on_edt, snapshot_log


# ---------------------------------------------------------------------------
# Option vocabularies (kept in sync with the GUI combo boxes)
# ---------------------------------------------------------------------------

# gui/enforcement_detector.py EDStrings (per-user and unauthenticated detector)
ENFORCEMENT_DETECTOR_TYPES = [
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
    "Status code NOT equals: (numbers only)",
]

# gui/match_replace.py MRStrings
MATCH_REPLACE_TYPES = [
    "Headers (simple string):",
    "Headers (regex):",
    "Body (simple string):",
    "Body (regex):",
    "Path (simple string):",
    "Path (regex):",
]

# gui/interception_filters.py IFStrings
INTERCEPTION_FILTER_TYPES = [
    "Scope items only: (Content is not required)",
    "URL Contains (simple string): ",
    "URL Contains (regex): ",
    "URL Not Contains (simple string): ",
    "URL Not Contains (regex): ",
    "Request Body contains (simple string): ",
    "Request Body contains (regex): ",
    "Request Body NOT contains (simple string): ",
    "Request Body Not contains (regex): ",
    "Response Body contains (simple string): ",
    "Response Body contains (regex): ",
    "Response Body NOT contains (simple string): ",
    "Response Body Not contains (regex): ",
    "Request headers contain: ",
    "Request headers don't contain: ",
    "Response headers contain: ",
    "Response headers don't contain: ",
    "Only HTTP methods (newline separated): ",
    "Ignore HTTP methods (newline separated): ",
    "Ignore spider requests: (Content is not required)",
    "Ignore proxy requests: (Content is not required)",
    "Ignore target requests: (Content is not required)",
    "Ignore OPTIONS requests: (Content is not required)",
    "Drop proxy listener ports: (Separated by comma)",
]

AND_OR_OPTIONS = ["And", "Or"]


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _status_map(extender):
    return {
        "bypassed": extender.BYPASSSED_STR,
        "enforced": extender.ENFORCED_STR,
        "ambiguous": extender.IS_ENFORCED_STR,
        "disabled": "Disabled",
    }


def _resp_length(extender, requestResponse):
    if requestResponse is None or requestResponse.getResponse() is None:
        return 0
    response = requestResponse.getResponse()
    try:
        return len(response) - extender._helpers.analyzeResponse(response).getBodyOffset()
    except Exception:
        return len(response)


def _msg_text(extender, requestResponse, which):
    if requestResponse is None:
        return None
    data = requestResponse.getRequest() if which == "request" else requestResponse.getResponse()
    if data is None:
        return None
    return extender._helpers.bytesToString(data)


def _user_id_name_map(extender):
    return run_on_edt(
        lambda: dict((uid, ud['user_name']) for uid, ud in extender.userTab.user_tabs.items()))


def _model_to_str_list(model):
    return [str(model.getElementAt(i)) for i in range(model.getSize())]


def _build_filter_entry(item):
    """Accept a raw string (stored verbatim) or a {type, content} object and
    return the canonical stored string used by addFilterHelper: 'Title: content'.
    """
    if isinstance(item, (str, unicode)):
        return item
    if isinstance(item, dict):
        ftype = item.get("type", "")
        content = item.get("content", "")
        title = ftype.split(":")[0].strip()
        return title + ": " + content
    raise ValueError("filter entry must be a string or {type, content} object")


# ---------------------------------------------------------------------------
# Status / lifecycle
# ---------------------------------------------------------------------------

def _status(server, args):
    ext = server.extender
    count = len(snapshot_log(ext))
    users = run_on_edt(
        lambda: [{"id": uid, "name": ud['user_name']}
                 for uid, ud in sorted(ext.userTab.user_tabs.items())])
    return {
        "enabled": bool(ext.intercept),
        "result_count": count,
        "mcp_port": server.port,
        "users": users,
    }


def _start(server, args):
    from gui.configuration_tab import set_running
    run_on_edt(lambda: set_running(server.extender, True))
    return {"enabled": True}


def _stop(server, args):
    from gui.configuration_tab import set_running
    run_on_edt(lambda: set_running(server.extender, False))
    return {"enabled": False}


def _clear_results(server, args):
    from gui.configuration_tab import ClearTableRunnable
    from java.util.concurrent import TimeUnit
    ext = server.extender
    before = len(snapshot_log(ext))
    future = ext.executor.submit(ClearTableRunnable(ext))
    future.get(10, TimeUnit.SECONDS)
    return {"cleared": before}


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

def _list_results(server, args, use_regex=False):
    ext = server.extender
    status_filter = (args.get("status") or "all").lower()
    user_filter = args.get("user")
    method_filter = args.get("method")
    url_contains = args.get("url_contains")
    url_regex = args.get("url_regex")
    offset = int(args.get("offset", 0))
    count = int(args.get("count", 50))
    if offset < 0:
        offset = 0
    if count < 1:
        count = 1
    if count > 500:
        count = 500

    target_status = None
    if status_filter != "all":
        target_status = _status_map(ext).get(status_filter)
        if target_status is None:
            raise ValueError("invalid status: %s" % status_filter)

    compiled = None
    if use_regex and url_regex:
        compiled = re.compile(url_regex, re.IGNORECASE)

    id_name = _user_id_name_map(ext)
    entries = snapshot_log(ext)

    items = []
    for le in entries:
        url = le._url.toString()
        method = str(le._method)
        if method_filter and method_filter.upper() != method.upper():
            continue
        if url_contains and url_contains not in url:
            continue
        if compiled is not None and compiled.search(url) is None:
            continue

        user_verdicts = {}
        for uid, ud in le._userEnforcements.items():
            name = id_name.get(uid, "user_%s" % uid)
            user_verdicts[name] = {
                "length": _resp_length(ext, ud.get('requestResponse')),
                "status": ud.get('enforcementStatus'),
            }

        unauth = None
        if le._unauthorizedRequestResponse is not None:
            unauth = {
                "length": _resp_length(ext, le._unauthorizedRequestResponse),
                "status": le._enfocementStatusUnauthorized,
            }

        if user_filter is not None:
            if user_filter not in user_verdicts:
                continue
            if target_status is not None and user_verdicts[user_filter]["status"] != target_status:
                continue
        elif target_status is not None:
            statuses = [le._enfocementStatusUnauthorized]
            statuses.extend(v["status"] for v in user_verdicts.values())
            if target_status not in statuses:
                continue

        items.append({
            "id": le._id,
            "method": method,
            "url": url,
            "orig_length": _resp_length(ext, le._originalrequestResponse),
            "unauthenticated": unauth,
            "users": user_verdicts,
        })

    total = len(items)
    page = items[offset:offset + count]
    return {"total": total, "offset": offset, "count": len(page), "items": page}


def _list_results_regex(server, args):
    return _list_results(server, args, use_regex=True)


def _get_result(server, args):
    ext = server.extender
    rid = args.get("id")
    if rid is None:
        raise ValueError("id is required")
    id_name = _user_id_name_map(ext)
    entries = snapshot_log(ext)
    le = None
    for e in entries:
        if e._id == rid:
            le = e
            break
    if le is None:
        raise ValueError("result id not found: %s" % rid)

    users = {}
    for uid, ud in le._userEnforcements.items():
        name = id_name.get(uid, "user_%s" % uid)
        rr = ud.get('requestResponse')
        users[name] = {
            "request": _msg_text(ext, rr, "request"),
            "response": _msg_text(ext, rr, "response"),
            "status": ud.get('enforcementStatus'),
        }

    unauth = None
    if le._unauthorizedRequestResponse is not None:
        unauth = {
            "request": _msg_text(ext, le._unauthorizedRequestResponse, "request"),
            "response": _msg_text(ext, le._unauthorizedRequestResponse, "response"),
            "status": le._enfocementStatusUnauthorized,
        }

    return {
        "id": le._id,
        "method": str(le._method),
        "url": le._url.toString(),
        "original": {
            "request": _msg_text(ext, le._originalrequestResponse, "request"),
            "response": _msg_text(ext, le._originalrequestResponse, "response"),
        },
        "unauthenticated": unauth,
        "users": users,
    }


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def _read_user(ext, uid):
    ud = ext.userTab.user_tabs[uid]
    mr = ud['mr_instance']
    rules = []
    for i in range(mr.MRModel.getSize()):
        key = mr.MRModel.getElementAt(i)
        rd = mr.badProgrammerMRModel.get(key)
        if rd:
            rules.append({"type": rd['type'], "match": rd['match'], "replace": rd['replace']})
    ed = ud['ed_instance']
    return {
        "id": uid,
        "name": ud['user_name'],
        "headers_text": ud['headers_instance'].replaceString.getText(),
        "match_replace_rules": rules,
        "enforcement_detector": {
            "filters": _model_to_str_list(ed.EDModel),
            "and_or": ed.AndOrType.getSelectedItem(),
        },
    }


def _list_users(server, args):
    ext = server.extender
    return {"users": run_on_edt(
        lambda: [_read_user(ext, uid) for uid in sorted(ext.userTab.user_tabs.keys())])}


def _get_last_headers(server, args):
    ext = server.extender
    return {
        "cookies": getattr(ext, 'lastCookiesHeader', "") or "",
        "authorization": getattr(ext, 'lastAuthorizationHeader', "") or "",
    }


def _apply_user_config(ext, uid, cfg):
    """Apply a user config dict to user `uid`. MUST run on the EDT."""
    ud = ext.userTab.user_tabs.get(uid)
    if ud is None:
        raise ValueError("user not found: %s" % uid)

    if cfg.get("name"):
        ext.userTab.set_user_name(uid, cfg["name"])

    fetch = cfg.get("fetch_from_last_request")
    if fetch == "cookies":
        val = getattr(ext, 'lastCookiesHeader', "") or ""
        if val:
            ud['headers_instance'].replaceString.setText(val)
    elif fetch == "authorization":
        val = getattr(ext, 'lastAuthorizationHeader', "") or ""
        if val:
            ud['headers_instance'].replaceString.setText(val)
    elif "headers_text" in cfg:
        ud['headers_instance'].replaceString.setText(cfg["headers_text"] or "")

    if "match_replace_rules" in cfg:
        mr = ud['mr_instance']
        mr.MRModel.clear()
        mr.badProgrammerMRModel.clear()
        for rule in (cfg["match_replace_rules"] or []):
            rtype = rule.get("type")
            match = rule.get("match", "")
            replace = rule.get("replace", "")
            key = rtype + " " + match + "->" + replace
            regex_match = None
            if rtype and "(regex)" in rtype:
                try:
                    regex_match = re.compile(match)
                except re.error:
                    regex_match = None
            mr.badProgrammerMRModel[key] = {
                "match": match, "regexMatch": regex_match, "replace": replace, "type": rtype}
            mr.MRModel.addElement(key)

    if "enforcement_detector" in cfg:
        ed_cfg = cfg["enforcement_detector"] or {}
        ed = ud['ed_instance']
        if "filters" in ed_cfg:
            ed.EDModel.clear()
            for item in (ed_cfg["filters"] or []):
                ed.EDModel.addElement(_build_filter_entry(item))
        if ed_cfg.get("and_or"):
            ed.AndOrType.setSelectedItem(ed_cfg["and_or"])


def _add_user(server, args):
    ext = server.extender
    users_cfg = args.get("users")
    if users_cfg is None:
        single = {}
        for k in ("name", "headers_text", "fetch_from_last_request",
                  "match_replace_rules", "enforcement_detector"):
            if k in args:
                single[k] = args[k]
        users_cfg = [single]
    if not isinstance(users_cfg, list):
        raise ValueError("users must be an array")

    def build():
        created = []
        for cfg in users_cfg:
            ext.userTab.add_user()
            uid = ext.userTab.user_count
            _apply_user_config(ext, uid, cfg or {})
            created.append({"id": uid, "name": ext.userTab.user_tabs[uid]['user_name']})
        return created

    return {"created": run_on_edt(build)}


def _update_user(server, args):
    ext = server.extender
    uid = args.get("user_id")
    if uid is None:
        raise ValueError("user_id is required")
    uid = int(uid)

    def build():
        if uid not in ext.userTab.user_tabs:
            raise ValueError("user not found: %s" % uid)
        _apply_user_config(ext, uid, args)
        return _read_user(ext, uid)

    return run_on_edt(build)


def _remove_user(server, args):
    ext = server.extender
    uid = args.get("user_id")
    if uid is None:
        raise ValueError("user_id is required")
    uid = int(uid)

    def build():
        if uid not in ext.userTab.user_tabs:
            return {"removed": False}
        ext.userTab.remove_user(uid)
        return {"removed": uid not in ext.userTab.user_tabs}

    return run_on_edt(build)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def _get_config(server, args):
    ext = server.extender

    def build():
        return {
            "running": bool(ext.intercept),
            "ignore_304_204": ext.ignore304.isSelected(),
            "prevent_304": ext.prevent304.isSelected(),
            "intercept_from_repeater": ext.interceptRequestsfromRepeater.isSelected(),
            "check_unauthenticated": ext.doUnauthorizedRequest.isSelected(),
            "replace_query_params": ext.replaceQueryParam.isSelected(),
            "auto_scroll": ext.autoScroll.isSelected(),
            "table_filter": {
                "show_bypassed": ext.showBypassed.isSelected(),
                "show_is_enforced": ext.showIsEnforced.isSelected(),
                "show_enforced": ext.showEnforced.isSelected(),
            },
        }

    return run_on_edt(build)


def _set_config(server, args):
    ext = server.extender
    from gui.configuration_tab import set_running

    def build():
        if "running" in args:
            set_running(ext, bool(args["running"]))
        if "ignore_304_204" in args:
            ext.ignore304.setSelected(bool(args["ignore_304_204"]))
        if "prevent_304" in args:
            ext.prevent304.setSelected(bool(args["prevent_304"]))
        if "intercept_from_repeater" in args:
            ext.interceptRequestsfromRepeater.setSelected(bool(args["intercept_from_repeater"]))
        if "check_unauthenticated" in args:
            ext.doUnauthorizedRequest.setSelected(bool(args["check_unauthenticated"]))
        if "auto_scroll" in args:
            ext.autoScroll.setSelected(bool(args["auto_scroll"]))
        if "replace_query_params" in args:
            ext.replaceQueryParam.setSelected(bool(args["replace_query_params"]))
            # setSelected does not fire actionPerformed; replicate the button's side effect.
            if getattr(ext, 'configuration_tab_instance', None):
                ext.configuration_tab_instance.replaceQueryHanlder(None)
        tf = args.get("table_filter") or {}
        if "show_bypassed" in tf:
            ext.showBypassed.setSelected(bool(tf["show_bypassed"]))
        if "show_is_enforced" in tf:
            ext.showIsEnforced.setSelected(bool(tf["show_is_enforced"]))
        if "show_enforced" in tf:
            ext.showEnforced.setSelected(bool(tf["show_enforced"]))
        return None

    run_on_edt(build)
    return _get_config(server, args)


def _get_filter_options(server, args):
    return {
        "enforcement_detector_types": ENFORCEMENT_DETECTOR_TYPES,
        "match_replace_types": MATCH_REPLACE_TYPES,
        "interception_filter_types": INTERCEPTION_FILTER_TYPES,
        "and_or_options": AND_OR_OPTIONS,
        "status_values": ["all", "bypassed", "enforced", "ambiguous", "disabled"],
    }


# ---------------------------------------------------------------------------
# Interception filters (global)
# ---------------------------------------------------------------------------

def _get_interception_filters(server, args):
    ext = server.extender
    return {"filters": run_on_edt(lambda: _model_to_str_list(ext.IFModel))}


def _set_interception_filters(server, args):
    ext = server.extender
    filters = args.get("filters")
    if filters is None:
        raise ValueError("filters is required (array of strings or {type, content})")
    if not isinstance(filters, list):
        raise ValueError("filters must be an array")
    entries = [_build_filter_entry(f) for f in filters]

    def build():
        ext.IFModel.clear()
        for e in entries:
            ext.IFModel.addElement(e)
        return _model_to_str_list(ext.IFModel)

    return {"filters": run_on_edt(build)}


# ---------------------------------------------------------------------------
# Unauthenticated enforcement detector (global)
# ---------------------------------------------------------------------------

def _get_unauth_detector(server, args):
    ext = server.extender

    def build():
        return {
            "filters": _model_to_str_list(ext.EDModelUnauth),
            "and_or": ext.AndOrTypeUnauth.getSelectedItem(),
        }

    return run_on_edt(build)


def _set_unauth_detector(server, args):
    ext = server.extender

    def build():
        if "filters" in args:
            ext.EDModelUnauth.clear()
            for item in (args["filters"] or []):
                ext.EDModelUnauth.addElement(_build_filter_entry(item))
        if args.get("and_or"):
            ext.AndOrTypeUnauth.setSelectedItem(args["and_or"])
        return {
            "filters": _model_to_str_list(ext.EDModelUnauth),
            "and_or": ext.AndOrTypeUnauth.getSelectedItem(),
        }

    return run_on_edt(build)


# ---------------------------------------------------------------------------
# Export & state
# ---------------------------------------------------------------------------

def _export(server, args):
    ext = server.extender
    fmt = (args.get("format") or "html").lower()
    status_filter = args.get("status_filter", "All Statuses")
    remove_dups = bool(args.get("remove_duplicates", True))
    from gui.export import build_html_report, build_csv_report

    def build():
        ext._lock.acquire()
        try:
            if fmt == "csv":
                return build_csv_report(ext, status_filter, remove_dups)
            return build_html_report(ext, status_filter, remove_dups)
        finally:
            ext._lock.release()

    content = run_on_edt(build)
    return {"format": fmt, "content": content}


def _save_state(server, args):
    ext = server.extender
    path = args.get("path")
    if not path:
        raise ValueError("path is required")

    def build():
        ext.save_restore_instance.save_state_to_path(path)
        return {"saved": True, "path": path}

    return run_on_edt(build)


def _restore_state(server, args):
    ext = server.extender
    path = args.get("path")
    if not path:
        raise ValueError("path is required")

    def build():
        ext.save_restore_instance.restore_state_from_path(path)
        return {"restored": True, "path": path, "result_count": ext._log.size()}

    return run_on_edt(build)


def _send_to_repeater(server, args):
    ext = server.extender
    rid = args.get("id")
    if rid is None:
        raise ValueError("id is required")
    variant = args.get("variant", "original")
    entries = snapshot_log(ext)
    le = None
    for e in entries:
        if e._id == rid:
            le = e
            break
    if le is None:
        raise ValueError("result id not found: %s" % rid)

    if variant == "original":
        rr = le._originalrequestResponse
    elif variant == "unauthenticated":
        rr = le._unauthorizedRequestResponse
    else:
        name_to_id = run_on_edt(
            lambda: dict((ud['user_name'], uid) for uid, ud in ext.userTab.user_tabs.items()))
        uid = name_to_id.get(variant)
        if uid is None:
            raise ValueError("unknown variant/user: %s" % variant)
        ud = le.get_user_enforcement(uid)
        rr = ud['requestResponse'] if ud else None

    if rr is None:
        raise ValueError("no request/response available for variant: %s" % variant)

    svc = rr.getHttpService()
    secure = svc.getProtocol() == "https"
    ext._callbacks.sendToRepeater(svc.getHost(), svc.getPort(), secure, rr.getRequest(), "Autorize (MCP)")
    return {"sent": True, "variant": variant}


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_FILTER_ENTRY_SCHEMA = {
    "oneOf": [
        {"type": "string"},
        {"type": "object", "properties": {
            "type": {"type": "string"}, "content": {"type": "string"}}},
    ]
}

_MR_RULE_SCHEMA = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": MATCH_REPLACE_TYPES},
        "match": {"type": "string"},
        "replace": {"type": "string"},
    },
    "required": ["type", "match", "replace"],
}

_ED_SCHEMA = {
    "type": "object",
    "properties": {
        "filters": {"type": "array", "items": _FILTER_ENTRY_SCHEMA,
                    "description": "Each entry is a raw 'Title: content' string, or {type, content} "
                                   "where type is one of the enforcement_detector_types."},
        "and_or": {"type": "string", "enum": AND_OR_OPTIONS},
    },
}

TOOLS = [
    ("autorize_status",
     "Get Autorize status: whether scanning is on, number of results, MCP port, and configured users.",
     {"type": "object", "properties": {}},
     _status),

    ("autorize_start",
     "Turn Autorize scanning on (equivalent to the 'Autorize is off/on' toggle).",
     {"type": "object", "properties": {}},
     _start),

    ("autorize_stop",
     "Turn Autorize scanning off.",
     {"type": "object", "properties": {}},
     _stop),

    ("autorize_clear_results",
     "Clear the Autorize results table. Returns how many rows were removed.",
     {"type": "object", "properties": {}},
     _clear_results),

    ("autorize_list_results",
     "List Autorize results (paginated). Each item includes per-user and unauthenticated "
     "verdicts and response lengths. Filter by status, user name, HTTP method, or URL substring.",
     {"type": "object", "properties": {
         "status": {"type": "string", "enum": ["all", "bypassed", "enforced", "ambiguous", "disabled"],
                    "default": "all"},
         "user": {"type": "string", "description": "Restrict to one low-priv user's verdict, by name."},
         "method": {"type": "string"},
         "url_contains": {"type": "string"},
         "offset": {"type": "integer", "default": 0, "minimum": 0},
         "count": {"type": "integer", "default": 50, "minimum": 1, "maximum": 500}}},
     _list_results),

    ("autorize_list_results_regex",
     "Like autorize_list_results but matches the URL against a case-insensitive regex (url_regex).",
     {"type": "object", "properties": {
         "status": {"type": "string", "enum": ["all", "bypassed", "enforced", "ambiguous", "disabled"],
                    "default": "all"},
         "user": {"type": "string"},
         "method": {"type": "string"},
         "url_regex": {"type": "string"},
         "offset": {"type": "integer", "default": 0, "minimum": 0},
         "count": {"type": "integer", "default": 50, "minimum": 1, "maximum": 500}}},
     _list_results_regex),

    ("autorize_get_result",
     "Get full detail for one result by id: original, unauthenticated, and every per-user "
     "request/response pair plus its verdict.",
     {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]},
     _get_result),

    ("autorize_list_users",
     "List configured low-priv users with their headers text, match/replace rules, and enforcement detector.",
     {"type": "object", "properties": {}},
     _list_users),

    ("autorize_add_user",
     "Create one or more low-priv users. Pass a single user's fields, or a 'users' array to create "
     "several at once. Each may set name, headers_text (or fetch_from_last_request), match_replace_rules, "
     "and enforcement_detector.",
     {"type": "object", "properties": {
         "name": {"type": "string"},
         "headers_text": {"type": "string"},
         "fetch_from_last_request": {"type": "string", "enum": ["cookies", "authorization"]},
         "match_replace_rules": {"type": "array", "items": _MR_RULE_SCHEMA},
         "enforcement_detector": _ED_SCHEMA,
         "users": {"type": "array", "items": {"type": "object", "properties": {
             "name": {"type": "string"},
             "headers_text": {"type": "string"},
             "fetch_from_last_request": {"type": "string", "enum": ["cookies", "authorization"]},
             "match_replace_rules": {"type": "array", "items": _MR_RULE_SCHEMA},
             "enforcement_detector": _ED_SCHEMA}}}}},
     _add_user),

    ("autorize_get_last_headers",
     "Read the last-captured Cookie and Authorization header values (the source used by the GUI's "
     "'Fetch Cookies header' / 'Fetch Authorization header' buttons).",
     {"type": "object", "properties": {}},
     _get_last_headers),

    ("autorize_update_user",
     "Update a low-priv user's configuration. Set headers_text directly, or populate it from the last "
     "captured request via fetch_from_last_request ('cookies'|'authorization'). match_replace_rules and "
     "enforcement_detector, when provided, REPLACE the existing sets (all types supported).",
     {"type": "object", "properties": {
         "user_id": {"type": "integer"},
         "name": {"type": "string"},
         "headers_text": {"type": "string"},
         "fetch_from_last_request": {"type": "string", "enum": ["cookies", "authorization"]},
         "match_replace_rules": {"type": "array", "items": _MR_RULE_SCHEMA},
         "enforcement_detector": _ED_SCHEMA}, "required": ["user_id"]},
     _update_user),

    ("autorize_remove_user",
     "Remove a low-priv user by id (the last remaining user cannot be removed).",
     {"type": "object", "properties": {"user_id": {"type": "integer"}}, "required": ["user_id"]},
     _remove_user),

    ("autorize_get_config",
     "Read Autorize's general configuration checkboxes and the table filter state.",
     {"type": "object", "properties": {}},
     _get_config),

    ("autorize_set_config",
     "Update Autorize's general configuration. Only provided keys are changed.",
     {"type": "object", "properties": {
         "running": {"type": "boolean"},
         "ignore_304_204": {"type": "boolean"},
         "prevent_304": {"type": "boolean"},
         "intercept_from_repeater": {"type": "boolean"},
         "check_unauthenticated": {"type": "boolean"},
         "replace_query_params": {"type": "boolean"},
         "auto_scroll": {"type": "boolean"},
         "table_filter": {"type": "object", "properties": {
             "show_bypassed": {"type": "boolean"},
             "show_is_enforced": {"type": "boolean"},
             "show_enforced": {"type": "boolean"}}}}},
     _set_config),

    ("autorize_get_filter_options",
     "List the valid type strings for enforcement detectors, match/replace rules, and interception "
     "filters, plus and/or and status values. Use these when constructing filter entries.",
     {"type": "object", "properties": {}},
     _get_filter_options),

    ("autorize_get_interception_filters",
     "Get the global interception filters (the scope/URL/method/etc. rules that gate what Autorize tests).",
     {"type": "object", "properties": {}},
     _get_interception_filters),

    ("autorize_set_interception_filters",
     "Replace the global interception filters. Each entry is a raw 'Title: content' string, or "
     "{type, content} where type is one of the interception_filter_types.",
     {"type": "object", "properties": {
         "filters": {"type": "array", "items": _FILTER_ENTRY_SCHEMA}}, "required": ["filters"]},
     _set_interception_filters),

    ("autorize_get_unauth_detector",
     "Get the global unauthenticated enforcement detector (filters + And/Or).",
     {"type": "object", "properties": {}},
     _get_unauth_detector),

    ("autorize_set_unauth_detector",
     "Update the global unauthenticated enforcement detector. filters (when provided) REPLACES the set; "
     "all enforcement_detector_types are supported.",
     {"type": "object", "properties": {
         "filters": {"type": "array", "items": _FILTER_ENTRY_SCHEMA},
         "and_or": {"type": "string", "enum": AND_OR_OPTIONS}}},
     _set_unauth_detector),

    ("autorize_export",
     "Export the results table as an HTML or CSV report string.",
     {"type": "object", "properties": {
         "format": {"type": "string", "enum": ["html", "csv"], "default": "html"},
         "status_filter": {"type": "string",
                           "description": "One of 'All Statuses', 'As table filter', or an exact status string.",
                           "default": "All Statuses"},
         "remove_duplicates": {"type": "boolean", "default": True}}},
     _export),

    ("autorize_save_state",
     "Save the full Autorize state (users, filters, detectors, checkboxes, and all captured results) to "
     "a file at the given absolute path.",
     {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
     _save_state),

    ("autorize_restore_state",
     "Restore Autorize state from a file previously written by autorize_save_state (or the GUI Save button).",
     {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
     _restore_state),

    ("autorize_send_to_repeater",
     "Send a result's request into Burp Repeater. variant is 'original', 'unauthenticated', or a user name.",
     {"type": "object", "properties": {
         "id": {"type": "integer"},
         "variant": {"type": "string", "default": "original"}}, "required": ["id"]},
     _send_to_repeater),
]

_HANDLERS = dict((name, handler) for (name, _desc, _schema, handler) in TOOLS)


def list_tools():
    return [{"name": name, "description": desc, "inputSchema": schema}
            for (name, desc, schema, _handler) in TOOLS]


def get_handler(name):
    return _HANDLERS.get(name)
