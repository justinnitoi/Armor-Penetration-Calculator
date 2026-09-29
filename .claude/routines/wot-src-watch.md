# wot-src watch (daily Routine)

Instructions for the scheduled Routine that watches the decompiled WoT client
sources for changes that affect this mod. Each firing starts in a fresh
session with no memory of earlier runs; everything it needs is in this file
and in the state file described below.

## Inputs

- **Upstream:** `https://github.com/izeberg/wot-src.git`, branch `NA`
  (read-only — never push there).
- **Mod repo:** `justinnitoi/armor-penetration-calculator`, base branch `2.0`.
- **State:** branch `wot-src-watch` of the mod repo, file
  `.claude/wot-src-watch.json`:
  ```json
  {
    "branch": "NA",
    "last_checked_sha": "<full sha>",
    "last_checked_subject": "<commit subject, e.g. v.2.4.0.1 #950>",
    "last_checked_at": "<UTC ISO-8601>",
    "last_reported_sha": "<sha of last run that found relevant changes, or null>",
    "last_pr": "<url of last draft PR, or null>"
  }
  ```

## Watch list

Paths are relative to the wot-src repo root. Keep this list in sync with what
the mod imports/patches (`grep -rn "^from\|^import" src/res/scripts/client`
and the patch sites in `core/ap_hooks.py`) — add to it if a new stock import
appears.

**Critical** — the mod patches or copies code from these; changes usually
need a mod update:

| wot-src path | What the mod depends on |
|---|---|
| `sources/res/scripts/client/AvatarInputHandler/gun_marker_ctrl.py` | `_CrosshairShotResults.getShotResult`, `__shotResultDefault`, `__shotResultModernHE` (overridden; the two `__shotResult*` bodies are largely copied into `ap_hooks.py`), and mangled helpers `__isDestructibleComponent`, `__collectDebugPiercingData`, `__sendDebugInfo` called by name |
| `sources/res/scripts/client/AvatarInputHandler/__init__.py` | `AvatarInputHandler.activatePostmortem` (wrapped), `gun_marker_ctrl` import |
| `sources/res/scripts/client/PlayerEvents.py` | `g_playerEvents.onAvatarReady`, `onAvatarBecomeNonPlayer`, `onAccountShowGUI` |
| `sources/res/scripts/client/aih_constants.py` | `SHOT_RESULT` |
| `sources/res/scripts/common/items/components/component_constants.py` | `MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS` |

**Secondary** — review, but these rarely break the mod:

| wot-src path | What the mod depends on |
|---|---|
| `sources/res/scripts/client/frameworks/wulf/` | `PositionAnchor`, `ViewFlags`, `ViewModel`, `ViewSettings`, `WindowFlags`, `WindowLayer` (`gui/ap_gameface_api.py`) |
| `sources/res/scripts/client/gui/impl/pub/` | `ViewImpl`, `WindowImpl` |
| `sources/res/scripts/client/helpers/__init__.py` | `getClientLanguage` only |
| `sources/res/scripts/common/debug_utils.py` | `LOG_CURRENT_EXCEPTION` only |

## Steps

1. **Load state.** Fetch the `wot-src-watch` branch of the mod repo and read
   `.claude/wot-src-watch.json`. If it is missing or unreadable, stop and
   report that as the run's result (do not guess a baseline).

2. **Fetch upstream.** Blobless clone so it stays small:
   `git clone --filter=blob:none --no-checkout --branch NA https://github.com/izeberg/wot-src.git wotsrc`
   Record the new `HEAD` sha and subject. If `HEAD == last_checked_sha`,
   stop: nothing new upstream. No PR, no state change needed.

3. **Diff the watch list.**
   `git diff --stat <last_checked_sha> HEAD -- <every watch-list path>`
   - Empty → no relevant change. Update the state file (new
     `last_checked_sha`/`subject`/`at`), push it, and finish with a one-line
     "no relevant changes in <old>..<new>" result.
   - Non-empty → continue.

4. **Analyze.** For each changed watched file, read the actual diff. Then,
   against the mod code on `2.0`:
   - For `gun_marker_ctrl.py`: extract the new stock bodies of
     `getShotResult`, `__shotResultDefault`, `__shotResultModernHE` and diff
     them against the old stock bodies. Map every stock change onto the
     corresponding spot in `src/res/scripts/client/ap_calculator/core/ap_hooks.py`
     (`my_shot_result_default` / `my_shot_result_modern_he` /
     `my_get_shot_result` wrapper). Check each signature still matches what the
     wrapper passes (`cls, gunMarker, excludeTeam, piercingMultiplier`).
   - Confirm every mangled name the mod touches
     (`_CrosshairShotResults__isDestructibleComponent`,
     `__collectDebugPiercingData`, `__sendDebugInfo`, `__shotResultDefault`,
     `__shotResultModernHE`) still exists on `_CrosshairShotResults`.
   - For every other changed file: confirm each symbol the mod imports or
     patches still exists with a compatible signature.
   Classify the outcome: **no action needed**, **fix ported**, or
   **needs a human decision** (e.g. stock logic restructured so the copied
   bodies can't be mechanically updated).

5. **Port the fix** (only if action is needed).
   - Branch from `origin/2.0`: `wot-src/NA-<first 8 chars of new sha>`.
   - Make the minimal change that brings the mod in line with the new stock
     code. Preserve the mod's own additions (armor/angle/track bookkeeping
     and `call_update_gui()` funnel) — only mirror what stock changed.
   - Do not bump `src/meta.xml` / `debug.py` versions; the maintainer does
     that on release.
   - Syntax check: if a Python 2.7 interpreter is available, run
     `python2.7 -m py_compile` on every changed `.py`. If not, say so in the
     PR — do **not** compile with Python 3 as a substitute for a real check
     (only use `python3 -m py_compile` as an extra sanity pass, noting its
     limits).
   - Commit, push the branch, and open a **draft** PR into `2.0` titled
     `wot-src NA <subject>: <one-line summary>`. PR body: the report (step
     6) plus an in-client test checklist (deploy with `build.ps1`, enter a
     battle, aim at armor/tracks/gun, try AP/APCR/HEAT/HE incl. modern HE,
     die and confirm the overlay hides).
   - If the outcome is **needs a human decision**, still open the draft PR
     (with whatever partial port is safe, or no code change) so the report
     and proposed approach live in one place, and say clearly what the
     maintainer has to decide.

6. **Report.** The run's final message (which is emailed) must contain:
   - upstream range checked: `<old sha> (<subject>) → <new sha> (<subject>)`
   - each changed watched file with a 1–3 line plain-English summary
   - the outcome classification
   - the draft PR link, if one was opened
   - anything that could not be verified (always: in-client testing)

7. **Save state.** Update `.claude/wot-src-watch.json` on `wot-src-watch`
   (`last_checked_*`, plus `last_reported_sha`/`last_pr` when a PR was
   opened) and push it. Only advance `last_checked_sha` after the PR (if
   any) is open — a failed run must be retried from the same baseline next
   time.

## Pushing

Push state updates to `wot-src-watch` and fixes to `wot-src/NA-<sha>`. If the
session's git access only allows pushing to a session-designated branch,
use the GitHub MCP tools instead: `create_or_update_file` for the state file
on `wot-src-watch`, and for the fix either `push_files` to
`wot-src/NA-<sha>` (after `create_branch` from `2.0`) or the designated
branch. Never push to `2.0` directly, never force-push, never touch
`izeberg/wot-src`.
