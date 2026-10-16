# Armor Penetration Calculator 2

A World of Tanks mod that shows, while you aim, the effective armor of the spot under your reticle, your exact chance to penetrate it, and the impact angle.

<img width="284" alt="100% penetration chance" src="images/m4-100%25.png" />
<img width="284" alt="34% penetration chance" src="images/m4-34%25.png" />
<img width="284" alt="1% penetration chance" src="images/m4-1%25.png" />

*Screenshots taken with a 125 mm penetration AP shell.*

## Two mods, two branches

This repository holds two separate mods that are released separately:

| Branch | Mod | UI technology |
|---|---|---|
| [`v2`](../../tree/v2) | **Armor Penetration Calculator 2** (this README) | Gameface (HTML/JS) overlay, needs OpenWG Gameface |
| [`v1`](../../tree/v1) | **Armor Penetration Calculator** (the original) | GUIFlash overlay (needs GUIFlash) |

Each branch has its own code, build scripts, and releases. Pick the branch for the mod you want to download or contribute to.

## Features

- Effective armor value computed from the game's own shot calculation: shell normalization, ricochet angles, overmatch, spaced armor, and HEAT/HE behavior.
- Exact penetration probability. A shell's penetration rolls on a Gaussian distribution between 75% and 125% of its average (±25% is the 3-sigma point), so the chance is calculated, not guessed.
- Impact angle, so you can see when a slight change turns a ricochet into a pen.
- Customizable colors, a color gradient, a colorblind palette, and per-label toggles.
- Light on performance: it reuses the calculations the client already does every frame.

## Requirements

- World of Tanks **2.4.1** or newer.
- OpenWG Gameface. **Required**: without it the overlay never appears.
- Optional, for an in-garage settings panel: [Aslain's Mod Menu](https://github.com/Aslain/modmenu) or ModsSettingsApi.

## Installation

1. Download the `.wotmod` file from the [latest release](../../releases), or from the [Discord server](https://discord.gg/PrzqyneRXv).
2. Put it in `World_of_Tanks/mods/<game version>/` (for example `mods/2.4.1.0/`).
3. Make sure OpenWG Gameface is installed too.
4. Launch the game. The labels appear when you aim at an enemy tank.

Settings are stored in `mods/configs/pademinune/Armor Penetration Calculator 2/config.json`. Delete that file to reset to defaults.

## Telemetry

Once per game launch, when the garage first loads, the mod sends one request to `wot-telemetry.onrender.com` containing your **player name, server, and mod version**. It is used only to count how many people use each version. It sends nothing else and nothing during battles. You can read the code in [`ap_logger.py`](src/res/scripts/client/ap_calculator/ap_logger.py).

## Building from source

You need Python 3.6+ to run the build script and Python 2.7 to compile the mod (the game only loads 2.7 bytecode).

```
python build/build.py package                     # -> bin/wotmods/*.wotmod
python build/build.py deploy --wot-root "C:/Program Files/World_of_Tanks_NA"
python build/build.py uninstall --wot-root "C:/Program Files/World_of_Tanks_NA"
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full development workflow.

## Contributing

Bug reports, fixes, translations, and features are welcome, for either mod. Read [CONTRIBUTING.md](CONTRIBUTING.md) first, especially the section about which branch to target.

## Support

Questions and support: [Discord](https://discord.gg/PrzqyneRXv). Like the mod? [Support it on Ko-fi](https://ko-fi.com/pademinune).

## License

Copyright (C) 2026 pademinune (Justin Nitoi).

The mod's source code is licensed under the [GNU General Public License v3.0](LICENSE). You can use, modify, and redistribute it, but any version you distribute must also be released under GPL-3.0 with its source code available.

**Not covered by this license:**

- **Fonts** (`*.ttf` files, such as PF DIN Max and Warhelios) belong to their respective owners. They are included only for in-game rendering and are not licensed under GPL-3.0.
- **World of Tanks** and its assets, names, and client code belong to Wargaming. Parts of `core/ap_hooks.py` are adapted from the game client's own code so the mod can extend it. This project is not affiliated with or endorsed by Wargaming.
