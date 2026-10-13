"""Match calendar posts to YouTube videos and pull analytics in."""
from __future__ import annotations

import re
from datetime import datetime

from . import repo, youtube

VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
URL_PATTERNS = [
    re.compile(r"(?:youtube\.com/watch\?(?:.*&)?v=)([A-Za-z0-9_-]{11})"),
    re.compile(r"(?:youtu\.be/)([A-Za-z0-9_-]{11})"),
    re.compile(r"(?:youtube\.com/shorts/)([A-Za-z0-9_-]{11})"),
    re.compile(r"(?:youtube\.com/embed/)([A-Za-z0-9_-]{11})"),
]


def parse_video_id(text: str) -> str | None:
    """Accepts a bare id or any common YouTube URL form."""
    t = (text or "").strip()
    if not t:
        return None
    if VIDEO_ID_RE.match(t):
        return t
    for pat in URL_PATTERNS:
        m = pat.search(t)
        if m:
            return m.group(1)
    return None


def _post_date(row) -> str:
    if row["publish_at"]:
        return str(row["publish_at"])[:10]
    return str(row["created_at"])[:10]


def match_posts_to_videos(videos: list[dict], tolerance_days: int = 2) -> dict[int, dict]:
    """Pairs a post to a video by publish date, then by title similarity.

    Only yt-channel posts are considered. Exact video_id on the post always wins.
    """
    pairs: dict[int, dict] = {}
    used: set[str] = set()
    by_id = {v["video_id"]: v for v in videos}
    for row in repo.posts_with_video():
        vid = row["video_id"]
        if vid in by_id:
            pairs[row["id"]] = by_id[vid]
            used.add(vid)

    remaining = [v for v in videos if v["video_id"] not in used]
    yt_posts = [p for p in repo.list_posts(channel="yt", limit=500)
                if p["id"] not in pairs]
    yt_posts.sort(key=lambda p: _post_date(p))

    for post in yt_posts:
        p_date = _post_date(post)
        p_title = (post["title"] or post["hook"] or "").lower()
        best = None
        for v in remaining:
            score = 0.0
            if v.get("published_at") == p_date:
                score += 10
            else:
                try:
                    gap = abs((datetime.fromisoformat(v["published_at"])
                               - datetime.fromisoformat(p_date)).days)
                except (ValueError, TypeError):
                    gap = 99
                if gap > tolerance_days:
                    continue
                score += max(0, 5 - gap)
            vt = (v.get("title") or "").lower()
            shared = len(set(p_title.split()) & set(vt.split()))
            score += shared * 0.5
            if score > 0 and (best is None or score > best[0]):
                best = (score, v)
        if best and best[0] >= 5:
            pairs[post["id"]] = best[1]
            remaining.remove(best[1])

    return pairs


def sync(days: int = 28, dry_run: bool = False) -> dict:
    start, end = youtube.default_window(days)
    videos = youtube.recent_videos(max_results=50)
    if not videos:
        return {"videos": 0, "matched": 0, "written": 0, "rows": [],
                "window": (start, end), "channel": {}}

    pairs = match_posts_to_videos(videos)
    stats = youtube.analytics_by_video(start, end)
    written = 0
    rows = []
    for post_id, video in sorted(pairs.items()):
        if not dry_run:
            repo.link_video(video["video_id"], post_id, video.get("title", ""),
                            video.get("published_at"))
        a = stats.get(video["video_id"], {})
        # Analytics returns ratios for these two; the database stores them raw
        # and every report converts on the way out.
        raw_ctr = float(a.get("impressionsClickThroughRate", 0) or 0)
        raw_avp = float(a.get("averageViewPercentage", 0) or 0)
        row = {
            "post_id": post_id,
            "video_id": video["video_id"],
            "title": video.get("title", ""),
            "views": int(a.get("views", 0) or 0),
            "likes": int(a.get("likes", 0) or 0),
            "comments": int(a.get("comments", 0) or 0),
            "shares": int(a.get("shares", 0) or 0),
            "watch_minutes": round(float(a.get("estimatedMinutesWatched", 0) or 0), 1),
            "impressions": int(a.get("impressions", 0) or 0),
            "ctr": round(raw_ctr * 100, 2),
            "avg_view_percent": round(raw_avp * 100, 1),
            "subs_gained": int(a.get("subscribersGained", 0) or 0),
            "subs_lost": int(a.get("subscribersLost", 0) or 0),
        }
        rows.append(row)
        if not dry_run and (row["views"] or row["impressions"]):
            repo.record_youtube_metrics(
                post_id,
                views=row["views"], likes=row["likes"], comments=row["comments"],
                shares=row["shares"], watch_minutes=row["watch_minutes"],
                impressions=row["impressions"], ctr=raw_ctr,
                avg_view_percent=raw_avp,
                subs_gained=row["subs_gained"], subs_lost=row["subs_lost"],
            )
            written += 1
    if not dry_run:
        repo.touch_sync([v["video_id"] for v in videos])

    rows.sort(key=lambda r: r["views"], reverse=True)
    return {
        "videos": len(videos),
        "matched": len(pairs),
        "written": written,
        "rows": rows,
        "window": (start, end),
        "channel": youtube.channel_info(),
    }
