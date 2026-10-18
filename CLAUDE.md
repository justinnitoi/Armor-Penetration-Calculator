# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A World of Tanks client mod ("pademinune's Armor Penetration Calculator 2"). While a shell is on the reticle it computes penetration chance against the aimed component and draws the result as an in-battle overlay in a Gameface (HTML/JS) window. Targets WoT **2.4.1+**, where the client registers mod views natively. OpenWG Gameface is still a hard dependency, but only on the JS side: `APBattleView.js` imports its shared `gui/gameface/mods/libs/model.js`, and without it the overlay never updates. Runs inside the WoT client's embedded **Python 2.7** (BigWorld) interpreter; there is no standalone runtime and nothing here executes outside the game client.

Two skills in `.claude/skills/` cover the underlying platform in depth — consult them instead of re-deriving this from scratch: `wot-modding-fundamentals` (how .wotmod packaging, res_mods/mods precedence, and monkey-patch "modding" works in general) and `gameface-wulf-primer` (how the Wulf/ViewModel/View/Window/gen_resources pipeline that drives the overlay works).

## Commands

**Tests** run offline on Python 2.7, the client's version: `python build/build.py test`, or directly `python2.7 tests/run_tests.py`. They cover the shot analysis, hooks, config, GUI state, math and translations. How they work:
- `tests/fakes.py` registers small hand-written stand-ins for the client modules the mod imports. The fake `ViewModel` records what would reach the JS.
- `tests/stock.py` downloads the **real** stock `gun_marker_ctrl.py`, pinned by `WOT_SRC_COMMIT`, into gitignored `tests/.cache/`, and loads it behind an auto-stub importer. The parity tests in `test_shot_analysis.py` compare `shot_analysis` with stock's own per-plate debug data. Never commit the downloaded WG file.
- After a client update, run `python2.7 tests/stock.py diff` to see how `_CrosshairShotResults` changed. Then bump `WOT_SRC_COMMIT`, rerun the tests, and re-port `shot_analysis` where they fail.

Gameface rendering, real collision geometry and the settings panels still need a manual check in game (deploy, launch the client, enter a battle). CI (`.github/workflows/ci.yml`) runs the tests and `package` on every push/PR to `v2`. A `v*` tag matching `VERSION` also creates a **draft** GitHub release with the `.wotmod`. There is no linter config.

Everything goes through one cross-platform script, `build/build.py` (Python 3.6+, run from anywhere — paths resolve relative to the script). It compiles the mod with a **separate Python 2.7** interpreter, found as the first of `python27` / `python2.7` / `python2` on `PATH`, else `C:\Program Files\Python27\python.exe` on Windows (`DEFAULT_PYTHON27`; override with `--python27 /path/to/python2.7`). Shell aliases/functions don't count: the lookup uses `shutil.which`, which only sees real executables, and refuses to run if that interpreter isn't 2.7 — the client cannot load any other bytecode. What ships is one table at the top of the script (`PY_ROOTS` compiled, `ASSETS` copied, all mirrored from `src/res/`), shared by every subcommand; add new script roots or asset dirs there.

**Fast local iteration** — compiles every `.py` under `src/res/scripts/client/gui/mods` and `src/res/scripts/client/ap_calculator` and deploys the `.pyc` files plus Gameface web assets, tooltip icons, translations, and the `gui/gen_resources` view registration as loose `res_mods/<version>/` overrides into a real WoT install (also removes a stale sibling `.py` per module, and the pre-2.2.0 `mods/configs/res_map/APBattleView.json` if present):
```
python build/build.py deploy --wot-root "C:/Program Files/World_of_Tanks_NA" --version 2.4.1.0
```
`--wot-root` defaults to `C:\Program Files\World_of_Tanks_NA` on Windows and is required elsewhere; `--version` defaults to `2.4.1.0`. Close the WoT client first (a running client locks files under its install dir); writing under `Program Files` may need an elevated shell. Adding a new `gen_resources` declaration needs a client restart (the client reads them at startup); JS/CSS/Python edits just need a re-deploy and a new battle (restart the client too if a change doesn't seem to take effect).

**Remove a deploy** — `python build/build.py uninstall --wot-root ... --version ...` deletes exactly what `deploy` writes (derived from the same table) and prunes emptied directories.

**Produce a real package** — same compile step, staged into `bin/package` and zipped (ZIP_STORED, `meta.xml` at the root, reproducible) into a `.wotmod`; does not touch any WoT install:
```
python build/build.py package
```
Output is `bin/wotmods/pademinune-AP_Calculator-<version>.wotmod`. The version comes from `VERSION` in `src/res/scripts/client/ap_calculator/debug.py` — the single source of truth for the mod version (also used for the in-client log prefix, the settings-panel title, and the telemetry payload). `package` rewrites `src/meta.xml`'s `<version>` to match before staging, so never edit the version in `meta.xml` by hand.

## Game client source dependencies

The mod has no stable API to build on. It imports and monkey-patches stock client modules, so it breaks whenever WG renames or reshapes any of the items below. The reference for these files is the decompiled client at [izeberg/wot-src, `NA` branch](https://github.com/izeberg/wot-src/tree/NA). Paths below are relative to `sources/res/scripts/` in that repo. After a client update, diff these files first.

**Patched or mirrored (highest breakage risk)**: `core/ap_hooks.py`, `core/shot_analysis.py`
- `client/AvatarInputHandler/gun_marker_ctrl.py`, class `_CrosshairShotResults` (not `_StandardShotResult`, which has its own `getShotResult`):
  - `getShotResult`, `__shotResultDefault` and `__shotResultModernHE` are **wrapped, never replaced**: the stock method runs first and its result is returned untouched, so the reticle's coloring always matches vanilla. Afterwards `shot_analysis.analyze_default` / `analyze_modern_he` re-walk the same `collisionsDetails` to compute the overlay's armor/angle/flags. Those two functions **mirror** the stock bodies' armor logic. When the stock methods change, compare them line by line with the mirrors (the parity tests in `tests/` show what moved). A mismatch can only make the overlay's numbers drift; it can't break the reticle.
  - `init()` runs `_check_compatibility()` first. If any internal below is missing, or a wrapped method's signature changed (`(cls, gunMarker, collisionsDetails, fullPiercingPower, shell, minPP, maxPP, entity)`, and `getShotResult(cls, gunMarker, excludeTeam, piercingMultiplier)`), it logs "incompatible" and patches nothing.
  - Overlay-side errors go through `debug.log_exception()` (each distinct error logged once) and are swallowed. Never let one propagate out of a wrapper.
  - The mirrors call these class internals: `_shouldRicochet`, `_computePenetrationArmor`, `_SHELL_EXTRA_DATA`, and the name-mangled `__isDestructibleComponent`.
  - They also read fields off the stock objects passed in:
    - collision details: `compName`, `dist`, `hitAngleCos`, `matInfo`
    - `matInfo`: `armor`, `kind`, `useHitAngle`, `collideOnceOnly`, `vehicleDamageFactor`
    - shell descriptor: `kind`, `type.piercingPowerLossFactorByDistance`, `type.shieldPenetration`, `type.maxDamage`
- `client/gui/Scaleform/daapi/view/battle/shared/crosshair/plugins.py`: `ShotResultIndicatorPlugin.__onGunMarkerStateChanged(markerType, ...)` is wrapped (`_install_marker_filter`). This plugin is the **only caller** of `getShotResult`: once per marker type (client and server) on each update, and only while the player's reticle setting colors by shot result. The wrapper makes the overlay follow only the server marker while `GunMarkersSetInfo().isServerMarkerActivated`, otherwise every marker. Optional: if the import fails, it logs and the overlay follows every marker.
- `client/AvatarInputHandler/__init__.py`: `AvatarInputHandler.activatePostmortem` is wrapped.
- `client/vehicle_systems/tankStructure.py`: `TankPartIndexes` is the source of the hardcoded `compName` checks (`0` chassis, `3` gun, `>= 4` extra track pairs). These are literals in `shot_analysis.py`, not imports, so a renumbering fails silently.

**Imported (breaks on rename/move)**
| Module | Names | Used by |
|---|---|---|
| `client/aih_constants.py` | `SHOT_RESULT`, `GUN_MARKER_TYPE` | `core/ap_hooks.py` |
| `common/items/components/component_constants.py` | `MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS`, `MODERN_HE_DAMAGE_ABSORPTION_FACTOR` (read with a `0.0` fallback) | `core/ap_hooks.py` |
| `client/gui/battle_control/controllers/crosshair_proxy.py` | `GunMarkersSetInfo` (`.isServerMarkerActivated`) | `core/ap_hooks.py` (optional) |
| `client/PlayerEvents.py` | `g_playerEvents`: `onAvatarReady`, `onAvatarBecomeNonPlayer`, `onAccountShowGUI` | `core/ap_hooks.py`, `ap_logger.py` |
| `client/frameworks/wulf/__init__.py` | `PositionAnchor`, `ViewFlags`, `ViewModel`, `ViewSettings`, `WindowFlags`, `WindowLayer` | `gui/ap_gameface_api.py` |
| `client/gui/impl/gen/__init__.py` | `R` | `gui/ap_gameface_api.py` |
| `client/gui/impl/gen/resources/__init__.py` | `R` (must support `.dyn()`) | `gui/ap_gameface_api.py` (`_layout_id()`) |
| `client/gui/impl/pub/__init__.py` | `ViewImpl`, `WindowImpl` | `gui/ap_gameface_api.py` |
| `common/debug_utils.py` | `LOG_CURRENT_EXCEPTION` | `gui/ap_gameface_api.py` |
| `client/helpers/__init__.py` | `getClientLanguage` | `settings_gui/language.py` |

Engine built-ins (`BigWorld`, `ResMgr`) are native modules with no `.py` in wot-src. The mod uses `BigWorld.player()` (`.name`, `.connectionMgr.serverUserName`) and `BigWorld.wg_openWebBrowser`, plus `ResMgr.openSection`. Third-party imports are not in wot-src either. They come from other mods: `gui.modsSettingsApi` and `gui.aslainMenu`, both optional (see Settings).

`.claude/routines/wot-src-watch.md` drives a scheduled routine that diffs wot-src for changes to these files. Its watch list duplicates this section, so update both when the mod starts or stops importing or patching a stock module.

## Architecture

**Entry point and load order.** `src/res/scripts/client/gui/mods/mod_AP_Calculator.py` is the file the stock client auto-loads; it does nothing but `import ap_calculator`. That triggers `src/res/scripts/client/ap_calculator/__init__.py`, which imports (in order) `core`, `settings_gui`, then `ap_logger` — import order matters, since each subpackage runs its monkey-patching `init()` calls as an import side effect rather than through any explicit "start" call.

**Shot-result hooking** (`core/ap_hooks.py`) is the core of the mod: it wraps `gun_marker_ctrl._CrosshairShotResults.getShotResult` / `__shotResultDefault` / `__shotResultModernHE` (mangled-name access required since the wrappers live outside the class). After the stock method returns, `core/shot_analysis.py` re-derives total armor crossed, ricochet/hit-track/hit-gun flags, and hit angle into a `ShotAnalysis`. It has no game imports; the stock class is passed in as `cls`. It also hooks `g_playerEvents.onAvatarReady` / `onAvatarBecomeNonPlayer` to open/close the Gameface window with battle lifecycle, and `AvatarInputHandler.activatePostmortem` to hide the overlay on death. Every analysis funnels into `call_update_gui()`, which computes penetration probability (`core/ap_math.py`, a pure Gaussian-CDF calc with no game-engine dependency) and calls `gui.ap_gui.gui_state.update_gui()`.

**GUI state → Gameface bridge.** `gui/ap_gui.py` holds one `GuiState` with per-label (`ArmorLabel`/`ProbLabel`/`AngleLabel`) and `TrackIndicator` objects that dedupe against `last_state` before pushing, so redundant frames don't cross into Gameface; they push `(name, value)` pairs through `ap_window.update_params()`. `gui/ap_gameface_api.py` is the actual Wulf plumbing: `GamefaceWindow` owns the window lifecycle (`open_window` / `update_params` / `close_window`) and a cache of last-sent values, over `APBattleVM`/`APBattleView`/`APBattleWindow` (`ViewModel`/`ViewImpl`/`WindowImpl`, layoutID looked up natively via `R.dyn(...)` in `_layout_id()`). The `(name, default)` list passed to `GamefaceWindow(...)` for the module-level `ap_window` is the entire Python↔JS contract: each entry's default value fixes its type (`str` → string property, `bool` → bool property), its list position is its property index (`APBattleVM` sizes itself from the list), and `update_params()` raises `TypeError` on a value of any other type and skips one that hasn't changed. The check is an exact `type()` match, so a Python 2 `unicode` value is rejected for a `str` parameter — encode it to `str` first. JS reads them by name in `src/res/gui/AP_Calculator_2/gameface/APBattleView.js` through a bare `ModelObserver`. Adding a parameter takes two changes: an entry in the `ap_window` list, and reading it in `render()` in the JS. The view is registered by `src/res/gui/gen_resources/ap_calculator_2.json`, which the 2.4.1+ client loads natively into its `R` tree (id `R.mods.ap_calculator_2.views.APBattleView` — must match `RES_MOD_ID` and the path walked in `_layout_id()`). Don't reintroduce `openwg_gameface.ModDynAccessor` / `mods/configs/res_map/`: on WG 2.4.1+ OpenWG ignores those and the accessor always returns `-1`, so the window silently never opens.

**Settings.** `gui/ap_config.py` owns `DEFAULT_CONFIG`, a flat dict of dotted keys (`"track_indicator.enabled"`) that is the canonical settings schema. It saves only the non-default overrides as JSON to `mods/configs/pademinune/Armor Penetration Calculator 2/config.json` (relative to the WoT install). `load_config()` validates per key: an unknown key, or a value `_coerce()` can't convert to its default's type (int and float convert to each other, nothing else does), is dropped and logged on its own, and the file is rewritten. Only an unparsable file resets everything, after being kept as `config.json.bak`. The file also stores `config_version` (`CONFIG_VERSION`); bump it and migrate in `load_config()` if a key is ever renamed. Python 2's `json.load` returns strings as `unicode`, so `_coerce` converts them back to `str` (`_to_str`). Values from the settings panels go through the same `_coerce` in `update_global_settings()`, because the overlay's exact-type check would reject a `unicode` color. An empty `.jailbreak` file in that same folder sets `JAILBROKEN`, which force-enables the track indicator whatever the setting says. `gui/ap_constants.py` materializes that config into plain class attributes (`Colors`, `Colorblind`, `ArmorLabelSettings`, etc.) at import time and again via `update_constants()` whenever settings are saved; hot game-loop code reads these classes rather than the config dict directly. `settings_gui/__init__.py` picks whichever settings UI provider is actually installed — tries `aslain_settings` (Aslain's Mod Menu, `gui.aslainMenu`), falls back to `legacy_settings` (`ModsSettingsApi`), and silently ships with no settings panel if neither is present; the two provider modules are near-duplicates of each other's template-building code by necessity (different upstream APIs), not an oversight. The Mod Menu API is documented at [Aslain/modmenu](https://github.com/Aslain/modmenu) (`docs/api.md` walkthrough, `docs/reference.md` every builder/method, `examples/`); that repo is the most up-to-date source, so read it there (e.g. `https://raw.githubusercontent.com/Aslain/modmenu/main/docs/reference.md`) before changing `aslain_settings.py` rather than inferring the API from `legacy_settings`. `settings_gui/language.py` resolves `tr()`/`tooltip()` calls against `src/res/gui/AP_Calculator_2/translations/translations_<locale>.json`.

**Telemetry.** `ap_calculator/ap_logger.py` fires one POST (player name, server, mod version) to an external endpoint the first time the account GUI shows, best-effort (swallows all exceptions). The `BigWorld` fields are read on the main thread; only the request runs on a daemon thread, so a slow endpoint can't stall the garage. The payload and the lack of an opt-out are deliberate owner decisions; don't change them without asking. Treat this file with extra care since it's the one place player-identifying data leaves the client.
