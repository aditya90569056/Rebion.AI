"""Repository helpers: posts, metrics, tags, links."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta

from .db import CHANNELS, connect, ensure

VALID_STATUS = ("idea", "draft", "scheduled", "published", "archived")
VALID_CHANNELS = tuple(CHANNELS)


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


# ---------------------------------------------------------------- posts

def add_post(
    hook: str,
    channel: str,
    content: str = "",
    caption: str = "",
    title: str = "",
    tags: str = "",
    link: str = "",
    publish_at: str | None = None,
    status: str = "idea",
) -> int:
    ensure()
    if channel not in VALID_CHANNELS:
        raise ValueError(f"unknown channel '{channel}' (use: {', '.join(VALID_CHANNELS)})")
    if status not in VALID_STATUS:
        raise ValueError(f"unknown status '{status}' (use: {', '.join(VALID_STATUS)})")
    ts = now()
    conn = connect()
    try:
        cur = conn.execute(
            """INSERT INTO posts
               (hook, channel, status, content, caption, title, tags, link,
                publish_at, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (hook, channel, status, content, caption, title, tags, link, publish_at, ts, ts),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def get_post(post_id: int) -> sqlite3.Row | None:
    conn = connect()
    try:
        return conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    finally:
        conn.close()


def list_posts(
    channel: str | None = None,
    status: str | None = None,
    limit: int = 50,
) -> list[sqlite3.Row]:
    ensure()
    q = "SELECT * FROM posts WHERE 1=1"
    args: list = []
    if channel:
        q += " AND channel = ?"
        args.append(channel)
    if status:
        q += " AND status = ?"
        args.append(status)
    q += " ORDER BY COALESCE(publish_at, created_at) DESC, id DESC LIMIT ?"
    args.append(limit)
    conn = connect()
    try:
        return list(conn.execute(q, args))
    finally:
        conn.close()


def upcoming(days: int = 7) -> list[sqlite3.Row]:
    ensure()
    start = today()
    end = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    conn = connect()
    try:
        return list(
            conn.execute(
                """SELECT * FROM posts
                   WHERE publish_at IS NOT NULL
                     AND status != 'published'
                     AND date(publish_at) BETWEEN ? AND ?
                   ORDER BY publish_at""",
                (start, end),
            )
        )
    finally:
        conn.close()


def overdue() -> list[sqlite3.Row]:
    ensure()
    conn = connect()
    try:
        return list(
            conn.execute(
                """SELECT * FROM posts
                   WHERE publish_at IS NOT NULL
                     AND status NOT IN ('published','archived')
                     AND date(publish_at) < ?
                   ORDER BY publish_at""",
                (today(),),
            )
        )
    finally:
        conn.close()


def update_post(post_id: int, **fields) -> int:
    ensure()
    allowed = {"hook", "status", "content", "caption", "title", "tags", "link", "publish_at", "channel", "video_id"}
    bad = set(fields) - allowed
    if bad:
        raise ValueError(f"cannot update: {', '.join(sorted(bad))}")
    if "status" in fields and fields["status"] not in VALID_STATUS:
        raise ValueError(f"unknown status '{fields['status']}'")
    if "channel" in fields and fields["channel"] not in VALID_CHANNELS:
        raise ValueError(f"unknown channel '{fields['channel']}'")
    if not fields:
        return 0
    fields["updated_at"] = now()
    sets = ", ".join(f"{k} = ?" for k in fields)
    conn = connect()
    try:
        cur = conn.execute(
            f"UPDATE posts SET {sets} WHERE id = ?", (*fields.values(), post_id)
        )
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


def delete_post(post_id: int) -> int:
    conn = connect()
    try:
        cur = conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


# ------------------------------------------------------- yt video links

def link_video(video_id: str, post_id: int | None = None, title: str = "",
               published_at: str | None = None) -> None:
    ensure()
    if post_id is not None and get_post(post_id) is None:
        raise ValueError(f"post {post_id} does not exist")
    conn = connect()
    try:
        conn.execute(
            """INSERT INTO yt_videos (video_id, post_id, title, published_at, created_at)
               VALUES (?,?,?,?,?)
               ON CONFLICT(video_id) DO UPDATE SET
                 post_id=COALESCE(excluded.post_id, yt_videos.post_id),
                 title=COALESCE(NULLIF(excluded.title,''), yt_videos.title),
                 published_at=COALESCE(excluded.published_at, yt_videos.published_at)""",
            (video_id, post_id, title, published_at, now()),
        )
        if post_id is not None:
            conn.execute("UPDATE posts SET video_id = ?, updated_at = ? WHERE id = ?",
                         (video_id, now(), post_id))
        conn.commit()
    finally:
        conn.close()


def video_map() -> dict[str, int]:
    conn = connect()
    try:
        return {
            r["video_id"]: r["post_id"]
            for r in conn.execute("SELECT video_id, post_id FROM yt_videos WHERE post_id IS NOT NULL")
        }
    finally:
        conn.close()


def posts_with_video() -> list[sqlite3.Row]:
    ensure()
    conn = connect()
    try:
        return list(conn.execute(
            "SELECT * FROM posts WHERE video_id IS NOT NULL AND video_id != '' ORDER BY id"
        ))
    finally:
        conn.close()


def touch_sync(video_ids: list[str]) -> None:
    if not video_ids:
        return
    ts = now()
    conn = connect()
    try:
        conn.executemany(
            "UPDATE yt_videos SET last_synced = ? WHERE video_id = ?",
            [(ts, v) for v in video_ids],
        )
        conn.commit()
    finally:
        conn.close()


# -------------------------------------------------------------- metrics
def add_metrics(
    post_id: int,
    views: int = 0,
    likes: int = 0,
    comments: int = 0,
    shares: int = 0,
    reach: int = 0,
    captured_at: str | None = None,
) -> int:
    ensure()
    if get_post(post_id) is None:
        raise ValueError(f"post {post_id} does not exist")
    conn = connect()
    try:
        conn.execute(
            """INSERT INTO metrics
               (post_id, views, likes, comments, shares, reach, captured_at, source)
               VALUES (?,?,?,?,?,?,?,'manual')
               ON CONFLICT(post_id, captured_at) DO UPDATE SET
                 views=excluded.views, likes=excluded.likes,
                 comments=excluded.comments, shares=excluded.shares,
                 reach=excluded.reach""",
            (post_id, views, likes, comments, shares, reach, captured_at or today()),
        )
        conn.commit()
    finally:
        conn.close()
    return post_id


def record_youtube_metrics(
    post_id: int,
    views: int = 0,
    likes: int = 0,
    comments: int = 0,
    shares: int = 0,
    watch_minutes: float = 0.0,
    impressions: int = 0,
    ctr: float = 0.0,
    avg_view_percent: float = 0.0,
    subs_gained: int = 0,
    subs_lost: int = 0,
    captured_at: str | None = None,
) -> int:
    ensure()
    if get_post(post_id) is None:
        raise ValueError(f"post {post_id} does not exist")
    conn = connect()
    try:
        conn.execute(
            """INSERT INTO metrics
               (post_id, views, likes, comments, shares, reach, captured_at, source,
                watch_minutes, impressions, ctr, avg_view_percent,
                subs_gained, subs_lost)
               VALUES (?,?,?,?,?,0,?,'youtube',?,?,?,?,?,?)
               ON CONFLICT(post_id, captured_at) DO UPDATE SET
                 views=excluded.views, likes=excluded.likes,
                 comments=excluded.comments, shares=excluded.shares,
                 watch_minutes=excluded.watch_minutes,
                 impressions=excluded.impressions, ctr=excluded.ctr,
                 avg_view_percent=excluded.avg_view_percent,
                 subs_gained=excluded.subs_gained, subs_lost=excluded.subs_lost,
                 source='youtube'""",
            (post_id, views, likes, comments, shares, captured_at or today(),
             watch_minutes, impressions, ctr, avg_view_percent, subs_gained, subs_lost),
        )
        conn.commit()
    finally:
        conn.close()
    return post_id


def latest_metrics() -> dict[int, sqlite3.Row]:
    conn = connect()
    try:
        return {
            r["post_id"]: r
            for r in conn.execute(
                """SELECT m.* FROM metrics m
                   JOIN (SELECT post_id, MAX(captured_at) AS mx
                         FROM metrics GROUP BY post_id) t
                     ON m.post_id = t.post_id AND m.captured_at = t.mx"""
            )
        }
    finally:
        conn.close()


# ------------------------------------------------------------ hashtags

def add_tags(tags: str, tag_group: str = "general") -> int:
    ensure()
    n = 0
    conn = connect()
    try:
        for raw in tags.replace(",", " ").split():
            tag = raw if raw.startswith("#") else f"#{raw}"
            conn.execute(
                """INSERT INTO hashtags (tag, tag_group) VALUES (?, ?)
                   ON CONFLICT(tag) DO UPDATE SET tag_group = excluded.tag_group""",
                (tag, tag_group),
            )
            n += 1
        conn.commit()
    finally:
        conn.close()
    return n


def list_tags(tag_group: str | None = None) -> list[sqlite3.Row]:
    ensure()
    q = "SELECT * FROM hashtags"
    args: list = []
    if tag_group:
        q += " WHERE tag_group = ?"
        args.append(tag_group)
    q += " ORDER BY tag_group, uses, tag"
    conn = connect()
    try:
        return list(conn.execute(q, args))
    finally:
        conn.close()


def pick_tags(count: int, tag_group: str | None = None, seed: str = "") -> list[str]:
    """Rotate least-used tags so the same set never repeats back to back."""
    rows = list_tags(tag_group)
    if not rows:
        return []
    salt = seed or today()
    rows.sort(key=lambda r: (r["uses"], r["last_used"] or "", r["tag"]))
    chosen = rows[:count]
    ts = now()
    conn = connect()
    try:
        for r in chosen:
            conn.execute(
                "UPDATE hashtags SET uses = uses + 1, last_used = ? WHERE id = ?",
                (ts, r["id"]),
            )
        conn.commit()
    finally:
        conn.close()
    return [r["tag"] for r in chosen]


def bump_tags(tags: str) -> None:
    add_tags(tags)
    ts = now()
    conn = connect()
    try:
        for raw in tags.replace(",", " ").split():
            tag = raw if raw.startswith("#") else f"#{raw}"
            conn.execute(
                "UPDATE hashtags SET uses = uses + 1, last_used = ? WHERE tag = ?",
                (ts, tag),
            )
        conn.commit()
    finally:
        conn.close()


# --------------------------------------------------------------- links

def save_link(
    base_url: str,
    full_url: str,
    source: str,
    medium: str,
    campaign: str,
    post_id: int | None = None,
) -> int:
    ensure()
    conn = connect()
    try:
        cur = conn.execute(
            """INSERT INTO links
               (post_id, base_url, full_url, source, medium, campaign, created_at)
               VALUES (?,?,?,?,?,?,?)""",
            (post_id, base_url, full_url, source, medium, campaign, now()),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def list_links(limit: int = 30) -> list[sqlite3.Row]:
    conn = connect()
    try:
        return list(
            conn.execute("SELECT * FROM links ORDER BY id DESC LIMIT ?", (limit,))
        )
    finally:
        conn.close()


# ------------------------------------------------------------- summary

def counts_by_channel() -> dict[str, dict[str, int]]:
    conn = connect()
    try:
        out: dict[str, dict[str, int]] = {}
        for r in conn.execute(
            "SELECT channel, status, COUNT(*) AS n FROM posts GROUP BY channel, status"
        ):
            out.setdefault(r["channel"], {})[r["status"]] = r["n"]
        return out
    finally:
        conn.close()
