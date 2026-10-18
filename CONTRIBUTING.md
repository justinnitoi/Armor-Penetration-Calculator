# Contributing

Thanks for helping out. This guide covers how the repository is laid out, how to build and test, and what a good pull request looks like.

Questions are welcome on the [Discord server](https://discord.gg/PrzqyneRXv) or in a GitHub issue.

## Pick the right branch first

This repository contains **two different mods**, released separately. They share no code, so a change for one does not apply to the other.

| Branch | Mod | Notes |
|---|---|---|
| `v2` | Armor Penetration Calculator 2 | Gameface (HTML/JS) overlay. Built with `build/build.py`. |
| `v1` | Armor Penetration Calculator (original) | GUIFlash overlay. Built with the PowerShell scripts in `build/`. |

- Branch off the mod's branch (`v1` or `v2`) and open your pull request **against that same branch**.
- If a fix applies to both mods, open **two pull requests**, one per branch. Each needs its own port, since the code is different.
- Say which mod the PR is for in the title, for example `[v1] Fix angle label color` or `[v2] Add Japanese translation`.
- Other branches (such as `wot-src-watch`) hold automation state. Don't target them.

## Ways to contribute

- **Bug reports.** Open an issue with: which mod (v1 or v2) and its version, your game client version and region, other mods you have installed, what you expected versus what happened, and the relevant part of `python.log` from your WoT folder (search it for the mod's name or `Traceback`).
- **Translations** (v2). Copy `src/res/gui/AP_Calculator_2/translations/translations_en.json` to `translations_<locale>.json`, or fix an existing one. Keep every key, translate only the values. A new language also needs its code added to `SUPPORTED_LANGUAGES` in `settings_gui/language.py`. This is a good first contribution.
- **Fixes after a game update.** The mod patches stock client code, so client updates can break it. `CLAUDE.md` lists every game file the v2 mod depends on and what to diff after an update.
- **Features.** For anything bigger than a small fix, open an issue first so we can agree on the approach before you put time in.

## Development setup (v2)

You need:

- **Python 3.6+** to run the build script.
- **Python 2.7** to compile the mod, because the game client only loads Python 2.7 bytecode. The script finds `python27`, `python2.7`, or `python2` on your `PATH` (on Windows it also checks `C:\Program Files\Python27\python.exe`), or you can pass `--python27 /path/to/python2.7`.
- A World of Tanks install, version 2.4.1 or newer, with OpenWG Gameface installed.

### Build and test

```
# Compile and copy loose files into res_mods/ of your game install (fast iteration)
python build/build.py deploy --wot-root "C:/Program Files/World_of_Tanks_NA" --version 2.4.1.0

# Remove everything deploy put there
python build/build.py uninstall --wot-root "C:/Program Files/World_of_Tanks_NA" --version 2.4.1.0

# Build a real .wotmod into bin/wotmods/
python build/build.py package
```

Close the game client before deploying (it locks its files), and use an elevated shell if your install is under `Program Files`.

```
# Run the offline tests (Python 2.7; downloads one stock game file into tests/.cache/ the first time)
python build/build.py test
```

The tests check the armor math against the game's own shot-result code, plus the config, overlay state and translations. CI runs them on every pull request. They can't see the overlay itself, so also test in game: deploy, launch the game, and go into a battle (the Training Room or a Topography Lesson works well). Check the overlay with the shell types and situations your change affects, and check `python.log` for errors.

### Code layout

- `src/res/scripts/client/gui/mods/mod_AP_Calculator.py`: the entry point the game loads.
- `src/res/scripts/client/ap_calculator/core/`: shot-result hooks (`ap_hooks.py`) and the penetration math (`ap_math.py`).
- `src/res/scripts/client/ap_calculator/gui/`: settings schema (`ap_config.py`), constants, and the Gameface bridge.
- `src/res/scripts/client/ap_calculator/settings_gui/`: the in-garage settings panels.
- `src/res/gui/AP_Calculator_2/`: the overlay's HTML/CSS/JS, tooltip images, and translations.

`CLAUDE.md` goes into much more depth on the architecture and is worth reading before a non-trivial change.

## Development setup (v1)

v1 uses the PowerShell scripts in `build/` on that branch (`build.ps1`, `package.ps1`, `uninstall.ps1`), which expect `python27` on your `PATH` and a default NA install path. Edit the path at the top of the script if your install is elsewhere. It also needs GUIFlash installed in the client.

## Pull request guidelines

- Keep each PR focused on one change. Separate unrelated fixes into separate PRs.
- Match the style of the surrounding code. Code must run on **Python 2.7**: no f-strings, type hints, or other Python 3 only syntax.
- In the description, say what you changed and why, and **how you tested it in game**, including the client version.
- Don't change the mod's version number, and in v2 never edit the version in `src/meta.xml`. The maintainer bumps versions at release time (in v2 the only source is `VERSION` in `ap_calculator/debug.py`).
- Don't commit build output (`bin/`, `*.pyc`).
- Don't add new network requests or collect any new player data. The single telemetry call in `ap_logger.py` is documented in the README, and changes to it need discussion in an issue first.
- Don't add third-party files (fonts, images, code) unless their license allows redistribution, and say where they came from.

## License

By submitting a contribution, you agree that it is licensed under the [GNU General Public License v3.0](LICENSE), the same license as the rest of the project.
