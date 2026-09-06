#!/usr/bin/env python3
"""Rating a finding with the OWASP risk rating methodology.

Likelihood = average of 8 factors (threat agent and vulnerability), impact = average of 8 factors
(technical and business), each 0-9. Levels: <3 low, <6 medium, ≥6 high. Matrix: high impact ×
high likelihood = critical; high×medium or medium×high = high; etc.

Usage:
  risk_rating.py --skill 5 --motive 4 --opportunity 7 --size 9 --discovery 7 --exploit 5 \
      --awareness 6 --detection 8 --confidentiality 7 --integrity 5 --availability 1 \
      --accountability 7 --financial 3 --reputation 5 --compliance 5 --privacy 7 \
      --title "IDOR in /api/orders/[id]" --where "src/app/api/orders/[id]/route.ts:12"
  risk_rating.py --json finding.json      # same fields in JSON; prints a Markdown row
  risk_rating.py --scales                 # prints each factor's scale
"""
import argparse, json, sys

LIKELIHOOD = {
    "skill": ("Attacker skill", {1: "no technical skills", 3: "some technical", 5: "advanced tool user", 6: "network and programming skills", 9: "pentest skills"}),
    "motive": ("Motive", {1: "low or no reward", 4: "possible reward", 9: "high reward"}),
    "opportunity": ("Opportunity", {0: "requires expensive access or resources", 4: "special access or resources", 7: "some access or resources", 9: "no access or resources"}),
    "size": ("Group size", {2: "developers or administrators", 4: "internal users", 5: "partners", 6: "authenticated users", 9: "anonymous internet users"}),
    "discovery": ("Ease of discovery", {1: "practically impossible", 3: "hard", 7: "easy", 9: "automated tools"}),
    "exploit": ("Ease of exploit", {1: "theoretical", 3: "hard", 5: "easy", 9: "automated tools"}),
    "awareness": ("Awareness", {1: "unknown", 4: "hidden", 6: "obvious", 9: "public"}),
    "detection": ("Intrusion detection", {1: "active detection", 3: "logged and reviewed", 8: "logged without review", 9: "not logged"}),
}
IMPACT = {
    "confidentiality": ("Loss of confidentiality", {2: "minimal non-sensitive data", 6: "minimal critical or extensive non-sensitive", 7: "extensive critical data", 9: "all data"}),
    "integrity": ("Loss of integrity", {1: "minimal slightly corrupt", 3: "minimal seriously corrupt", 5: "extensive slightly corrupt", 7: "extensive seriously corrupt", 9: "all corrupt"}),
    "availability": ("Loss of availability", {1: "minimal secondary services", 5: "minimal primary or extensive secondary", 7: "extensive primary", 9: "all services"}),
    "accountability": ("Loss of accountability", {1: "fully traceable", 7: "possibly traceable", 9: "completely anonymous"}),
    "financial": ("Financial damage", {1: "less than the cost to fix", 3: "minor effect on results", 7: "significant effect", 9: "bankruptcy"}),
    "reputation": ("Reputation damage", {1: "minimal", 4: "loss of major accounts", 5: "loss of goodwill", 9: "brand damage"}),
    "compliance": ("Non-compliance", {2: "minor violation", 5: "clear violation", 7: "high-profile violation"}),
    "privacy": ("Privacy violation", {3: "one person", 5: "hundreds", 7: "thousands", 9: "millions"}),
}


def level(x):
    return "low" if x < 3 else "medium" if x < 6 else "high"


def severity(lk, im):
    m = {("high", "high"): "critical", ("high", "medium"): "high", ("medium", "high"): "high",
         ("high", "low"): "medium", ("medium", "medium"): "medium", ("low", "high"): "medium",
         ("medium", "low"): "low", ("low", "medium"): "low", ("low", "low"): "note"}
    return m[(level(im), level(lk))]


def main():
    ap = argparse.ArgumentParser()
    for k, (label, _) in {**LIKELIHOOD, **IMPACT}.items():
        ap.add_argument(f"--{k}", type=float, help=label)
    ap.add_argument("--title"); ap.add_argument("--where", default=""); ap.add_argument("--fix", default="")
    ap.add_argument("--json", help="JSON file with the factors and title/where/fix")
    ap.add_argument("--scales", action="store_true")
    a = ap.parse_args()

    if a.scales:
        for group, name in ((LIKELIHOOD, "Likelihood"), (IMPACT, "Impact")):
            print(f"\n## {name}")
            for k, (label, scale) in group.items():
                print(f"- --{k} · {label}: " + " · ".join(f"{v} = {d}" for v, d in scale.items()))
        return

    data = {}
    if a.json:
        data = json.load(open(a.json, encoding="utf-8"))
    for k in list(LIKELIHOOD) + list(IMPACT) + ["title", "where", "fix"]:
        v = getattr(a, k)
        if v is not None:
            data[k] = v
    missing = [k for k in list(LIKELIHOOD) + list(IMPACT) if k not in data]
    if missing:
        sys.exit("Missing factors: " + ", ".join(missing) + ". Use --scales to see the scales.")
    for k in list(LIKELIHOOD) + list(IMPACT):
        if not 0 <= float(data[k]) <= 9:
            sys.exit(f"{k} must be between 0 and 9")

    lk = sum(float(data[k]) for k in LIKELIHOOD) / len(LIKELIHOOD)
    im = sum(float(data[k]) for k in IMPACT) / len(IMPACT)
    tech = sum(float(data[k]) for k in ("confidentiality", "integrity", "availability", "accountability")) / 4
    biz = sum(float(data[k]) for k in ("financial", "reputation", "compliance", "privacy")) / 4
    sev = severity(lk, im)
    effect = {"critical": "blocks the phase", "high": "blocks the launch", "medium": "backlog before day 30", "low": "maintenance backlog", "note": "note it"}[sev]

    print(f"Likelihood {lk:.1f} ({level(lk)}) · Impact {im:.1f} ({level(im)}; technical {tech:.1f}, business {biz:.1f}) → **{sev}** · {effect}\n")
    title = data.get("title") or "[title]"
    print("| Severity | Where | What can happen | How to verify | Fix | Goes to | Lik. | Imp. |")
    print("|---|---|---|---|---|---|---|---|")
    print(f"| {sev} | {data.get('where') or '[file:line or URL]'} | {title}: [two-sentence story] | [steps or command] | {data.get('fix') or '[concrete fix]'} | [role] | {lk:.1f} | {im:.1f} |")


if __name__ == "__main__":
    main()
