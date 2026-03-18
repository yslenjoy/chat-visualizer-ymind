#!/usr/bin/env python3
"""
Fetch shared chat content from chatbot share links.

Supported:
- ChatGPT: https://chatgpt.com/share/...  (JSON API)
- Gemini:  https://gemini.google.com/share/...  (Playwright)
- Claude:  https://claude.ai/share/...  (Playwright, headed mode for Cloudflare)

Example:
  python3 fetch-chat.py "https://chatgpt.com/share/..." --out raw_chat.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _fetch_html(url: str, timeout: int) -> requests.Response:
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    return resp


def _fetch_json(url: str, timeout: int) -> Dict[str, Any]:
    headers = {**HEADERS, "Accept": "application/json"}
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def _text_normalize(text: str) -> str:
    text = text.replace("\u200b", "").replace("\ufeff", "")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _resolve_url(url: str) -> str:
    """Follow redirects to get the final URL (handles short links like g.co)."""
    try:
        r = requests.head(url, headers=HEADERS, allow_redirects=True, timeout=10)
        return r.url
    except Exception:
        return url


def _guess_provider(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "chatgpt.com" in host:
        return "chatgpt"
    if "claude.ai" in host:
        return "claude"
    if "gemini.google.com" in host:
        return "gemini"
    # Short link: follow redirect then re-check
    if host in ("g.co", "goo.gl") or url.startswith("https://g.co/"):
        resolved = _resolve_url(url)
        if resolved != url:
            return _guess_provider(resolved)
    return "unknown"


def _extract_title(html: str) -> Optional[str]:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    if m:
        return m.group(1).strip()
    return None


# --- ChatGPT ---

def _collect_messages_from_mapping(mapping: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse ChatGPT's mapping structure into a message list."""
    messages: List[Dict[str, Any]] = []
    for node in mapping.values():
        msg = node.get("message") if isinstance(node, dict) else None
        if not msg:
            continue
        role = msg.get("author", {}).get("role") if isinstance(msg, dict) else None
        content = msg.get("content") if isinstance(msg, dict) else None
        parts = []
        if isinstance(content, dict):
            parts = content.get("parts") or []
        text = "\n".join(p for p in parts if isinstance(p, str))
        if not text:
            continue
        messages.append(
            {
                "id": msg.get("id"),
                "role": role or "unknown",
                "content": _text_normalize(text),
                "created_at": msg.get("create_time"),
            }
        )
    messages.sort(key=lambda m: m.get("created_at") or 0)
    return messages


def _fetch_chatgpt_playwright(url: str, timeout: int) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    """ChatGPT Playwright fallback: render share page headlessly (no cookies saved)."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
        page.wait_for_timeout(8000)

        title = page.title() or None

        messages: List[Dict[str, Any]] = []
        turns = page.query_selector_all("[data-message-author-role]")
        for turn in turns:
            role_attr = turn.get_attribute("data-message-author-role")
            if role_attr not in ("user", "assistant"):
                continue
            text = _text_normalize(turn.inner_text() or "")
            if text:
                messages.append({"role": role_attr, "content": text})

        browser.close()

    return title, messages


def _fetch_chatgpt(url: str, timeout: int) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    """ChatGPT: try /backend-api/share/{id} first; fall back to Playwright on 403."""
    import requests as _requests
    share_id = urlparse(url).path.rstrip("/").split("/")[-1]
    api_url = f"https://chatgpt.com/backend-api/share/{share_id}"
    try:
        data = _fetch_json(api_url, timeout)
        title = data.get("title")
        mapping = data.get("mapping", {})
        messages = _collect_messages_from_mapping(mapping)
        return title, messages
    except _requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 403:
            print("  [ChatGPT] API returned 403, falling back to Playwright ...")
            return _fetch_chatgpt_playwright(url, timeout)
        raise


# --- Gemini (Playwright) ---

def _fetch_gemini(url: str, timeout: int) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    """Gemini: use Playwright to render the share page and extract messages."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
        # Wait for JS to render the conversation (Gemini share pages need ~12s)
        page.wait_for_timeout(12000)

        title = page.title() or None
        # Clean up default title
        if title and "gemini" in title.lower() and "direct access" in title.lower():
            title = None

        messages: List[Dict[str, Any]] = []

        # Each turn is a .share-turn-viewer containing one user query + one AI response
        turns = page.query_selector_all(".share-turn-viewer")
        if not turns:
            # Fallback: try extracting from the whole page
            turns = [page.query_selector("chat-app")]

        for turn in turns:
            if not turn:
                continue
            # User query
            query_els = turn.query_selector_all(".query-text-line")
            if query_els:
                user_text = "\n".join(
                    _text_normalize(el.inner_text() or "") for el in query_els
                )
                if user_text:
                    messages.append({
                        "role": "user",
                        "content": user_text,
                    })

            # AI response
            response_el = turn.query_selector(".message-content")
            if response_el:
                ai_text = _text_normalize(response_el.inner_text() or "")
                if ai_text:
                    messages.append({
                        "role": "assistant",
                        "content": ai_text,
                    })

        # Get conversation title from the h1 headline
        h1 = page.query_selector("h1.headline")
        if h1:
            title = _text_normalize(h1.inner_text() or "") or title

        browser.close()

    return title, messages


# --- Claude (Playwright, headed mode for Cloudflare) ---

def _launch_headed_browser(p, timeout_ms: int):
    """Launch a headed Chromium browser with anti-detection for Cloudflare."""
    browser = p.chromium.launch(
        headless=False,
        args=["--disable-blink-features=AutomationControlled"],
    )
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1280, "height": 720},
        locale="en-US",
    )
    page = context.new_page()
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => false });")
    return browser, page


def _fetch_claude(url: str, timeout: int) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    """Claude: use Playwright in headed mode to bypass Cloudflare and extract messages."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser, page = _launch_headed_browser(p, timeout * 1000)
        page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
        # Wait for Cloudflare challenge + page render
        page.wait_for_timeout(15000)

        title = page.title() or None
        # Clean up " | Claude" suffix
        if title:
            title = re.sub(r"\s*\|\s*Claude\s*$", "", title).strip() or None
        # Skip Cloudflare challenge page title
        if title and "just a moment" in title.lower():
            title = None

        messages: List[Dict[str, Any]] = []

        # User messages: div with class containing "font-user-message"
        user_els = page.query_selector_all('[class*="font-user-message"]')
        # AI responses: top-level div with class containing "font-claude-response"
        ai_els = page.query_selector_all('[class*="font-claude-response"]:not(p)')

        # Build ordered message list by interleaving user/assistant
        # They appear in DOM order, alternating
        u_idx, a_idx = 0, 0
        # Collect all with positions for proper ordering
        ordered = []
        for el in user_els:
            text = _text_normalize(el.inner_text() or "")
            if text:
                bbox = el.bounding_box()
                y = bbox["y"] if bbox else u_idx * 10000
                ordered.append((y, "user", text))
                u_idx += 1
        for el in ai_els:
            text = _text_normalize(el.inner_text() or "")
            if text:
                bbox = el.bounding_box()
                y = bbox["y"] if bbox else a_idx * 10000 + 5000
                ordered.append((y, "assistant", text))
                a_idx += 1

        ordered.sort(key=lambda x: x[0])
        for _, role, text in ordered:
            messages.append({"role": role, "content": text})

        browser.close()

    return title, messages


# --- Dispatch ---

def _fetch_provider(provider: str, url: str, timeout: int) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    if provider == "chatgpt":
        return _fetch_chatgpt(url, timeout)
    if provider == "gemini":
        return _fetch_gemini(url, timeout)
    if provider == "claude":
        return _fetch_claude(url, timeout)
    raise ValueError(f"Unknown provider: {provider}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch chatbot share pages and extract messages.")
    parser.add_argument("urls", nargs="+", help="Share URLs to fetch")
    parser.add_argument("--out", default="shared_chats.json", help="Output JSON path")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout (seconds)")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    results: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    for url in args.urls:
        fetch_url = url
        provider = _guess_provider(url)
        if provider == "unknown":
            fetch_url = _resolve_url(url)
            provider = _guess_provider(fetch_url)
            if fetch_url != url:
                print(f"Resolved: {url} -> {fetch_url}")
        print(f"Fetching [{provider}]: {fetch_url} ...")
        try:
            title, messages = _fetch_provider(provider, fetch_url, timeout=args.timeout)
            results.append(
                {
                    "url": url,
                    "provider": provider,
                    "title": title,
                    "messages": messages,
                    "message_count": len(messages),
                }
            )
            print(f"  -> {len(messages)} message(s) extracted")
        except Exception as exc:
            print(f"  -> ERROR: {exc}", file=sys.stderr)
            errors.append({"url": url, "provider": provider, "error": str(exc)})

    payload = {
        "fetched_at": _now_iso(),
        "items": results,
        "errors": errors,
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\nWrote {len(results)} item(s) to {args.out}")
    if errors:
        print(f"{len(errors)} error(s) encountered. See 'errors' in output.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
