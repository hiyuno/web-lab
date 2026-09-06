# Saved style presets

Presets saved from the style lab (`skills/design-system/app`, "Save preset to web-lab"). One
file per preset, `<slug>.tokens.json`, in the web-lab DTCG schema with the knob positions and
the sample copy in `$extensions.web-lab.lab`. They are versioned with the repo, so they travel
with the roles.

## Using one in a project

Say the preset's name when starting or designing a project: "use Template A". Frost then:

1. Copies `skills/design-system/presets/<slug>.tokens.json` to the project's
   `docs/04-design/tokens.tokens.json` and runs `tokens_to_tailwind.py` to get `tokens.css` with
   the contrast check.
2. Takes the knobs as the visual direction (step 4.1 is reduced to confirming it with the real
   copy instead of exploring three variants), and continues with components, templates and the
   prototype on those tokens.
3. Osmani builds on that `tokens.css` in phase 5.

Headless, from the app folder:

```bash
npx tsx src/cli.ts --saved "Template A" --json tokens.tokens.json --css tokens.css
```

## Editing

Open the lab, pick the preset under "Saved in web-lab", tune, and save again with the same name
to overwrite. "Delete" removes the file. Never store client secrets or personal data here; a
preset is design decisions only.
