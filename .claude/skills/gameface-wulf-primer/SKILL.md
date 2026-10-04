---
name: gameface-wulf-primer
description: Use when the user wants to understand HOW WoT's Gameface/Wulf UI stack works from first principles (not just this project's specific widgets) — what Wulf/ViewModel/ViewImpl/WindowImpl are, how gui/gen_resources + the native R tree register a mod's own view (and the pre-2.4.1 res_map + ModDynAccessor way), how ModelObserver connects Python to JS, window position vs size mechanics (and the SURFACE_REASSERT_MS timing trap), click-through/hit-test behavior, or how to deploy a NEW standalone Gameface mod (res_mods vs mods, the gui/gen_resources path, Python 2.7 bytecode). Complements the harness skills wotmod-gameface-widget (front-end DOM/CSS conventions) and wotmod-architecture (domain/adapter/bridge layering) — this skill is the conceptual "why does any of this work" layer underneath both, aimed at someone learning the stack rather than editing this project's shipped features. For THIS project's actual battle/garage widgets see moe-battle / moe-garage.
---

# Gameface + Wulf: how the stack actually works

Conceptual reference distilled from a long Q&A session building a minimal test mod
(`simple_label_mod` — a static in-battle text label) from scratch. Use this to answer
"how does X work" questions or to scaffold a new standalone Gameface mod, independent
of the MoE Calculator's own features.

## The layer stack

1. **Coherent Gameface** — third-party HTML/CSS/JS rendering engine (Chromium/Blink-
   derived, GPU-composited) that WG licensed and embedded in the client.
2. **Wulf** (`frameworks.wulf`) — **made by Wargaming**. Their own Python abstraction
   over the engine: `WindowImpl`, `ViewImpl`, `ViewModel`. WG's own developers use this
   for their newer UI screens.
3. **OpenWG GameFace** — **a community-made mod**, not WG's. Before WoT 2.4.1 it was
   the door that let a mod's own view in front of Wulf at all (`res_map` registration,
   `ModDynAccessor`). **Since 2.4.1 the WG client registers mod views natively** (see
   below), and on WG OpenWG is down to: `gf_mod_inject` (injecting CSS/JS into WG's own
   documents) and its shared JS helper libs (`gui/gameface/mods/libs/*.js`, e.g.
   `model.js`'s `ModelObserver`). Its res_map helpers are Lesta-only now; on WG they are
   importable stubs that log a deprecation warning and resolve to `-1`.
4. **Your mod** — Python domain logic + a `ViewModel` + HTML/CSS/JS on top of all three.

## Registering a new view: gen_resources → R → layoutID (WG 2.4.1+)

- The client loads every `gui/gen_resources/*.json` from all mounted resource paths
  (packaged `.wotmod`s and `res_mods\<version>\`) into the shared `R` tree at startup.
  No `res_map.json` rewrite, **no restart dance**. A mod ships one declaration file,
  named after the mod (a mod `images.json` would REPLACE the client's own):

  ```json
  [
      {
          "type": "Layout",
          "id": "R.mods.<your_mod>.views.<Name>",
          "path": "coui://gui/<your_mod>/<Name>.html",
          "parameters": { "entrance": "<Name>", "impl": "gameface" }
      }
  ]
  ```

  Strict JSON (no trailing commas — invalid JSON breaks resource loading for the whole
  UI). IDs start with `R.`, claim your own `R.mods.<mod_id>.*` subtree; first declarer
  of an ID wins, duplicates are skipped with a warning.
- Resolve the numeric `layoutID` natively, via `dyn()` at every step — plain attribute
  access raises `AttributeError` when a node is missing, and `R.mods` itself only
  exists once some mod declares under it:

  ```python
  from gui.impl.gen import R

  def _layout_id():
      node = R
      for name in ("mods", "<your_mod>", "views", "<Name>"):
          node = node.dyn(name)
          if not node:
              return -1   # declaration not loaded (pre-2.4.1 client / not deployed)
      return node()
  ```

  Don't persist numeric IDs between client runs.
- **Pre-2.4.1 / Lesta (legacy):** a `mods/configs/res_map/<Name>.json` fragment with an
  `itemID`, merged into `res_map.json` by OpenWG's `ResMapManager` (one-time client
  restart), resolved with `openwg_gameface.ModDynAccessor(itemID)`. On WG 2.4.1+ this
  path is dead: OpenWG ignores the fragments and `ModDynAccessor()` always returns `-1`,
  so a mod still using it just never opens its window.

## Wulf's three building blocks

| Class | Answers | Owns |
|---|---|---|
| `WindowImpl` | Where on screen, what size, what stacking layer | position, size (indirectly), layer, focus |
| `ViewImpl` | What content (which HTML page) | the loaded document, bound to one ViewModel |
| `ViewModel` | What data flows Python ↔ JS | typed named properties, pushed via transactions |

Bound together at construction:

```python
class MyView(ViewImpl):
    def __init__(self, layout_id):   # from _layout_id() above
        super(MyView, self).__init__(
            ViewSettings(layout_id, ViewFlags.VIEW, MyViewModel()))
    @property
    def viewModel(self):
        return self.getViewModel()

class MyWindow(WindowImpl):
    def __init__(self, content):
        super(MyWindow, self).__init__(
            WindowFlags.WINDOW, content=content, layer=WindowLayer.WINDOW)
    def _onReady(self):
        self.show(focus=False)
```

`_onReady` / `_onLoading` are **framework-invoked hooks** — like `__init__`, nothing in
your own code calls them; the Wulf base class calls `self._onLoading(...)` /
`self._onReady()` internally once the document/window actually reaches that lifecycle
stage (async — not necessarily the same tick as construction).

## ViewModel: the data contract

Typed, named schema shared between Python and JS:

```python
class MyViewModel(ViewModel):
    def __init__(self):
        super(MyViewModel, self).__init__(properties=1, commands=0)
    def _initialize(self):
        super(MyViewModel, self)._initialize()
        self._addStringProperty("text", "")   # index 0, name "text"
    def setText(self, v):
        self._setString(0, v)
```

- Each property has an **index** (Python writes by index via generated setters) and a
  **name** (JS reads by name off `model.<name>`).
- Writes are batched in a **transaction**, which is what actually marshals the change
  and fires JS's update notification:

  ```python
  with rvm.transaction() as tx:
      tx.setText("hello")
  ```

- A transaction is **per-property** — skip a setter and that property simply isn't
  sent. Skip opening the transaction entirely if nothing changed, to avoid the cost.
- **Defaults are visible to JS immediately**, even before any transaction — if a value
  never changes (a static label), just bake it into `_addStringProperty("text", "the
  value")` and skip `push()`/`_onLoading` entirely.
- Optional reverse channel: `self._addCommand("onClick")` lets JS call back into
  Python — needed only for genuinely interactive UI (see "Making it clickable" below).

## The full connection chain

```
gen_resources Layout entry (HTML+CSS+JS bundle)
        ↑ resolved by layoutID (via R.mods.<mod>.views.<Name>())
   ViewImpl  ←──bound at construction──  ViewModel instance
        ↓ window loads the HTML page
   Gameface engine injects a `model` global into that page's JS scope
        ↓
   ModelObserver() wraps that global (from a SHARED lib, not per-mod code)
        ↓
   your render(model) reads named fields, updates the DOM
```

One ViewModel instance, three things pointing at it: the `ViewImpl` that owns it, the
JS page that reads it, and the Python bridge code that writes it (`view.viewModel` is
literally `getViewModel()` handing back the same instance).

## JS side: ModelObserver

```js
import { ModelObserver } from "../libs/model.js";   // path depth matters -- see below

const observer = ModelObserver();

function render(model) {
    let el = document.getElementById("my-label");
    if (!el) {
        el = document.createElement("div");
        el.id = "my-label";
        document.body.appendChild(el);
    }
    el.textContent = (model && model.text) || "";
}

engine.whenReady.then(() => {
    observer.onUpdate(render);   // fires on every Python push
    observer.subscribe();
    render(observer.model);      // paint immediately with whatever's there now
});
```

- **`libs/model.js` import path depth is a real, silent-failure trap.** It's a SHARED
  helper OpenWG ships, sitting at `gui/gameface/mods/libs/model.js` — i.e. one level
  above the `mods/` subfolder. Count YOUR OWN folder depth under `mods/` and use that
  many `../`:
  - `gui/gameface/mods/<name>/View.js` (one segment under mods/) → `"../libs/model.js"`
  - `gui/gameface/mods/<author>/<Name>/View.js` (two segments) → `"../../libs/model.js"`

  Get this wrong and the top-level `import` fails silently — the window/view still
  load fine (that's Python/engine-level, logged separately), but your script never
  executes at all, so nothing ever renders and there's no error shown in-game. If a
  window loads (confirmed in `python.log`: `layoutID` resolved, not `-1`, "Load view"
  logged) but nothing appears, check this path first.

- **Standalone registered view vs injected sub-view** — two different `ModelObserver`
  usages:
  - **Standalone window** (own Layout entry, own window — this pattern): the model
    IS the view's own root → `ModelObserver()` with **no feature name**, read fields
    directly (`model.text`).
  - **Injected sub-view** (`gf_mod_inject` appending into an EXISTING WG document —
    the garage-widget pattern, not covered in depth here): the model is nested under
    a feature name, JS unwraps a named submodel instead.

## WindowImpl: position and size are two unrelated mechanisms

**Position — Python's job, `window.move(...)`**, in **logical GUI-space pixels**
(physical px ÷ interface-scale), not raw screen pixels:

```python
from frameworks.wulf import PositionAnchor
self.move(50, 50, xAnchor=PositionAnchor.LEFT, yAnchor=PositionAnchor.TOP)
```

For proportional/anchored placement (not a fixed offset), self-calibrate: `window.position`
only means something AFTER a move, so clamp to a far sentinel first to read the movable
extent, then place for real:

```python
_FAR = 1 << 20
def _place(window):
    window.move(_FAR, _FAR, xAnchor=PositionAnchor.LEFT, yAnchor=PositionAnchor.TOP)
    max_x, max_y = window.position          # now = movable extent (space - windowSize)
    window.move(100, 100, xAnchor=PositionAnchor.LEFT, yAnchor=PositionAnchor.TOP)
```

**Size — NOT Python's job at all**, despite intuition. There is no Python-side size
setter (`windowSize` writes from Python land silently in `__dict__` and do nothing).
The decompiled client (izeberg/wot-src, `frameworks/wulf/windows_system/window.py`)
confirms it: `Window.size` only reads `proxy.windowSize` from the native window, and
size changes arrive FROM native via `Window._cResized(width, height)`, which fires
`onSizeChanged(uniqueID, width, height)`. The PAGE pushes its own size via a JS global:

```js
viewEnv.resizeViewRem(width, height);   // logical px ("rem"), same units as window.move
```

A view that never calls this gets the engine's fallback: a flat **256×256** logical-px
default after a "Size calculation timeout."

**The timing trap** (confirmed live-measured in the MoE Calculator's `MoEBarTransient.js`,
and again in this mod's `APBattleView.js` on client 2.4.0.x): pushing the size once is NOT
enough. The surface stays 256×256 at first, the engine still logs `Size calculation
timeout. Set the default view size.` even though the page called `resizeViewRem` at
mount, and only the delayed second push actually lands — the window visibly switches
to the requested size a few seconds in. Fix: push at mount, then push AGAIN after the
fallback's deadline has passed:

```js
const SURFACE_REASSERT_MS = 4000;   // shipped value; comfortably past the observed ~2.2s deadline
function pushSize() {
    if (typeof viewEnv === "undefined" || !viewEnv) return;
    viewEnv.resizeViewRem(viewW, viewH);
}
engine.whenReady.then(() => {
    pushSize();
    setTimeout(pushSize, SURFACE_REASSERT_MS);
});
```

Only bother with this if you actually need a surface bigger than 256×256 — a short
label doesn't. Once JS resizes, Python finds out via `onSizeChanged` (subscribe with
`self.onSizeChanged += handler`, WG's `+=` idiom for a Wulf window Event) — useful if
your position math depends on the real size. The handler receives `(uniqueID, width,
height)`, so logging it is the reliable way to see what size actually took effect:
`self.onSizeChanged += lambda _uid, w, h: LOG_NOTE("[mod] window size ->", w, h)`.

**Content exceeding the surface is CLIPPED**, not truncated with an ellipsis or
auto-shrunk — the window is a fixed-size render surface (like a texture), not a
scrollable viewport. Content outside its pixel bounds is simply not drawn, silently.
Normal CSS wrapping still applies within the visible area (long text wraps instead of
overflowing horizontally, unless `white-space: nowrap`), but wrapped lines that push
past the surface's HEIGHT are clipped the same way. For predictable behavior on
variable-length content, use explicit CSS truncation (`white-space: nowrap; overflow:
hidden; text-overflow: ellipsis; max-width: ...`) rather than relying on the surface
happening to be big enough.

## Click-through / input-stealing

**A window's RECTANGLE is a solid hit-test target by default — it is NOT click-through
out of the box.** Two separate hit-test layers:

- **Inside the page** (DOM-level): `pointer-events: none` in CSS works normally — stops
  YOUR elements from being click targets for the page's own event handling.
- **The window's rectangle** (engine-level, cross-surface): a completely different
  hit-test the engine runs to decide which window owns a click at a screen location.
  `pointer-events: none` has **zero effect** here. If your window's rectangle is
  topmost at that screen position, the engine still considers it hit — regardless of
  what's drawn inside it.

The only real fix is geometric: **keep the window's rectangle small** (content-sized,
not `WINDOW_FULLSCREEN`) so the area that could ever intercept a click is tiny. A
full-screen window — even with every element `pointer-events:none` — captures mouse
hit-testing across the WHOLE screen whenever the cursor is raised (Ctrl in battle).

Layer also matters: `WindowLayer.WINDOW` (7) sits below the modal in-battle menu
(`TOP_WINDOW`, 10); `WindowLayer.OVERLAY` (11) sits above it and can starve the menu of
keyboard input if your window ends up as the input sink. Use `WINDOW`, not `OVERLAY`,
for a passive HUD overlay.

`self.show(focus=False)` keeps the window from grabbing keyboard focus at all — a
non-interactive overlay should always use this.

## Making it clickable

Fully supported (WG's own garage screens do exactly this) — this test mod deliberately
avoids it. To add a real button/menu:
- Drop `pointer-events: none` on the interactive element (or set it back to `auto`).
- Let the window accept focus/input (don't force `focus=False` unconditionally).
- Keep the window's clickable footprint tight to just the interactive area — battle is
  a risky context for this (a stray click meant for your button could fire the gun or
  hit the wrong menu instead); garage is safer to build interactive UI in.
- Pure visual reveal (a dropdown that's just DOM/CSS state) needs no Python involvement
  — a click listener toggling a class, same as any `render()` already toggles
  `style.display`.
- Something Python needs to react to needs a `ViewModel` **command**
  (`self._addCommand("onClick")`) — the reverse channel.

## One window can host only one ViewImpl

`WindowImpl(..., content=<one view>, ...)` — always singular, no evidence anywhere of
multiple views per window. The real MoE Calculator runs **three separate** Window+View+
ViewModel trios simultaneously for its three screen-scattered UI elements (corner
overlay, centre-screen progress bar, centre-screen efficiency bar) — but WITHIN the
corner overlay, its three stacked rows (damage/percent/assist) all live in ONE window,
as DOM siblings inside one document.

**Rule of thumb**: labels close together (a stack in one corner) → one small `ViewImpl`
with multiple DOM elements. Labels scattered across the screen → one Window+View+
ViewModel trio PER region — each needs its OWN `Layout` entry with its own `R.mods.*`
id (a duplicate id is skipped, making one layout unreachable), its own open/close
lifecycle.

## Deploying a standalone test mod

Two destinations inside a WoT install, and loose files win:

- **`mods/<version>/`** — packaged `.wotmod` files (real ZIP_STORED archives; WoT
  rejects compressed archives). The "real" distribution form.
- **`res_mods/<version>/`** — **loose, unpacked files, and these OUTRANK `.wotmod`
  packages.** Fastest path for testing: no zip, no `meta.xml`, no Python compilation
  needed in principle (the client's embedded Python 2.7 can import raw `.py` directly)
  — though compiling with Python 2.7 first (`python27 -m py_compile foo.py` → `foo.pyc`)
  is safer and matches how this project's own build does it.

Loose-file layout (no `res/` prefix — that only exists inside a packaged `.wotmod`'s
ZIP root):

```
res_mods\<version>\gui\gen_resources\<your_mod>.json      <- view registration (2.4.1+)
res_mods\<version>\gui\<your_mod>\...                      <- html/css/js
res_mods\<version>\scripts\client\gui\mods\mod_x.py       <- or .pyc
```

(Pre-2.4.1 the registration instead lived at `<WoT install>\mods\configs\res_map\`,
outside any version folder — only relevant for Lesta / old clients now.)

**Gotchas**:
- `Program Files` is write-protected — deploying there needs an elevated (Administrator)
  shell.
- **Never leave both `.py` and `.pyc` for the same module in the destination** — a stale
  sibling of either kind can shadow the fresh one and you silently run old code. This
  project's own `build/build.py deploy` deletes a stale `.py` before copying each `.pyc`.
- `gen_resources` declarations are read at client startup, so ADDING a new one (or a
  new id) needs a client restart; JS/CSS/Python edits generally take effect on the next
  battle without a restart — when in doubt, restart.
- **Troubleshooting a window that loads (per `python.log`) but shows nothing**: check
  the `ModelObserver` import path depth first (see above) — a failed top-level JS
  import fails completely silently from the game's perspective.

## Minimal worked example: a static in-battle label

Five files. The window/view/JS parts were proven to load under the pre-2.4.1 res_map
registration; the registration below is the 2.4.1+ `gen_resources` equivalent. A
debugged import-path bug is folded in already. Use as a scaffold for any new standalone
Gameface window.

**`res/gui/gen_resources/simple_label.json`**
```json
[
    {
        "type": "Layout",
        "id": "R.mods.simple_label.views.SimpleLabelView",
        "path": "coui://gui/gameface/mods/simple_label/SimpleLabelView.html",
        "parameters": { "entrance": "SimpleLabelView", "impl": "gameface" }
    }
]
```

**`res/gui/gameface/mods/simple_label/SimpleLabelView.html`**
```html
<!doctype html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <title>SimpleLabelView</title>
        <link rel="stylesheet" href="SimpleLabelView.css" />
    </head>
    <body>
        <script type="module" src="SimpleLabelView.js"></script>
    </body>
</html>
```

**`res/gui/gameface/mods/simple_label/SimpleLabelView.css`**
```css
body { margin: 0; background: transparent; pointer-events: none; }
#simple-label {
    display: inline-block; padding: 6px 10px;
    font-family: Arial, sans-serif; font-size: 20px; color: #ffffff;
    text-shadow: 0 0 4px rgba(0, 0, 0, 0.85);
}
```

**`res/gui/gameface/mods/simple_label/SimpleLabelView.js`**
```js
// ONE folder segment under mods/ (mods/simple_label/) -> ONE "../" to libs/model.js.
import { ModelObserver } from "../libs/model.js";

const observer = ModelObserver();

function render(model) {
    let el = document.getElementById("simple-label");
    if (!el) {
        el = document.createElement("div");
        el.id = "simple-label";
        document.body.appendChild(el);
    }
    el.textContent = (model && model.text) || "";
}

engine.whenReady.then(() => {
    observer.onUpdate(render);
    observer.subscribe();
    render(observer.model);
});
```

**`res/scripts/client/gui/mods/mod_simple_label.py`** (static-default version — no
push needed since the text never changes; see "Defaults are visible to JS immediately"
above)
```python
# -*- coding: utf-8 -*-
from debug_utils import LOG_CURRENT_EXCEPTION
from frameworks.wulf import ViewModel, ViewSettings, ViewFlags, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.pub import ViewImpl, WindowImpl


def _layout_id():
    node = R
    for name in ("mods", "simple_label", "views", "SimpleLabelView"):
        node = node.dyn(name)
        if not node:
            return -1
    return node()


class SimpleLabelVM(ViewModel):
    def __init__(self):
        super(SimpleLabelVM, self).__init__(properties=1, commands=0)

    def _initialize(self):
        super(SimpleLabelVM, self)._initialize()
        self._addStringProperty("text", "Hello from battle!")   # baked-in default


class SimpleLabelView(ViewImpl):
    def __init__(self, layout_id):
        super(SimpleLabelView, self).__init__(
            ViewSettings(layout_id, ViewFlags.VIEW, SimpleLabelVM()))


class SimpleLabelWindow(WindowImpl):
    def __init__(self, content):
        super(SimpleLabelWindow, self).__init__(
            WindowFlags.WINDOW, content=content, layer=WindowLayer.WINDOW)

    def _onReady(self):
        self.show(focus=False)


_active = None


def open_window():
    global _active
    if _active is not None:
        return
    layout = _layout_id()
    if layout < 0:
        return   # gen_resources declaration not loaded
    view = SimpleLabelView(layout)
    window = SimpleLabelWindow(view)
    _active = (window, view)
    window.load()


def close_window():
    global _active
    if _active is None:
        return
    window, _view = _active
    _active = None
    window.destroy()


def _on_avatar_ready(*a, **kw):
    try:
        open_window()
    except Exception:
        LOG_CURRENT_EXCEPTION()


def _on_avatar_teardown(*a, **kw):
    try:
        close_window()
    except Exception:
        LOG_CURRENT_EXCEPTION()


def _install():
    import openwg_gameface  # noqa: F401  -- hard dependency, raises if absent
    from PlayerEvents import g_playerEvents
    g_playerEvents.onAvatarReady += _on_avatar_ready
    g_playerEvents.onAvatarBecomeNonPlayer += _on_avatar_teardown


try:
    _install()
except Exception:
    LOG_CURRENT_EXCEPTION()
```

Deliberately skipped in this scaffold (add only if actually needed): settings toggle,
explicit `window.move` positioning, `viewEnv.resizeViewRem` sizing, re-arm guard on the
listener subscription, live data reads.
