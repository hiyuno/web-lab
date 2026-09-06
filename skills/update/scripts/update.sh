#!/usr/bin/env bash
# Refreshes the web-lab roles and skills linked into ~/.claude from this repo.
# Safe to run from any project: it resolves the repo root from its own path,
# because the skill folder is symlinked into ~/.claude/skills/update.
set -euo pipefail
shopt -s nullglob

# --- resolve this script's own real path, then the repo root ---
resolve_path() {
  local p="$1"
  if out="$(readlink -f "$p" 2>/dev/null)"; then
    printf '%s\n' "$out"
  else
    python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$p"
  fi
}

SCRIPT_PATH="$(resolve_path "$0")"
ROOT="$(cd "$(dirname "$SCRIPT_PATH")/../../.." && pwd)"

if [[ ! -f "$ROOT/CLAUDE.md" || ! -d "$ROOT/agents" ]]; then
  echo "error: no web-lab checkout found at $ROOT (missing CLAUDE.md or agents/)" >&2
  exit 1
fi

NO_PULL=0
DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --no-pull) NO_PULL=1 ;;
    --dry-run) DRY_RUN=1 ;;
    *)
      echo "error: unknown flag '$arg' (expected --no-pull and/or --dry-run)" >&2
      exit 1
      ;;
  esac
done

say() { printf '%s\n' "$*"; }
would() { printf '+ %s\n' "$*"; }

AGENTS_LINKED=0
SKILLS_LINKED=0
VENDOR_LINKED=0
LINKS_REMOVED=0

say "== web-lab update =="
say "repo: $ROOT"
[[ "$DRY_RUN" -eq 1 ]] && say "(dry run: no files will change)"

# --- Step: Pull ---
say ""
say "-- Pull --"
BEFORE="$(git -C "$ROOT" rev-parse HEAD)"

if [[ "$NO_PULL" -eq 1 ]]; then
  say "Skipping pull (--no-pull)"
else
  if [[ -n "$(git -C "$ROOT" status --porcelain --untracked-files=no)" ]]; then
    say "Local changes present, skipping pull"
  else
    if [[ "$DRY_RUN" -eq 1 ]]; then
      would "git -C $ROOT pull --ff-only"
    else
      if ! git -C "$ROOT" pull --ff-only; then
        say "warning: git pull failed, continuing with the current checkout"
      fi
    fi
    if [[ "$DRY_RUN" -eq 1 ]]; then
      would "git -C $ROOT submodule update --init"
    else
      if ! git -C "$ROOT" submodule update --init; then
        say "warning: submodule update failed, continuing"
      fi
    fi
  fi
fi

# --- Step: Link roles ---
say ""
say "-- Link roles --"
if [[ "$DRY_RUN" -eq 1 ]]; then
  would "mkdir -p $HOME/.claude/agents"
else
  mkdir -p "$HOME/.claude/agents"
fi

for f in "$ROOT"/agents/*.md; do
  target="$HOME/.claude/agents/$(basename "$f")"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    would "ln -sfn $f $target"
  else
    ln -sfn "$f" "$target"
  fi
  AGENTS_LINKED=$((AGENTS_LINKED + 1))
done

for link in "$HOME"/.claude/agents/*; do
  [[ -L "$link" ]] || continue
  tgt="$(readlink "$link")"
  case "$tgt" in
    "$ROOT/agents/"*)
      if [[ ! -e "$tgt" ]]; then
        if [[ "$DRY_RUN" -eq 1 ]]; then
          would "rm $link  # dangling, was $tgt"
        else
          rm "$link"
        fi
        LINKS_REMOVED=$((LINKS_REMOVED + 1))
      fi
      ;;
  esac
done

# --- Step: Link skills ---
say ""
say "-- Link skills --"
if [[ "$DRY_RUN" -eq 1 ]]; then
  would "mkdir -p $HOME/.claude/skills"
else
  mkdir -p "$HOME/.claude/skills"
fi

for d in "$ROOT"/skills/*/; do
  d="${d%/}"
  [[ -f "$d/SKILL.md" ]] || continue
  target="$HOME/.claude/skills/$(basename "$d")"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    would "ln -sfn $d $target"
  else
    ln -sfn "$d" "$target"
  fi
  SKILLS_LINKED=$((SKILLS_LINKED + 1))
done

VENDOR_DIR="$ROOT/vendor/interfaces/skills"
if [[ -d "$VENDOR_DIR" ]] && [[ -n "$(ls -A "$VENDOR_DIR" 2>/dev/null)" ]]; then
  for d in "$VENDOR_DIR"/*/; do
    d="${d%/}"
    [[ -f "$d/SKILL.md" ]] || continue
    target="$HOME/.claude/skills/$(basename "$d")"
    if [[ "$DRY_RUN" -eq 1 ]]; then
      would "ln -sfn $d $target"
    else
      ln -sfn "$d" "$target"
    fi
    VENDOR_LINKED=$((VENDOR_LINKED + 1))
  done
else
  say "warning: $VENDOR_DIR is empty or missing, skipping vendor skills (run: git -C $ROOT submodule update --init)"
fi

for link in "$HOME"/.claude/skills/*; do
  [[ -L "$link" ]] || continue
  tgt="$(readlink "$link")"
  case "$tgt" in
    "$ROOT"/*)
      if [[ ! -e "$tgt" ]]; then
        if [[ "$DRY_RUN" -eq 1 ]]; then
          would "rm $link  # dangling, was $tgt"
        else
          rm "$link"
        fi
        LINKS_REMOVED=$((LINKS_REMOVED + 1))
      fi
      ;;
  esac
done

# --- Step: Report ---
say ""
say "-- Report --"
AFTER="$(git -C "$ROOT" rev-parse HEAD)"
say "before: $BEFORE"
say "after:  $AFTER"
if [[ "$BEFORE" != "$AFTER" ]]; then
  say ""
  say "commits pulled:"
  git -C "$ROOT" log --oneline "$BEFORE..$AFTER"
fi

if [[ -d "$ROOT/vendor/interfaces" ]]; then
  VENDOR_VERSION="$(git -C "$ROOT/vendor/interfaces" describe --tags --always 2>/dev/null || echo "unknown")"
else
  VENDOR_VERSION="not present"
fi
say ""
say "interfaces submodule: $VENDOR_VERSION"

say ""
say "roles linked: $AGENTS_LINKED"
say "skills linked (web-lab): $SKILLS_LINKED"
say "skills linked (vendor):  $VENDOR_LINKED"
say "dangling links removed: $LINKS_REMOVED"

say ""
if [[ "$DRY_RUN" -eq 1 ]]; then
  say "Dry run: nothing was changed. $AGENTS_LINKED role(s) and $((SKILLS_LINKED + VENDOR_LINKED)) skill(s) would be linked into ~/.claude."
else
  say "Done: $AGENTS_LINKED role(s) and $((SKILLS_LINKED + VENDOR_LINKED)) skill(s) linked into ~/.claude, $LINKS_REMOVED dangling link(s) removed."
fi
