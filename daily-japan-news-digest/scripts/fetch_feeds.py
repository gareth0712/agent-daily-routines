#!/usr/bin/env python3
"""fetch_feeds.py — deterministic RSS/Atom fetcher for daily-japan-news-digest.

Why: the old routine had an LLM WebFetch each feed and self-report what it
saw — no independent proof. This script fetches every source itself (stdlib
only), parses RSS 2.0 / Atom / RSS 1.0 (RDF), and writes zero-trust JSON
Lines logs so a run can be verified from the filesystem, not an agent claim.
"""
import argparse
import concurrent.futures
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

JST = timezone(timedelta(hours=9))
UTC = timezone.utc
UA = "Mozilla/5.0 (compatible; agent-daily-routines/1.0)"
RETRY_DELAY_S = 2
SUMMARY_MAX_CHARS = 500
ATOM_NS = "{http://www.w3.org/2005/Atom}"
DC_NS = "{http://purl.org/dc/elements/1.1/}"
RDF_ITEM = "{http://purl.org/rss/1.0/}item"


def now_jst_iso():
    return datetime.now(JST).isoformat(timespec="seconds")


def to_jst_iso(dt):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(JST).isoformat(timespec="seconds")


def parse_date(text):
    if not text:
        return None
    text = text.strip()
    try:
        dt = parsedate_to_datetime(text)
        if dt is not None:
            return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except (TypeError, ValueError):
        pass
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except ValueError:
        return None


class Logger:
    """Appends JSON-Lines entries to actions.log / errors.log (zero-trust)."""

    def __init__(self, log_dir):
        os.makedirs(log_dir, exist_ok=True)
        self.actions_path = os.path.join(log_dir, "actions.log")
        self.errors_path = os.path.join(log_dir, "errors.log")
        for p in (self.actions_path, self.errors_path):
            if not os.path.exists(p):
                open(p, "a", encoding="utf-8").close()

    def _write(self, path, level, action, detail):
        entry = {"ts": now_jst_iso(), "level": level, "action": action, "detail": detail}
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def info(self, action, detail):
        self._write(self.actions_path, "INFO", action, detail)

    def warn(self, action, detail):
        self._write(self.errors_path, "WARN", action, detail)

    def error(self, action, detail):
        self._write(self.errors_path, "ERROR", action, detail)


def classify_error(exc):
    """Map an exception to one of: http_403/404/5xx, timeout, network_policy, parse_error, other."""
    if isinstance(exc, urllib.error.HTTPError):
        code = exc.code
        via = (exc.headers.get("Via", "") if exc.headers else "")
        body = ""
        try:
            body = exc.read(500).decode("utf-8", "ignore")
        except Exception:
            pass
        blocked = "agentproxy" in via.lower() or "agentproxy" in body.lower() or re.search(r"\bblocked\b", body, re.I)
        if code == 407 or blocked:
            return "network_policy", f"HTTPError: {code} {exc.reason}"
        if code == 403:
            return "http_403", f"HTTPError: {code} {exc.reason}"
        if code == 404:
            return "http_404", f"HTTPError: {code} {exc.reason}"
        if 500 <= code < 600:
            return "http_5xx", f"HTTPError: {code} {exc.reason}"
        return "other", f"HTTPError: {code} {exc.reason}"
    if isinstance(exc, urllib.error.URLError):
        reason = str(exc.reason)
        if "timed out" in reason.lower():
            return "timeout", f"URLError: {reason}"
        if re.search(r"\b(blocked|proxy|agentproxy)\b", reason, re.I):
            return "network_policy", f"URLError: {reason}"
        return "other", f"URLError: {reason}"
    if isinstance(exc, TimeoutError):
        return "timeout", f"TimeoutError: {exc}"
    if isinstance(exc, ElementTree.ParseError):
        return "parse_error", f"ParseError: {exc}"
    return "other", f"{type(exc).__name__}: {exc}"


def fetch_url(url, timeout, cafile):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    kwargs = {"timeout": timeout}
    if cafile:
        import ssl
        kwargs["context"] = ssl.create_default_context(cafile=cafile)
    with urllib.request.urlopen(req, **kwargs) as resp:
        return resp.status, resp.geturl(), resp.read()


def extract_items(root):
    """RSS2 <item>, Atom <entry>, RSS1.0/RDF <item> — in that priority order."""
    items = root.findall(".//item") or root.findall(f".//{ATOM_NS}entry") or root.findall(f".//{RDF_ITEM}")
    return items


def field_text(el, *names):
    for name in names:
        child = el.find(name)
        if child is not None and child.text:
            return child.text.strip()
    return None


def extract_link(el):
    links = el.findall(f"{ATOM_NS}link")
    for l in links:  # prefer rel="alternate"
        if l.get("rel") in (None, "alternate") and l.get("href"):
            return l.get("href")
    for l in links:
        if l.get("href"):
            return l.get("href")
    link_el = el.find("link")
    if link_el is not None:
        if link_el.text and link_el.text.strip():
            return link_el.text.strip()
        if link_el.get("href"):
            return link_el.get("href")
    return None


def extract_date(el):
    for tag in ("pubDate", f"{DC_NS}date", f"{ATOM_NS}published", "published", f"{ATOM_NS}updated", "updated"):
        dt = parse_date(field_text(el, tag))
        if dt:
            return dt
    return None


def strip_html(text):
    """Feed descriptions are often HTML; keep a short plain-text excerpt for fallback summaries."""
    if not text:
        return None
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:SUMMARY_MAX_CHARS] or None


def parse_feed(body):
    root = ElementTree.fromstring(body)
    return [
        {
            "title": field_text(el, "title", f"{ATOM_NS}title") or "(無標題)",
            "link": extract_link(el) or "",
            "published_dt": extract_date(el),
            "summary": strip_html(field_text(el, "description", f"{ATOM_NS}summary", f"{ATOM_NS}content", "{http://purl.org/rss/1.0/modules/content/}encoded")),
        }
        for el in extract_items(root)
    ]


def fetch_source(category_key, source, args, logger):
    name, url = source["name"], source["url"]
    result = {"category": category_key, "name": name, "url": url, "status": None, "items": [], "http_status": None, "newest_iso": None}
    try:
        try:
            status, final_url, body = fetch_url(url, args.timeout, args.cafile)
        except Exception as first:  # one retry: some CDNs (e.g. NHK) answer 403/5xx at random
            if classify_error(first)[0] not in ("http_403", "http_5xx", "timeout", "other"):
                raise
            time.sleep(RETRY_DELAY_S)
            status, final_url, body = fetch_url(url, args.timeout, args.cafile)
        result["http_status"] = status
        items = parse_feed(body)
    except Exception as exc:  # network / HTTP / XML — classify and log, never abort the run
        err_class, msg = classify_error(exc)
        logger.error("fetch_rss", {"category": category_key, "source": name, "url": url, "error": f"{err_class}: {msg}"})
        result["status"] = "error"
        return result

    cutoff = datetime.now(UTC) - timedelta(hours=args.lookback_hours)
    dated = sorted((i for i in items if i["published_dt"]), key=lambda i: i["published_dt"], reverse=True)
    undated = [i for i in items if not i["published_dt"]]
    kept = [i for i in dated if i["published_dt"] >= cutoff][: args.max_items_per_source]
    if len(kept) < args.max_items_per_source and undated:
        logger.warn("fetch_rss", {"category": category_key, "source": name, "url": url, "warning": "missing_pubdate"})
        kept += undated[: args.max_items_per_source - len(kept)]

    newest_iso = None
    if dated:
        newest_iso = to_jst_iso(dated[0]["published_dt"])
        if dated[0]["published_dt"] < datetime.now(UTC) - timedelta(days=args.stale_days):
            logger.warn("fetch_rss", {"category": category_key, "source": name, "url": url, "warning": "stale_feed", "newest_item": newest_iso})

    out_items = [
        {
            "source": name,
            "title": i["title"],
            "link": i["link"],
            "published": to_jst_iso(i["published_dt"]) if i["published_dt"] else None,
            "summary": i["summary"],
            "lang": source.get("lang"),
        }
        for i in kept
    ]

    detail = {"category": category_key, "source": name, "items": len(out_items), "status": status}
    if final_url != url:
        detail["url_effective"] = final_url
    logger.info("fetch_rss", detail)

    result.update(status="ok", items=out_items, newest_iso=newest_iso)
    return result


def build_output(cfg, results, args):
    by_key = {}
    for r in results:
        by_key.setdefault(r["category"], []).append(r)

    categories = {}
    for cat_key, cat in cfg.get("categories", {}).items():
        sources_out, all_items = [], []
        for r in by_key.get(cat_key, []):
            sources_out.append({"name": r["name"], "url": r["url"], "status": r["http_status"] or "error", "items": len(r["items"])})
            all_items.extend(r["items"])
        dated = sorted((i for i in all_items if i["published"]), key=lambda i: i["published"], reverse=True)
        undated = [i for i in all_items if not i["published"]]
        categories[cat_key] = {
            "label": cat.get("label"),
            "priority": cat.get("priority"),
            "summaryDepth": cat.get("summaryDepth"),
            "items": (dated + undated)[: args.max_total_per_category],
            "sources": sources_out,
        }
    return {"generated_at": now_jst_iso(), "lookback_hours": args.lookback_hours, "categories": categories}


def print_summary(results):
    header = ("category", "source", "http", "items", "newest", "note")
    rows = [
        (r["category"], r["name"], str(r["http_status"] or "ERR"), str(len(r["items"])), r["newest_iso"] or "-",
         "ok" if r["status"] == "ok" else "fetch failed (see errors.log)")
        for r in sorted(results, key=lambda r: (r["category"], r["name"]))
    ]
    widths = [max(len(h), *(len(row[i]) for row in rows)) if rows else len(h) for i, h in enumerate(header)]
    line = lambda row: " | ".join(str(c).ljust(w) for c, w in zip(row, widths))
    print(line(header))
    print("-+-".join("-" * w for w in widths))
    for row in rows:
        print(line(row))
    ok = sum(1 for r in results if r["status"] == "ok")
    print(f"\n{ok}/{len(results)} sources fetched successfully.")
    return ok


def main():
    ap = argparse.ArgumentParser(description="Deterministic RSS/Atom fetcher with zero-trust logging.")
    ap.add_argument("--sources", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--log-dir", default="daily-japan-news-digest/logs")
    ap.add_argument("--lookback-hours", type=float, default=None)
    ap.add_argument("--timeout", type=float, default=20.0)
    args = ap.parse_args()

    with open(args.sources, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    meta = cfg.get("meta", {})
    args.max_items_per_source = meta.get("maxItemsPerSource", 5)
    args.max_total_per_category = meta.get("maxTotalItemsPerCategory", 15)
    args.stale_days = meta.get("staleFeedDays", 7)
    if args.lookback_hours is None:
        args.lookback_hours = meta.get("lookbackHours", 24)

    cafile = os.environ.get("SSL_CERT_FILE") or ("/root/.ccr/ca-bundle.crt" if os.path.exists("/root/.ccr/ca-bundle.crt") else None)
    args.cafile = cafile

    logger = Logger(args.log_dir)
    tasks = [(ck, src) for ck, cat in cfg.get("categories", {}).items() for src in cat.get("sources", [])]

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        futs = [pool.submit(fetch_source, ck, src, args, logger) for ck, src in tasks]
        for fut in concurrent.futures.as_completed(futs):
            results.append(fut.result())

    output = build_output(cfg, results, args)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    ok_count = print_summary(results)
    sys.exit(2 if results and ok_count == 0 else 0)


if __name__ == "__main__":
    main()
