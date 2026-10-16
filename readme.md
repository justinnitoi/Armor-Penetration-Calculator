# Armor Penetration Calculator

<img width="284" height="270" alt="m4-100%" src="https://github.com/user-attachments/assets/bb634f0c-cd3c-4324-bae8-8f33afb2cd0c" />
<img width="300" height="328" alt="m4-34%" src="https://github.com/user-attachments/assets/0ac9168a-ffb3-41e4-a923-fd96e7ee82dd" />
<img width="238" height="233" alt="m4-1%" src="https://github.com/user-attachments/assets/a48185c4-c4fe-46c5-9a62-b7ff40a48450" />

*Photos were taken with a 125mm pen AP shell*

## Overview

For questions or mod support join the [Discord server](https://discord.gg/PrzqyneRXv).

This mod is also on the offical [Wargaming mod portal](https://wgmods.net/7605/).

This mod displays the exact effective armor value, penetration probability, and angle of a tank you are aiming at.

> *How is this different from other effective armor mods?*

- They don't compute and display the exact probability of penetrating.
    - You would have to estimate this in the moment based on your shell's penetration and their armor.
    - This wastes crucial time and is very innacurate (especially since the distribution is not uniform).

- This mod has more features and receives regular updates.
    - If a WOT update modifies the client code in such a way that breaks these mods, this mod will be updated quickly.


> *What is the best way to use this mod?*

Sometimes in battles, it is better to save your shot rather than
taking a chance on an orange pen indicator.
If you try to pen when you have a 20% chance, you will likely bounce
and take a shot in return for nothing.
Instead, it may be better to save your shot for a few seconds until you get
a better opportunity.

Also, when aiming at a well armored tank, with this mod you can find the
optimal spot to shoot that will maximize your chance of penning.

### Features
- Displays the exact effective armor value following game mechanics
    - Shell-specific normalization
    - Ricochet angles
    - Gun caliber overmatching
    - Spaced armor
    - HEAT shell dissipation through spaced armor
- Computes and displays probability of penetration
- Computes and displays probability of killing a low hp tank
    - Takes into account their armor and hp
- Displays the exact armor angle so that you know when to change angles to turn a ricochet into a pen
- Great performance since the mod uses calculations already done by the game
- Customize the mod to your liking by changing the settings

### Config
There is a settings gui for the config you can edit in the garage.

You can also change the display settings (text size, color, position) using the config file found in `mods/configs/pademinune`.
To revert back to default settings, just delete the config file and when you restart the game, the default file will be created again.

## Installation

1. Download `unzip-me.zip` from the [latest release](https://github.com/pademinune/Armor-Penetration-Calculator/releases).

2. Put the zip file in your `mods/x.x.x.x/` folder found in your local
World of Tanks installation folder.

3. Unzip and extract the `.wotmod` files into that folder.

4. Launch World of Tanks and the labels will appear when looking at an enemy
tank.

## Incompatibilities
- Hitmarker mod found in ProMod

## Probability Details

In World of Tanks, a shell's actual penetration is sampled from a Gaussian distribution ranging from 75% to 125% of its average penetration value. The 25% deviation from the mean is treated as the 3-sigma point.

For example, a shell with 100mm average penetration can roll anywhere from 75mm to 125mm, with most rolls clustering near 100mm.

So if you have 400mm penetration, bouncing off targets with under 350mm effective armor is very unlikely.

Credit to this [reddit post](https://www.reddit.com/r/WorldofTanks/comments/4z53s0/infographic_damage_spread_in_world_of_tanks/) for doing
the research and discovering the distribution.

## Two mods, two branches

This repository holds two separate mods that are released separately: this one, the original **Armor Penetration Calculator** (branch [`v1`](../../tree/v1), GUIFlash overlay), and **Armor Penetration Calculator 2** (branch [`v2`](../../tree/v2), Gameface overlay). Each branch has its own code and releases.

## Contributing

Bug reports, fixes, and features are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) first, especially the section about which branch to target.

## License

Copyright (C) 2026 pademinune (Justin Nitoi).

The mod's source code is licensed under the [GNU General Public License v3.0](LICENSE). You can use, modify, and redistribute it, but any version you distribute must also be released under GPL-3.0 with its source code available.

World of Tanks and its assets, names, and client code belong to Wargaming. This project is not affiliated with or endorsed by Wargaming.
