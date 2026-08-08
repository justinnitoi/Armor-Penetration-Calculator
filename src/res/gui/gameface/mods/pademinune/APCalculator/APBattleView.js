// APBattleView.js -- reads this view's own root ViewModel (APBattleVM: per-row
// armorText/armorVisible/armorColor, probText/probVisible/probColor,
// angleText/angleVisible/angleColor) and paints the three label rows already
// in the HTML, each shown/hidden independently. No feature name in
// ModelObserver(): this page IS the view's root model (a standalone registered
// window), not a submodel injected into someone else's document.
// Two folder segments under mods/ (pademinune/APCalculator/) -> two "../" to libs/model.js.
import { ModelObserver } from "../../libs/model.js";

const observer = ModelObserver();

const armorEl = document.getElementById("armor-label");
const probEl = document.getElementById("prob-label");
const angleEl = document.getElementById("angle-label");
// const bgEl = document.getElementById("label-bg");


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
        return;
    }

    const armorVisible = model.armorVisible;
    const probVisible = model.probVisible;
    const angleVisible = model.angleVisible;

    renderRow(armorEl, model.armorText, armorVisible, model.armorColor);
    renderRow(probEl, model.probText, probVisible, model.probColor);
    renderRow(angleEl, model.angleText, angleVisible, model.angleColor);

    // Background box tracks whichever row is visible; borrows armor's color
    // (falling back through prob/angle) since it no longer has its own.
    // const anyVisible = armorVisible || probVisible || angleVisible;
    // bgEl.style.display = anyVisible ? "" : "none";
    // const bgColor = model.armorColor || model.probColor || model.angleColor;
    // bgEl.style.borderColor = bgColor ? "#" + bgColor + "59" : ""; // ~35% alpha, matches the default CSS border
}

engine.whenReady.then(() => {
    observer.onUpdate(render);   // called every time Python pushes a change
    observer.subscribe();
    render(observer.model);      // paint immediately with whatever's there now
});
