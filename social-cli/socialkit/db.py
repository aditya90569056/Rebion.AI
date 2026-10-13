"""SQLite storage layer for social-cli."""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DEFAULT_HOME = Path(__file__).resolve().parent.parent / "data"
DB_NAME = "social.db"

CHANNELS = {
    "yt": {"platform": "youtube", "label": "YouTube Shorts"},
    "ig1": {"platform": "instagram", "label": "Instagram 1"},
    "ig2": {"platform": "instagram", "label": "Instagram 2"},
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    hook        TEXT NOT NULL,
    channel     TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'idea',
    content     TEXT DEFAULT '',
    caption     TEXT DEFAULT '',
    title       TEXT DEFAULT '',
    tags        TEXT DEFAULT '',
    link        TEXT DEFAULT '',
    publish_at  TEXT,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS metrics (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id      INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    views        INTEGER NOT NULL DEFAULT 0,
    likes        INTEGER NOT NULL DEFAULT 0,
    comments     INTEGER NOT NULL DEFAULT 0,
    shares       INTEGER NOT NULL DEFAULT 0,
    reach        INTEGER NOT NULL DEFAULT 0,
    captured_at  TEXT NOT NULL,
    UNIQUE(post_id, captured_at)
);

CREATE TABLE IF NOT EXISTS hashtags (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    tag       TEXT NOT NULL UNIQUE,
    tag_group TEXT NOT NULL DEFAULT 'general',
    uses      INTEGER NOT NULL DEFAULT 0,
    last_used TEXT
);

CREATE TABLE IF NOT EXISTS links (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id    INTEGER REFERENCES posts(id) ON DELETE SET NULL,
    base_url   TEXT NOT NULL,
    full_url   TEXT NOT NULL,
    source     TEXT NOT NULL,
    medium     TEXT NOT NULL,
    campaign   TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS yt_videos (
    video_id    TEXT PRIMARY KEY,
    post_id     INTEGER REFERENCES posts(id) ON DELETE SET NULL,
    title       TEXT DEFAULT '',
    published_at TEXT,
    last_synced  TEXT,
    created_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_posts_channel  ON posts(channel);
CREATE INDEX IF NOT EXISTS idx_posts_status   ON posts(status);
CREATE INDEX IF NOT EXISTS idx_posts_publish  ON posts(publish_at);
CREATE INDEX IF NOT EXISTS idx_metrics_post   ON metrics(post_id);
CREATE INDEX IF NOT EXISTS idx_tags_group    ON hashtags(tag_group);
"""

# Columns added after v1. Applied on open so existing databases keep working.
MIGRATIONS = (
    ("posts", "video_id", "TEXT"),
    ("metrics", "watch_minutes", "REAL"),
    ("metrics", "impressions", "INTEGER"),
    ("metrics", "ctr", "REAL"),
    ("metrics", "avg_view_percent", "REAL"),
    ("metrics", "subs_gained", "INTEGER"),
    ("metrics", "subs_lost", "INTEGER"),
    ("metrics", "source", "TEXT"),
)


def data_home() -> Path:
    env = os.environ.get("SOCIAL_CLI_HOME")
    return Path(env).expanduser().resolve() if env else DEFAULT_HOME


def db_path() -> Path:
    return data_home() / DB_NAME


def connect() -> sqlite3.Connection:
    home = data_home()
    home.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _migrate(conn: sqlite3.Connection) -> None:
    for table, column, coltype in MIGRATIONS:
        cols = {r["name"] for r in conn.execute(f"PRAGMA table_info({table})")}
        if column not in cols:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")


def init() -> Path:
    conn = connect()
    try:
        conn.executescript(SCHEMA)
        _migrate(conn)
        conn.commit()
    finally:
        conn.close()
    return db_path()


def ensure() -> None:
    init()
