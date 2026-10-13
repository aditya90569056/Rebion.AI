"""social - CLI for a YouTube Shorts channel and two Instagram accounts.

Planning and optimization only: it never posts, likes or comments on any
account. With an optional read-only Google sign-in it pulls your own YouTube
analytics so numbers are never typed in by hand.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime

from socialkit import brief, links, report, repo, score, sync, youtube
from socialkit.db import CHANNELS, db_path, init


def out(*a):
    print(*a)


def err(*a):
    print(*a, file=sys.stderr)


def grade_bar(pct: int, width: int = 24) -> str:
    filled = round(width * pct / 100)
    return f"[{'#' * filled}{'-' * (width - filled)}] {pct:3d}%"


def print_scores(block: dict) -> None:
    out(f"  {block['kind'].upper()}  {block['grade']}  {grade_bar(block['percent'])}")
    for c in block["checks"]:
        passed = c["points"] >= c["max"]
        mark = "OK " if passed else "   "
        out(f"    {mark}{c['points']:>5.1f}/{c['max']:<5.1f} {c['name']}")
        if c["tip"] and not passed:
            out(f"          -> {c['tip']}")


# ------------------------------------------------------------- calendar

def cmd_init(a):
    p = init()
    out(f"Initialised database: {p}")
    out("Channels: " + ", ".join(f"{k} ({v['label']})" for k, v in CHANNELS.items()))
    out("\nNext:  python social.py add \"your hook\" --channel yt --date 2026-10-01")


def cmd_add(a):
    pid = repo.add_post(
        hook=a.hook, channel=a.channel, content=a.content or "", caption=a.caption or "",
        title=a.title or "", tags=a.tags or "", link=a.link or "",
        publish_at=a.date, status=a.status,
    )
    if a.tags:
        repo.add_tags(a.tags)
    out(f"Created post #{pid} on {a.channel}")
    if a.date:
        out(f"  Scheduled: {a.date}")
    s = score.score_hook(a.hook)
    out(f"  Hook score: {s['grade']} ({s['percent']}%)")
    for c in s["checks"]:
        if c["tip"] and c["points"] < c["max"]:
            out(f"    - {c['name']}: {c['tip']}")
    out(f"\nRun:  python social.py brief {pid}")


def cmd_list(a):
    rows = repo.list_posts(channel=a.channel, status=a.status, limit=a.limit)
    if not rows:
        out("No posts match. Add one with:  python social.py add \"hook\" --channel yt")
        return
    out(f"{'ID':>3}  {'CH':<4} {'STATUS':<10} {'PUBLISH':<12} {'VID':<12} HOOK")
    out("-" * 92)
    for r in rows:
        hook = (r["hook"] or "")[:34]
        out(f"{r['id']:>3}  {r['channel']:<4} {r['status']:<10} "
            f"{(r['publish_at'] or '-'):<12} {(r['video_id'] or '-'):<12} {hook}")


def cmd_show(a):
    r = repo.get_post(a.id)
    if not r:
        err(f"Post {a.id} not found.")
        return 1
    out(f"Post #{r['id']}  [{r['channel']}]  {r['status']}")
    out(f"Hook      : {r['hook']}")
    if r["title"]:
        out(f"Title     : {r['title']}")
    if r["publish_at"]:
        out(f"Publish   : {r['publish_at']}")
    if r["video_id"]:
        out(f"Video ID  : {r['video_id']}")
    if r["caption"]:
        out(f"Caption   : {r['caption']}")
    if r["content"]:
        out(f"Content   : {r['content']}")
    if r["tags"]:
        out(f"Tags      : {r['tags']}")
    if r["link"]:
        out(f"Link      : {r['link']}")


def cmd_update(a):
    fields = {}
    for src, dst in (("hook", "hook"), ("status", "status"), ("content", "content"),
                     ("caption", "caption"), ("title", "title"), ("tags", "tags"),
                     ("link", "link"), ("channel", "channel"), ("date", "publish_at")):
        v = getattr(a, src, None)
        if v is not None:
            fields[dst] = v
    if not fields:
        err("Nothing to update.")
        return 1
    try:
        n = repo.update_post(a.id, **fields)
    except ValueError as e:
        err(str(e))
        return 1
    if n == 0:
        err(f"Post {a.id} not found.")
        return 1
    if fields.get("tags"):
        repo.add_tags(fields["tags"])
    out(f"Updated post #{a.id}: {', '.join(fields)}")


def cmd_delete(a):
    n = repo.delete_post(a.id)
    if n == 0:
        err(f"Post {a.id} not found.")
        return 1
    out(f"Deleted post #{a.id}")


def cmd_schedule(a):
    date = a.date or datetime.now().strftime("%Y-%m-%d %H:%M")
    try:
        repo.update_post(a.id, publish_at=date, status=a.status or "scheduled")
    except ValueError as e:
        err(str(e))
        return 1
    out(f"Post #{a.id} scheduled for {date}")


def cmd_upcoming(a):
    rows = repo.upcoming(a.days)
    if not rows:
        out(f"Nothing scheduled in the next {a.days} days.")
        return
    out(f"Next {a.days} days")
    out("-" * 70)
    for r in rows:
        out(f"{r['publish_at']:<17} [{r['channel']}] #{r['id']}  {r['hook'][:36]}")


def cmd_overdue(a):
    rows = repo.overdue()
    if not rows:
        out("Nothing overdue.")
        return
    out("Overdue (past publish date, not published)")
    out("-" * 70)
    for r in rows:
        out(f"{r['publish_at']:<17} [{r['channel']}] #{r['id']}  {r['hook'][:36]}")


def cmd_brief(a):
    r = repo.get_post(a.id)
    if not r:
        err(f"Post {a.id} not found.")
        return 1
    b = brief.build(r, base_url=a.url or "", campaign=a.campaign or "")
    out("=" * 70)
    out(f"PUBLISHING BRIEF  #{b['id']}  {b['channel_label']}  [{b['status']}]")
    if b["publish_at"]:
        out(f"Scheduled: {b['publish_at']}")
    out("=" * 70)
    for k, v in b["assets"].items():
        out(f"\n--- {k} ---")
        out(v or "(empty)")
    if b.get("cross_post"):
        out("\n--- Cross-post checklist ---")
        for c in b["cross_post"]:
            out(f"  {c['label']}: {c['note']}")
    out("\n--- Pre-publish checklist ---")
    for item in b["checklist"]:
        out(f"  [ ] {item}")
    out("\n--- Scores ---")
    for blk in b["scores"].values():
        print_scores(blk)
        out()


# --------------------------------------------------------------- scoring

def cmd_score(a):
    text = a.text or ""
    title = a.title or ("" if a.caption else text)
    caption = a.caption or ("" if a.title else text)
    blocks = []
    if a.hook:
        blocks.append(score.score_hook(a.hook))
    if a.title or (text and not a.caption and not a.hook):
        blocks.append(score.score_youtube(title, a.description or "", a.tags or ""))
    elif a.caption:
        blocks.append(score.score_instagram(caption, a.tags or ""))
    if not blocks:
        if text:
            blocks.append(score.score_hook(text))
        else:
            err("Nothing to score. Pass text, or use --hook / --title / --caption.")
            return 1
    for b in blocks:
        print_scores(b)


def cmd_keywords(a):
    kws = score.keywords(a.text, limit=a.limit)
    if not kws:
        out("No indexable keywords found.")
        return
    out("Keywords: " + ", ".join(kws))


# --------------------------------------------------------------- hashtags

def cmd_tags_add(a):
    n = repo.add_tags(a.tags, a.group)
    out(f"Added {n} tag(s) to pool (group: {a.group})")


def cmd_tags_list(a):
    rows = repo.list_tags(a.group)
    if not rows:
        out("Tag pool is empty. Add some with:  python social.py tags add \"#fyp #viral\"")
        return
    out(f"{'TAG':<26} {'GROUP':<12} {'USES':>5}  LAST USED")
    out("-" * 66)
    for r in rows:
        out(f"{r['tag']:<26} {r['tag_group']:<12} {r['uses']:>5}  {r['last_used'] or '-'}")


def cmd_tags_pick(a):
    tags = repo.pick_tags(a.count, a.group, seed=a.seed or "")
    if not tags:
        out("Tag pool is empty. Add some with:  python social.py tags add \"#fyp #viral\"")
        return
    out(" ".join(tags))


# ------------------------------------------------------------------ links

def cmd_utm(a):
    source = a.source or links.source_for(a.channel)
    medium = a.medium or links.medium_for(a.channel)
    campaign = a.campaign or links.slugify(a.hook or "campaign", 40)
    url = links.build_utm(a.url, source, medium, campaign, term=a.term or "",
                          content=links.slugify(a.hook or "", 30))
    repo.save_link(a.url, url, source, medium, campaign, a.post)
    out(url)


def cmd_link(a):
    rows = repo.list_links(a.limit)
    if not rows:
        out("No tracked links yet.")
        return
    for r in rows:
        out(f"#{r['id']}  {r['created_at']}  post={r['post_id'] or '-'}")
        out(f"   {r['full_url']}")


# ---------------------------------------------------------------- metrics

def cmd_metrics(a):
    try:
        repo.add_metrics(a.id, a.views, a.likes, a.comments, a.shares, a.reach)
    except ValueError as e:
        err(str(e))
        return 1
    out(f"Recorded metrics for post #{a.id} on {datetime.now().date()}")


def cmd_top(a):
    rows = report.top_posts(a.metric, a.limit)
    if not rows:
        out("No metrics recorded. Add them with:  python social.py metrics <id> --views 1200")
        return
    out(f"Top {len(rows)} by {a.metric}")
    out("-" * 88)
    out(f"{'ID':>3} {'CH':<4} {'VIEWS':>8} {'LIKES':>7} {'CMTS':>6} {'SHARE':>6} {'ER%':>6}  HOOK")
    for r in rows:
        out(f"{r['id']:>3} {r['channel']:<4} {r['views']:>8} {r['likes']:>7} "
            f"{r['comments']:>6} {r['shares']:>6} {r['engagement_rate']:>6.2f}  {r['hook'][:30]}")


def cmd_summary(a):
    s = report.summary()
    if not s:
        out("No metrics recorded yet.")
        return
    out(f"{'CHANNEL':<16} {'POSTS':>5} {'VIEWS':>9} {'LIKES':>7} {'CMTS':>6} "
        f"{'SHARE':>6} {'ER%':>6} {'AVG VIEWS':>10}")
    out("-" * 80)
    for ch, v in sorted(s.items()):
        label = CHANNELS.get(ch, {}).get("label", ch)
        out(f"{label:<16} {v['posts']:>5} {v['views']:>9} {v['likes']:>7} "
            f"{v['comments']:>6} {v['shares']:>6} {v['engagement_rate']:>6.2f} {v['avg_views']:>10}")


def cmd_weekly(a):
    w = report.weekly(a.days)
    out("=" * 70)
    out(f"LAST {w['days']} DAYS  -  {w['published_count']} published with metrics")
    out("=" * 70)
    if w["rows"]:
        out(f"{'ID':>3} {'CH':<4} {'VIEWS':>8} {'WATCH MIN':>10} {'AVG %':>6} {'ER%':>6}  HOOK")
        out("-" * 78)
        for r in w["rows"]:
            out(f"{r['id']:>3} {r['channel']:<4} {r['views']:>8} {r['watch_minutes']:>10.1f} "
                f"{r['avg_view_percent']:>6.1f} {r['engagement_rate']:>6.2f}  {r['hook'][:28]}")
    else:
        out("  (no published posts with metrics in this window)")
    if w["summary"]:
        out("\nBy channel")
        out("-" * 62)
        for ch, v in sorted(w["summary"].items()):
            out(f"  {CHANNELS.get(ch, {}).get('label', ch):<16} "
                f"views {v['views']:>8}  avg {v['avg_views']:>7}  ER {v['engagement_rate']:.2f}%")
    if w["scheduled_upcoming"]:
        out("\nScheduled ahead")
        out("-" * 62)
        for p in w["scheduled_upcoming"][:15]:
            out(f"  {p['publish_at']:<17} [{p['channel']}] #{p['id']} {p['hook'][:30]}")


# --------------------------------------------------------------- youtube

def cmd_auth(a):
    if a.auth_cmd == "login":
        try:
            youtube.login(port=a.port, open_browser=not a.no_browser)
        except youtube.YouTubeError as e:
            err(str(e))
            return 1
        out("Signed in. Read-only access to your own channel.")
        out(f"Token cached at: {youtube.token_path()}")
        try:
            c = youtube.channel_info()
            out(f"Channel: {c['title']}  ({c['id']})")
            out(f"Subscribers: {c['subscribers']:,}   Videos: {c['videos']}   Views: {c['views']:,}")
        except youtube.YouTubeError as e:
            out(f"(could not read channel yet: {e})")
        return 0

    if a.auth_cmd == "status":
        st = youtube.token_status()
        if not st["signed_in"]:
            out("Not signed in. Run:  python social.py auth login")
            return 0
        out("Signed in.")
        out(f"  scopes     : {st['scopes']}")
        out(f"  obtained   : {st['obtained_at']}")
        out(f"  can refresh: {'yes' if st['has_refresh'] else 'no (re-login needed)'}")
        try:
            c = youtube.channel_info()
            out(f"  channel    : {c['title']} ({c['id']})")
            out(f"  subs       : {c['subscribers']:,}")
        except youtube.YouTubeError as e:
            out(f"  channel    : unavailable ({e})")
        return 0

    if a.auth_cmd == "logout":
        out("Signed out." if youtube.sign_out() else "Was not signed in.")
        return 0

    if a.auth_cmd == "channel":
        try:
            c = youtube.channel_info()
        except youtube.YouTubeError as e:
            err(str(e))
            return 1
        out(f"Name       : {c['title']}")
        out(f"Channel ID : {c['id']}")
        out(f"Handle     : {c['handle'] or '-'}")
        out(f"Subscribers: {c['subscribers']:,}")
        out(f"Videos     : {c['videos']:,}")
        out(f"Total views: {c['views']:,}")
        return 0
    return 1


def cmd_link_video(a):
    vid = sync.parse_video_id(a.video)
    if not vid:
        err(f"Could not find a video id in '{a.video}'.")
        return 1
    post_id = a.post
    if post_id is None:
        out(f"Video ID: {vid}")
        out("Add --post ID to attach it to a calendar entry.")
        return 0
    try:
        repo.link_video(vid, post_id)
    except ValueError as e:
        err(str(e))
        return 1
    out(f"Linked post #{post_id} <-> {vid}")
    return 0


def cmd_videos(a):
    try:
        vids = youtube.recent_videos(a.limit)
    except youtube.YouTubeError as e:
        err(str(e))
        return 1
    if not vids:
        out("No videos found on the signed-in channel.")
        return 0
    linked = repo.video_map()
    out(f"{'VIDEO ID':<13} {'PUBLISHED':<12} {'POST':<6} TITLE")
    out("-" * 92)
    for v in vids:
        pid = linked.get(v["video_id"])
        post = f"#{pid}" if pid else "-"
        out(f"{v['video_id']:<13} {v['published_at']:<12} {post:<6} {v['title'][:52]}")
    out(f"\nAttach one with:  python social.py link {vids[0]['video_id']} --post 1")
    return 0


def cmd_sync(a):
    if a.dry_run:
        out("Dry run: nothing will be written.\n")
    try:
        result = sync.sync(days=a.days, dry_run=a.dry_run)
    except youtube.YouTubeError as e:
        err(str(e))
        return 1

    ch = result.get("channel") or {}
    if ch:
        out(f"Channel: {ch.get('title')}   subs {ch.get('subscribers', 0):,}")
    out(f"Window: {result['window'][0]} to {result['window'][1]}")
    out(f"Recent videos: {result['videos']}   matched to posts: {result['matched']}   "
        f"metrics written: {result['written']}")
    if result["rows"]:
        out()
        out(f"{'POST':>4} {'VIEWS':>8} {'WATCH MIN':>10} {'AVG %':>6} {'CTR%':>6} "
            f"{'LIKES':>6} {'COM':>5} {'+SUB':>5}  TITLE")
        out("-" * 104)
        for r in result["rows"]:
            out(f"{r['post_id']:>4} {r['views']:>8} {r['watch_minutes']:>10.1f} "
                f"{r['avg_view_percent']:>6.1f} {r['ctr']:>6.2f} {r['likes']:>6} "
                f"{r['comments']:>5} {r['subs_gained']:>5}  {r['title'][:34]}")
    if result["matched"] < result["videos"]:
        out(f"\n{result['videos'] - result['matched']} video(s) had no matching post.")
        out("Link them manually:  python social.py link <video_id> --post <id>")
    out("\nRun 'python social.py weekly' to see the digest.")
    return 0


def cmd_yt_stats(a):
    vid = sync.parse_video_id(a.video)
    if not vid:
        err(f"Could not find a video id in '{a.video}'.")
        return 1
    try:
        s = youtube.video_stats(vid)
    except youtube.YouTubeError as e:
        err(str(e))
        return 1
    if not s:
        err("Video not found or not yours.")
        return 1
    out(f"Title   : {s['title']}")
    out(f"Duration: {s['duration']}")
    out(f"Views   : {s['views']:,}")
    out(f"Likes   : {s['likes']:,}")
    out(f"Comments: {s['comments']:,}")
    if s["views"]:
        out(f"Like rt : {s['likes'] / s['views'] * 100:.2f}%")
    return 0


# ----------------------------------------------------------------- parser

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="social",
        description="Content planning + optimization for YouTube Shorts and 2 Instagram "
                    "accounts. Reads your own YouTube analytics when signed in. Never posts, "
                    "likes or comments on any account.",
    )
    s = p.add_subparsers(dest="cmd", required=True)

    s.add_parser("init", help="create the local database").set_defaults(func=cmd_init)

    add = s.add_parser("add", help="add a post to the calendar")
    add.add_argument("hook", help="the hook / first line")
    add.add_argument("--channel", "-c", required=True, choices=repo.VALID_CHANNELS)
    add.add_argument("--date", help="publish date, YYYY-MM-DD or 'YYYY-MM-DD HH:MM'")
    add.add_argument("--title", help="video title (YouTube)")
    add.add_argument("--caption", help="caption text (Instagram)")
    add.add_argument("--content", help="extra body / script notes")
    add.add_argument("--tags", help="hashtags, space separated")
    add.add_argument("--link", help="destination URL")
    add.add_argument("--status", default="idea", choices=repo.VALID_STATUS)
    add.set_defaults(func=cmd_add)

    ls = s.add_parser("list", help="list posts")
    ls.add_argument("--channel", "-c", choices=repo.VALID_CHANNELS)
    ls.add_argument("--status", choices=repo.VALID_STATUS)
    ls.add_argument("--limit", type=int, default=30)
    ls.set_defaults(func=cmd_list)

    sh = s.add_parser("show", help="show one post")
    sh.add_argument("id", type=int)
    sh.set_defaults(func=cmd_show)

    up = s.add_parser("update", help="update a post")
    up.add_argument("id", type=int)
    up.add_argument("--hook")
    up.add_argument("--channel", choices=repo.VALID_CHANNELS)
    up.add_argument("--status", choices=repo.VALID_STATUS)
    up.add_argument("--title")
    up.add_argument("--caption")
    up.add_argument("--content")
    up.add_argument("--tags")
    up.add_argument("--link")
    up.add_argument("--date")
    up.set_defaults(func=cmd_update)

    de = s.add_parser("delete", help="delete a post")
    de.add_argument("id", type=int)
    de.set_defaults(func=cmd_delete)

    sc = s.add_parser("schedule", help="set a publish date")
    sc.add_argument("id", type=int)
    sc.add_argument("--date")
    sc.add_argument("--status", default="scheduled", choices=repo.VALID_STATUS)
    sc.set_defaults(func=cmd_schedule)

    uc = s.add_parser("upcoming", help="what's coming up")
    uc.add_argument("--days", type=int, default=7)
    uc.set_defaults(func=cmd_upcoming)

    od = s.add_parser("overdue", help="past due, not published")
    od.set_defaults(func=cmd_overdue)

    br = s.add_parser("brief", help="full publishing brief for a post")
    br.add_argument("id", type=int)
    br.add_argument("--url", help="base URL for the tracked link")
    br.add_argument("--campaign")
    br.set_defaults(func=cmd_brief)

    sr = s.add_parser("score", help="score a hook, title or caption")
    sr.add_argument("text", nargs="?", help="text to score")
    sr.add_argument("--hook", help="score as a hook")
    sr.add_argument("--title", help="video title (YouTube)")
    sr.add_argument("--caption", help="caption text (Instagram)")
    sr.add_argument("--description", help="YouTube description")
    sr.add_argument("--tags", help="hashtags")
    sr.set_defaults(func=cmd_score)

    kw = s.add_parser("keywords", help="extract keywords from text")
    kw.add_argument("text")
    kw.add_argument("--limit", type=int, default=8)
    kw.set_defaults(func=cmd_keywords)

    tg = s.add_parser("tags", help="hashtag pool")
    tsub = tg.add_subparsers(dest="tags_cmd", required=True)
    ta = tsub.add_parser("add", help="add tags to the pool")
    ta.add_argument("tags")
    ta.add_argument("--group", "-g", default="general")
    ta.set_defaults(func=cmd_tags_add)
    tl = tsub.add_parser("list", help="list the pool")
    tl.add_argument("--group", "-g")
    tl.set_defaults(func=cmd_tags_list)
    tp = tsub.add_parser("pick", help="pick least-used tags (rotates)")
    tp.add_argument("-n", "--count", type=int, default=8)
    tp.add_argument("--group", "-g")
    tp.add_argument("--seed", help="shuffle seed, e.g. a post id")
    tp.set_defaults(func=cmd_tags_pick)

    ut = s.add_parser("utm", help="build a tracked link")
    ut.add_argument("url")
    ut.add_argument("--channel", "-c", choices=repo.VALID_CHANNELS)
    ut.add_argument("--source")
    ut.add_argument("--medium")
    ut.add_argument("--campaign")
    ut.add_argument("--term")
    ut.add_argument("--hook", help="used to derive utm_content")
    ut.add_argument("--post", type=int)
    ut.set_defaults(func=cmd_utm)

    lk = s.add_parser("links", help="recent tracked links")
    lk.add_argument("--limit", type=int, default=15)
    lk.set_defaults(func=cmd_link)

    mt = s.add_parser("metrics", help="record performance for a post")
    mt.add_argument("id", type=int)
    mt.add_argument("--views", type=int, default=0)
    mt.add_argument("--likes", type=int, default=0)
    mt.add_argument("--comments", type=int, default=0)
    mt.add_argument("--shares", type=int, default=0)
    mt.add_argument("--reach", type=int, default=0)
    mt.set_defaults(func=cmd_metrics)

    tp2 = s.add_parser("top", help="best performing posts")
    tp2.add_argument("--metric", default="views",
                     choices=("views", "likes", "comments", "shares",
                              "interactions", "engagement_rate",
                              "watch_minutes", "avg_view_percent", "ctr",
                              "subs_gained"))
    tp2.add_argument("--limit", type=int, default=10)
    tp2.set_defaults(func=cmd_top)

    sm = s.add_parser("summary", help="totals by channel")
    sm.set_defaults(func=cmd_summary)

    wk = s.add_parser("weekly", help="weekly performance digest")
    wk.add_argument("--days", type=int, default=7)
    wk.set_defaults(func=cmd_weekly)

    au = s.add_parser("auth", help="sign in to your own Google account (read-only)")
    ausub = au.add_subparsers(dest="auth_cmd", required=True)
    al = ausub.add_parser("login", help="run the OAuth browser flow")
    al.add_argument("--port", type=int, default=8765)
    al.add_argument("--no-browser", action="store_true")
    ast = ausub.add_parser("status", help="show the current sign-in state")
    ast.set_defaults(func=cmd_auth)
    ao = ausub.add_parser("logout", help="delete the cached token")
    ao.set_defaults(func=cmd_auth)
    ac = ausub.add_parser("channel", help="show the signed-in channel")
    ac.set_defaults(func=cmd_auth)
    au.set_defaults(func=cmd_auth)

    lk2 = s.add_parser("link", help="attach a YouTube video to a post")
    lk2.add_argument("video", help="video id or any YouTube URL")
    lk2.add_argument("--post", "-p", type=int, help="post id to attach to")
    lk2.set_defaults(func=cmd_link_video)

    vd = s.add_parser("videos", help="list your recent uploads")
    vd.add_argument("--limit", type=int, default=25)
    vd.set_defaults(func=cmd_videos)

    sy = s.add_parser("sync", help="pull real YouTube analytics into the calendar")
    sy.add_argument("--days", type=int, default=28, help="analytics window")
    sy.add_argument("--dry-run", action="store_true", help="show matches, write nothing")
    sy.set_defaults(func=cmd_sync)

    ys = s.add_parser("yt-stats", help="stats for one video")
    ys.add_argument("video", help="video id or URL")
    ys.set_defaults(func=cmd_yt_stats)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    a = parser.parse_args(argv)
    try:
        return a.func(a) or 0
    except (ValueError, youtube.YouTubeError) as e:
        err(f"error: {e}")
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
