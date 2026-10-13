"""Scoring rules for YouTube Shorts titles/captions and Instagram captions.

Scoring is advisory only. It measures structure that correlates with reach on
each platform; it does not and cannot predict actual performance.
"""
from __future__ import annotations

import re

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from",
    "had", "has", "have", "he", "her", "his", "i", "if", "in", "is", "it",
    "its", "me", "my", "no", "not", "of", "on", "or", "our", "she", "so",
    "than", "that", "the", "their", "them", "then", "there", "these", "they",
    "this", "to", "up", "was", "we", "were", "what", "when", "which", "who",
    "why", "will", "with", "you", "your", "s", "t", "re", "ve", "ll", "d",
    "m", "just", "get", "got", "how", "can", "do", "does", "done", "like",
}

CTA_PATTERNS = [
    r"\bfollow\b", r"\bsubscribe\b", r"\bcomment\b", r"\bshare\b", r"\bsave\b",
    r"\blink (in )?bio\b", r"\bsign up\b", r"\bjoin\b", r"\btap\b", r"\bclick\b",
    r"\blet me know\b", r"\bdrop a\b", r"\btell me\b", r"\bsmash\b",
]

POWER_WORDS = [
    "how", "why", "free", "secret", "best", "top", "new", "easy", "fast",
    "instant", "simple", "proven", "hidden", "mistake", "hack", "truth",
    "before", "after", "never", "always", "stop", "avoid", "warning",
    "fix", "step", "guide", "tips", "beginner", "advanced", "under",
    "nobody", "everyone", "exactly", "literally", "changed", "money",
]

YT_TITLE = {"min": 30, "max": 70}
YT_DESC = {"min": 150, "max": 5000}
IG_CAPTION = {"min": 80, "max": 2200}
IG_HASHTAGS = {"min": 3, "max": 15}
YT_HASHTAGS = {"min": 2, "max": 15}


class Score:
    def __init__(self, name: str, points: float, max_points: float, tip: str = ""):
        self.name = name
        self.points = points
        self.max_points = max_points
        self.tip = tip

    @property
    def ok(self) -> bool:
        return self.points >= self.max_points

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "points": round(self.points, 1),
            "max": self.max_points,
            "tip": self.tip,
        }


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", (text or "").lower())


def keywords(text: str, limit: int = 6) -> list[str]:
    counts: dict[str, int] = {}
    for w in words(text):
        if w in STOPWORDS or len(w) < 3 or w.isdigit():
            continue
        counts[w] = counts.get(w, 0) + 1
    return [w for w, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:limit]]


def keywords_from(text: str, limit: int = 4) -> list[str]:
    uniq: list[str] = []
    for w in words(text):
        if w in STOPWORDS or len(w) < 3 or w in uniq:
            continue
        uniq.append(w)
        if len(uniq) >= limit:
            break
    return uniq


def has_cta(text: str) -> bool:
    low = (text or "").lower()
    return any(re.search(p, low) for p in CTA_PATTERNS)


def count_hashtags(text: str) -> int:
    return len(re.findall(r"#\w+", text or ""))


def keyword_coverage(text: str, kws: list[str]) -> float:
    if not kws:
        return 0.0
    low = (text or "").lower()
    hit = sum(1 for k in kws if k in low)
    return hit / len(kws)


def score_title(title: str, kws: list[str] | None = None) -> list[Score]:
    t = (title or "").strip()
    n = len(t)
    out: list[Score] = []

    if YT_TITLE["min"] <= n <= YT_TITLE["max"]:
        out.append(Score("Title length", 20, 20))
    elif n < YT_TITLE["min"]:
        out.append(Score("Title length", max(4, 20 * n / YT_TITLE["min"]), 20,
                         f"Short titles get cut off. Aim {YT_TITLE['min']}-{YT_TITLE['max']} chars (now {n})."))
    else:
        out.append(Score("Title length", 10, 20,
                         f"Trim to {YT_TITLE['max']} chars max or it truncates (now {n})."))

    kws = kws or keywords_from(t)
    if not kws:
        out.append(Score("Keyword in title", 0, 15, "No indexable words found in the title."))
    elif kws[0] in t.lower().split() or t.lower().startswith(kws[0]):
        out.append(Score("Keyword in title", 15, 15))
    elif keyword_coverage(t, kws[:3]) > 0:
        out.append(Score("Keyword in title", 9, 15, "Put your main keyword in the first 3 words."))
    else:
        out.append(Score("Keyword in title", 0, 15, "Main keyword missing from the title."))

    power = [p for p in POWER_WORDS if re.search(rf"\b{p}\b", t.lower())]
    if power:
        out.append(Score("Curiosity trigger", 10, 10))
    else:
        out.append(Score("Curiosity trigger", 5, 10,
                         f"No power word. Try: {', '.join(POWER_WORDS[:6])}."))

    if re.search(r"[0-9]", t):
        out.append(Score("Number / specificity", 8, 8))
    else:
        out.append(Score("Number / specificity", 4, 8, "A specific number tends to earn more clicks."))

    if t and t == t.strip() and not t.endswith(("...", "…")):
        out.append(Score("Clean and complete", 7, 7))
    else:
        out.append(Score("Clean and complete", 3, 7, "Trim stray punctuation and avoid trailing dots."))

    return out


def score_youtube(title: str, description: str = "", hashtags: str = "") -> dict:
    body = f"{title}\n{description} {hashtags}"
    kws = keywords_from(title, 4) or keywords_from(description, 4)
    scores = score_title(title, kws)
    desc = (description or "").strip()

    if len(desc) >= YT_DESC["min"]:
        scores.append(Score("Description length", 15, 15))
    elif desc:
        scores.append(Score("Description length", 8, 15,
                            f"Add {YT_DESC['min'] - len(desc)} more chars. Descriptions are indexed by search."))
    else:
        scores.append(Score("Description length", 0, 15, "Description is empty - it feeds YouTube search."))

    cov = keyword_coverage(desc, kws)
    if cov >= 0.6:
        scores.append(Score("Keyword in description", 10, 10))
    elif cov > 0:
        scores.append(Score("Keyword in description", 6, 10))
    else:
        scores.append(Score("Keyword in description", 0, 10,
                            f"Add your keyword naturally: {', '.join(kws[:4]) or 'n/a'}."))

    n_tags = count_hashtags(f"{desc} {hashtags}")
    lo, hi = YT_HASHTAGS["min"], YT_HASHTAGS["max"]
    if lo <= n_tags <= hi:
        scores.append(Score("Hashtags", 10, 10))
    elif n_tags < lo:
        scores.append(Score("Hashtags", 5, 10, f"Use {lo}-{hi} hashtags; you have {n_tags}."))
    else:
        scores.append(Score("Hashtags", 3, 10, f"{n_tags} hashtags is over the useful range (max {hi})."))

    scores.append(Score("Call to action", 8 if has_cta(body) else 0, 8,
                        "No CTA found. Ask for a subscribe, comment or share."))
    return finish(scores, "youtube")


def score_instagram(caption: str, hashtags: str = "") -> dict:
    cap = (caption or "").strip()
    full = f"{cap} {hashtags}"
    kws = keywords_from(cap, 4)
    n = len(cap)
    scores: list[Score] = []

    if n == 0:
        scores.append(Score("Caption length", 0, 20, "Caption is empty. Even a one-line hook helps."))
    elif n > IG_CAPTION["max"]:
        scores.append(Score("Caption length", 0, 20,
                            f"{n} chars is over the {IG_CAPTION['max']} limit and will be cut."))
    elif n < IG_CAPTION["min"]:
        scores.append(Score("Caption length", 20 * n / IG_CAPTION["min"], 20,
                            f"Thin caption. Aim for {IG_CAPTION['min']}+ chars."))
    else:
        scores.append(Score("Caption length", 20, 20))

    first_line = cap.split("\n", 1)[0]
    if kws and keyword_coverage(first_line, kws[:2]) > 0:
        scores.append(Score("Hook in first line", 18, 18))
    else:
        scores.append(Score("Hook in first line", 6, 18,
                            "The first line is all most people see before 'more'. Put the payoff there."))

    if first_line.rstrip().endswith((".", "!", "?", ":", ")")):
        scores.append(Score("Readable opening", 10, 10))
    else:
        scores.append(Score("Readable opening", 5, 10, "End the opening line with punctuation for a clean break."))

    n_tags = count_hashtags(full)
    lo, hi = IG_HASHTAGS["min"], IG_HASHTAGS["max"]
    if lo <= n_tags <= hi:
        scores.append(Score("Hashtags", 14, 14))
    elif n_tags < lo:
        scores.append(Score("Hashtags", 7, 14, f"Use {lo}-{hi} hashtags; you have {n_tags}."))
    else:
        scores.append(Score("Hashtags", 4, 14, f"{n_tags} hashtags is heavy. {lo}-{hi} reads better."))

    scores.append(Score("Call to action", 12 if has_cta(full) else 0, 12,
                        "No CTA. Ask for a save, share or comment."))
    scores.append(Score("Line breaks", 8 if "\n" in cap else 3, 8,
                        "Add line breaks so it skims well on mobile."))
    return finish(scores, "instagram")


def score_hook(hook: str) -> dict:
    h = (hook or "").strip()
    n = len(h)
    scores: list[Score] = []
    if 20 <= n <= 90:
        scores.append(Score("Hook length", 20, 20))
    elif n < 20:
        scores.append(Score("Hook length", 20 * n / 20, 20, f"Expand to 20-90 chars (now {n})."))
    else:
        scores.append(Score("Hook length", 10, 20, f"Long for a hook. Trim to 90 (now {n})."))

    if re.search(r"\b(you|your|you're|you're)\b", h, re.I):
        scores.append(Score("Direct address", 16, 16))
    else:
        scores.append(Score("Direct address", 6, 16, "Address the viewer: 'you', 'your'."))

    if re.search(r"[?!]", h):
        scores.append(Score("Open loop", 14, 14))
    else:
        scores.append(Score("Open loop", 6, 14, "A question or suspense creates a reason to keep watching."))

    nums = re.findall(r"\b\d+\b", h)
    if nums:
        scores.append(Score("Specificity", 12, 12))
    else:
        scores.append(Score("Specificity", 6, 12, "A number or time frame makes it concrete."))

    if re.search(r"\b(never|stop|don't|don't|avoid|mistake|worst|wrong)\b", h, re.I):
        scores.append(Score("Tension", 10, 10))
    else:
        scores.append(Score("Tension", 4, 10, "Name a mistake or risk to create tension."))

    if h and not h.lower().startswith(("like this is", "so basically", "hey guys")):
        scores.append(Score("No filler", 8, 8))
    else:
        scores.append(Score("No filler", 3, 8, "Drop the preamble and open on the payoff."))

    return finish(scores, "hook")


def finish(scores: list[Score], kind: str) -> dict:
    total = sum(s.points for s in scores)
    maximum = sum(s.max_points for s in scores) or 1
    pct = total / maximum
    if pct >= 0.85:
        grade = "A"
    elif pct >= 0.7:
        grade = "B"
    elif pct >= 0.55:
        grade = "C"
    elif pct >= 0.4:
        grade = "D"
    else:
        grade = "E"
    return {
        "kind": kind,
        "score": round(total, 1),
        "max": maximum,
        "percent": round(pct * 100),
        "grade": grade,
        "checks": [s.as_dict() for s in scores],
    }
