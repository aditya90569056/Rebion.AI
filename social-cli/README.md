# social-cli

Content planning and optimization CLI for **one YouTube Shorts channel + two Instagram accounts**.

It never posts, likes or comments on any account. Everything runs locally in a SQLite file, and
the Google integration is **read-only**: it pulls your own YouTube analytics so you never type
numbers in by hand.

## Setup

```powershell
cd social-cli
python social.py init
```

No third-party packages. Python 3.10+ standard library only.

## Channels

| Key    | Account          |
| ------ | ---------------- |
| `yt`   | YouTube Shorts   |
| `ig1`  | Instagram 1      |
| `ig2`  | Instagram 2      |

## Daily use

```powershell
# 1. Log a content idea
python social.py add "Nobody tells you this about reels" -c yt --date "2026-10-01 18:00" `
  --title "3 shorts hooks that actually work" --tags "#shorts #reels"

# 2. Get the full publishing brief (assets, checklists, scores, tracked link)
python social.py brief 1 --url "https://yoursite.com/guide" --campaign oct-push

# 3. See what is coming up and what you missed
python social.py upcoming --days 7
python social.py overdue

# 4. After posting, mark it done
python social.py update 1 --status published

# 5. Pull real stats (YouTube) or type them in (Instagram)
python social.py sync
python social.py metrics 2 --views 3400 --likes 210 --comments 18

# 6. Review
python social.py weekly
python social.py top --metric avg_view_percent
python social.py summary
```

## YouTube analytics sync

Instead of hand-entering views and likes, sign in once with your own Google account and let the
tool read the numbers.

### One-time setup

1. Go to <https://console.cloud.google.com/apis/credentials>
2. Create a project (or pick an existing one) and enable **YouTube Data API v3** and
   **YouTube Analytics API**
3. Create an **OAuth client ID** → type **Desktop app**
4. Download the JSON and save it as `social-cli/data/google_client.json`
5. Run `python social.py auth login` and approve in the browser

```powershell
python social.py auth login      # opens the browser, caches a token
python social.py auth status     # confirm which channel is connected
python social.py auth channel    # name, id, subscribers, video count
python social.py auth logout     # delete the cached token
```

Only two read-only scopes are requested: `youtube.readonly` and `yt-analytics.readonly`. The tool
cannot post, comment, like, or change anything on your channel even if you wanted it to.

### Pulling data

```powershell
python social.py videos            # your recent uploads, and which are linked to a post
python social.py sync --dry-run    # show the matches, write nothing
python social.py sync --days 28    # write views, watch time, CTR, retention, subs into the calendar
python social.py yt-stats "https://youtu.be/VIDEOID"   # one video
```

`sync` matches calendar posts to real videos by publish date, then title similarity. When a
confidence threshold is not met it leaves them unlinked and tells you, rather than guessing:

```powershell
python social.py link "https://youtu.be/VIDEOID" --post 7
```

Once synced, the extra fields feed straight into the reports — `avg_view_percent` (retention) and
`ctr` (thumbnail/hook appeal) usually explain performance far better than raw views.

The Analytics API reports numbers slowly; data for the most recent couple of days is often absent
or incomplete. That is expected, not a bug.

## Commands

### Calendar

| Command | Purpose |
| --- | --- |
| `init` | create the database |
| `add "HOOK" -c CHANNEL` | add a post (`--date --title --caption --content --tags --link --status`) |
| `list` | list posts (`--channel --status --limit`) |
| `show ID` | one post in detail |
| `update ID --field VALUE` | change any field |
| `delete ID` | remove a post |
| `schedule ID --date "YYYY-MM-DD HH:MM"` | set publish date |
| `upcoming --days 7` | what is scheduled |
| `overdue` | past date, not published |
| `brief ID --url URL` | everything needed to publish on that channel |

### Scoring

| Command | Purpose |
| --- | --- |
| `score --hook "TEXT"` | hook quality: length, direct address, open loop, specificity, tension |
| `score "TITLE" --description D --tags T` | YouTube: title length, keyword placement, description depth, hashtag range, CTA |
| `score --caption "TEXT" --tags T` | Instagram: caption length vs the 2200 cap, hook in first line, hashtag range, CTA, line breaks |
| `keywords "TEXT"` | extract indexable keywords |

Scores are structural heuristics, not predictions. A high score means the text is well-formed for
search and retention; it does not guarantee reach. The tips are the useful part.

### Hashtag pool

```powershell
python social.py tags add "#shorts #reels #fyp" -g reach
python social.py tags pick -n 5 -g reach --seed 1
python social.py tags list
```

`pick` returns the least-used tags in a group and bumps their counters, so the same set stops
repeating. Use `--seed` with a post id to get a deterministic set per post.

### Tracked links

```powershell
python social.py utm "https://yoursite.com/lead" -c ig1 --hook "reel about the calendar" --post 2
```

Generates `utm_source` / `utm_medium` / `utm_campaign` / `utm_content`, mapping the channel to the
right source and medium automatically (`yt` → `youtube`/`short`, IG → `instagram`/`social`).
Existing query parameters are preserved. `links` lists recent ones.

Put these in YouTube's description and rotate the IG link-in-bio, then read the results in your
own analytics. That is the only way to know which source actually drove watch time.

### YouTube

| Command | Purpose |
| --- | --- |
| `auth login / status / channel / logout` | manage the read-only Google sign-in |
| `videos` | recent uploads, with the posts they are linked to |
| `link VIDEO --post ID` | attach a video (id or any YouTube URL) to a post |
| `sync --days 28 --dry-run` | pull analytics into the calendar |
| `yt-stats VIDEO` | views, likes, comments, duration for one video |

## Data

`data/social.db`, overridable with the `SOCIAL_CLI_HOME` environment variable. Tables: `posts`,
`metrics`, `hashtags`, `links`, `yt_videos`. Schema changes are applied automatically on open, so
an older database keeps working. Back it up by copying the file.

`data/google_token.json` is your access token. Treat it like a password: it is not in git, and
`auth logout` deletes it.

## Tests

```powershell
python -m unittest discover -s tests
```

54 tests. The YouTube tests mock the network, so they run offline and never touch your channel.

## What is deliberately not here

Automated likes, comments, follows or views. Those are fake engagement, they violate the YouTube
Terms of Service, and a channel caught doing it is terminated. Every number this tool reports comes
from a real viewer.

