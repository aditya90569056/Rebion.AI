"""YouTube Data + Analytics API access using only the standard library.

Authentication is a one-time Google OAuth loopback flow against your own Google
account. Tokens are cached in the data directory. Nothing is ever posted: the
scopes requested here are read-only.
"""
from __future__ import annotations

import json
import secrets
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from .db import data_home

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]
AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
DATA_API = "https://www.googleapis.com/youtube/v3"
ANALYTICS_API = "https://youtubeanalytics.googleapis.com/v2/reports"
REDIRECT_HOST = "localhost"


class YouTubeError(RuntimeError):
    pass


def token_path() -> Path:
    return data_home() / "google_token.json"


def credentials_path() -> Path:
    return data_home() / "google_client.json"


# ----------------------------------------------------------------- config

def load_credentials() -> tuple[str, str]:
    """Returns (client_id, client_secret) from the data dir or env vars."""
    import os

    env_id = os.environ.get("GOOGLE_CLIENT_ID")
    env_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    if env_id and env_secret:
        return env_id, env_secret
    p = credentials_path()
    if p.exists():
        data = json.loads(p.read_text(encoding="utf-8"))
        section = data.get("installed") or data.get("web") or data
        cid = section.get("client_id")
        csec = section.get("client_secret")
        if cid and csec:
            return cid, csec
    raise YouTubeError(
        "No Google API credentials found.\n"
        "  1. Open https://console.cloud.google.com/apis/credentials\n"
        "  2. Create an OAuth client (Desktop app)\n"
        "  3. Enable 'YouTube Data API v3' and 'YouTube Analytics API'\n"
        "  4. Save the JSON as: " + str(p)
    )


# ------------------------------------------------------------------ oauth

def _post_form(url: str, data: dict) -> dict:
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        try:
            msg = json.loads(detail).get("error_description", detail)
        except json.JSONDecodeError:
            msg = detail
        raise YouTubeError(f"Google rejected the request: {msg}") from e
    except urllib.error.URLError as e:
        raise YouTubeError(f"Network error talking to Google: {e.reason}") from e


def _serve_once(port: int, timeout: int = 300) -> tuple[str, str | None]:
    result: dict = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            params = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(self.path).query))
            result["code"] = params.get("code")
            result["error"] = params.get("error")
            body = b"<html><body style='font-family:sans-serif;padding:40px'>" \
                   b"<h2>social-cli</h2><p>Authentication complete. " \
                   b"You can close this tab and return to the terminal.</p></body></html>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args) -> None:
            pass

    httpd = HTTPServer((REDIRECT_HOST, port), Handler)
    httpd.timeout = timeout
    thread = threading.Thread(target=httpd.handle_request, daemon=True)
    thread.start()
    thread.join(timeout)
    httpd.server_close()
    if not result:
        raise YouTubeError("Timed out waiting for the browser redirect.")
    if result.get("error"):
        raise YouTubeError(f"Authorization failed: {result['error']}")
    return result["code"], None


def login(port: int = 8765, open_browser: bool = True) -> dict:
    """Runs the OAuth loopback flow and caches the token."""
    client_id, client_secret = load_credentials()
    state = secrets.token_urlsafe(24)
    auth_url = (
        f"{AUTH_ENDPOINT}?"
        + urllib.parse.urlencode({
            "client_id": client_id,
            "redirect_uri": f"http://{REDIRECT_HOST}:{port}",
            "response_type": "code",
            "scope": " ".join(SCOPES),
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        })
    )
    print(f"Opening your browser to authorise read-only access.\nIf it does not open, go to:\n{auth_url}\n")
    if open_browser:
        try:
            webbrowser.open(auth_url)
        except Exception:
            pass
    code, _ = _serve_once(port)
    token = _post_form(TOKEN_ENDPOINT, {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": f"http://{REDIRECT_HOST}:{port}",
        "grant_type": "authorization_code",
    })
    token["obtained_at"] = datetime.now().isoformat(timespec="seconds")
    token_path().write_text(json.dumps(token, indent=2), encoding="utf-8")
    try:
        token_path().chmod(0o600)
    except OSError:
        pass
    return token


def load_token() -> dict:
    p = token_path()
    if not p.exists():
        raise YouTubeError("Not signed in. Run:  python social.py auth login")
    return json.loads(p.read_text(encoding="utf-8"))


def token_status() -> dict:
    if not token_path().exists():
        return {"signed_in": False}
    token = load_token()
    return {
        "signed_in": True,
        "scopes": token.get("scope", ""),
        "expires": token.get("expires_at"),
        "has_refresh": bool(token.get("refresh_token")),
        "obtained_at": token.get("obtained_at"),
    }


def sign_out() -> bool:
    p = token_path()
    if p.exists():
        p.unlink()
        return True
    return False


def _access_token() -> str:
    token = load_token()
    expires = token.get("expires_at")
    if expires and expires > time.time() + 60:
        return token["access_token"]
    if not token.get("refresh_token"):
        raise YouTubeError("Token expired and has no refresh token. Run:  python social.py auth login")
    client_id, client_secret = load_credentials()
    fresh = _post_form(TOKEN_ENDPOINT, {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": token["refresh_token"],
        "grant_type": "refresh_token",
    })
    token["access_token"] = fresh["access_token"]
    token["expires_at"] = time.time() + fresh.get("expires_in", 3600)
    token.pop("obtained_at", None)
    token["obtained_at"] = datetime.now().isoformat(timespec="seconds")
    token_path().write_text(json.dumps(token, indent=2), encoding="utf-8")
    return token["access_token"]


# ------------------------------------------------------------------- http

def _get(url: str, params: dict) -> dict:
    token = _access_token()
    full = f"{url}?{urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})}"
    req = urllib.request.Request(full, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        try:
            parsed = json.loads(detail)
            msg = parsed.get("error", {}).get("message") or parsed.get("error_description") or detail
        except json.JSONDecodeError:
            msg = detail
        if e.code == 403:
            msg = f"{msg} (check the API is enabled in your Google Cloud project and the scope is granted)"
        raise YouTubeError(msg) from e
    except urllib.error.URLError as e:
        raise YouTubeError(f"Network error: {e.reason}") from e


# ------------------------------------------------------------------- api

def channel_info() -> dict:
    data = _get(f"{DATA_API}/channels", {"part": "snippet,statistics", "mine": "true"})
    items = data.get("items") or []
    if not items:
        raise YouTubeError("No channel found for the signed-in Google account.")
    item = items[0]
    return {
        "id": item["id"],
        "title": item["snippet"]["title"],
        "handle": item["snippet"].get("customUrl", ""),
        "subscribers": int(item.get("statistics", {}).get("subscriberCount", 0)),
        "views": int(item.get("statistics", {}).get("viewCount", 0)),
        "videos": int(item.get("statistics", {}).get("videoCount", 0)),
    }


def recent_videos(max_results: int = 50) -> list[dict]:
    """Latest uploads on the signed-in channel, newest first."""
    data = _get(f"{DATA_API}/search", {
        "part": "snippet",
        "forMine": "true",
        "type": "video",
        "order": "date",
        "maxResults": min(int(max_results), 50),
    })
    out = []
    for item in data.get("items", []):
        sn = item["snippet"]
        out.append({
            "video_id": item["id"]["videoId"],
            "title": sn.get("title", ""),
            "published_at": sn.get("publishedAt", "")[:10],
        })
    return out


def video_stats(video_id: str) -> dict:
    data = _get(f"{DATA_API}/videos", {
        "part": "statistics,snippet,contentDetails",
        "id": video_id,
    })
    items = data.get("items") or []
    if not items:
        return {}
    item = items[0]
    st = item.get("statistics", {})
    return {
        "video_id": video_id,
        "title": item["snippet"].get("title", ""),
        "views": int(st.get("viewCount", 0)),
        "likes": int(st.get("likeCount", 0)),
        "comments": int(st.get("commentCount", 0)),
        "duration": item.get("contentDetails", {}).get("duration", ""),
    }


ANALYTICS_METRICS = [
    "views",
    "estimatedMinutesWatched",
    "averageViewDuration",
    "averageViewPercentage",
    "subscribersGained",
    "subscribersLost",
    "likes",
    "shares",
    "comments",
    "impressions",
    "impressionsClickThroughRate",
]


def analytics_by_video(start: str, end: str, limit: int = 200) -> dict[str, dict]:
    """Returns {video_id: {metric: value}} for the signed-in channel."""
    data = _get(ANALYTICS_API, {
        "ids": "channel==MINE",
        "startDate": start,
        "endDate": end,
        "metrics": ",".join(ANALYTICS_METRICS),
        "dimensions": "video",
        "sort": "-views",
        "maxResults": limit,
    })
    headers = data.get("columnHeaders", [])
    names = [h["name"] for h in headers]
    out: dict[str, dict] = {}
    for row in data.get("rows", []):
        rec = dict(zip(names, row))
        vid = rec.get("video") or rec.get("videoId")
        if not vid:
            continue
        out[vid] = {k: v for k, v in rec.items() if k not in ("video",)}
    return out


def audience_demographics(start: str, end: str) -> list[dict]:
    """Age/gender split, useful for spotting a mismatched audience."""
    data = _get(ANALYTICS_API, {
        "ids": "channel==MINE",
        "startDate": start,
        "endDate": end,
        "metrics": "views,estimatedMinutesWatched",
        "dimensions": "ageGroup,gender",
        "sort": "-views",
    })
    headers = [h["name"] for h in data.get("columnHeaders", [])]
    return [dict(zip(headers, r)) for r in data.get("rows", [])]


def default_window(days: int = 28) -> tuple[str, str]:
    end = datetime.now().date()
    start = end - timedelta(days=days)
    return start.isoformat(), end.isoformat()
