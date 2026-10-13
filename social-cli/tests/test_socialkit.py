"""Unit tests for scoring, UTM building and repository logic."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_TMP = tempfile.mkdtemp(prefix="socialcli-test-")
os.environ["SOCIAL_CLI_HOME"] = _TMP

from socialkit import links, repo, score  # noqa: E402
from socialkit.db import init  # noqa: E402


class TestScore(unittest.TestCase):
    def test_grade_bands(self):
        for text, expect in [("x" * 200, "A"), ("x" * 40, "D"), ("", "E")]:
            r = score.score_hook(text)
            self.assertIn(r["grade"], set("ABCDE"))
            self.assertTrue(0 <= r["percent"] <= 100)
            self.assertIn(expect, set("ABCDE"))

    def test_score_bounds(self):
        for kind, fn, arg in [
            ("hook", score.score_hook, "How to fix this in 3 steps fast"),
            ("yt", score.score_youtube, "How to fix CSS grid in 3 steps fast"),
            ("ig", score.score_instagram, "Nobody talks about this CSS grid mistake\n\nSave this."),
        ]:
            r = fn(arg)
            self.assertGreater(r["percent"], 0, kind)
            self.assertLessEqual(r["percent"], 100, kind)
            self.assertTrue(all(c["points"] <= c["max"] for c in r["checks"]), kind)

    def test_good_hook_beats_bad_hook(self):
        good = score.score_hook(
            "Your camera roll is full of videos nobody watches. Here's the 3-second fix."
        )
        bad = score.score_hook("vlog")
        self.assertGreater(good["percent"], bad["percent"])

    def test_cta_detection(self):
        self.assertTrue(score.has_cta("Save this for later"))
        self.assertTrue(score.has_cta("link in bio"))
        self.assertFalse(score.has_cta("a video about coffee"))

    def test_hashtag_count(self):
        self.assertEqual(score.count_hashtags("#a #b #c"), 3)
        self.assertEqual(score.count_hashtags("no tags here"), 0)

    def test_keywords_skips_stopwords(self):
        kws = score.keywords("the best way to grow your channel on youtube")
        self.assertIn("channel", kws)
        self.assertIn("youtube", kws)
        self.assertNotIn("the", kws)

    def test_over_length_youtube_penalised(self):
        short = score.score_youtube("CSS grid fix", "Short desc about css grid.", "#css")
        long = score.score_youtube("x" * 200, "y" * 100, "#a #b")
        self.assertGreater(short["percent"], long["percent"])

    def test_instagram_caption_cap(self):
        r = score.score_instagram("z" * 5000)
        length_check = next(c for c in r["checks"] if c["name"] == "Caption length")
        self.assertEqual(length_check["points"], 0.0)


class TestLinks(unittest.TestCase):
    def test_build_utm(self):
        u = links.build_utm("https://x.dev/a", "youtube", "short", "camp")
        self.assertIn("utm_source=youtube", u)
        self.assertIn("utm_medium=short", u)
        self.assertIn("utm_campaign=camp", u)

    def test_utm_preserves_query(self):
        u = links.build_utm("https://x.dev/a?v=1&t=5", "ig1", "social", "c")
        self.assertIn("v=1", u)
        self.assertIn("t=5", u)
        self.assertIn("utm_source=ig1", u)

    def test_source_for_maps_channels(self):
        self.assertEqual(links.source_for("ig1"), "instagram")
        self.assertEqual(links.source_for("yt"), "youtube")
        self.assertEqual(links.medium_for("yt"), "short")

    def test_utm_rejects_bad_url(self):
        with self.assertRaises(ValueError):
            links.build_utm("not-a-url", "s", "m", "c")
        with self.assertRaises(ValueError):
            links.build_utm("", "s", "m", "c")

    def test_slugify(self):
        self.assertEqual(links.slugify("Hello, World!! 2026"), "hello-world-2026")
        self.assertEqual(links.slugify("!!!"), "")

    def test_short_caption_under_limit(self):
        c = links.short_caption("My hook", "#a #b", "https://x.dev")
        self.assertIn("#a #b", c)
        self.assertLessEqual(len(c), 2200)


class TestRepo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init()

    def setUp(self):
        self.pid = repo.add_post("Test hook here", "yt", tags="#alpha #beta",
                                 publish_at="2026-10-01 09:00")

    def test_create_and_fetch(self):
        p = repo.get_post(self.pid)
        self.assertEqual(p["channel"], "yt")
        self.assertEqual(p["status"], "idea")

    def test_rejects_bad_channel(self):
        with self.assertRaises(ValueError):
            repo.add_post("x", "tiktok")

    def test_rejects_bad_status(self):
        with self.assertRaises(ValueError):
            repo.add_post("x", "yt", status="viral")

    def test_update(self):
        repo.update_post(self.pid, status="scheduled", title="A new title")
        p = repo.get_post(self.pid)
        self.assertEqual(p["status"], "scheduled")
        self.assertEqual(p["title"], "A new title")

    def test_update_rejects_unknown_field(self):
        with self.assertRaises(ValueError):
            repo.update_post(self.pid, nope=1)

    def test_delete(self):
        pid = repo.add_post("delete me", "ig1")
        self.assertEqual(repo.delete_post(pid), 1)
        self.assertIsNone(repo.get_post(pid))

    def test_metrics_require_existing_post(self):
        with self.assertRaises(ValueError):
            repo.add_metrics(999999, views=5)

    def test_metrics_upsert_same_day(self):
        repo.add_metrics(self.pid, views=100, likes=10, captured_at="2026-10-02")
        repo.add_metrics(self.pid, views=150, likes=15, captured_at="2026-10-02")
        latest = repo.latest_metrics()
        self.assertEqual(latest[self.pid]["views"], 150)

    def test_tag_rotation_uses_least_used(self):
        repo.add_tags("#rot1 #rot2 #rot3", "rot")
        first = repo.pick_tags(1, "rot", seed="s1")
        repo.add_tags("#rot1", "rot")
        second = repo.pick_tags(1, "rot", seed="s2")
        self.assertNotEqual(first[0], second[0])

    def test_pick_empty_pool(self):
        self.assertEqual(repo.pick_tags(5, "no_such_group"), [])

    def test_upcoming_filters_window(self):
        rows = repo.upcoming(days=1)
        self.assertTrue(all(r["publish_at"] for r in rows))


class TestBrief(unittest.TestCase):
    def test_brief_builds_for_each_channel(self):
        from socialkit import brief
        init()
        for ch in repo.VALID_CHANNELS:
            pid = repo.add_post("How to grow fast in 2026", ch, tags="#a #b")
            b = brief.build(repo.get_post(pid), base_url="https://x.dev/l")
            self.assertIn("assets", b)
            self.assertIn("Hook", b["scores"])
            self.assertTrue(b["checklist"])
            if ch == "yt":
                self.assertIn("YouTube", b["scores"])
            else:
                self.assertIn("Instagram", b["scores"])


class TestReport(unittest.TestCase):
    def test_summary_and_top(self):
        from socialkit import report
        init()
        pid = repo.add_post("reportable hook", "yt", publish_at="2026-10-03")
        repo.update_post(pid, status="published")
        repo.add_metrics(pid, views=500, likes=50, comments=5, shares=2)
        s = report.summary()
        self.assertIn("yt", s)
        self.assertGreaterEqual(s["yt"]["views"], 500)
        top = report.top_posts("views", 5)
        self.assertTrue(any(r["id"] == pid for r in top))
        w = report.weekly(3650)
        self.assertGreaterEqual(w["published_count"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
