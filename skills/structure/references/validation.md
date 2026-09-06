# Structure validation · [project]

Date: [yyyy-mm-dd] · Author: Rosenfeld

## Card sorting (step 2.3)

**Preparation.** One card per content item, between 30 and 60, with a neutral name (not the
label you want to validate). Open if there is no prior structure: participants group and name.
Closed if you want to validate categories already proposed.

**Script for the user or participant.**
1. "Here are cards with things the site will have. Group them however feels natural. There is no right answer."
2. "Give each group a name, with the words you would use to search for it."
3. "Any card you did not know where to put? Any you would put in two places?"

**Tools.** With remote people: OptimalSort, Maze or a Miro board. With the user as proxy: a table
in this document.

**Result.** Table in `organization.md`: groups, cards, agreement percentage and names. Agreement
under 50 % on a card means it belongs in two places or needs another name.

## Tree testing (step 2.7)

**Preparation.** The sitemap hierarchy in plain text, labels only, no design or descriptions.
Five to eight tasks covering the main tasks in `flows.md`, written without using the labels'
words ("where would you find out how much it costs?" and not "where is Pricing?").

**Script.**
1. "I am going to show you a site's menu as a list. For each question, tell me where you would click first and then where you would go until you find it."
2. One task at a time. Do not help. Note the first click, the path and whether they got there.
3. At the end: "Any label you did not understand?"

**Record.**

| Task | Correct target | Participant | First click | Path | Got there | Direct (no backtracking) |
|------|----------------|-------------|-------------|------|-----------|--------------------------|
| | | P1 | | | yes/no | yes/no |

**Summary per task.**

| Task | Success (%) | Correct first click (%) | Direct (%) | Diagnosis | Sitemap change |
|------|-------------|-------------------------|------------|-----------|----------------|
| | | | | label / location / missing page | |

**Interpretation.** Low success with correct first click: the problem is at the second level.
Wrong first click in more than half: the top-level label does not smell like what is behind it.
High success but indirect: it works but costs; review nearby names.

**Threshold.** Fewer than five participants or participants who already know the project: note
"not validated" and continue. Decisions are marked as assumptions in the spec.

## Result

- Participants: [n] · Proxy: yes/no
- Changes applied to the sitemap: [ ]
- Pending validation: [ ]
