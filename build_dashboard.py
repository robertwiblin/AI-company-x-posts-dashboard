#!/usr/bin/env python3
"""Rebuild index.html from ../ai_staff_tweets.csv, ../accounts.csv and ../employment_history.csv.

Run from anywhere:  python3 build_dashboard.py
Only standard-library Python is needed. The page it writes works offline and contains no handles or post text:
just anonymous job stints and, for each AI post, the day and its labels.
"""
import csv, json, os, datetime as dt, collections

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(HERE)
AI_TOPICS = {"AI (keyword match)", "AI"}
INCLUDED = {"Yes", "Maybe: light poster"}
LABS = ["OpenAI", "Anthropic", "Google DeepMind", "Meta", "xAI"]
CATS = ["OWN", "PRODUCTS", "RESEARCH", "INDUSTRY", "RISK", "POLICY", "FUTURE", "OTHER"]
STANCES = ["-", "CONCERNED", "REASSURING", "NEUTRAL"]

def read(name):
    with open(os.path.join(DATA_DIR, name), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

accounts = [a for a in read("accounts.csv") if a["include"] in INCLUDED]
hist = collections.defaultdict(list)
for h in read("employment_history.csv"):
    if h["company"] in LABS: hist[h["handle"].lower()].append(h)
tweets = read("ai_staff_tweets.csv")
first = min(dt.date.fromisoformat(t["date_utc"][:10]) for t in tweets)
# the last day of data is partial (pulls stop at midday UTC), so stop the day before it
last = min(max(dt.date.fromisoformat(t["collected_on"]) for t in tweets),
           max(dt.date.fromisoformat(t["date_utc"][:10]) for t in tweets)) - dt.timedelta(days=1)
T = (last - first).days + 1
day = lambda s, default: (dt.date.fromisoformat(s) - first).days if s else default

# One member per job stint: people who changed labs count for each lab only while they worked there.
members, person = [], {}   # member: [person, lab, technical, regular, first day, last day]
for a in accounts:
    p = person.setdefault(a["handle"].lower(), len(person))
    for st in hist.get(a["handle"].lower()) or [{"company": a["company"], "from": "", "to": ""}]:
        s0, s1 = max(0, day(st["from"], 0)), min(T - 1, day(st["to"], T - 1))
        if s0 <= s1 and st["company"] in LABS:
            members.append([p, LABS.index(st["company"]), int(a["role_type"] == "Technical"), int(a["include"] == "Yes"), s0, s1])
by_handle = collections.defaultdict(list)
for i, m in enumerate(members):
    by_handle[m[0]].append(i)
handle_person = {h: p for h, p in person.items()}

posts, n_ai, missing = [], 0, 0
for t in tweets:
    p = handle_person.get(t["handle"].lower())
    if p is None or t["ai_topic"] not in AI_TOPICS: continue
    d = (dt.date.fromisoformat(t["date_utc"][:10]) - first).days
    for i in by_handle[p]:
        if members[i][4] <= d <= members[i][5]:
            cat = t.get("category") or ""
            if cat not in CATS: missing += 1; cat = "OTHER"
            st = t.get("risk_stance") or "-"
            off = int(t["off_message"]) if t.get("off_message", "") in ("0", "1", "2", "3") else 0
            posts += [i, d, CATS.index(cat) * 16 + STANCES.index(st if st in STANCES else "-") * 4 + off]
            n_ai += 1
data = {
    "start": first.isoformat(), "days": T, "end": last.isoformat(),
    "collected": max(t["collected_on"] for t in tweets), "ai_posts": n_ai, "people": len(person),
    "labs": LABS, "members": members, "posts": posts,
}
html = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
html = html.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))
with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)
print(f"Wrote index.html: {len(person)} people, {len(members)} job stints, {n_ai} AI posts ({missing} without a category), {first} to {last}")
