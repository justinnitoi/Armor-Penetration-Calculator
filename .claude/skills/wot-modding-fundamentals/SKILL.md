---
name: wot-modding-fundamentals
description: Use when the user asks general questions about how World of Tanks client modding works — not this specific project's features, but the mechanics any WoT mod relies on: what a .wotmod package actually is (ZIP_STORED + meta.xml + res/ tree), res_mods vs mods/VERSION precedence and the per-version folder trap, why scripts/client/gui/mods/mod_*.py auto-loads while other paths shadow stock game modules, monkey-patching stock Python classes/functions as "the modding API" (there isn't a real one), Python 2.7 bytecode version-locking and stale .py/.pyc shadowing, common third-party mod frameworks (OpenWG Gameface, ModsSettingsApi, ModsListApi) as soft/optional dependencies, where a mod should persist settings on disk, or why a mod breaks after a client update. Complements gameface-wulf-primer, which covers only the Gameface/Wulf UI layer — this is the broader foundation: packaging, loading, patching, and the ecosystem.
---

# WoT client modding: how it actually works

Conceptual reference distilled from building and packaging a real shipped mod (an
in-battle armor/penetration calculator: Python game-logic patches + a Gameface overlay +
a settings-panel integration). General to WoT modding as a discipline — not tied to any
one mod's features. For the Gameface/Wulf UI stack specifically, see
`gameface-wulf-primer`.

## There is no official modding API

World of Tanks (Wargaming, built on the BigWorld/Core engine) ships its own client-side
game logic as Python — historically Python 2.7, embedded in the client executable. WG
does not publish a modding SDK. "Modding" means:

1. Decompiling WG's shipped `.pyc` client scripts (community tooling exists for this)
   to read what the stock code actually does.
2. Dropping your own Python file(s) at a matching path so the client's own import
   machinery loads yours **instead of, or alongside**, WG's.
3. **Monkey-patching**: reassigning attributes on WG's already-imported classes/modules
   at your mod's import time — swapping a method, wrapping a function, subscribing to an
   event bus. There's no plugin registry, no hook manifest, no versioned interface
   contract. If WG restructures the function you patched in a later patch, your mod
   silently breaks (wrong result, exception swallowed by a broad `except`, or a
   `LOG_CURRENT_EXCEPTION()` in the log and nothing visibly happening).

This is why WoT modding knowledge lives in forums/Discords/GitHub rather than docs —
everyone is working from the same decompiled source, and stock behavior changes
underneath mods every content patch.

## Two install locations, and precedence

```
<WoT install>\mods\<version>\<author>.<name>_<ver>.wotmod   <- packaged, real ZIP
<WoT install>\mods\configs\...                              <- NOT version-scoped; shared config trees (res_map, per-mod settings)
<WoT install>\res_mods\<version>\...                         <- loose, unpacked files
```

- **`res_mods\<version>\`** — loose files laid out exactly as they'd sit inside a
  `.wotmod`'s `res/` folder (minus the `res/` prefix itself). **These outrank packed
  `.wotmod`s** for the same relative path — fastest iteration loop for development,
  no zipping, no `meta.xml` needed to just test a script change.
- **`mods\<version>\*.wotmod`** — the real distributable form users install.
- `<version>` is the exact client version string (e.g. `2.3.1.1`) the mod targets.
  **Get this wrong and the override is silently never loaded** — no error, the stock
  behavior just runs as if the mod weren't installed. This is the single most common
  "my mod doesn't do anything" bug report in this ecosystem.
- Some paths are NOT version-scoped even though they look like they should be —
  `mods\configs\res_map\` (Gameface view registration) and other `mods\configs\...`
  trees live directly under the install root, one level up from any `<version>` folder.

## The `.wotmod` package format

A `.wotmod` is a **plain ZIP archive using STORE (no compression)** — the client
rejects `.wotmod`s built with DEFLATE, so packaging tools must explicitly force
zero-compression (e.g. PowerShell's `[System.IO.Compression.CompressionLevel]::NoCompression`,
or `zipfile.ZIP_STORED` in Python). Layout, confirmed from an actual shipped package:

```
meta.xml                                   <- at the ZIP ROOT, not inside res/
res/scripts/client/gui/mods/mod_x.pyc
res/gui/...
res/mods/configs/res_map/...
```

`meta.xml`:

```xml
<root>
    <id>com.author.modname</id>      <!-- reverse-domain-style, globally unique -->
    <version>1.2.3</version>          <!-- compared character-by-character (ASCII) -->
    <name>Human-readable name</name>
    <description>Shown in the in-game mod manager / launcher.</description>
</root>
```

- `id` also controls **grouping/load order** relative to other packages sharing the
  same id — the client treats same-id `.wotmod`s as versions of one mod (picks the
  highest `<version>`, by ASCII comparison — zero-pad segments so `"9" < "10"` sorts
  correctly as strings).
- A missing or malformed `meta.xml` tends to make a mod invisible to the client's mod
  manager rather than throwing a loud error — check this first if a packaged mod "isn't
  there" even though the file exists in `mods\<version>\`.

## Auto-loaded scripts vs. shadowed stock modules

`scripts/client/gui/mods/` is special: WG's own client code scans that directory and
**auto-imports every module it finds** (by convention `mod_*.py`, though the scan isn't
strictly name-filtered) — this is the one place a mod can add a brand-new entry point
with zero coordination with any other mod.

Everywhere else, a file only takes effect because it sits at the **exact same relative
path** as a stock module, and your version **fully replaces** WG's (or another mod's) at
that path — there is no merge, no super-call, no chaining. Two mods that both ship a
same-path override of a stock module conflict outright; whichever lands last in file
resolution order wins, silently overwriting the other's patch. This is why the idiomatic
pattern is: ship one small `mod_*.py` entry point (auto-loaded, low collision risk) that
then monkey-patches stock classes at runtime from Python, rather than shipping a
wholesale replacement of a stock module file.

Typical monkey-patch shape (reassign an already-bound attribute after import):

```python
from AvatarInputHandler import gun_marker_ctrl

original = gun_marker_ctrl._CrosshairShotResults.getShotResult.__func__

def my_version(cls, gunMarker, excludeTeam=0, piercingMultiplier=1):
    result = original(cls, gunMarker, excludeTeam, piercingMultiplier)
    # ... extra behavior ...
    return result

gun_marker_ctrl._CrosshairShotResults.getShotResult = classmethod(my_version)
```

- Capture `original` before overwriting — that's your only way to still call stock
  behavior; there's no `super()` path back to a monkey-patched attribute.
- Private/name-mangled attributes (`__foo` inside a class body) are still reachable from
  outside as `_ClassName__foo` — needed constantly when patching functions that call
  other "private" methods on the same class.
- Hooking into game events (rather than a single function) goes through WG's own
  observer-pattern buses, e.g. `PlayerEvents.g_playerEvents.onAvatarBecomePlayer += fn`
  (`+=` is WG's `Event` idiom, not a normal Python callable list) — spawn/despawn,
  vehicle destroyed, match start/end, etc. all have events like this; grep decompiled
  source for `g_playerEvents` or `g_currentVehicle` methods to find the right one rather
  than guessing.

## Python 2.7, and the stale-bytecode trap

The embedded interpreter is (for all WoT versions this applies to) **Python 2.7** —
bytecode is version-locked, so source must be compiled with a matching 2.7 toolchain
(`python27 -m py_compile foo.py` → `foo.pyc`) before it'll load; a mod written against
Python 3 syntax won't run at all.

**Never leave both `foo.py` and `foo.pyc` at the same destination path.** Which one the
import machinery picks is not guaranteed to be "the newest" — a stale sibling of either
kind can shadow a freshly rebuilt file and the mod silently keeps running old logic.
Delete both before every redeploy, or have the build script do it.

## Third-party mod frameworks: treat as optional, soft dependencies

Because there's no official API, the community has filled the gap with its own shared
libraries that many independent mods depend on. None of these are guaranteed to be
installed — a mod should degrade gracefully (or clearly declare the dependency) rather
than assume presence:

- **OpenWG Gameface** (`openwg_gameface`) — patches the client to let third-party mods
  register their own Gameface views (`res_map`, `ModDynAccessor`). See
  `gameface-wulf-primer` for the full mechanics.
- **ModsSettingsApi** (`gui.modsSettingsApi`, by izeberg) — a shared in-game settings
  panel other mods plug into instead of building their own settings UI:

  ```python
  from gui.modsSettingsApi import g_modsSettingsApi, templates

  mod_linkage = "my_mod_id"          # unique key identifying this mod's panel
  template = {
      "modDisplayName": "My Mod",
      "enabled": True,
      "column1": [templates.createCheckbox("Enable Foo", "foo_enabled", True, tooltip="...")],
  }

  def on_settings_save(linkage, new_settings):
      if linkage == mod_linkage:
          ...  # apply new_settings[...] to your own live config

  g_modsSettingsApi.setModTemplate(mod_linkage, template, on_settings_save, None)
  ```

  The template's field keys (`"foo_enabled"` above) are exactly the keys `new_settings`
  comes back with in the save callback — they're your own naming choice, not fixed by
  the API.
- **ModsListApi** (by poliroid) — a shared "installed mods" listing/menu surface, same
  spirit as ModsSettingsApi but for mod discovery rather than configuration.

These ship as their own `.wotmod`s (visible sitting alongside a project's own package in
a WoT install's `mods\<version>\` folder) and must be installed for a dependent mod to
actually do anything — a mod that hard-imports one of these at module scope with no
guard will raise on load if the dependency is missing, taking the whole mod down instead
of just the integration.

## Where a mod should persist its own settings

The client process's working directory is the WoT install root, so a relative path from
Python code lands there — the community convention is a per-author folder under
`mods\configs\`, not the user's AppData or Documents:

```python
CONFIG_FOLDER = os.path.join("mods", "configs", "<author>")
CONFIG_PATH = os.path.join(CONFIG_FOLDER, "<mod-name>.json")
```

Plain JSON via the stdlib `json` module is typical — no special serialization API is
provided. Because this lives outside any `<version>`-scoped folder, settings persist
across WoT client updates even though the mod package itself has to be redeployed to the
new version's `res_mods`/`mods` folder. Write a small migration step (fill in missing
keys from defaults rather than overwriting the whole file) since a returning user's
on-disk config will predate newer settings your mod adds later — and wrap the initial
load in a try/except that falls back to regenerating defaults, since a half-written or
manually-edited config file is a realistic failure mode, not a hypothetical.

## Why mods break on client updates, and what to check first

WoT ships content patches roughly every couple of months. Common breakage modes, roughly
in order of likelihood:

1. **Version folder mismatch** — `res_mods\<old-version>\` no longer matches the
   running client; the override is silently ignored. Fix: redeploy under the new
   version string (or, if the platform supports it, a wildcard/latest folder).
2. **Decompiled-target drift** — the stock function a mod monkey-patches got
   restructured (renamed locals, reordered branches, new parameters). The patch either
   throws (visible in `python.log` if the mod's own code isn't over-broadly catching
   exceptions) or runs but silently produces wrong results. Fix: re-decompile the
   current version's stock module and diff against what the patch assumes.
3. **Dependency mod not yet updated** — OpenWG Gameface / ModsSettingsApi / etc. lag
   behind a fresh WoT patch by days; a dependent mod looks broken but the actual fault
   is upstream. Check the dependency's own changelog/Discord before assuming your own
   code regressed.

`python.log` (WoT install root, or the user's WoT profile folder depending on client
config) is the first place to look — WG's own `LOG_CURRENT_EXCEPTION()` idiom, which
most mods borrow, writes a full traceback there rather than surfacing anything in-game.
