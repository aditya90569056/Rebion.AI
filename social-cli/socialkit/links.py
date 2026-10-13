"""UTM link building and per-channel share copy."""
from __future__ import annotations

import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

SOURCES = {
    "yt": "youtube",
    "ig1": "instagram",
    "ig2": "instagram",
}
MEDIUMS = {
    "yt": "short",
    "ig1": "social",
    "ig2": "social",
}
PLATFORM_LABEL = {
    "yt": "YouTube Shorts",
    "ig1": "Instagram 1",
    "ig2": "Instagram 2",
}


def slugify(text: str, max_len: int = 50) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s[:max_len].strip("-")


def build_utm(url: str, source: str, medium: str, campaign: str, term: str = "",
              content: str = "") -> str:
    if not url or not url.strip():
        raise ValueError("a base URL is required")
    parts = urlsplit(url.strip())
    if not parts.scheme or not parts.netloc:
        raise ValueError(f"'{url}' is not a full URL (include https://)")
    existing = dict(parse_qsl(parts.query, keep_blank_values=True))
    existing["utm_source"] = source
    existing["utm_medium"] = medium
    existing["utm_campaign"] = campaign
    if term:
        existing["utm_term"] = term
    if content:
        existing["utm_content"] = content
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(existing), parts.fragment))


def source_for(channel: str) -> str:
    return SOURCES.get(channel, channel)


def medium_for(channel: str) -> str:
    return MEDIUMS.get(channel, "social")


def short_caption(hook: str, tags: str = "", link: str = "", max_len: int = 2200) -> str:
    parts = [hook.strip()]
    if tags.strip():
        parts.append(tags.strip())
    if link.strip():
        parts.append(f"link in bio: {link.strip()}")
    out = "\n\n".join(p for p in parts if p)
    return out[:max_len]


def yt_description(hook: str, tags: str = "", link: str = "", extra: str = "") -> str:
    blocks = [hook.strip()]
    if extra.strip():
        blocks.append(extra.strip())
    if tags.strip():
        blocks.append(tags.strip())
    if link.strip():
        blocks.append(f"Full video: {link.strip()}")
    return "\n\n".join(b for b in blocks if b)
