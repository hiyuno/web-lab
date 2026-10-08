# Learnings ledger

What the Web Master has already reviewed from each project's `docs/learnings.md`, so the next
`/web-master harvest` only brings what is new or changed. One row per source entry. Written only
by the Web Master, here in web-lab; nothing is ever written back into a project.

- **project**: the project's folder name under `~/Documents/GitSync/`.
- **role**: the `## <role>` section the entry was under (or `notes` for "Notes for web-lab").
- **header**: the entry's `yyyy-mm-dd · <project> · phase N` line.
- **fingerprint**: first 8 hex characters of sha1 of project + role + header + body. If the body
  changes in the project, the fingerprint changes and the entry comes back in the next harvest.
- **decision**: `merged` (evidence for an existing rule), `discarded` (specific to that site),
  `deferred` (kept in `learnings/<role>.md`), `promoted → <destination>`, `skipped: sensitive`
  (contained secrets, personal data or client content), `reverted`, `superseded`.
- **date**: the day the decision was made.

Rows are never deleted. A decision that changes gets a new row; the old one is marked
`superseded`.

| project | role | header | fingerprint | decision | date |
|---------|------|--------|-------------|----------|------|
