# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A World of Tanks client mod ("pademinune's Armor Penetration Calculator 2"). While a shell is on the reticle it computes penetration chance against the aimed component and draws the result as an in-battle overlay via OpenWG Gameface (a hard dependency — without it installed, the overlay never appears). Runs inside the WoT client's embedded **Python 2.7** (BigWorld) interpreter; there is no standalone runtime and nothing here executes outside the game client.

Two skills in `.claude/skills/` cover the underlying platform in depth — consult them instead of re-deriving this from scratch: `wot-modding-fundamentals` (how .wotmod packaging, res_mods/mods precedence, and monkey-patch "modding" works in general) and `gameface-wulf-primer` (how the Wulf/ViewModel/View/Window/res_map pipeline that drives the overlay works).

## Commands

There is no test suite, linter config, or CI in this repo — verification is manual (deploy with `build.ps1`, launch the client, enter a battle).

Both scripts resolve paths relative to themselves (run from anywhere) and require Python 2.7 on `PATH` as `python27` (override with `-Python27 "C:\path\to\python.exe"`) — compiling with Python 3 produces bytecode the client cannot load.

**Fast local iteration** — compiles every `.py` under `res\scripts\client\gui\mods` and `res\scripts\client\ap_calculator`, then deploys the compiled `.pyc` plus Gameface web assets, tooltip icons, translations, and the res_map entry as loose `res_mods` overrides into a real WoT install:
```powershell
.\build\build.ps1 -WotRoot "C:\Program Files\World_of_Tanks_NA" -Version "2.4.0.0"
```
Close the WoT client first (a running client locks files under its install dir); writing under `Program Files` may need an elevated shell. First-ever deploy needs a client restart so OpenWG picks up the new res_map entry — after that, re-running the script is enough for JS/CSS/Python edits (restart the client too if a change doesn't seem to take effect).

**Produce a real package** — same compile step, staged into `bin\package` and zipped (ZIP_STORED) into a `.wotmod`; does not touch any WoT install:
```powershell
.\build\package.ps1
```
Output is `bin\wotmods\pademinune-armor-pen-calc-<version>.wotmod`. The version comes from `src/meta.xml`'s `<version>` — that file is the single source of truth for the package version (`src/res/scripts/client/ap_calculator/debug.py`'s `VERSION` is a separate, manually-kept-in-sync constant used only for the in-client log prefix and the settings-panel title).

## What ships vs. what doesn't

Only part of the repo ends up in the client. `build.ps1`, `package.ps1`, and `uninstall.ps1` decide what ships by globbing whole directories, not by listing files. So any file dropped into a shipped directory ships, and anything outside those directories never does. Paths are relative to `src/`:

| Source | Deployed as | Notes |
|---|---|---|
| `res/scripts/client/gui/mods/*.py` | `scripts/client/gui/mods/*.pyc` | Compiled with Py2.7, recursive. Only `mod_AP_Calculator.py`, the auto-loaded entry point. |
| `res/scripts/client/ap_calculator/**/*.py` | `scripts/client/ap_calculator/**/*.pyc` | Compiled, recursive (keeps the subpackage layout). Only `.pyc` ships, never the `.py` source. |
| `res/gui/AP_Calculator_2/gameface/*` | same path | Copies only the files directly in the folder, not subfolders. `APBattleView.html` (loaded via `coui://` from the res_map entry) pulls in `.css`/`.js`, and the `.css` loads `PFDINMax-CompressedBold.ttf`. |
| `res/gui/AP_Calculator_2/tooltips/*` | same path | Settings-panel tooltip images, referenced by name from `settings_gui/aslain_settings.py` and `legacy_settings.py`. |
| `res/gui/AP_Calculator_2/translations/*` | same path | `translations_<locale>.json`, resolved by `settings_gui/language.py`. |
| `res/mods/configs/res_map/APBattleView.json` | `mods/configs/res_map/` (WoT root, **not** under `res_mods/<ver>`) | A single named file, not a glob. `package.ps1` puts it under `res/` inside the `.wotmod`. |
| `meta.xml` | `.wotmod` archive root | `package.ps1` only. `build.ps1` doesn't use it. |

**Never shipped:**
- `src/other_res/`: spare fonts, unused icons, and `wot-background.jpg` (only referenced by a commented-out rule in `APBattleView.css`). To ship a file from here, move it into a shipped directory.
- `images/`: screenshots and thumbnails for the mod listing or README.
- `build/`, `.claude/`, and `bin/` (build output, gitignored).

When adding a new asset directory or script root, update the path tables in all three `build/*.ps1` scripts. Otherwise `build.ps1` deploys it but `package.ps1` drops it, or `uninstall.ps1` leaves it behind.

## Architecture

**Entry point and load order.** `src/res/scripts/client/gui/mods/mod_AP_Calculator.py` is the file the stock client auto-loads; it does nothing but `import ap_calculator`. That triggers `src/res/scripts/client/ap_calculator/__init__.py`, which imports (in order) `core`, `settings_gui`, then `ap_logger` — import order matters, since each subpackage runs its monkey-patching `init()` calls as an import side effect rather than through any explicit "start" call.

**Shot-result hooking** (`core/ap_hooks.py`) is the core of the mod: it replaces `gun_marker_ctrl._CrosshairShotResults.getShotResult` / `__shotResultDefault` / `__shotResultModernHE` (mangled-name access required since the replacements live outside the class) to re-derive total armor crossed, ricochet/hit-track/hit-gun flags, and hit angle while the stock logic still runs. It also hooks `g_playerEvents.onAvatarReady` / `onAvatarBecomeNonPlayer` to open/close the Gameface window with battle lifecycle, and `AvatarInputHandler.activatePostmortem` to hide the overlay on death. Every code path funnels into `call_update_gui()`, which computes penetration probability (`core/ap_math.py`, a pure Gaussian-CDF calc with no game-engine dependency) and calls `gui.ap_gui.gui_state.update_gui()`.

**GUI state → Gameface bridge.** `gui/ap_gui.py` holds one `GuiState` with per-label (`ArmorLabel`/`ProbLabel`/`AngleLabel`) and `TrackIndicator` objects that dedupe against `last_state` before pushing, so redundant frames don't cross into Gameface. `gui/ap_gameface_api.py` is the actual Wulf plumbing (`ViewModel`/`ViewImpl`/`WindowImpl`, res_map-driven `ModDynAccessor` lookup) — its `APBattleVM` string/bool properties are the entire Python↔JS contract, read on the JS side by `src/res/gui/AP_Calculator_2/gameface/APBattleView.js` via a bare `ModelObserver`. The view is registered by `src/res/mods/configs/res_map/APBattleView.json` (`itemID: "APBattleView"`, must match `RES_MAP_ITEM_ID` in `ap_gameface_api.py`).

**Settings.** `gui/ap_config.py` owns `DEFAULT_CONFIG` (the canonical settings schema) and loads/saves only the non-default overrides as JSON under `mods/configs/pademinune/Armor Penetration Calculator 2/AP_Calculator-2.1.0+.json` (relative to the WoT install). `gui/ap_constants.py` materializes that config into plain class attributes (`Colors`, `Colorblind`, `ArmorLabelSettings`, etc.) at import time and again via `update_constants()` whenever settings are saved; hot game-loop code reads these classes rather than the config dict directly. `settings_gui/__init__.py` picks whichever settings UI provider is actually installed — tries `aslain_settings` (Aslain's Mod Pack API), falls back to `legacy_settings` (`ModsSettingsApi`), and silently ships with no settings panel if neither is present; the two provider modules are near-duplicates of each other's template-building code by necessity (different upstream APIs), not an oversight. `settings_gui/language.py` resolves `tr()`/`tooltip()` calls against `src/res/gui/AP_Calculator_2/translations/translations_<locale>.json`.

**Telemetry.** `ap_calculator/ap_logger.py` fires one anonymous-ish POST (player name, server, mod version) to an external endpoint the first time the account GUI shows, best-effort (swallows all exceptions). Treat this file with extra care since it's the one place player-identifying data leaves the client.

**Build vs. package duplication.** `build.ps1` and `package.ps1` intentionally duplicate the same `Invoke-PyCompile` helper and source/dest path table — one moves compiled output straight into a live WoT install for iteration, the other copies it into a disposable staging dir for zipping. Keep both in sync when changing what ships (new asset dirs, new script roots, etc.).
