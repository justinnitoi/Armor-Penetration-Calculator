# Roadmap

What is planned for **Armor Penetration Calculator 2** (the `v2` branch), in the order it is planned to ship. Each phase is its own release. The plan can change. If you want to work on an item, open an issue first so work isn't duplicated (see [CONTRIBUTING.md](CONTRIBUTING.md)).

The order is: make the mod unable to break the game, make it trustworthy, make it more useful, then make it easier to maintain.

## Phase 1: Reliability

**Status: merged into `v2` ([#12](../../pull/12)), not yet released.**

Goal: the mod can never make the game worse than vanilla.

- [x] The stock shot-result code is wrapped, never replaced. The reticle's coloring is always exactly the game's own, and an error in the overlay is logged once and can't reach the reticle.
- [x] Startup compatibility check: if a client update removes or changes something the mod relies on, the mod logs "incompatible" and disables itself cleanly instead of misbehaving.
- [x] With the server reticle enabled, the overlay follows only the server marker, so it no longer flickers between client and server results.
- [x] Track indicator now works in colorblind mode and with custom colors. The 7% / 93% thresholds are named constants.
- [x] Settings are validated one at a time: an unknown or invalid setting is dropped on its own instead of resetting every setting. The config file now has a version number for future migrations.
- [x] The telemetry request runs in the background, so a slow server can't freeze the garage.
- [ ] Release.

## Phase 2: Tests and tooling (ships with Phase 1)

**Status: done.** Not visible to players.

- [x] Offline test suite (`python build/build.py test`) for the shot analysis, hooks, config, GUI state, math and translations.
- [x] Parity tests against the game's real shot-result code, downloaded from [wot-src](https://github.com/izeberg/wot-src) at a pinned commit and never committed.
- [x] `python2.7 tests/stock.py diff` shows how the stock code changed after a client update.
- [x] Every translation file must have exactly the keys of the English one.
- [x] CI runs the tests and builds the package on every push and PR. A `v*` tag creates a draft GitHub release with the `.wotmod`.

## Phase 3: New features

All of these use data the mod already has. Roughly ordered by value for effort.

- [ ] **Overlay position, scale and background.** Settings for X/Y offset, size, and the background panel.
- [ ] **One-shot / shots-to-kill marker.** An optional tag when a penetration would kill the target, or how many shots it would take. Off by default.
- [ ] **Spaced armor and gun mantlet markers.** When the shot would end in spaced armor, tracks or the mantlet, say so instead of just hiding the numbers.
- [ ] **Modern HE expected damage.** A penetration chance is misleading for modern HE, which always does some damage. Show the estimated damage after absorption instead.
- [ ] **Armor vs. penetration readout.** An optional "245 / 230" format, through a configurable format string.
- [ ] **Configurable thresholds.** User-set cutoffs for the low and high chance colors (currently 7% and 93%).

## Phase 4: Maintainability

- [ ] **One settings schema.** Define each setting once and render it for both Aslain's Mod Menu and ModsSettingsApi, instead of two near-duplicate builders. Adding a setting becomes a one-place change.
- [ ] **One label class.** The armor, chance and angle labels share almost all their code.
- [ ] **Release hygiene.** A `CHANGELOG.md`, a table of compatible client versions in the README, and an issue template that asks for `python.log`.

## Not planned

- Server-side or crowd-sourced features, such as weak-spot heatmaps. They would send more data off the player's machine.
- Changes to the original mod on the `v1` branch. It is a separate mod.
