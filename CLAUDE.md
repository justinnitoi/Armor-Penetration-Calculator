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

## Game client source dependencies

The mod has no stable API to build on. It imports and monkey-patches stock client modules, so it breaks whenever WG renames or reshapes any of the items below. The reference for these files is the decompiled client at [izeberg/wot-src, `NA` branch](https://github.com/izeberg/wot-src/tree/NA). Paths below are relative to `sources/res/scripts/` in that repo. After a client update, diff these files first.

**Patched or replicated (highest breakage risk)**: `core/ap_hooks.py`
- `client/AvatarInputHandler/gun_marker_ctrl.py`, class `_CrosshairShotResults` (not `_StandardShotResult`, which has its own `getShotResult`):
  - `getShotResult` is wrapped.
  - `__shotResultDefault` and `__shotResultModernHE` are **replaced wholesale**, with copies of the stock bodies plus armor-tracking additions. When the stock versions change, re-port them by hand: compare the stock method line by line against `my_shot_result_default` / `my_shot_result_modern_he`. Signatures must stay `(cls, gunMarker, collisionsDetails, fullPiercingPower, shell, minPP, maxPP, entity)`.
  - The replacements call these class internals: `_shouldRicochet`, `_computePenetrationArmor`, `_SHELL_EXTRA_DATA`, `_CRIT_ONLY_SHOT_RESULT`, and the name-mangled `__isDestructibleComponent`, `__collectDebugPiercingData`, `__sendDebugInfo`.
  - They also read fields off the stock objects passed in:
    - collision details: `compName`, `dist`, `hitAngleCos`, `matInfo`
    - `matInfo`: `armor`, `kind`, `useHitAngle`, `collideOnceOnly`, `vehicleDamageFactor`, `extra`
    - shell descriptor: `kind`, `piercingPowerRandomization`, `armorDamage`, `type.piercingPowerLossFactorByDistance`, `type.shieldPenetration`, `type.maxDamage`
    - `entity.health`
- `client/AvatarInputHandler/__init__.py`: `AvatarInputHandler.activatePostmortem` is wrapped.
- `client/vehicle_systems/tankStructure.py`: `TankPartIndexes` is the source of the hardcoded `compName` checks (`0` chassis, `3` gun, `>= 4` extra track pairs). These are literals in `ap_hooks.py`, not imports, so a renumbering fails silently.

**Imported (breaks on rename/move)**
| Module | Names | Used by |
|---|---|---|
| `client/aih_constants.py` | `SHOT_RESULT` | `core/ap_hooks.py` |
| `common/items/components/component_constants.py` | `MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS` | `core/ap_hooks.py` |
| `client/PlayerEvents.py` | `g_playerEvents`: `onAvatarReady`, `onAvatarBecomeNonPlayer`, `onAccountShowGUI` | `core/ap_hooks.py`, `ap_logger.py` |
| `client/frameworks/wulf/__init__.py` | `PositionAnchor`, `ViewFlags`, `ViewModel`, `ViewSettings`, `WindowFlags`, `WindowLayer` | `gui/ap_gameface_api.py` |
| `client/gui/impl/pub/__init__.py` | `ViewImpl`, `WindowImpl` | `gui/ap_gameface_api.py` |
| `common/debug_utils.py` | `LOG_CURRENT_EXCEPTION` | `gui/ap_gameface_api.py` |
| `client/helpers/__init__.py` | `getClientLanguage` | `settings_gui/language.py` |

Engine built-ins (`BigWorld`, `ResMgr`) are native modules with no `.py` in wot-src. The mod uses `BigWorld.player()` (`.name`, `.connectionMgr.serverUserName`) and `BigWorld.wg_openWebBrowser`, plus `ResMgr.openSection`. Third-party imports are not in wot-src either. They come from other mods: `openwg_gameface` (`ModDynAccessor`), `gui.modsSettingsApi`, and `gui.aslainMenu`.

## Architecture

**Entry point and load order.** `src/res/scripts/client/gui/mods/mod_AP_Calculator.py` is the file the stock client auto-loads; it does nothing but `import ap_calculator`. That triggers `src/res/scripts/client/ap_calculator/__init__.py`, which imports (in order) `core`, `settings_gui`, then `ap_logger` — import order matters, since each subpackage runs its monkey-patching `init()` calls as an import side effect rather than through any explicit "start" call.

**Shot-result hooking** (`core/ap_hooks.py`) is the core of the mod: it replaces `gun_marker_ctrl._CrosshairShotResults.getShotResult` / `__shotResultDefault` / `__shotResultModernHE` (mangled-name access required since the replacements live outside the class) to re-derive total armor crossed, ricochet/hit-track/hit-gun flags, and hit angle while the stock logic still runs. It also hooks `g_playerEvents.onAvatarReady` / `onAvatarBecomeNonPlayer` to open/close the Gameface window with battle lifecycle, and `AvatarInputHandler.activatePostmortem` to hide the overlay on death. Every code path funnels into `call_update_gui()`, which computes penetration probability (`core/ap_math.py`, a pure Gaussian-CDF calc with no game-engine dependency) and calls `gui.ap_gui.gui_state.update_gui()`.

**GUI state → Gameface bridge.** `gui/ap_gui.py` holds one `GuiState` with per-label (`ArmorLabel`/`ProbLabel`/`AngleLabel`) and `TrackIndicator` objects that dedupe against `last_state` before pushing, so redundant frames don't cross into Gameface. `gui/ap_gameface_api.py` is the actual Wulf plumbing (`ViewModel`/`ViewImpl`/`WindowImpl`, res_map-driven `ModDynAccessor` lookup) — its `APBattleVM` string/bool properties are the entire Python↔JS contract, read on the JS side by `src/res/gui/AP_Calculator_2/gameface/APBattleView.js` via a bare `ModelObserver`. The view is registered by `src/res/mods/configs/res_map/APBattleView.json` (`itemID: "APBattleView"`, must match `RES_MAP_ITEM_ID` in `ap_gameface_api.py`).

**Settings.** `gui/ap_config.py` owns `DEFAULT_CONFIG` (the canonical settings schema) and loads/saves only the non-default overrides as JSON under `mods/configs/pademinune/Armor Penetration Calculator 2/AP_Calculator-2.1.0+.json` (relative to the WoT install). `gui/ap_constants.py` materializes that config into plain class attributes (`Colors`, `Colorblind`, `ArmorLabelSettings`, etc.) at import time and again via `update_constants()` whenever settings are saved; hot game-loop code reads these classes rather than the config dict directly. `settings_gui/__init__.py` picks whichever settings UI provider is actually installed — tries `aslain_settings` (Aslain's Mod Pack API), falls back to `legacy_settings` (`ModsSettingsApi`), and silently ships with no settings panel if neither is present; the two provider modules are near-duplicates of each other's template-building code by necessity (different upstream APIs), not an oversight. `settings_gui/language.py` resolves `tr()`/`tooltip()` calls against `src/res/gui/AP_Calculator_2/translations/translations_<locale>.json`.

**Telemetry.** `ap_calculator/ap_logger.py` fires one anonymous-ish POST (player name, server, mod version) to an external endpoint the first time the account GUI shows, best-effort (swallows all exceptions). Treat this file with extra care since it's the one place player-identifying data leaves the client.

**Build vs. package duplication.** `build.ps1` and `package.ps1` intentionally duplicate the same `Invoke-PyCompile` helper and source/dest path table — one moves compiled output straight into a live WoT install for iteration, the other copies it into a disposable staging dir for zipping. Keep both in sync when changing what ships (new asset dirs, new script roots, etc.).
