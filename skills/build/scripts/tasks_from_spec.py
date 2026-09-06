#!/usr/bin/env python3
"""Phase 5, step 5.2: generates docs/05-development/tasks.md from the spec's stories.

Reads docs/01-discovery/spec.md (the /discovery template): "### S-xx · title" sections, the
"As a ..., I want ..., so that ..." sentence, "Priority: ..." and the "- Given ..., when ...,
then ..." criteria. Emits one section per story with the criteria as test cases and an empty
task table to complete with references/task.md.

Usage:
  tasks_from_spec.py docs/01-discovery/spec.md > docs/05-development/tasks.md
  tasks_from_spec.py spec.md --only must   # filter by priority
"""
import argparse, re, sys
from datetime import date

STORY = re.compile(r"^###\s+(S-\d+)\s*[·\-–:]\s*(.+?)\s*$", re.M)


def parse(md):
    heads = list(STORY.finditer(md))
    stories = []
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(md)
        body = md[h.end():end]
        # cut at the next level-2 section if any
        cut = re.search(r"^## ", body, re.M)
        if cut:
            body = body[:cut.start()]
        asa = re.search(r"^\s*As an?\s+(.+?)$", body, re.M | re.I)
        prio = re.search(r"^\s*Priority:\s*(\w+)", body, re.M | re.I)
        crits = [c.strip() for c in re.findall(r"^\s*[-*]\s+(Given\b.+?)$", body, re.M | re.I)]
        stories.append(dict(id=h.group(1), title=h.group(2).strip(),
                            asa=("As a " + asa.group(1).strip()) if asa else "",
                            prio=(prio.group(1).lower() if prio else "no priority"),
                            crits=crits))
    return stories


def render(stories, only=None):
    out = ["# Tasks · [project]", "",
           f"Date: {date.today().isoformat()} · Generated from docs/01-discovery/spec.md · Complete each task with references/task.md",
           "", "Track: `fe` (Osmani) · `be` (Hopper) · `infra` (foundation) · `media` (Bellard). Status: `pending` → `in progress` → `in review` → `done`.", "",
           "## Work order", "",
           "1. T-000 repo foundation (step 5.1)", "2. Base components: button, field, link, header, footer",
           "3. Templates in sitemap order", "4. Flows with data (if there is a backend)", "5. Staging integration", ""]
    n = 0
    for s in stories:
        if only and s["prio"] != only:
            continue
        n += 1
        out += [f"## {s['id']} · {s['title']}", "", f"Priority: {s['prio']}", ""]
        if s["asa"]:
            out += [s["asa"], ""]
        out += ["### Test cases (from the acceptance criteria)", ""]
        if s["crits"]:
            out += ["| # | Criterion | Test type | File | Status |", "|---|-----------|-----------|------|--------|"]
            for j, c in enumerate(s["crits"], 1):
                out.append(f"| {s['id']}.C{j} | {c} | unit / e2e | | red |")
        else:
            out.append("_No criteria in the spec. Go back to Cooper before creating tasks._")
        out += ["", "### Tasks", "",
                "| Id | Task | Track | Depends on | Covers | Status | PR |",
                "|----|------|-------|------------|--------|--------|----|",
                f"| {s['id']}.T1 | | fe / be | | {s['id']}.C1 | pending | |", ""]
    out += ["## Out of this phase", "", "- [could stories postponed, with a reason]", ""]
    if n == 0:
        out.append("_No `### S-xx · title` stories found in the spec._")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--only", choices=["must", "should", "could"])
    a = ap.parse_args()
    stories = parse(open(a.spec, encoding="utf-8").read())
    if not stories:
        sys.exit("No stories in the format '### S-01 · title' found in the spec.")
    print(render(stories, a.only))
    print(f"{len(stories)} stories, {sum(len(s['crits']) for s in stories)} criteria", file=sys.stderr)


if __name__ == "__main__":
    main()
