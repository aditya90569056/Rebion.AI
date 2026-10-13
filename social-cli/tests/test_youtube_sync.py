"""Offline tests for the YouTube sync layer: URL parsing, post/video matching,
token handling and analytics field mapping. No network calls."""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_TMP = tempfile.mkdtemp(prefix="socialcli-yttest-")
os.environ["SOCIAL_CLI_HOME"] = _TMP

from socialkit import repo, sync, youtube  # noqa: E402
from socialkit.db import init  # noqa: E402

VID_A = "dQw4w9WgXcQ"
VID_B = "abcdefghijk"
VID_C = "0123456789a"


class IsolatedDb(unittest.TestCase):
    """Each test gets its own data directory so ordering cannot leak state."""

    def setUp(self):
        self._home = tempfile.mkdtemp(prefix="socialcli-case-")
        os.environ["SOCIAL_CLI_HOME"] = self._home
        init()

    def tearDown(self):
        shutil.rmtree(self._home, ignore_errors=True)


class TestParseVideoId(IsolatedDb):
    def test_bare_id(self):
        self.assertEqual(sync.parse_video_id(VID_A), VID_A)

    def test_all_url_shapes(self):
        cases = {
            f"https://www.youtube.com/watch?v={VID_A}": VID_A,
            f"https://youtube.com/watch?feature=share&v={VID_A}": VID_A,
            f"https://youtu.be/{VID_A}": VID_A,
            f"https://www.youtube.com/shorts/{VID_A}": VID_A,
            f"https://www.youtube.com/embed/{VID_A}": VID_A,
            f"https://m.youtube.com/watch?v={VID_A}&t=30": VID_A,
        }
        for url, expect in cases.items():
            self.assertEqual(sync.parse_video_id(url), expect, url)

    def test_rejects_junk(self):
        for bad in ["", "not a video", "https://vimeo.com/12345",
                    "https://youtube.com/watch?v=short"]:
            self.assertIsNone(sync.parse_video_id(bad), bad)


class TestMatching(IsolatedDb):
    def setUp(self):
        super().setUp()
        self.conn_pids = []
        for title, date in [
            ("3 hooks that work", "2026-09-10"),
            ("reels editing tips", "2026-09-12"),
            ("a completely different video", "2026-01-05"),
        ]:
            self.conn_pids.append(
                repo.add_post(title, "yt", title=title, publish_at=date)
            )

    def _videos(self):
        return [
            {"video_id": VID_A, "title": "3 hooks that work", "published_at": "2026-09-10"},
            {"video_id": VID_B, "title": "reels editing tips", "published_at": "2026-09-12"},
        ]

    def test_matches_by_exact_date(self):
        pairs = sync.match_posts_to_videos(self._videos())
        self.assertEqual(pairs[self.conn_pids[0]]["video_id"], VID_A)
        self.assertEqual(pairs[self.conn_pids[1]]["video_id"], VID_B)

    def test_does_not_match_distant_post(self):
        pairs = sync.match_posts_to_videos(self._videos())
        self.assertNotIn(self.conn_pids[2], pairs)

    def test_each_video_used_once(self):
        vids = [{"video_id": VID_A, "title": "x", "published_at": "2026-09-10"}]
        pairs = sync.match_posts_to_videos(vids)
        used = [v["video_id"] for v in pairs.values()]
        self.assertEqual(len(used), len(set(used)))

    def test_explicit_video_id_wins(self):
        repo.link_video(VID_C, self.conn_pids[0], "3 hooks that work", "2026-09-10")
        pairs = sync.match_posts_to_videos(
            [{"video_id": VID_C, "title": "3 hooks that work", "published_at": "2026-09-10"}]
        )
        self.assertEqual(pairs[self.conn_pids[0]]["video_id"], VID_C)

    def test_ignores_non_yt_posts(self):
        ig = repo.add_post("ig post", "ig1", publish_at="2026-09-10")
        pairs = sync.match_posts_to_videos(self._videos())
        self.assertNotIn(ig, pairs)

    def test_empty_video_list(self):
        self.assertEqual(sync.match_posts_to_videos([]), {})


class TestSyncRecord(IsolatedDb):
    def setUp(self):
        super().setUp()
        self.pid = repo.add_post("hook for sync", "yt", title="hook for sync",
                                 publish_at="2026-09-10")
        self.video = {"video_id": VID_A, "title": "hook for sync",
                      "published_at": "2026-09-10"}
        self.analytics = {
            VID_A: {
                "views": 5000,
                "estimatedMinutesWatched": 900.0,
                "likes": 300,
                "comments": 25,
                "shares": 40,
                "impressions": 60000,
                "impressionsClickThroughRate": 0.0812,
                "averageViewPercentage": 0.634,
                "subscribersGained": 12,
                "subscribersLost": 1,
            }
        }

    def _run(self, dry_run=False):
        with mock.patch.object(sync.youtube, "recent_videos", return_value=[self.video]), \
             mock.patch.object(sync.youtube, "analytics_by_video",
                               return_value=self.analytics), \
             mock.patch.object(sync.youtube, "channel_info", return_value={
                 "id": "UC1", "title": "Test", "handle": "@t", "subscribers": 100,
                 "views": 5000, "videos": 1}), \
             mock.patch.object(sync.youtube, "default_window",
                               return_value=("2026-08-13", "2026-09-10")):
            return sync.sync(days=28, dry_run=dry_run)

    def test_writes_metrics(self):
        r = self._run()
        self.assertEqual(r["written"], 1)
        self.assertEqual(r["matched"], 1)
        row = r["rows"][0]
        self.assertEqual(row["views"], 5000)
        self.assertEqual(row["watch_minutes"], 900.0)
        self.assertEqual(row["ctr"], 8.12)
        self.assertEqual(row["avg_view_percent"], 63.4)
        m = repo.latest_metrics()[self.pid]
        self.assertEqual(m["views"], 5000)
        self.assertEqual(m["source"], "youtube")
        self.assertAlmostEqual(m["ctr"], 0.0812, places=4)

    def test_links_video_to_post(self):
        self._run()
        p = repo.get_post(self.pid)
        self.assertEqual(p["video_id"], VID_A)
        self.assertEqual(repo.video_map()[VID_A], self.pid)

    def test_dry_run_writes_nothing(self):
        r = self._run(dry_run=True)
        self.assertEqual(r["written"], 0)
        self.assertIsNone(repo.get_post(self.pid)["video_id"])
        self.assertEqual(repo.latest_metrics(), {})

    def test_repeat_sync_upserts_same_day(self):
        self._run()
        self._run()
        rows = [r for r in repo.latest_metrics().values() if r["post_id"] == self.pid]
        self.assertEqual(len(rows), 1)

    def test_no_videos_returns_clean(self):
        with mock.patch.object(sync.youtube, "recent_videos", return_value=[]):
            r = sync.sync()
        self.assertEqual(r["videos"], 0)
        self.assertEqual(r["rows"], [])


class TestCredentials(IsolatedDb):
    def test_missing_credentials_message(self):
        if youtube.credentials_path().exists():
            youtube.credentials_path().unlink()
        with mock.patch.dict(os.environ, {"GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": ""}):
            with self.assertRaises(youtube.YouTubeError) as ctx:
                youtube.load_credentials()
        self.assertIn("console.cloud.google.com", str(ctx.exception))

    def test_reads_installed_section(self):
        p = youtube.credentials_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"installed": {"client_id": "cid", "client_secret": "sec"}}),
                     encoding="utf-8")
        try:
            with mock.patch.dict(os.environ, {"GOOGLE_CLIENT_ID": "",
                                               "GOOGLE_CLIENT_SECRET": ""}):
                self.assertEqual(youtube.load_credentials(), ("cid", "sec"))
        finally:
            p.unlink()

    def test_token_status_without_token(self):
        if youtube.token_path().exists():
            youtube.token_path().unlink()
        self.assertFalse(youtube.token_status()["signed_in"])


class TestYoutubeHelpers(IsolatedDb):
    def test_default_window_length(self):
        from datetime import date
        start, end = youtube.default_window(28)
        gap = date(*(int(x) for x in end.split("-"))) - date(*(int(x) for x in start.split("-")))
        self.assertEqual(gap.days, 28)

    def test_load_token_missing_raises(self):
        if youtube.token_path().exists():
            youtube.token_path().unlink()
        with self.assertRaises(youtube.YouTubeError):
            youtube.load_token()

    def test_analytics_metric_list(self):
        self.assertIn("averageViewPercentage", youtube.ANALYTICS_METRICS)
        self.assertIn("impressionsClickThroughRate", youtube.ANALYTICS_METRICS)

    def test_scopes_are_read_only(self):
        for scope in youtube.SCOPES:
            self.assertTrue(scope.endswith("readonly"), scope)

    def test_refresh_uses_refresh_token(self):
        youtube.token_path().write_text(json.dumps({
            "access_token": "old", "refresh_token": "r", "expires_at": 1,
        }), encoding="utf-8")
        with mock.patch.object(youtube, "load_credentials", return_value=("cid", "sec")), \
             mock.patch.object(youtube, "_post_form",
                               return_value={"access_token": "new", "expires_in": 3600}) as pf:
            token = youtube._access_token()
        self.assertEqual(token, "new")
        self.assertEqual(pf.call_args[0][1]["grant_type"], "refresh_token")
        self.assertEqual(json.loads(youtube.token_path().read_text(encoding="utf-8"))
                         ["access_token"], "new")


class TestCli(IsolatedDb):
    def setUp(self):
        super().setUp()
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        import social
        self.social = social

    def test_parser_builds_all_commands(self):
        parser = self.social.build_parser()
        for cmd in ["init", "add", "list", "brief", "score", "tags", "utm",
                    "metrics", "top", "summary", "weekly", "auth", "link",
                    "videos", "sync", "yt-stats"]:
            self.assertIn(cmd, parser._subparsers._group_actions[0].choices, cmd)

    def test_link_with_bad_id_returns_1(self):
        self.assertEqual(self.social.main(["link", "junk-value", "--post", "1"]), 1)

    def test_yt_stats_bad_id_returns_1(self):
        self.assertEqual(self.social.main(["yt-stats", "junk"]), 1)

    def test_sync_surfaces_missing_credentials(self):
        if youtube.credentials_path().exists():
            youtube.credentials_path().unlink()
        with mock.patch.dict(os.environ, {"GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": ""}):
            self.assertEqual(self.social.main(["sync"]), 1)

    def test_add_list_roundtrip(self):
        self.assertEqual(self.social.main([
            "add", "a test hook", "-c", "yt", "--date", "2026-10-01", "--tags", "#x"]), 0)
        self.assertEqual(self.social.main(["list"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
