// APBattleView.js -- reads this view's own root ViewModel (APBattleVM: per-row
// armorText/armorVisible/armorColor, probText/probVisible/probColor,
// angleText/angleVisible/angleColor) and paints the three label rows already
// in the HTML, each shown/hidden independently. No feature name in
// ModelObserver(): this page IS the view's root model (a standalone registered
// window), not a submodel injected into someone else's document.
// libs/model.js is a SHARED file OpenWG ships at a fixed location:
// gui/gameface/mods/libs/model.js. This view now lives at gui/AP_Calculator_2/gameface/,
// a sibling branch of gui/gameface/ -- not nested under gui/gameface/mods/ anymore --
// so the path back to that fixed shared lib is "up to gui/, then down into
// gameface/mods/libs/model.js", not a plain "../../libs/model.js".
import { ModelObserver } from "../../gameface/mods/libs/model.js";

const observer = ModelObserver();

const armorEl = document.getElementById("armor-label");
const probEl = document.getElementById("prob-label");
const angleEl = document.getElementById("angle-label");
const bgEl = document.getElementById("label-bg");
const trackEl = document.getElementById("track-indicator");


// display:"" defers to the CSS default (shown), "none" drops it from layout
// entirely -- same trick the old body-level toggle used, just per-element now.
function renderRow(el, text, visible, color) {
    el.style.display = visible ? "" : "none";
    if (!visible) {
        return;
    }
    el.textContent = text || "";
    el.style.color = color ? "#" + color : "";
}

function render(model) {
    if (!model) {
        bgEl.style.display = "none";
        armorEl.style.display = "none";
        probEl.style.display = "none";
        angleEl.style.display = "none";
        trackEl.style.display = "none";
        return;
    }

    const armorVisible = model.armorVisible;
    const probVisible = model.probVisible;
    const angleVisible = model.angleVisible;

    renderRow(armorEl, model.armorText, armorVisible, model.armorColor);
    renderRow(probEl, model.probText, probVisible, model.probColor);
    renderRow(angleEl, model.angleText, angleVisible, model.angleColor);

    trackEl.style.display = model.trackVisible ? "" : "none";

    // Background box tracks whichever row is visible; borrows armor's color
    // (falling back through prob/angle) since it no longer has its own.
    const anyVisible = armorVisible || probVisible || angleVisible;
    bgEl.style.display = anyVisible ? "" : "none";
}

// The window's surface size is set by the page, not Python -- a page that never
// asks gets the engine's 256x256 fallback after a "Size calculation timeout".
// Declare it explicitly instead; must match html/body width/height in
// APBattleView.css (logical px, same units as window.move on the Python side).
const VIEW_WIDTH = 256;
const VIEW_HEIGHT = 256;
// The engine's fallback fires ~2.2s after load and clobbers any earlier resize,
// so push once at mount and again once that deadline has safely passed.
const SURFACE_REASSERT_MS = 4000;

function pushSize() {
    if (typeof viewEnv === "undefined" || !viewEnv) {
        return;
    }
    viewEnv.resizeViewRem(VIEW_WIDTH, VIEW_HEIGHT);
}

engine.whenReady.then(() => {
    pushSize();
    setTimeout(pushSize, SURFACE_REASSERT_MS);

    observer.onUpdate(render);   // called every time Python pushes a change
    observer.subscribe();
    render(observer.model);      // paint immediately with whatever's there now
});
