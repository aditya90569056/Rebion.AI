"""Per-post publishing brief: everything needed to publish across 3 channels."""
from __future__ import annotations

from . import links, repo
from .score import score_hook, score_instagram, score_youtube


def build(post, base_url: str = "", campaign: str = "") -> dict:
    hook = post["hook"] or ""
    channel = post["channel"]
    title = post["title"] or ""
    caption = post["caption"] or ""
    tags = post["tags"] or ""
    link = post["link"] or base_url

    tracked = ""
    if link:
        tracked = links.build_utm(
            link,
            links.source_for(channel),
            links.medium_for(channel),
            campaign or f"{channel}-{post['id']}",
            content=links.slugify(hook, 30),
        )

    result = {
        "id": post["id"],
        "hook": hook,
        "channel": channel,
        "channel_label": links.PLATFORM_LABEL.get(channel, channel),
        "status": post["status"],
        "publish_at": post["publish_at"],
        "tracked_link": tracked,
    }

    if channel == "yt":
        desc = links.yt_description(hook, tags, tracked, post["content"] or "")
        result["assets"] = {
            "Title (60 char max)": title or hook,
            "Description": desc,
            "Hashtags": tags,
            "Tracking link": tracked,
        }
        result["scores"] = {
            "Hook": score_hook(hook),
            "YouTube": score_youtube(title or hook, desc, tags),
        }
        result["checklist"] = [
            "Hook visible in first 1 second of the clip",
            "Title under 60 characters, main keyword first",
            "Description has keyword + a CTA",
            "Thumbnail reads at small size",
            "Tracking link in description",
        ]
    else:
        cap = links.short_caption(hook or caption, tags, tracked)
        result["assets"] = {
            "Caption": cap,
            "First line (hook)": cap.split("\n", 1)[0],
            "Hashtags": tags,
            "Tracking link": tracked,
        }
        result["scores"] = {
            "Hook": score_hook(hook),
            "Instagram": score_instagram(cap, tags),
        }
        result["checklist"] = [
            "Hook readable on first frame, text overlay included",
            "First caption line carries the payoff",
            "CTA asks for save / share / comment",
            "Cover image matches the hook",
            "Tracking link in bio for this campaign",
        ]

    if post["status"] != "published":
        result["cross_post"] = [
            {
                "channel": c,
                "label": links.PLATFORM_LABEL.get(c, c),
                "note": "Same clip, retitle for this channel's audience"
                if c != channel else "Source post",
            }
            for c in repo.VALID_CHANNELS
        ]
    return result
