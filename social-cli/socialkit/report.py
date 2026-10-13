"""Performance aggregation and reporting."""
from __future__ import annotations

from datetime import datetime, timedelta

from . import repo
from .db import CHANNELS, connect


def _engagement(m) -> dict:
    views = m["views"] or 0
    interactions = (m["likes"] or 0) + (m["comments"] or 0) + (m["shares"] or 0)
    return {
        "views": views,
        "likes": m["likes"] or 0,
        "comments": m["comments"] or 0,
        "shares": m["shares"] or 0,
        "reach": m["reach"] or 0,
        "interactions": interactions,
        "engagement_rate": round(interactions / views * 100, 2) if views else 0.0,
        "watch_minutes": round(m["watch_minutes"] or 0, 1),
        "impressions": m["impressions"] or 0,
        "ctr": round((m["ctr"] or 0) * 100, 2),
        "avg_view_percent": round((m["avg_view_percent"] or 0) * 100, 1),
        "subs_gained": m["subs_gained"] or 0,
        "subs_lost": m["subs_lost"] or 0,
    }


def top_posts(metric: str = "views", limit: int = 10) -> list[dict]:
    latest = repo.latest_metrics()
    rows = []
    for post_id, m in latest.items():
        p = repo.get_post(post_id)
        if not p:
            continue
        e = _engagement(m)
        rows.append({
            "id": post_id,
            "hook": p["hook"],
            "channel": p["channel"],
            "platform": CHANNELS[p["channel"]]["platform"],
            "publish_at": p["publish_at"],
            **{k: e[k] for k in ("views", "likes", "comments", "shares",
                                  "interactions", "engagement_rate",
                                  "watch_minutes", "impressions", "ctr",
                                  "avg_view_percent", "subs_gained", "subs_lost")},
        })
    rows.sort(key=lambda r: r.get(metric, 0) or 0, reverse=True)
    return rows[:limit]


def summary() -> dict:
    latest = repo.latest_metrics()
    per_channel: dict[str, dict] = {}
    for post_id, m in latest.items():
        p = repo.get_post(post_id)
        if not p:
            continue
        ch = p["channel"]
        slot = per_channel.setdefault(ch, {
            "views": 0, "likes": 0, "comments": 0, "shares": 0, "posts": 0,
            "watch_minutes": 0.0, "impressions": 0, "subs_gained": 0, "subs_lost": 0,
        })
        e = _engagement(m)
        for k in ("views", "likes", "comments", "shares", "watch_minutes",
                  "impressions", "subs_gained", "subs_lost"):
            slot[k] += e[k]
        slot["posts"] += 1
    for ch, slot in per_channel.items():
        inter = slot["likes"] + slot["comments"] + slot["shares"]
        slot["engagement_rate"] = round(inter / slot["views"] * 100, 2) if slot["views"] else 0.0
        slot["avg_views"] = round(slot["views"] / slot["posts"]) if slot["posts"] else 0
        slot["ctr"] = 0.0
        slot["avg_view_percent"] = 0.0
    return per_channel


def weekly(days: int = 7) -> dict:
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    conn = connect()
    try:
        published = list(
            conn.execute(
                "SELECT * FROM posts WHERE status = 'published' AND date(publish_at) >= ?",
                (cutoff,),
            )
        )
    finally:
        conn.close()

    latest = repo.latest_metrics()
    rows = []
    for p in published:
        m = latest.get(p["id"])
        if not m:
            continue
        rows.append({"id": p["id"], "hook": p["hook"], "channel": p["channel"],
                     "publish_at": p["publish_at"], **_engagement(m)})
    rows.sort(key=lambda r: r["views"], reverse=True)

    planned = repo.list_posts(status="scheduled", limit=200)
    return {
        "days": days,
        "published_count": len(rows),
        "rows": rows,
        "scheduled_upcoming": [
            {"id": p["id"], "hook": p["hook"], "channel": p["channel"],
             "publish_at": p["publish_at"]}
            for p in planned
            if p["publish_at"]
        ],
        "summary": summary(),
    }
