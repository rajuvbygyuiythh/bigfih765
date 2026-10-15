#!/usr/bin/env python3
"""Validate research artifacts, NOT remote services. Python 3.9+, no network."""
import json
from pathlib import Path
from urllib.parse import urlparse


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(root):
    data = json.loads((root / "sites.json").read_text(encoding="utf-8"))
    report = (root / "REPORT.md").read_text(encoding="utf-8")
    sources = data["sources"]
    require(data["phase"] == "passive_public_source_screening", "Phase drift")
    require(data["completion"] == "partial_not_runtime_audit", "Completion drift")
    require(len(data["sites"]) == 10, "Expected ten screened records")
    require(len({s["name"] for s in data["sites"]}) == 10, "Duplicate names")
    require(all(urlparse(u).scheme == "https" for u in sources.values()), "Source URL scheme")
    allowed_labels = {"documented", "observed_page_text", "unknown", "not_tested", "not_measured"}
    references = set()
    unknown_count = 0

    def walk(value):
        nonlocal unknown_count
        if isinstance(value, dict):
            for ref in value.get("source_ids", []):
                require(ref in sources, "Unknown source: " + ref)
                references.add(ref)
            if "classification" in value:
                require(value["classification"] in allowed_labels, "Unknown evidence label")
                if value["classification"] == "not_measured":
                    unknown_count += 1
                    require("value" in value and value["value"] is None, "Unmeasured field has a value")
                    require(bool(value.get("reason")), "Missing uncertainty reason")
                else:
                    require(bool(value.get("summary")), "Missing finding summary")
                    require(bool(value.get("source_ids")), "Missing source references")
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(data)
    for i, site in enumerate(data["sites"], 1):
        require(f'id="site-{i}"' in report, "Missing report dossier")
        require(site["name"] in report, "Missing site name in report")
        require(set(site["authentication"]) == {"guest", "login", "auto_signup"}, "Auth coverage")
        require({"response_headers", "tls_handshake", "csp", "waf", "captcha"} <= set(site["security"]), "Security coverage")
        require({"cookies", "localStorage", "indexedDB", "server_side_hints"} <= set(site["storage"]), "Storage coverage")
        require({"documented_interfaces", "observed_xhr_fetch", "observed_websocket"} <= set(site["network"]), "Network coverage")
        require(site["chat_delivery_test"]["result"] == "not_run", "Unexpected live-test claim")
        require(site["chat_delivery_test"]["messages_sent"] == 0, "Unexpected sent-message claim")
        require(site["decision"]["requirements"], "Missing next-check gates")
        for key in ("response_headers", "tls_handshake", "csp", "waf"):
            require(site["security"][key]["classification"] == "not_measured", "Unexpected security measurement")
    require(set(sources) == references, "Unused source reference")
    for number, url in enumerate(sources.values(), 1):
        require(f"[{number}]({url})" in report, "Report source missing")
    require("Messages sent: zero" in report, "Missing delivery boundary")
    print(f"PASS: {len(data['sites'])} dossiers, {len(sources)} source references, {unknown_count} explicit unmeasured fields")
    print("PASS: auth/security/network/storage coverage and source/report consistency")
    print("NOT TESTED: third-party login, API access, TLS, browser traffic/storage or chat delivery")


if __name__ == "__main__":
    validate(Path(__file__).resolve().parent)
