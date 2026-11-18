"""Which tracked lab (if any) an account worked at on a given date.
Accounts with rows in employment_history.csv: the stint covering the date (blank 'from' = before 17 Aug 2026, blank 'to' = still there).
If no stint covers the date, the person wasn't at a tracked lab then: their posts are left out and they aren't counted as staff that day.
All other accounts: their accounts.csv company for the whole period."""
import csv, collections
def load(acc_path, hist_path):
    acc = {r["handle"].lower(): r for r in csv.DictReader(open(acc_path, encoding="utf-8-sig"))}
    hist = collections.defaultdict(list)
    for r in csv.DictReader(open(hist_path, encoding="utf-8-sig")): hist[r["handle"].lower()].append(r)
    def employer(handle, day):  # day as 'YYYY-MM-DD'
        h = handle.lower()
        if h not in hist: return acc[h]["company"] if h in acc else None
        for s in hist[h]:
            if (not s["from"] or day >= s["from"]) and (not s["to"] or day <= s["to"]): return s["company"]
        return None
    return employer
if __name__ == "__main__":
    e = load("audit/accounts.csv", "audit/employment_history.csv")
    for h, d in [("@_catwu", "2026-10-01"), ("@_catwu", "2026-11-02"), ("@_catwu", "2026-11-10"), ("@ahall_research", "2026-08-17"),
                 ("@ahall_research", "2026-08-18"), ("@stellakaval", "2026-09-27"), ("@karpathy", "2026-09-01")]:
        print(h, d, "->", e(h, d))
