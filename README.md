# Dashboard: what AI company staff post about on X

Open `index.html` in any browser. It works offline: the data is built into the page. The page holds no names, handles or post text, only anonymous job stints and the date and labels of each AI post.

## Updating it

When `../ai_staff_tweets.csv`, `../accounts.csv` or `../employment_history.csv` change, rebuild the page:

    python3 build_dashboard.py

`template.html` holds the page's design and code; the build script fills in the data and writes `index.html`. Every combination of topic, stance, off-message score, lab, measure and window is calculated in the browser from that data, so adding filters costs nothing extra to build.

## What it shows

Posts tagged as about AI (`ai_topic` "AI" or "AI (keyword match)") from accounts whose `include` is "Yes" or "Maybe: light poster", filtered by the labels in `../categorisation/`: topic, stance on AI risk (risk and policy posts only) and off-message score (provisional).

People who changed labs (`../employment_history.csv`) count for each lab only while they worked there, and in each moving window someone counts only if they worked at that lab for all of it. The last day shown is the day before the last day of data, because each pull stops at midday UTC.

Measures, over a 7, 14 or 28-day moving window:
- Share of staff with at least one matching post (everyone counts once).
- Days with a matching post, per person per week (each day counts once).
- Matching posts as a share of all AI posts (counts posts; prolific people weigh more).
- Matching posts per day (counts posts).

Two views:
- **Level.** Optional 95% intervals treat each lab's tracked staff as a sample of its staff on X; use them to compare labs.
- **Change from period average.** Each person's value minus their own average over the whole period, averaged across people, with a 95% interval for that average difference (mean ± 1.96 standard errors across people). Because people are compared with themselves, the interval is narrow; use it to ask whether a group's behaviour has shifted.

The table shows every topic row against every lab for the latest window, with the change from the period average marked in colour only when its 95% interval excludes zero. With 72 cells, a few will be marked by chance.
